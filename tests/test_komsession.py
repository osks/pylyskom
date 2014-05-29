# -*- coding: utf-8 -*-

from pylyskom import komauxitems
from pylyskom.request import Requests
from pylyskom.komsession import KomSession
from pylyskom.errors import NoSuchText
from pylyskom.datatypes import AuxItem, Time
from mocks import MockConnection, MockTextStat, MockPerson


# TODO for get_user_area:
#
# Test what happens when:
#
# - person_stat.user_area = 0 (i.e. no user area)
# - text with user area does not exist
# - user area cannot be parsed


def create_komsession(pers_no, connection):
    ks = KomSession(connection_factory=lambda *args, **kwargs: connection)
    ks.connect('host', 'port', "test", "localhost", "test", "0.1")
    ks.login(pers_no, '') # needed because we change the user area for the logged in person
    return ks

def create_mockconnection():
    # Create a MockConnection that response to a GetTextStat call,
    # because we use that a lot in the tests below.
    ts = MockTextStat(creation_time=Time())
    ts.aux_items.append(
        AuxItem(komauxitems.AI_CONTENT_TYPE, data='x-kom/user-area'.encode('ascii')))
    c = MockConnection()
    c.mock_request(Requests.GetTextStat, lambda *args, **kwargs: ts)
    return c


def test_get_user_area__example():
    pers_no = 17
    user_area_text_no = 12345

    p = MockPerson(user_area=user_area_text_no)
    c = create_mockconnection()
    c.mock_request(Requests.GetPersonStat, lambda *args, **kwargs: p)
    c.mock_request(Requests.GetText, lambda *args, **kwargs: '8H 5Hjskom 70H{"filtered-authors": [18, 4711], "annat": "R\u00e4ksm\u00f6rg\u00e5s"}'.encode('latin-1'))
    ks = create_komsession(pers_no, c)
    
    block = ks.get_user_area_block(42, 'jskom')
    
    assert block is not None
    assert 'filtered-authors' in block
    assert 'annat' in block
    assert block['filtered-authors'] == [18, 4711]
    assert block['annat'] == u"Räksmörgås"


def test_get_user_area__gets_the_user_area_for_the_given_person():
    p = MockPerson(user_area=12345)
    c = create_mockconnection()
    ks = create_komsession(17, c)
    c.mock_request(Requests.GetPersonStat, lambda *args, **kwargs: p)
    c.mock_request(Requests.GetText,
                   lambda *args, **kwargs: '8H 5Hjskom 3Hhej'.encode('latin-1'))
    
    
    pers_no = 42
    block = ks.get_user_area_block(pers_no, 'jskom', json_decode=False)
    
    
    assert block == "hej"
    
    get_person_stat_calls = c.mock_get_request_calls(Requests.GetPersonStat)
    assert len(get_person_stat_calls) == 2 # first is for login
    assert get_person_stat_calls[1]['args'][0] == pers_no

    get_textstat_calls = c.mock_get_request_calls(Requests.GetTextStat)
    assert len(get_textstat_calls) == 1
    assert get_textstat_calls[0]['args'][0] == p.user_area

    get_text_calls = c.mock_get_request_calls(Requests.GetText)
    assert len(get_text_calls) == 1
    assert get_text_calls[0]['args'][0] == p.user_area





def test_set_user_area__sets_correct_content_type_on_new_user_area():
    c = create_mockconnection()
    ks = create_komsession(17, c)
    c.mock_request(Requests.GetPersonStat,
                   lambda *args, **kwargs: MockPerson(user_area=0))
    c.mock_request(Requests.CreateText,
                   lambda *args, **kwargs: 67890)


    ks.set_user_area_block(42, 'jskom', {})
    
    
    create_text_requests = c.mock_get_request_calls(Requests.CreateText)
    assert len(create_text_requests) == 1
    ai_cts = [ ai for ai in create_text_requests[0]['args'][2]
               if ai.tag == komauxitems.AI_CONTENT_TYPE ]
    assert len(ai_cts) == 1
    assert ai_cts[0].data == 'x-kom/user-area'


