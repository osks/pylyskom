# -*- coding: utf-8 -*-

from pylyskom import kom, komauxitems
from pylyskom.connection import Requests
from pylyskom.komsession import KomSession

from mocks import MockConnection, MockResponse, MockTextStat


# TODO for get_user_area:
#
# Test what happens when:
#
# - person_stat.user_area = 0 (i.e. no user area)
# - text with user area does not exist
# - user area cannot be parsed

def test_get_user_area__example():
    def create_mock_connection():
        c = MockConnection()
        def get_person_stat(*args, **kwargs):
            p = kom.Person()
            p.user_area = 12345 # text number
            return MockResponse(p)
        def get_text_stat(*args, **kwargs):
            ts = MockTextStat()
            ts.creation_time = kom.Time()
            ts.aux_items.append(
                kom.AuxItem(komauxitems.AI_CONTENT_TYPE, data='x-kom/user-area'.encode('ascii')))
            return MockResponse(ts)
        def get_text(*args, **kwargs):
            t = '8H 5Hjskom 70H{"filtered-authors": [17, 4711], "annat": "R\u00e4ksm\u00f6rg\u00e5s"}'.encode('ascii')
            return MockResponse(t)

        c.mock_request(Requests.GetPersonStat, get_person_stat)
        c.mock_request(Requests.GetTextStat, get_text_stat)
        c.mock_request(Requests.GetText, get_text)
        return c
    
    ks = KomSession(host=None, port=None, connection_factory=create_mock_connection)
    ks.connect("test", "localhost", "test", "0.1") # needed to create a connection
    ks.login(17, '') # needed because we change the user area for the logged in person
    
    block = ks.get_user_area_block('jskom')
    
    assert block is not None
    assert 'filtered-authors' in block
    assert 'annat' in block
    assert block['filtered-authors'] == [17, 4711]
    assert block['annat'] == u"Räksmörgås"


