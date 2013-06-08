# -*- coding: utf-8 -*-

import mimeparse


def decode_text(text, encoding, backup_encoding='latin1'):
    if encoding is None:
        encoding = backup_encoding
    
    try:
        decoded_text = text.decode(encoding)
    except UnicodeDecodeError:
        # (from iKOM) Fscking clients that can't detect coding...
        decoded_text = text.decode(backup_encoding)
    
    return decoded_text

def parse_content_type(contenttype):
    mime_type = mimeparse.parse_mime_type(contenttype)
    
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
