# -*- coding: utf-8 -*-

import json

from pylyskom.utils import decode_user_area, encode_user_area, parse_content_type


def test_decode_user_area__handles_empty_string():
    ua = b""
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 0


def test_decode_user_area__handles_empty_hollerith_string():
    ua = b" 0H"
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 0


def test_decode_user_area__handles_empty_blocks():
    ua = b"17H 6Hcommon 5Helisp 0H 0H"
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 2
    assert b"common" in blocks
    assert b"elisp" in blocks
    assert blocks[b"common"] == b""
    assert blocks[b"elisp"] == b""


def test_decode_user_area__handles_beginning_spaces():
    ua = b"  9H 6Hcommon 0H"
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 1
    assert b"common" in blocks
    assert blocks[b"common"] == b""


def test_decode_user_area__example():
    ua = b" 17H 6Hcommon 5Helisp 0H 73H 32Hkom-auto-confirm-new-conferences 3Hnil\n 22Hcreated-texts-are-read 1H0"
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 2
    assert b"common" in blocks
    assert b"elisp" in blocks
    assert blocks[b"common"] == b""
    assert blocks[b"elisp"] == b" 32Hkom-auto-confirm-new-conferences 3Hnil\n 22Hcreated-texts-are-read 1H0"


def test_encode_user_area__empty_ua():
    blocks = {}
    
    ua = encode_user_area(blocks)
    
    assert ua == b"0H"


def test_encode_user_area__one_block_with_empty_value():
    blocks = { b"common": b""}
    
    ua = encode_user_area(blocks)
    
    assert ua == b"9H 6Hcommon 0H"


def test_encode_user_area__one_block_with_one_empty_hollerith_string():
    blocks = { b"common": b"0H"}
    
    ua = encode_user_area(blocks)
    
    assert ua == b"9H 6Hcommon 2H0H"


def test_encode_user_area__blocks_are_put_in_alphabetical_order():
    blocks = { b"common": b"c", b"jskom": b"j", b"elisp": b"e"}
    
    ua = encode_user_area(blocks)
    
    assert ua == b"25H 6Hcommon 5Helisp 5Hjskom 1Hc 1He 1Hj"


def test_encode_user_area__block_with_json():
    obj = { 'filtered-authors': [ 17, 4711 ], 'annat': 'Räksmörgås' }
    blocks = { b"jskom": json.dumps(obj, sort_keys=True).encode('utf-8') }
    
    ua = encode_user_area(blocks)
    
    assert ua == b'8H 5Hjskom 70H{"annat": "R\u00e4ksm\u00f6rg\u00e5s", "filtered-authors": [17, 4711]}'


def test_encode_user_area__example():
    blocks = {
        b"common": b"",
        b"elisp": b"32Hkom-auto-confirm-new-conferences 3Hnil\n 22Hcreated-texts-are-read 1H0"
        }
    
    ua = encode_user_area(blocks)
    
    assert ua == b"17H 6Hcommon 5Helisp 0H 72H32Hkom-auto-confirm-new-conferences 3Hnil\n 22Hcreated-texts-are-read 1H0"


def test_parse_content_type():
    ct = 'application/pdf; name=foobar.pdf'
    parsed = parse_content_type(ct)
    assert parsed == (('application', 'pdf', dict(name='foobar.pdf')), None)

def test_parse_content_type_from_email():
    ct = 'application/pdf; name="=?iso-8859-1?q?f=f6rslag=5fmedlemsavgifter=2epdf?="'
    parsed = parse_content_type(ct)
    assert parsed == (('application', 'pdf', dict(name='"=?iso-8859-1?q?f=f6rslag=5fmedlemsavgifter=2epdf?="')), None)

def test_parse_content_type_from_androkom_image():
    ct = 'image/jpeg; name=https://lh3.googleusercontent.com/0D_7y-M=s0-d'
    parsed = parse_content_type(ct)
    assert parsed == (('image', 'jpeg', dict(name='https://lh3.googleusercontent.com/0D_7y-M=s0-d')), None)
