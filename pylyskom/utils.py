# -*- coding: utf-8 -*-

from __future__ import absolute_import
import six

from . import mimeparse
from .errors import Error
from .protocol import WHITESPACE, DIGITS, ORD_0, to_hstring


def decode_text(text, encoding, backup_encoding='latin1'):
    if encoding is None:
        encoding = backup_encoding
    
    try:
        decoded_text = text.decode(encoding)
    except LookupError:
        # Failed to find the given encoding (such as "x-unkown", for
        # example).
        decoded_text = text.decode(backup_encoding)
    except UnicodeDecodeError:
        # (from iKOM) Fscking clients that can't detect coding...
        decoded_text = text.decode(backup_encoding)
    
    return decoded_text

def parse_content_type(contenttype):
    try:
        mime_type = mimeparse.parse_mime_type(contenttype)
    except Exception:
        raise Error("Failed to parse mime type '%s'" % (contenttype,))
    
    if mime_type[0] == 'x-kom' and mime_type[1] == 'text':
        mime_type = ('text', 'x-kom-basic', mime_type[2])
    
    if "charset" in mime_type[2]:
        # Remove charset from mime_type, if we have it
        encoding = mime_type[2].pop("charset")
    else:
        encoding = None
    
    if encoding == 'x-ctext':
        encoding = 'latin1'
    
    return mime_type, encoding

def mime_type_tuple_to_str(mime_type):
    params = [ "%s=%s" % (k, v) for k, v in mime_type[2].items() ]
    t = "%s/%s" % (mime_type[0], mime_type[1])
    l = [t]
    l.extend(params)
    return ";".join(l)

def parse_hollerith_string(hstring):
    if not hstring:
        return None, hstring
    assert isinstance(hstring, six.binary_type)

    i = 0

    # Skip all leading whitespaces
    c = hstring[i:i+1]
    while c in WHITESPACE:
        i += 1
        c = hstring[i:i+1]

    # Parse length
    length = 0
    while c in DIGITS:
        length = length * 10 + (ord(c) - ORD_0)
        i += 1
        c = hstring[i:i+1]

    if c != b"H":
        raise Exception("Not a valid hollerith string")

    i += 1 # skip "H"
    hend = i + length
    return hstring[i:hend], hstring[hend:]


def to_hollerith_string(s):
    return to_hstring(s)


def decode_user_area(user_area):
    """Decodes the user area to a dictionary where the keys are the
    block names and the values are the hollerith string encoded block
    content.
    """
    h_block_names, h_blocks = parse_hollerith_string(user_area)

    def parse_block_names(hstring):
        # Parse block names
        block_names = []
        h_block_name, hstring = parse_hollerith_string(hstring)
        while h_block_name:
            block_names.append(h_block_name)
            h_block_name, hstring = parse_hollerith_string(hstring)
        return block_names

    def parse_blocks(hstring, block_names):
        blocks = {}
        for block_name in block_names:
            h_block, hstring = parse_hollerith_string(hstring)
            blocks[block_name] = h_block
        return blocks

    block_names = parse_block_names(h_block_names)
    blocks = parse_blocks(h_blocks, block_names)
    return blocks


def encode_user_area(blocks):
    """Encodes a dictionary to a user area. The keys should be the
    block names and the values are the hollerith string encoded
    blocks. The block names will be sorted alphabetically.
    """
    h_block_names = b""
    h_blocks = b""
    for block_name in sorted(blocks.keys()):
        h_block_names += b" " + to_hollerith_string(block_name)
        h_blocks += b" " + to_hollerith_string(blocks[block_name])

    return to_hollerith_string(h_block_names) + h_blocks
