# -*- coding: utf-8 -*-

import json

from pylyskom.utils import decode_user_area, encode_user_area


def test_decode_user_area__handles_empty_string():
    ua = ""
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 0


def test_decode_user_area__handles_empty_hollerith_string():
    ua = " 0H"
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 0


def test_decode_user_area__handles_empty_blocks():
    ua = "17H 6Hcommon 5Helisp 0H 0H"
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 2
    assert "common" in blocks
    assert "elisp" in blocks
    assert blocks["common"] == ""
    assert blocks["elisp"] == ""


def test_decode_user_area__handles_beginning_spaces():
    ua = "  9H 6Hcommon 0H"
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 1
    assert "common" in blocks
    assert blocks["common"] == ""


def test_decode_user_area__example():
    ua = " 17H 6Hcommon 5Helisp 0H 73H 32Hkom-auto-confirm-new-conferences 3Hnil\n 22Hcreated-texts-are-read 1H0"
    
    blocks = decode_user_area(ua)
    assert blocks is not None
    assert len(blocks) == 2
    assert "common" in blocks
    assert "elisp" in blocks
    assert blocks["common"] == ""
    assert blocks["elisp"] == " 32Hkom-auto-confirm-new-conferences 3Hnil\n 22Hcreated-texts-are-read 1H0"


def test_encode_user_area__empty_ua():
    blocks = {}
    
    ua = encode_user_area(blocks)
    
    assert ua == "0H"


def test_encode_user_area__one_block_with_empty_value():
    blocks = { "common": ""}
    
    ua = encode_user_area(blocks)
    
    assert ua == "9H 6Hcommon 0H"


def test_encode_user_area__one_block_with_one_empty_hollerith_string():
    blocks = { "common": "0H"}
    
    ua = encode_user_area(blocks)
    
    assert ua == "9H 6Hcommon 2H0H"


def test_encode_user_area__blocks_are_put_in_alphabetical_order():
    blocks = { "common": "c", "jskom": "j", "elisp": "e"}
    
    ua = encode_user_area(blocks)
    
    assert ua == "25H 6Hcommon 5Helisp 5Hjskom 1Hc 1He 1Hj"


def test_encode_user_area__block_with_json():
    obj = { 'filtered-authors': [ 17, 4711 ], 'annat': 'Räksmörgås' }
    blocks = { "jskom": json.dumps(obj) }
    
    ua = encode_user_area(blocks)
    
    assert ua == '8H 5Hjskom 70H{"filtered-authors": [17, 4711], "annat": "R\u00e4ksm\u00f6rg\u00e5s"}'


def test_encode_user_area__example():
    blocks = {
        "common": "",
        "elisp": "32Hkom-auto-confirm-new-conferences 3Hnil\n 22Hcreated-texts-are-read 1H0"
        }
    
    ua = encode_user_area(blocks)
    
    assert ua == "17H 6Hcommon 5Helisp 0H 72H32Hkom-auto-confirm-new-conferences 3Hnil\n 22Hcreated-texts-are-read 1H0"
