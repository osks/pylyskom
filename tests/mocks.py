from pylyskom.kom import CookedMiscInfo
from pylyskom.request import Requests
from pylyskom.cachedconnection import Cache


class MockResponse(object):
    """Mock of kom.Response
    """
    def __init__(self, resp=None):
        self.resp = resp
    
    def response(self):
        return self.resp


class MockTextStat(object):
    """Mock of kom.TextStat
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
    """Mock of kom.Person
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
        if request not in self.__request_calls:
            self.__request_calls[request] = []
        
        self.__request_calls[request].append(dict(args=args, kwargs=kwargs))

        if request in self.__mocked_requests:
            return self.__mocked_requests[request](*args, **kwargs)
        else:
            # Default is to return an empty MockResponse.
            return MockResponse()

    def mock_request(self, request, func):
        if func is None:
            raise Exception("Mocked request function is None")
        self.__mocked_requests[request] = func

    def mock_get_request_calls(self, request=None):
        if request is None:
            return self.__request_calls
        else:
            return self.__request_calls.get(request, [])
