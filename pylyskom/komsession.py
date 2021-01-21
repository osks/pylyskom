# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2021 Oskar Skoog. Released under GPL.

from __future__ import absolute_import
from typing import List, Optional
import base64
import functools
import json
import six

import errno
import socket
from . import mimeparse

from . import komauxitems, utils, requests
from .connection import Connection
from .cachedconnection import Client, CachingPersonClient
from .stats import stats

from .datatypes import (
    AuxItem,
    AuxItemInput,
    ConfType,
    Conference,
    CookedMiscInfo,
    ExtendedConfType,
    MIC_COMMENT,
    MIC_FOOTNOTE,
    MICommentTo,
    MIR_BCC,
    MIR_CC,
    MIR_TO,
    MIRecipient,
    Membership,
    MembershipType,
    PersonalFlags,
    TextStat,
    UConference,
    first_aux_items_with_tag,
)

class KomSessionException(Exception): pass
class KomSessionNotConnected(KomSessionException): pass
class KomSessionError(KomSessionException): pass
class AmbiguousName(KomSessionError): pass
class NameNotFound(KomSessionError): pass
class NoRecipients(KomSessionError): pass


MIRecipient_str_to_type = { 'to': MIR_TO,
                            'cc': MIR_CC,
                            'bcc': MIR_BCC }

MICommentTo_str_to_type = { 'comment': MIC_COMMENT,
                            'footnote': MIC_FOOTNOTE }




# KomPerson is intended for the full person-stat with all its info, but is
# not really used yet.
class KomPerson:
    def __init__(self, pers_no, username: str):
        self.pers_no = pers_no
        self.username = username

    def __repr__(self):
        return f"KomPerson({self.pers_no!r}, {self.username!r})"

# KomPersonName is intended for when only the pers-no and name are
# wanted.
class KomPersonName:
    def __init__(self, pers_no, username: str):
        self.pers_no = pers_no
        self.username = username

    def __repr__(self):
        return f"KomPersonName({self.pers_no!r}, {self.username!r})"


class KomMembershipUnread:
    def __init__(self, pers_no, conf_no, no_of_unread, unread_texts: List[int]):
        self.pers_no = pers_no
        self.conf_no = conf_no
        self.no_of_unread = no_of_unread
        self.unread_texts = unread_texts


class KomAuxItem:
    def __init__(self, aux_item: AuxItem, creator: KomPersonName):
        self.aux_no = aux_item.aux_no
        self.tag = aux_item.tag
        self.created_at = aux_item.created_at
        self.flags = aux_item.flags
        self.inherit_limit = aux_item.inherit_limit
        self.data = aux_item.data
        self.creator = creator


# KomConferenceName is intended for when only the conf-no and name are
# wanted.
class KomConferenceName:
    def __init__(self, conf_no, name):
        self.conf_no = conf_no
        self.name = name


# U stands for micro (as in the Protocol A spec)
class KomUConference:
    def __init__(self, conf_no, *,
                 uconf: Optional[UConference] = None,
                 name: Optional[str] = None,
                 type: Optional[ExtendedConfType] = None,
                 highest_local_no: Optional[int] = None,
                 nice: Optional[int] = None):
        self.conf_no = conf_no

        if uconf is None:
            self.name = name
            self.type = type
            self.highest_local_no = highest_local_no
            self.nice = nice
        else:
            if isinstance(uconf.name, six.binary_type):
                self.name = uconf.name.decode('latin1')
            else:
                self.name = uconf.name
            self.type = uconf.type
            self.highest_local_no = uconf.highest_local_no
            self.nice = uconf.nice


class KomConference:
    def __init__(self, conf_no, *,
                 conf: Conference,
                 creator: KomPersonName,
                 supervisor: KomConferenceName,
                 permitted_submitters: Optional[KomUConference],
                 super_conf: Optional[KomConferenceName],
                 aux_items: List[KomAuxItem]):
        self.conf_no = conf_no
        self.creator = creator
        self.supervisor = supervisor
        self.permitted_submitters = permitted_submitters
        self.super_conf = super_conf
        self.aux_items = aux_items

        self.name = conf.name.decode('latin1')
        self.type = conf.type
        self.creation_time = conf.creation_time
        self.last_written = conf.last_written
        self.presentation = conf.presentation
        self.msg_of_day = conf.msg_of_day
        self.nice = conf.nice
        self.keep_commented = conf.keep_commented
        self.no_of_members = conf.no_of_members
        self.first_local_no = conf.first_local_no
        self.no_of_texts = conf.no_of_texts
        self.expire = conf.expire


