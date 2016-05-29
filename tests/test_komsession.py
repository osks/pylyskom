# -*- coding: utf-8 -*-

from mock import MagicMock

from pylyskom import komauxitems
from pylyskom.requests import Requests
from pylyskom.komsession import KomSession
from pylyskom.errors import NoSuchText
from pylyskom.datatypes import AuxItemInput, Time
from .mocks import MockConnection, MockTextStat, MockPerson


# TODO for get_user_area:
#
# Test what happens when:
#
# - person_stat.user_area = 0 (i.e. no user area)
# - text with user area does not exist
# - user area cannot be parsed


def create_komsession(pers_no, connection):
    ks = KomSession(client_factory=lambda *args, **kwargs: connection)
    ks.connect('host', 'port', "test", "localhost", "test", "0.1")
    ks.login(pers_no, '') # needed because we change the user area for the logged in person
    return ks

def create_mockconnection():
    # Create a MockConnection that response to a GetTextStat call,
    # because we use that a lot in the tests below.
    ts = MockTextStat(creation_time=Time())
    ts.aux_items.append(
        AuxItemInput(tag=komauxitems.AI_CONTENT_TYPE, data='x-kom/user-area'.encode('ascii')))
    c = MockConnection() # really a mock CachingPersonClient
    c.mock_request(Requests.GET_TEXT_STAT, lambda request: ts)
    return c


def test_get_user_area__example():
    pers_no = 17
    user_area_text_no = 12345

    p = MockPerson(user_area=user_area_text_no)
    c = create_mockconnection()
    c.mock_request(Requests.GET_PERSON_STAT, lambda request: p)
    c.mock_request(Requests.GET_TEXT, lambda request: '8H 5Hjskom 70H{"filtered-authors": [18, 4711], "annat": "R\u00e4ksm\u00f6rg\u00e5s"}'.encode('latin-1'))
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
    c.mock_request(Requests.GET_PERSON_STAT, lambda request: p)
    c.mock_request(Requests.GET_TEXT, lambda request: '8H 5Hjskom 3Hhej'.encode('latin-1'))
    
    
    pers_no = 42
    block = ks.get_user_area_block(pers_no, 'jskom', json_decode=False)
    
    
    assert block == "hej"
    
    get_person_stat_calls = c.mock_get_request_calls(Requests.GET_PERSON_STAT)
    assert len(get_person_stat_calls) == 2 # first is for login
    assert get_person_stat_calls[1].pers_no == pers_no

    get_textstat_calls = c.mock_get_request_calls(Requests.GET_TEXT_STAT)
    assert len(get_textstat_calls) == 1
    assert get_textstat_calls[0].text_no == p.user_area

    get_text_calls = c.mock_get_request_calls(Requests.GET_TEXT)
    assert len(get_text_calls) == 1
    assert get_text_calls[0].text_no == p.user_area





def test_set_user_area__sets_correct_content_type_on_new_user_area():
    c = create_mockconnection()
    ks = create_komsession(17, c)
    c.mock_request(Requests.GET_PERSON_STAT, lambda request: MockPerson(user_area=0))
    c.mock_request(Requests.CREATE_TEXT, lambda request: 67890)


    ks.set_user_area_block(42, 'jskom', {})
    
    
    create_text_requests = c.mock_get_request_calls(Requests.CREATE_TEXT)
    assert len(create_text_requests) == 1
    ai_cts = [ ai for ai in create_text_requests[0].aux_items
               if ai.tag == komauxitems.AI_CONTENT_TYPE ]
    assert len(ai_cts) == 1
    assert ai_cts[0].data == 'x-kom/user-area'


def test_set_user_area__copies_old_user_area_text_if_person_already_has_user_area():
    c = create_mockconnection()
    ks = create_komsession(17, c)
    c.mock_request(Requests.GET_PERSON_STAT, lambda request: MockPerson(user_area=12345))
    c.mock_request(Requests.CREATE_TEXT, lambda request: 67890)
    c.mock_request(Requests.GET_TEXT, lambda request: \
                       '17H 6Hcommon 5Hjskom 6Hfoobar 0H'.encode('latin1'))


    ks.set_user_area_block(42, 'jskom', { 'filtered-authors': [18, 4711] })
    
    
    # Check CreateText request
    create_text_requests = c.mock_get_request_calls(Requests.CREATE_TEXT)
    assert len(create_text_requests) == 1
    assert create_text_requests[0].text == \
        '17H 6Hcommon 5Hjskom 6Hfoobar 32H{"filtered-authors": [18, 4711]}'.encode('latin-1')


