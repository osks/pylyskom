import errno
import logging
import socket
import threading
import time


log = logging.getLogger('pylyskom.stats')


class Stats(object):
    def __init__(self, prefix=None):
        self._lock = threading.RLock()
        self._stats = dict()
        self._prefix = prefix

    def set(self, name, value, agg=None):
        assert agg is not None
        if self._prefix:
            name = self._prefix + name
        with self._lock:
            prev_value = self._stats.get(name)
            if prev_value:
                self._stats[name] = Stats._agg(agg, prev_value, value)
            else:
                self._stats[name] = value

    def dump(self):
        with self._lock:
            return self._stats.copy()

    def reset(self):
        with self._lock:
            old = self._stats
            self._stats = dict()
            return old

    @staticmethod
    def _agg(func, val1, val2):
        if func == 'last':
            return val2
        if func == 'sum':
            return val1 + val2
        elif func == 'min':
            return min(val1, val2)
        elif func == 'max':
            return max(val1, val2)
        elif func == 'avg':
            return (val1 + val2) / 2
        else:
            raise RuntimeError("Unknown aggregation function: {}".format(func))


stats = Stats(prefix='pylyskom.')


class GraphiteTcpConnection(object):
    def __init__(self, host, port=2003, timeout=None):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._socket = None

    def connect(self):
        family, _, _, _, addr = socket.getaddrinfo(
            self._host, self._port, socket.AF_INET, socket.SOCK_STREAM)[0]
        self._socket = socket.socket(family, socket.SOCK_STREAM)
        self._socket.settimeout(self._timeout)
        self._socket.connect(addr)

    def close(self):
        if self._socket is None:
            return
        try:
            self._socket.close()
        except socket.error as e:
            if e.errno in (107, errno.ENOTCONN):
                # 107: Not connected anymore. Didn't find any errno
                # name, but the exception says "[Errno 107] Transport
                # endpoint is not connected".
                pass
            else:
                raise
        finally:
            self._socket = None

    def is_connected(self):
        if self._socket is None:
            return False
        return True

    def reconnect(self):
        self.close()
        self.connect()

    def send(self, metrics):
        if not self.is_connected():
            self.connect()
        data = serialize_graphite_plaintext(metrics)
        try:
            self._socket.sendall(data)
        except socket.error as e:
            # TODO: Attempt to reconnect and send again
            if e.errno in (107, errno.ENOTCONN):
                # 107: Not connected anymore. Didn't find any errno
                # name, but the exception says "[Errno 107] Transport
                # endpoint is not connected".
                self.close()
            elif e.errno in (32, errno.EPIPE): # Broken pipe
                self.close()
            else:
                raise


def serialize_graphite_plaintext(metrics):
    data = b''
    for m in metrics:
        # <metric path> <metric value> <metric timestamp>
        try:
            data += ("%s %s %d\n" % (m[0], m[1], m[2])).encode('ascii')
        except UnicodeDecodeError:
            log.exception("Failed to encode metrics as ascii: %s", m)
            # skip this metric
            continue
    return data


class StatsSender(threading.Thread):
    def __init__(self, statslist, conn, interval):
        threading.Thread.__init__(self)
        self._statslist = statslist
        self._conn = conn
        self._alive = threading.Event()
        self._alive.set()
        self._send_interval = interval

    def run(self):
        def step():
            self._step(time.time())
            return
        def should_continue():
            return self._alive.isSet()
        run_every(self._send_interval, step, should_continue)

    def join(self, timeout=None):
        self._alive.clear()
        threading.Thread.join(self, timeout)

    def _step(self, now):
        dump = merge_dicts([ s.dump() for s in self._statslist ])
        metrics = []
        for m in dump:
            metrics.append((m, dump[m], now))
        self._send(metrics)

    def _send(self, metrics):
        self._conn.send(metrics)


def run_every(interval, func, should_continue_func):
    sleep_max = 1.0
    init_t = time.time()
    init_iv = init_t // interval
    next_iv = init_iv + 1
    next_t = next_iv * interval
    while should_continue_func():
        now_t = time.time()
        now_iv = now_t // interval
        if now_t > next_t:
            func()
            after_t = time.time()
            after_iv = after_t // interval
            # skip interval if func() took more than interval time
            next_iv = max(now_iv, after_iv) + 1
            next_t = next_iv * interval
        after_t = time.time()
        sleep = min(sleep_max, max(0, next_t - after_t))
        time.sleep(sleep)


def merge_dicts(dicts):
    merged = dict()
    for d in dicts:
        merged.update(d)
    return merged