class KomMembership:
    def __init__(self, pers_no, *, membership: Membership, added_by: Optional[KomPersonName], conference: KomUConference):
        self.pers_no = pers_no
        self.added_by = added_by
        self.conference = conference

        self.position = membership.position
        self.last_time_read = membership.last_time_read
        self.priority = membership.priority
        self.added_at = membership.added_at
        self.type = membership.type


class KomText:
    def __init__(self, text_no=None, text: str = None, *,
                 text_stat: TextStat = None, aux_items: List[KomAuxItem] = None, author: KomPersonName = None):
        self.text_no = text_no
        self.text = text
        self.aux_items = aux_items
        self.author = author

        if text_stat is None:
            self.content_type = None
            self.creation_time = None
            self.no_of_marks = 0
            self.recipient_list = None
            self.comment_to_list = None
            self.comment_in_list = None
            self.subject = None
            self.body = None
        else:
            # self.text_content_type is for the encoded text
            self.text_content_type = KomText._get_content_type_from_text_stat(text_stat)
            mime_type, encoding = utils.parse_content_type(self.text_content_type)
            # self.content_type is for the decoded text (into subject and body)
            # and typically does not contain charset encoding since subject and body
            # have been decoded into Python unicode strings.
            self.content_type = utils.mime_type_tuple_to_str(mime_type)
            self.subject, self.body = KomText._decode_text(text, mime_type, encoding)

            self.creation_time = text_stat.creation_time
            self.no_of_marks = text_stat.no_of_marks
            self.recipient_list = text_stat.misc_info.recipient_list
            self.comment_to_list = text_stat.misc_info.comment_to_list
            self.comment_in_list = text_stat.misc_info.comment_in_list

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
            if text.find(b'\n') == -1:
                subject = "" # Should probably be None instead?
                rawbody = text
            else:
                rawsubject, rawbody = text.split(b'\n', 1)
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
            contenttype = first_aux_items_with_tag(
                text_stat.aux_items, komauxitems.AI_CONTENT_TYPE).data.decode('latin1')
        except AttributeError:
            contenttype = 'text/plain'
        return contenttype

    @staticmethod
    def create_new_text(subject, body, content_type, creating_software=None, recipient_list=None, comment_to_list=None):
        if recipient_list is None:
            recipient_list = []
        if comment_to_list is None:
            comment_to_list = []

        komtext = KomText()
        komtext.subject = subject
        komtext.body = body
        komtext.content_type = content_type

        # wtf are we doing here?
        mime_type, _ = utils.parse_content_type(content_type)
        content_type = utils.mime_type_tuple_to_str(mime_type)
        mime_type = mimeparse.parse_mime_type(content_type)

        if mime_type[0] == 'text':
            # We hard code utf-8 because it is The Correct Encoding. :)
            mime_type[2]['charset'] = 'utf-8'
            fulltext = subject + "\n" + body
            fulltext = fulltext.encode('utf-8')
        elif mime_type[0] == 'x-kom' and mime_type[1] == 'user-area':
            # Charset doesn't seem to be specified for user areas, but
            # in reality they contain Latin 1 text.
            fulltext = body.encode('latin-1')
        elif mime_type[0] == 'image':
            # We handle images in the same way as AndroKOM. That means
            # that the subject is encoded with latin-1, and the stored
            # text is latin-1-subject + "\n" + binary-body. Content
            # type is "image/jpeg; name=image:<???>". Note that there
            # is no information regarding how subjects are encoded.
            #
            # TODO: What do we do if we can't encode the subject with
            # latin-1?
            fulltext = subject.encode('latin-1') + b"\n" + body
        else:
            raise KomSessionError("Unhandled content type: %s" % (mime_type,))
        komtext.text = fulltext

        misc_info_recipient_list = []
        for r in recipient_list:
            misc_info_recipient_list.append(
                MIRecipient(type=MIRecipient_str_to_type[r['type']],
                            recpt=r['recpt']['conf_no']))
        komtext.recipient_list = misc_info_recipient_list

        misc_info_comment_to_list = []
        for ct in comment_to_list:
            misc_info_comment_to_list.append(
                MICommentTo(type=MICommentTo_str_to_type[ct['type']],
                            text_no=ct['text_no']))
        komtext.comment_to_list = misc_info_comment_to_list

        aux_items = []
        # We need to make sure all aux items are encoded.
        if creating_software is not None:
            aux_items.append(AuxItemInput(tag=komauxitems.AI_CREATING_SOFTWARE,
                                          data=creating_software.encode('utf-8')))
        final_content_type = utils.mime_type_tuple_to_str(mime_type)
        aux_items.append(AuxItemInput(tag=komauxitems.AI_CONTENT_TYPE,
                                      data=final_content_type.encode('utf-8')))
        komtext.text_content_type = final_content_type
        komtext.aux_items = aux_items
        return komtext