def test_set_user_area__copies_old_user_area_text_if_person_already_has_user_area():
    c = create_mockconnection()
    ks = create_komsession(17, c)
    c.mock_request(Requests.GetPersonStat,
                   lambda *args, **kwargs: MockPerson(user_area=12345))
    c.mock_request(Requests.CreateText,
                   lambda *args, **kwargs: 67890)
    c.mock_request(Requests.GetText, lambda *args, **kwargs: \
                       '17H 6Hcommon 5Hjskom 6Hfoobar 0H'.encode('latin1'))


    ks.set_user_area_block(42, 'jskom', { 'filtered-authors': [18, 4711] })
    
    
    # Check CreateText request
    create_text_requests = c.mock_get_request_calls(Requests.CreateText)
    assert len(create_text_requests) == 1
    assert create_text_requests[0]['args'][0] == \
        '17H 6Hcommon 5Hjskom 6Hfoobar 32H{"filtered-authors": [18, 4711]}'.encode('latin-1')


def test_set_user_area__creates_new_user_area_for_person_that_has_no_previous_user_area():
    pers_no = 42
    new_ua_text_no = 67890
    c = create_mockconnection()
    ks = create_komsession(17, c)
    c.mock_request(Requests.GetPersonStat,
                   lambda *args, **kwargs: MockPerson(user_area=0))
    c.mock_request(Requests.CreateText,
                   lambda *args, **kwargs: new_ua_text_no)


    ks.set_user_area_block(pers_no, 'jskom', { 'filtered-authors': [18, 4711] })
    
    
    # Check CreateText request
    create_text_requests = c.mock_get_request_calls(Requests.CreateText)
    assert len(create_text_requests) == 1
    assert create_text_requests[0]['args'][0] == \
        '8H 5Hjskom 32H{"filtered-authors": [18, 4711]}'.encode('latin-1')

    # Check SetUserArea request
    set_ua_requests = c.mock_get_request_calls(Requests.SetUserArea)
    assert len(set_ua_requests) == 1
    assert set_ua_requests[0]['args'][0] == pers_no
    assert set_ua_requests[0]['args'][1] == new_ua_text_no


def test_set_user_area__person_has_user_area_but_text_does_not_exist():
    user_area_text_no = 12345
    c = create_mockconnection()
    ks = create_komsession(17, c)
    
    c.mock_request(Requests.GetPersonStat,
                   lambda *args, **kwargs: MockPerson(user_area=user_area_text_no))
    def get_text_stat(*args, **kwargs):
        raise NoSuchText(args[0])
    c.mock_request(Requests.GetTextStat, get_text_stat)

    try:
        ks.set_user_area_block(42, 'jskom', {}) # should throw NoSuchText
        assert False
    except NoSuchText as e:
        # this is what should happen
        assert e.args[0] == user_area_text_no
    except:
        assert False

    assert len(c.mock_get_request_calls(Requests.GetText)) == 0
    assert len(c.mock_get_request_calls(Requests.CreateText)) == 0
    assert len(c.mock_get_request_calls(Requests.SetUserArea)) == 0


def test_set_user_area__gets_the_user_area_for_the_given_person():
    pers_no = 42
    c = create_mockconnection()
    ks = create_komsession(17, c)
    c.mock_request(Requests.GetPersonStat,
                   lambda *args, **kwargs: MockPerson(user_area=0))
    c.mock_request(Requests.CreateText, lambda *args, **kwargs: 67890)


    ks.set_user_area_block(pers_no, 'jskom', {})
    
    
    get_person_stat_calls = c.mock_get_request_calls(Requests.GetPersonStat)
    assert len(get_person_stat_calls) == 2 # first is for login
    assert get_person_stat_calls[1]['args'][0] == pers_no


def test_set_user_area__sets_user_area_for_the_correct_person_and_text_no():
    c = create_mockconnection()
    c.mock_request(Requests.GetPersonStat,
                   lambda *args, **kwargs: MockPerson(user_area=0))

    pers_no = 42
    new_ua_text_no = 67890
    c.mock_request(Requests.CreateText,
                   lambda *args, **kwargs: new_ua_text_no)
    c.mock_request(Requests.SetUserArea, lambda *args, **kwargs: None)
    ks = create_komsession(17, c)
    
    
    ks.set_user_area_block(pers_no, 'jskom', {})
    
    
    # Check SetUserArea request
    set_ua_requests = c.mock_get_request_calls(Requests.SetUserArea)
    assert len(set_ua_requests) == 1
    assert set_ua_requests[0]['args'][0] == pers_no
    assert set_ua_requests[0]['args'][1] == new_ua_text_no