def test_set_user_area__creates_new_user_area_for_person_that_has_no_previous_user_area():
    pers_no = 42
    new_ua_text_no = 67890
    c = create_mockconnection()
    ks = create_komsession(17, c)
    c.mock_request(Requests.GET_PERSON_STAT, lambda request: MockPerson(user_area=0))
    c.mock_request(Requests.CREATE_TEXT, lambda request: new_ua_text_no)


    ks.set_user_area_block(pers_no, 'jskom', { 'filtered-authors': [18, 4711] })
    
    
    # Check CreateText request
    create_text_requests = c.mock_get_request_calls(Requests.CREATE_TEXT)
    assert len(create_text_requests) == 1
    assert create_text_requests[0].text == \
        '8H 5Hjskom 32H{"filtered-authors": [18, 4711]}'.encode('latin-1')

    # Check SetUserArea request
    set_ua_requests = c.mock_get_request_calls(Requests.SET_USER_AREA)
    assert len(set_ua_requests) == 1
    assert set_ua_requests[0].pers_no == pers_no
    assert set_ua_requests[0].user_area == new_ua_text_no


def test_set_user_area__person_has_user_area_but_text_does_not_exist():
    user_area_text_no = 12345
    c = create_mockconnection()
    ks = create_komsession(17, c)
    
    c.mock_request(Requests.GET_PERSON_STAT,
                   lambda request: MockPerson(user_area=user_area_text_no))
    def get_text_stat(request):
        raise NoSuchText(request.text_no)
    c.mock_request(Requests.GET_TEXT_STAT, get_text_stat)

    try:
        ks.set_user_area_block(42, 'jskom', {}) # should throw NoSuchText
        assert False
    except NoSuchText as e:
        # this is what should happen
        assert e.args[0] == user_area_text_no
    except:
        assert False

    assert len(c.mock_get_request_calls(Requests.GET_TEXT)) == 0
    assert len(c.mock_get_request_calls(Requests.CREATE_TEXT)) == 0
    assert len(c.mock_get_request_calls(Requests.SET_USER_AREA)) == 0


def test_set_user_area__gets_the_user_area_for_the_given_person():
    pers_no = 42
    c = create_mockconnection()
    ks = create_komsession(17, c)
    c.mock_request(Requests.GET_PERSON_STAT, lambda request: MockPerson(user_area=0))
    c.mock_request(Requests.CREATE_TEXT, lambda request: 67890)


    ks.set_user_area_block(pers_no, 'jskom', {})
    
    
    get_person_stat_calls = c.mock_get_request_calls(Requests.GET_PERSON_STAT)
    assert len(get_person_stat_calls) == 2 # first is for login
    assert get_person_stat_calls[1].pers_no == pers_no


def test_set_user_area__sets_user_area_for_the_correct_person_and_text_no():
    c = create_mockconnection()
    c.mock_request(Requests.GET_PERSON_STAT,
                   lambda *args, **kwargs: MockPerson(user_area=0))

    pers_no = 42
    new_ua_text_no = 67890
    c.mock_request(Requests.CREATE_TEXT, lambda request: new_ua_text_no)
    c.mock_request(Requests.SET_USER_AREA, lambda request: None)
    ks = create_komsession(17, c)
    
    
    ks.set_user_area_block(pers_no, 'jskom', {})
    
    
    # Check SetUserArea request
    set_ua_requests = c.mock_get_request_calls(Requests.SET_USER_AREA)
    assert len(set_ua_requests) == 1
    assert set_ua_requests[0].pers_no == pers_no
    assert set_ua_requests[0].user_area == new_ua_text_no


def test_lookup_name_should_decode_utf8_string():
    mock_client = MagicMock()
    ks = KomSession(client_factory=lambda *args, **kwargs: mock_client)
    ks.connect('host', 'port', 'user', 'hostname', 'client_name', 'client_version')

    name = 'bj\xc3\xb6rn'
    ks.lookup_name(name, 1, 0)

    mock_client.lookup_name.assert_called_with(name.decode('utf-8'), 1, 0)


def test_lookup_name_should_handle_unicode_string():
    mock_client = MagicMock()
    ks = KomSession(client_factory=lambda *args, **kwargs: mock_client)
    ks.connect('host', 'port', 'user', 'hostname', 'client_name', 'client_version')

    name = u'bj\xf6rn'
    ks.lookup_name(name, 1, 0)

    mock_client.lookup_name.assert_called_with(name, 1, 0)
