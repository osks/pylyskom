# -*- coding: utf-8 -*-

import functools
import json

import errno
import socket
import mimeparse

import kom, komauxitems, utils
from connection import CachedPersonConnection, Requests


class KomSessionError(Exception): pass
class KomSessionNotConnected(KomSessionError): pass
class AmbiguousName(KomSessionError): pass
class NameNotFound(KomSessionError): pass
class NoRecipients(KomSessionError): pass


        

def check_connection(f):
    @functools.wraps(f)
    def decorated(komsession, *args, **kwargs):
        if not komsession.is_connected:
            raise KomSessionNotConnected()
        try:
            return f(komsession, *args, **kwargs)
        except socket.error as serr:
            if serr.errno in (errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN, errno.ETIMEDOUT):
                # If we got an error that indicates that the
                # connection has failed, then close and raise.
                komsession.close()
                raise KomSessionNotConnected(serr)

    return decorated


class KomSession(object):
    """ A LysKom session. """
    def __init__(self, host, port=4894, connection_factory=CachedPersonConnection):
        self.host = host
        self.port = port
        # TODO: We actually require the API of a
        # CachedPersonConnection. We should enhance the Connection
        # class and make CachedPersonConnection have the same API as
        # Connection.
        self._connection_factory = connection_factory
        self.conn = None
        self.session_no = None
        self.client_name = None
        self.client_version = None
    
    def connect(self, username, hostname, client_name, client_version):
        self.conn = self._connection_factory()
        self.conn.connect(self.host, self.port, user=username + "%" + hostname)
        self.conn.request(Requests.SetClientVersion, client_name, client_version).response()
        self.client_name = client_name
        self.client_version = client_version
        self.session_no = self.who_am_i()
        self.conn.request(Requests.SetConnectionTimeFormat, use_utc=1).response()
    
    def is_connected(self):
        return self.conn is not None
    
    def close(self):
        """Immediately close the connection, without sending a Disconnect request.
        """
        self.conn.close()
        self.conn = None
        self.client_name = None
        self.client_version = None
        self.session_no = None

    @check_connection
    def disconnect(self, session_no=0):
        """Session number 0 means this session (a logged in user can
        disconnect its other sessions).
        """
        self.conn.request(Requests.Disconnect, session_no).response()
        
        # Check if we disconnected our own session or not (you can
        # disconnect another LysKOM session that the logged in user is
        # a supervisor of).
        if session_no == 0 or session_no == self.session_no:
            self._close()
    
    @check_connection
    def login(self, pers_no, password):
        self.conn.login(pers_no, password)
        person_stat = self.conn.request(Requests.GetPersonStat, pers_no).response()
        return KomPerson(pers_no, person_stat)

    @check_connection
    def logout(self):
        self.conn.logout()

    @check_connection
    def get_person_no(self):
        return self.conn.get_person_no()

    @check_connection
    def who_am_i(self):
        return self.conn.request(Requests.WhoAmI).response()

    @check_connection
    def user_is_active(self):
        self.conn.request(Requests.UserActive).response()

    @check_connection
    def is_logged_in(self):
        return self.conn.is_logged_in()

    @check_connection
    def change_conference(self, conf_no):
        self.conn.change_conference(conf_no)
        
    @check_connection
    def create_person(self, name, passwd):
        flags = kom.PersonalFlags()
        pers_no = self.conn.request(Requests.CreatePerson, name.encode('latin1'),
                                    passwd.encode('latin1'), flags).response()
        return KomPerson(pers_no)

    @check_connection
    def create_conference(self, name, aux_items=None):
        conf_type = kom.ConfType()
        if aux_items is None:
            aux_items = []
        conf_no = self.conn.request(Requests.CreateConf, name.encode('latin1'), conf_type,
                                    aux_items).response()
        return conf_no
    
    @check_connection
    def lookup_name(self, name, want_pers, want_confs):
        return self.conn.lookup_name(name, want_pers, want_confs)

    @check_connection
    def lookup_name_exact(self, name, want_pers, want_confs):
        matches = self.lookup_name(name, want_pers, want_confs)
        return self._exact_lookup_match(name, matches)

    @check_connection
    def re_lookup_name(self, regexp, want_pers, want_confs):
        # The LysKOM server is always case sensitive, and it's kom.py
        # that tries to create a case-insensitive regexp. Doesn't seem
        # to work that well.
        return self.conn.regexp_lookup(regexp, want_pers, want_confs, case_sensitive=1)

    @check_connection
    def re_lookup_name_exact(self, regexp, want_pers, want_confs):
        matches = self.re_lookup_name(regexp, want_pers, want_confs)
        return self._exact_lookup_match(regexp, matches)

    @check_connection
    def _exact_lookup_match(self, lookup, matches):
        if len(matches) == 0:
            raise NameNotFound("recipient not found: %s" % lookup)
        elif len(matches) <> 1:
            raise AmbiguousName("ambiguous recipient: %s" % lookup)
        return matches[0][0]

    @check_connection
    def get_text_stat(self, text_no):
        return self.conn.textstats[text_no]
    
    @check_connection
    def add_membership(self, pers_no, conf_no, priority, where):
        mtype = kom.MembershipType()
        self.conn.request(Requests.AddMember, conf_no, pers_no, priority, where, mtype).response()
    
    @check_connection
    def delete_membership(self, pers_no, conf_no):
        self.conn.request(Requests.SubMember, conf_no, pers_no).response()

    @check_connection
    def get_membership(self, pers_no, conf_no):
        membership = self.conn.get_membership(pers_no, conf_no, want_read_ranges=False)
        return KomMembership(pers_no, membership)

    @check_connection
    def get_membership_unread(self, pers_no, conf_no):
        membership = self.conn.get_membership(pers_no, conf_no, want_read_ranges=True)
        unread_texts = self.conn.get_unread_texts_from_membership(membership)
        return KomMembershipUnread(pers_no, conf_no, len(unread_texts), unread_texts)

    @check_connection
    def get_memberships(self, pers_no, first, no_of_confs, unread=False, passive=False):
        if unread:
            # RegGetUnreadConfs never returns passive memberships so
            # that combination is not valid.
            assert passive == False
            conf_nos = self.conn.request(Requests.GetUnreadConfs, pers_no).response()
            # This may return conferences that don't have any unread
            # texts in them. We have to live with this, because we
            # don't want to get the unread texts in this case. It's
            # possible that we need to change this, which means that
            # unread=True may be a slower call.
            memberships = [ self.get_membership(pers_no, conf_no) for conf_no in conf_nos ]
            has_more = False
        else:
            ms_list = self.conn.get_memberships(pers_no, first, no_of_confs,
                                                want_read_ranges=False)
            
            # We need to check if there are more memberships to get
            # before we filter out the passive memberships.
            if len(ms_list) < no_of_confs:
                has_more = False
            else:
                has_more = True
            
            memberships = []
            for membership in ms_list:
                if (not passive) and membership.type.passive:
                    continue
                memberships.append(KomMembership(pers_no, membership))
        
        return memberships, has_more

    @check_connection
    def get_membership_unreads(self, pers_no):
        conf_nos = self.conn.request(Requests.GetUnreadConfs, pers_no).response()
        memberships = [ self.get_membership_unread(pers_no, conf_no)
                        for conf_no in conf_nos ]
        return [ m for m in memberships if m.no_of_unread > 0 ]
    
    @check_connection
    def get_conf_name(self, conf_no):
        return self.conn.conf_name(conf_no)
    
    @check_connection
    def get_conference(self, conf_no, micro=True):
        if micro:
            return KomUConference(conf_no, self.conn.uconferences[conf_no])
        else:
            return KomConference(conf_no, self.conn.conferences[conf_no])

    @check_connection
    def get_text(self, text_no):
        text_stat = self.get_text_stat(text_no)
        text = self.conn.request(Requests.GetText, text_no).response()
        return KomText(text_no=text_no, text=text, text_stat=text_stat)

    # TODO: offset/start number, so we can paginate. we probably need
    # to return the local text number for that.
    @check_connection
    def get_last_texts(self, conf_no, no_of_texts, offset=0, full_text=False):
        """Get the {no_of_texts} last texts in conference {conf_no},
        starting from {offset}.
        """
        #local_no_ceiling = 0 # means the higest numbered texts (i.e. the last)
        text_mapping = self.conn.request(
            Requests.LocalToGlobalReverse, conf_no, 0, no_of_texts).response()
        texts = [ KomText(text_no=m[1], text=None, text_stat=self.get_text_stat(m[1]))
                  for m in text_mapping.list if m[1] != 0 ]
        texts.reverse()
        return texts

    @check_connection
    def create_text(self, komtext):
        misc_info = kom.CookedMiscInfo()
        
        if komtext.recipient_list is not None:
            for rec in komtext.recipient_list:
                if rec is not None:
                    misc_info.recipient_list.append(rec)
        
        if komtext.comment_to_list is not None:
            for ct in komtext.comment_to_list:
                if ct is not None:
                    misc_info.comment_to_list.append(ct)
        
        mime_type = mimeparse.parse_mime_type(komtext.content_type)
        
        # TODO: how would we handle images?  Because a text consists
        # of both a subject and body, and you can have a text subject
        # in combination with an image, a charset is needed to specify
        # the encoding of the subject even for images.
        
        if mime_type[0] == 'text':
            # We hard code utf-8 because it is The Correct Encoding. :)
            mime_type[2]['charset'] = 'utf-8'
            fulltext = komtext.subject + "\n" + komtext.body
            fulltext = fulltext.encode('utf-8')
        elif mime_type[0] == 'x-kom' and mime_type[1] == 'user-area':
            # Charset doesn't seem to be specified for user areas, but
            # in reality they contain Latin 1 text.
            fulltext = komtext.body.encode('latin-1')
        else:
            raise KomSessionError("Unhandled content type: %s" % (mime_type,))

        content_type = utils.mime_type_tuple_to_str(mime_type)
        
        if komtext.aux_items is None:
            aux_items = []
        else:
            aux_items = komtext.aux_items
        
        # We need to make sure all aux items are encoded.
        creating_software = "%s %s" % (self.client_name, self.client_version)
        aux_items.append(kom.AuxItem(komauxitems.AI_CREATING_SOFTWARE,
                                     data=creating_software.encode('utf-8')))
        aux_items.append(kom.AuxItem(komauxitems.AI_CONTENT_TYPE,
                                     data=content_type.encode('utf-8')))

        text_no = self.conn.request(Requests.CreateText, fulltext, misc_info, aux_items).response()
        return text_no

    @check_connection
    def mark_as_read(self, text_no):
        text_stat = self.get_text_stat(text_no)
        for mi in text_stat.misc_info.recipient_list:
            self.conn.mark_as_read_local(mi.recpt, mi.loc_no)

    @check_connection
    def mark_as_unread(self, text_no):
        text_stat = self.get_text_stat(text_no)
        for mi in text_stat.misc_info.recipient_list:
            self.conn.mark_as_unread_local(mi.recpt, mi.loc_no)

    @check_connection
    def set_unread(self, conf_no, no_of_unread):
        self.conn.request(Requests.SetUnread, conf_no, no_of_unread).response()

    @check_connection
    def get_marks(self):
        return self.conn.request(Requests.GetMarks).response()

    @check_connection
    def mark_text(self, text_no, mark_type):
        self.conn.mark_text(text_no, mark_type)

    @check_connection
    def unmark_text(self, text_no):
        self.conn.unmark_text(text_no)

    @check_connection
    def get_user_area_block(self, pers_no, block_name, json_decode=True):
        """Get the block with the given block name from the user area
        for the given person. If there is no user area for the person,
        or if there is no block with the given name, None will be
        returned.
        
        If json_decode is True (default), the stored block will be
        passed to json.loads() before it is returned.
        
        If json_decode is False, then the block will be returned as a
        string.
        """
        person_stat = self.conn.request(Requests.GetPersonStat, pers_no).response()
        
        if person_stat.user_area == 0:
            # No user area
            return None
        
        text = self.get_text(person_stat.user_area)
        if text.content_type != 'x-kom/user-area':
            raise KomSessionError(
                "Unknown content type for user area text: %s" % (text.content_type,))

        blocks = utils.decode_user_area(text.body)
        block = blocks.get(block_name, None)
        if block is not None and json_decode:
            block = json.loads(block)
        
        return block
    
    @check_connection
    def set_user_area_block(self, pers_no, block_name, block, json_encode=True):
        """Set the block with the given block name in the user area
        for the given person. Will create a new text and set as the
        new user area for the person. If there already is a block with
        the given name, it will be over-written. The other blocks in
        the user area will copied to the new user area.
        
        If json_encode is True (default), the block will be passed to
        json.dumps() before it is saved.
        
        If json_encode is False, then the block should be a string
        that can be hollerith encoded.
        """
        person_stat = self.conn.request(Requests.GetPersonStat, pers_no).response()
        
        if person_stat.user_area == 0:
            # No existing user area, initiate a new dictionary of
            # blocks.
            blocks = dict()
        else:
            user_area = self.get_text(person_stat.user_area)
            if user_area.content_type != 'x-kom/user-area':
                raise KomSessionError(
                    "Unknown content type for user area text: %s" % (user_area.content_type,))

            blocks = utils.decode_user_area(user_area.body)
        
        if json_encode:
            blocks[block_name] = json.dumps(block)
        else:
            blocks[block_name] = block

        new_user_area = KomText()
        new_user_area.content_type = 'x-kom/user-area'
        new_user_area.body = utils.encode_user_area(blocks)
        new_user_area_text_no = self.create_text(new_user_area)
        self.conn.request(Requests.SetUserArea, pers_no, new_user_area_text_no).response()
        # TODO: Should it remove the old user area?



