from pylyskom import requests
from pylyskom.datatypes import CookedMiscInfo
from pylyskom.cachedconnection import Cache


class MockTextStat(object):
    """Mock of TextStat datatype
    """
    def __init__(self, creation_time=None):
        self.creation_time = creation_time
        self.author = None
        self.no_of_lines = None
        self.no_of_chars = None
        self.no_of_marks = None
        self.misc_info = CookedMiscInfo()
        self.aux_items = []


class MockPerson(object):
    """Mock of Person data type
    """
    def __init__(self, user_area=None):
        self.user_area = user_area


class MockConnection(object):
    """Mock of connection.CachedPersonConnection.
    
    TODO: Make it a mock of connection.Connection by unifying the APIs.
    """
    def __init__(self):
        # Mock specifics
        self.__mocked_requests = dict()
        
        # Key is request. Values are list of {'args': args, 'kwargs': kwargs} dictionaries.
        self.__request_calls = dict()
        
        # Connection specifics
        self._pers_no = 0

        # TODO: We should get a better API in CachedConnection/Connection.
        self.textstats = Cache(self.fetch_textstat, "TextStat")

    def fetch_textstat(self, no):
        return self.request(requests.ReqGetTextStat(no))

    def connect(self, host, port, user):
        pass

    def login(self, pers_no, password):
        self.request(requests.ReqLogin(pers_no, password, invisible=0))
        self._pers_no = pers_no

    def logout(self):
        self.request(requests.ReqLogout())
        self._pers_no = 0

    def get_person_no(self):
        return self._pers_no

    def request(self, request):
        request_no = request.CALL_NO
        if request_no not in self.__request_calls:
            self.__request_calls[request_no] = []

        self.__request_calls[request_no].append(request)

        if request_no in self.__mocked_requests:
            return self.__mocked_requests[request_no](request)
        else:
            # Default is to return None
            return None

    def mock_request(self, request_no, func):
        if func is None:
            raise Exception("Mocked request function is None")
        self.__mocked_requests[request_no] = func

    def mock_get_request_calls(self, request_no=None):
        if request_no is None:
            return self.__request_calls
        else:
            return self.__request_calls.get(request_no, [])

    def conf_name(self, conf_no, default="", include_no=0):
        # FIXME: This is not how it works, but we don't use the result right now.
        return ""


class MockSocket():
    def __init__(self, recv_data=None):
        self.send_data = b""
        self.recv_data = b""
        if recv_data is None:
            recv_data = []
        if isinstance(recv_data, bytes):
            recv_data = [ recv_data ]
        for rd in recv_data:
            assert isinstance(rd, bytes)
            self.recv_data += rd

    def send(self, s):
        assert isinstance(s, bytes)
        self.send_data += s
        return len(s)

    def recv(self, bufsize):
        i = min(len(self.recv_data), bufsize)
        r = self.recv_data[:i]
        self.recv_data = self.recv_data[i:]
        assert isinstance(r, bytes)
        return r

    def close(self):
        pass