def create_client(host, port, user):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    conn = Connection(s, user)
    client = Client(conn)
    return CachingPersonClient(client)


def check_connection(f):
    @functools.wraps(f)
    def decorated(komsession, *args, **kwargs):
        if not komsession.is_connected():
            raise KomSessionNotConnected()
        try:
            return f(komsession, *args, **kwargs)
        except socket.error as serr:
            if serr.errno in (errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN, errno.ETIMEDOUT):
                # If we got an error that indicates that the
                # connection has failed, then close and raise.
                komsession.close()
                raise KomSessionNotConnected(serr)
            else:
                raise KomSessionException(serr)

    return decorated


# Idea: rename KomSession to KomClient?
class KomSession(object):
    """ A LysKom session.

    Should handle either unicode strings or utf-8 encoded strings. (FIXME)

    TODO[Python3]: Only handle (unicode) strings, not bytes, in the
    external interfaces for things that are real strings. ??? (Or only
    bytes? Seems inconvient at this level.)

    """
    def __init__(self, client_factory=create_client):
        # TODO: We actually require the API of a
        # CachingPersonClient. We should enhance the Connection
        # class and make CachingPersonClient have the same API as
        # Connection.
        self._client_factory = client_factory
        self._client = None
        self._session_no = None
        self._client_name = None
        self._client_version = None

    def connect(self, host, port, username, hostname, client_name, client_version):
        assert not self.is_connected() # todo: raise better exception
        # decode if not already unicode (assuming utf-8)
        if isinstance(client_name, six.binary_type):
            client_name = client_name.decode('utf-8')
        if isinstance(client_version, six.binary_type):
            client_version = client_version.decode('utf-8')

        self._client = self._client_factory(host, port, user=username + "%" + hostname)

        # todo: we shouldn't require client name/version. specify in
        # constructor instead (because I don't think it should be
        # possible to change after connecting) - but send the request
        # here (if they are set).
        self._client.request(requests.ReqSetClientVersion(client_name, client_version))
        self._client_name = client_name
        self._client_version = client_version

        self._session_no = self.who_am_i()
        self._client.request(requests.ReqSetConnectionTimeFormat(use_utc=1))

    def is_connected(self):
        return self._client is not None

    def close(self):
        """Immediately close the connection, without sending a Disconnect request.
        """
        try:
            if self._client is not None:
                self._client.close()
        finally:
            self._client = None
            self._client_name = None
            self._client_version = None
            self._session_no = None

    @check_connection
    def disconnect(self, session_no=0):
        """Send a disconnect request.

        Session number 0 (the default) means the current session (a
        logged in user can disconnect its other sessions).

        If session_no=0, the KomSession will also be closed.

        """
        self._client.request(requests.ReqDisconnect(session_no))

        # Check if we disconnected our own session or not (you can
        # disconnect another LysKOM session that the logged in user is
        # a supervisor of).
        if session_no == 0 or session_no == self._session_no:
            self.close()

    @check_connection
    def login(self, pers_no, password):
        if isinstance(password, six.binary_type):
            password = password.decode('utf-8')
        pers_no = int(pers_no)
        self._client.login(pers_no, password)
        return self._get_person(pers_no)

    @check_connection
    def logout(self):
        self._client.logout()

    def get_current_person_no(self):
        return self._client.get_person_no()

    @check_connection
    def who_am_i(self):
        return self._client.request(requests.ReqWhoAmI())

    @check_connection
    def user_is_active(self):
        self._client.request(requests.ReqUserActive())

    @check_connection
    def is_logged_in(self):
        return self._client.is_logged_in()

    @check_connection
    def change_conference(self, conf_no):
        self._client.change_conference(conf_no)

    @check_connection
    def create_person(self, name, passwd):
        # decode if not already unicode (assuming utf-8)
        if isinstance(name, six.binary_type):
            name = name.decode('utf-8')
        if isinstance(passwd, six.binary_type):
            passwd = passwd.decode('utf-8')

        flags = PersonalFlags()
        aux_items = []
        pers_no = self._client.request(
            requests.ReqCreatePerson(name, passwd, flags, aux_items))
        stats.set('komsession.persons.created.last', 1, agg='sum')
        return self._get_person(pers_no)

    def _get_person(self, pers_no):
        username = self._client.conf_name(pers_no)
        return KomPerson(pers_no, username)

    @check_connection
    def get_person(self, pers_no):
        return self._get_person(pers_no)

    @check_connection
    def create_conference(self, name, aux_items=None):
        # decode if not already unicode (assuming utf-8)
        if isinstance(name, six.binary_type):
            name = name.decode('utf-8')

        conf_type = ConfType()
        if aux_items is None:
            aux_items = []
        conf_no = self._client.request(
            requests.ReqCreateConf(name.encode('latin1'), conf_type, aux_items))
        stats.set('komsession.conferences.created.last', 1, agg='sum')
        return conf_no

    @check_connection
    def delete_conference(self, conf_no):
        self._client.request(requests.ReqDeleteConf(conf_no))

    @check_connection
    def lookup_name(self, name, want_pers, want_confs):
        if isinstance(name, six.binary_type):
            name = name.decode('utf-8')
        return self._client.lookup_name(name, want_pers, want_confs)

    def lookup_name_exact(self, name, want_pers, want_confs):
        matches = self.lookup_name(name, want_pers, want_confs)
        return self._exact_lookup_match(name, matches)

    @check_connection
    def re_lookup_name(self, regexp, want_pers, want_confs):
        # The LysKOM server is always case sensitive, and it's kom.py
        # that tries to create a case-insensitive regexp. Doesn't seem
        # to work that well.
        return self._client.regexp_lookup(regexp, want_pers, want_confs, case_sensitive=1)

    def re_lookup_name_exact(self, regexp, want_pers, want_confs):
        matches = self.re_lookup_name(regexp, want_pers, want_confs)
        return self._exact_lookup_match(regexp, matches)

    @staticmethod
    def _exact_lookup_match(lookup, matches):
        if len(matches) == 0:
            raise NameNotFound("recipient not found: %s" % lookup)
        elif len(matches) != 1:
            raise AmbiguousName("ambiguous recipient: %s" % lookup)
        return matches[0][0]

    @check_connection
    def get_text_stat(self, text_no):
        return self._client.textstats[text_no]

    @check_connection
    def add_membership(self, pers_no, conf_no, priority, where):
        mtype = MembershipType()
        self._client.request(requests.ReqAddMember(conf_no, pers_no, priority, where, mtype))

    @check_connection
    def delete_membership(self, pers_no, conf_no):
        self._client.request(requests.ReqSubMember(conf_no, pers_no))

    @check_connection
    def get_membership(self, pers_no, conf_no):
        membership = self._client.get_membership(pers_no, conf_no, want_read_ranges=False)
        added_by = self._get_person(membership.added_by)
        conference = KomUConference(conf_no, uconf=self._client.uconferences[conf_no])
        return KomMembership(pers_no, added_by=added_by, conference=conference, membership=membership)

    @check_connection
    def get_membership_unread(self, pers_no, conf_no):
        membership = self._client.get_membership(pers_no, conf_no, want_read_ranges=True)
        unread_texts = self._client.get_unread_texts_from_membership(membership)
        return KomMembershipUnread(pers_no, conf_no, len(unread_texts), unread_texts)

    @check_connection
    def get_memberships(self, pers_no, first, no_of_confs, unread=False, passive=False):
        if unread:
            # RegGetUnreadConfs never returns passive memberships so
            # that combination is not valid.
            assert passive == False
            conf_nos = self._client.request(requests.ReqGetUnreadConfs(pers_no))
            # This may return conferences that don't have any unread
            # texts in them. We have to live with this, because we
            # don't want to get the unread texts in this case. It's
            # possible that we need to change this, which means that
            # unread=True may be a slower call.
            memberships = [ self.get_membership(pers_no, conf_no) for conf_no in conf_nos ]
            has_more = False
        else:
            ms_list = self._client.get_memberships(pers_no, first, no_of_confs,
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
                memberships.append(KomMembership(
                    pers_no,
                    added_by=self._get_person(membership.added_by),
                    conference=self._get_uconference(membership.conference),
                    membership=membership))

        return memberships, has_more

    @check_connection
    def get_membership_unreads(self, pers_no):
        conf_nos = self._client.request(requests.ReqGetUnreadConfs(pers_no))
        memberships = [ self.get_membership_unread(pers_no, conf_no)
                        for conf_no in conf_nos ]
        return [ m for m in memberships if m.no_of_unread > 0 ]

    @check_connection
    def get_conf_name(self, conf_no):
        return self._client.conf_name(conf_no)

    def _get_komauxitem(self, aux_item: AuxItem):
        creator = self._get_person(aux_item.creator)
        return KomAuxItem(aux_item, creator)

    def _get_komtext(self, text_no, text, text_stat: TextStat):
        author = self._get_person(text_stat.author)
        aux_items = [ self._get_komauxitem(ai) for ai in text_stat.aux_items ]
        return KomText(text_no=text_no, text=text, text_stat=text_stat, aux_items=aux_items, author=author)

    def _get_uconference(self, conf_no):
        return KomUConference(conf_no, uconf=self._client.uconferences[conf_no])

    def _get_conference(self, conf_no):
        conf = self._client.conferences[conf_no]
        aux_items = [ self._get_komauxitem(aux_item) for aux_item in conf.aux_items ]

        super_conf = None
        if conf.super_conf != 0:
            # super_conf can be 0, but invalid to get conf-stat for it.
            super_conf = self._get_uconference(conf.super_conf)

        permitted_submitters = None
        # if permitted_submitters is 0, anyone can submit articles
        if conf.permitted_submitters != 0:
            permitted_submitters = self._get_uconference(conf.permitted_submitters)

        return KomConference(
            conf_no,
            conf=conf,
            creator=self._get_person(conf.creator),
            supervisor=self._get_uconference(conf.supervisor),
            permitted_submitters=permitted_submitters,
            super_conf=super_conf,
            aux_items=aux_items)

    @check_connection
    def get_conference(self, conf_no, micro=True):
        conf_no = int(conf_no)
        if micro:
            return self._get_uconference(conf_no)
        else:
            return self._get_conference(conf_no)

    @check_connection
    def get_text(self, text_no) -> KomText:
        text_stat = self.get_text_stat(text_no)
        text = self._client.request(requests.ReqGetText(text_no))
        return self._get_komtext(text_no=text_no, text=text, text_stat=text_stat)

    # TODO: offset/start number, so we can paginate. we probably need
    # to return the local text number for that.
    @check_connection
    def get_last_texts(self, conf_no, no_of_texts, offset=0, full_text=False) -> List[KomText]:
        """Get the {no_of_texts} last texts in conference {conf_no},
        starting from {offset}.
        """
        #local_no_ceiling = 0 # means the higest numbered texts (i.e. the last)
        text_mapping = self._client.request(
            requests.ReqLocalToGlobalReverse(conf_no, 0, no_of_texts))
        texts = [ self._get_komtext(text_no=m[1], text=None, text_stat=self._client.textstats[m[1]])
                  for m in text_mapping.list if m[1] != 0 ]
        texts.reverse()
        return texts

    @check_connection
    def create_text(self, subject, body, content_type, content_encoding=None,
                    recipient_list=None, comment_to_list=None):
        # decode if not already unicode (assuming utf-8)
        if isinstance(subject, six.binary_type):
            subject = subject.decode('utf-8')
        if isinstance(body, six.binary_type):
            body = body.decode('utf-8')
        if isinstance(content_type, six.binary_type):
            content_type = content_type.decode('utf-8')

        if content_encoding is not None:
            if content_encoding == "base64":
                body = base64.b64decode(body)
            else:
                raise ValueError("Invalid content_encoding: {}".format(content_encoding))

        creating_software = "%s %s" % (self._client_name, self._client_version)

        komtext = KomText.create_new_text(
            subject, body, content_type,
            creating_software=creating_software,
            recipient_list=recipient_list,
            comment_to_list=comment_to_list)

        misc_info = CookedMiscInfo()
        misc_info.recipient_list = komtext.recipient_list
        misc_info.comment_to_list = komtext.comment_to_list

        text_no = self._client.request(
            requests.ReqCreateText(komtext.text, misc_info, komtext.aux_items))
        stats.set('komsession.texts.created.last', 1, agg='sum')
        return text_no

    @check_connection
    def mark_as_read(self, text_no):
        text_stat = self.get_text_stat(text_no)
        for mi in text_stat.misc_info.recipient_list:
            self._client.mark_as_read_local(mi.recpt, mi.loc_no)

    @check_connection
    def mark_as_unread(self, text_no):
        text_stat = self.get_text_stat(text_no)
        for mi in text_stat.misc_info.recipient_list:
            self._client.mark_as_unread_local(mi.recpt, mi.loc_no)

    @check_connection
    def set_unread(self, conf_no, no_of_unread):
        self._client.request(requests.ReqSetUnread(conf_no, no_of_unread))

    @check_connection
    def get_marks(self):
        return self._client.request(requests.ReqGetMarks())

    @check_connection
    def mark_text(self, text_no, mark_type):
        self._client.mark_text(text_no, mark_type)

    @check_connection
    def unmark_text(self, text_no):
        self._client.unmark_text(text_no)

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
        person_stat = self._client.request(requests.ReqGetPersonStat(pers_no))

        if person_stat.user_area == 0:
            # No user area
            return None

        # TODO: don't use external get_text method here - it should decode the body,
        # but we don't want to do that.
        text = self.get_text(person_stat.user_area)
        if text.content_type != 'x-kom/user-area':
            raise KomSessionError(
                "Unknown content type for user area text: %s" % (text.content_type,))

        blocks = utils.decode_user_area(text.body.encode('latin1')) #HACK
        block = blocks.get(block_name, None)
        if block is not None and json_decode:
            block = json.loads(block.decode('latin1')) #HACK

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
        person_stat = self._client.request(requests.ReqGetPersonStat(pers_no))

        if person_stat.user_area == 0:
            # No existing user area, initiate a new dictionary of
            # blocks.
            blocks = dict()
        else:
            # TODO: don't use external get_text method here - it
            # should decode the body, but we don't want to do that.
            user_area = self.get_text(person_stat.user_area)
            if user_area.content_type != 'x-kom/user-area':
                raise KomSessionError(
                    "Unknown content type for user area text: %s" % (user_area.content_type,))

            blocks = utils.decode_user_area(user_area.body.encode('latin1')) # HACK

        if json_encode:
            blocks[block_name] = json.dumps(block).encode('latin1') # HACK
        else:
            blocks[block_name] = block

        new_user_area_text_no = self.create_text(
            subject=None,
            body=utils.encode_user_area(blocks),
            content_type='x-kom/user-area')
        self._client.request(requests.ReqSetUserArea(pers_no, new_user_area_text_no))
        # TODO: Should it remove the old user area?