class KomPerson(object):
    def __init__(self, pers_no, person_stat=None):
        self.pers_no = pers_no
        
        if person_stat is None:
            #self.username = None
            #self.privileges = None
            #self.flags = None
            #self.last_login = None
            self.user_area = None
            #self.total_time_present = None
            #self.sessions = None
            #self.created_lines = None
            #self.created_bytes = None
            #self.read_texts = None
            #self.no_of_text_fetches = None
            #self.user_area = None
            #self.created_persons = None
            #self.created_confs = None
            #self.first_created_local_no = None
            #self.no_of_created_texts = None
            #self.no_of_marks = None
            #self.no_of_cons = None
        else:
            self.user_area = person_stat.user_area


class KomMembership(object):
    def __init__(self, pers_no, membership):
        self.pers_no = pers_no
        self.position = membership.position
        self.last_time_read = membership.last_time_read
        self.conference = membership.conference
        self.priority = membership.priority
        self.added_by = membership.added_by
        self.added_at = membership.added_at
        self.type = membership.type


class KomMembershipUnread(object):
    def __init__(self, pers_no, conf_no, no_of_unread, unread_texts):
        self.pers_no = pers_no
        self.conf_no = conf_no
        self.no_of_unread = no_of_unread
        self.unread_texts = unread_texts


