class MockResponse(object):
    def __init__(self, resp):
        self.resp = resp
    
    def response(self):
        return self.resp
