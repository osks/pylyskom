from pylyskom.kom import CookedMiscInfo
from pylyskom.connection import Requests, Cache


class MockResponse(object):
    def __init__(self, resp=None):
        self.resp = resp
    
    def response(self):
        return self.resp


class MockTextStat(object):
    def __init__(self):
        # Just make sure the properties exist
        self.creation_time = None
        self.author = None
        self.no_of_lines = None
        self.no_of_chars = None
        self.no_of_marks = None
        self.misc_info = CookedMiscInfo()
        self.aux_items = []
        

class MockConnection(object):
    def __init__(self):
        self._pers_no = 0
        self._mocked_requests = dict()
        
        # TODO: We should get a better API in CachedConnection/Connection.
        self.textstats = Cache(self.fetch_textstat, "TextStat")

    def fetch_textstat(self, no):
        return self.request(Requests.GetTextStat, no).response()

    def connect(self, host, port, user):
        pass

    def login(self, pers_no, password):
        self.request(Requests.Login, pers_no, password, invisible=0).response()
        self._pers_no = pers_no

    def logout(self):
        self.request(Requests.Logout).response()
        self._pers_no = 0

    def get_person_no(self):
        return self._pers_no

    def request(self, request, *args, **kwargs):
        if request in self._mocked_requests:
            return self._mocked_requests[request](*args, **kwargs)
        elif request == Requests.SetClientVersion:
            return MockResponse()
        elif request == Requests.WhoAmI:
            return MockResponse(4711) # current session number
        elif request == Requests.Login:
            return MockResponse()
        elif request == Requests.Logout:
            return MockResponse()
        else:
            raise Exception("Unhandled request: %s" % (request,))

    def mock_request(self, request, func):
        if func is None:
            raise Exception("Mocked request function is None")
        self._mocked_requests[request] = func