class KomConference(object):
    def __init__(self, conf_no=None, conf=None):
        self.conf_no = conf_no
        
        if conf is not None:
            self.name = conf.name.decode('latin1')
            self.type = conf.type
            self.creation_time = conf.creation_time
            self.last_written = conf.last_written
            self.creator = conf.creator
            self.presentation = conf.presentation
            self.supervisor = conf.supervisor
            self.permitted_submitters = conf.permitted_submitters
            self.super_conf = conf.super_conf
            self.msg_of_day = conf.msg_of_day
            self.nice = conf.nice
            self.keep_commented = conf.keep_commented
            self.no_of_members = conf.no_of_members
            self.first_local_no = conf.first_local_no
            self.no_of_texts = conf.no_of_texts
            self.expire = conf.expire
            self.aux_items = conf.aux_items


class KomUConference(object):
    """U stands for micro"""
    def __init__(self, conf_no=None, uconf=None):
        self.conf_no = conf_no
        
        if uconf is not None:
            self.name = uconf.name.decode('latin1')
            self.type = uconf.type
            self.highest_local_no = uconf.highest_local_no
            self.nice = uconf.nice


class KomText(object):
    def __init__(self, text_no=None, text=None, text_stat=None):
        self.text_no = text_no
        
        if text_stat is None:
            self.content_type = None
            self.creation_time = None
            self.author = None
            self.no_of_marks = 0
            self.recipient_list = None
            self.comment_to_list = None
            self.comment_in_list = None
            self.subject = None
            self.body = None
            self.aux_items = None
        else:
            mime_type, encoding = utils.parse_content_type(
                KomText._get_content_type_from_text_stat(text_stat))
            self.content_type = utils.mime_type_tuple_to_str(mime_type)
            
            self.creation_time = text_stat.creation_time
            self.author = text_stat.author
            self.no_of_marks = text_stat.no_of_marks
            self.recipient_list = text_stat.misc_info.recipient_list
            self.comment_to_list = text_stat.misc_info.comment_to_list
            self.comment_in_list = text_stat.misc_info.comment_in_list
            self.aux_items = text_stat.aux_items
            self.subject, self.body = KomText._decode_text(text, mime_type, encoding)

    @staticmethod
    def _decode_text(text, mime_type, encoding):
        if text is None:
            return None, None

        subject = None
        body = None

        # text_stat is required for this
        if mime_type[0] == "x-kom" and mime_type[1] == "user-area":
            body = utils.decode_text(text, encoding)
        else:
            # If a text has no linefeeds, it only has a body
            if text.find('\n') == -1:
                subject = "" # Should probably be None instead?
                rawbody = text
            else:
                rawsubject, rawbody = text.split('\n', 1)
                # TODO: should we always decode the subject?
                subject = utils.decode_text(rawsubject, encoding)
        
            if mime_type[0] == 'text':
                # Only decode body if media type is text, and not
                # an image, for example.  Also, if the subject is
                # empty, everything becomes the subject, which
                # will get decoded.  Figure out how to handle all
                # this. Assume empty subject means everything in
                # body?
                body = utils.decode_text(rawbody, encoding)
            else:
                body = rawbody
        
        return subject, body

    @staticmethod
    def _get_content_type_from_text_stat(text_stat):
        try:
            contenttype = kom.first_aux_items_with_tag(
                text_stat.aux_items, komauxitems.AI_CONTENT_TYPE).data.decode('latin1')
        except AttributeError:
            contenttype = 'text/plain'
        return contenttype
