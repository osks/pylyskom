# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.

from typing import Optional

from .datatypes import (
    ArrayAuxItem,
    String,
    ConfNo,
    TextNo,
    PersNo,
    Int32,
    TextStat,
    SessionNo,
    WhoInfo)


class AsyncMessages:
    """Enum like object which give names to the async message numbers
    in the protocol.
    """
    NEW_TEXT_OLD = 0
    NEW_NAME = 5
    I_AM_ON = 6
    SYNC_DB = 7
    LEAVE_CONF = 8
    LOGIN = 9
    REJECTED_CONNECTION = 11
    SEND_MESSAGE = 12
    LOGOUT = 13
    DELETED_TEXT = 14
    NEW_TEXT = 15
    NEW_RECIPIENT = 16
    SUB_RECIPIENT = 17
    NEW_MEMBERSHIP = 18
    NEW_USER_AREA = 19
    NEW_PRESENTATION = 20
    NEW_MOTD = 21
    TEXT_AUX_CHANGED = 22


#
# Classes for asynchronous messages from the server are all
# subclasses of AsyncMessage.
#

class AsyncMessage:
    MSG_NO: Optional[int] = None

    def to_json(self):
        """Serializes the message to a dictionary that can be
        represented as json. The MSG_NO for the AsyncMessage should be
        available as the value for the key 'msg_no'.

        Subclasses should override this if they have more
        properties. The 'msg_no' key should still always be available.
        
        @returns A dictionary that can be json serialized.
        """
        return dict(msg_no=self.MSG_NO)

    @classmethod
    def parse(cls, conn):
        """Parses the message from the connection and returns a new
        instance of the parsed message."""
        raise NotImplementedError()

    @classmethod
    def from_json(cls, json_obj):
        """Parses the message from a dictionary that has be
        deserialized form json, and returns a new instance of the
        parsed message.
        
        @param json_obj A dictionary with the json representation.

        @returns A new instance of the message.
        """
        raise NotImplementedError()

# async-new-text-old [0] (1) Obsolete (10) <DEFAULT>
class AsyncNewTextOld(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_TEXT_OLD

    def __init__(self, text_no, text_stat):
        self.text_no = text_no
        self.text_stat = text_stat

    def to_json(self):
        d = AsyncMessage.to_json(self)
        d['text_no'] = self.text_no
        # TODO: text_stat=self.text_stat.to_json()
        return d

    def __str__(self):
        return "<AsyncNewTextOld %d>" % (self.text_no,)

    @classmethod
    def parse(cls, conn):
        obj = cls(TextNo.parse(conn), TextStat.parse(conn, old_format=1))
        return obj

    @classmethod
    def from_json(cls, json_obj):
        obj = cls(json_obj['text_no'])
        #TODO: cls.text_stat = TextStat.from_json(json_obj['text_stat'])
        return obj

# async-i-am-off [1] (1) Obsolete
# async-i-am-on-onsolete [2] (1) Obsolete

# async-new-name [5] (1) Recommended <DEFAULT>
class AsyncNewName(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_NAME
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.conf_no = ConfNo.parse(conn)
        obj.old_name = String.parse(conn)
        obj.new_name = String.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncNewName %d: %s => %s>" % (self.conf_no, self.old_name, self.new_name)

# async-i-am-on [6] Recommended
class AsyncIAmOn(AsyncMessage):
    MSG_NO = AsyncMessages.I_AM_ON
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.info = WhoInfo.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncIAmOn %s>" % (self.info, )

# async-sync-db [7] (1) Recommended <DEFAULT>
class AsyncSyncDB(AsyncMessage):
    MSG_NO = AsyncMessages.SYNC_DB
    @classmethod
    def parse(cls, conn):
        obj = cls()
        return obj

    def __str__(self):
        return "<AsyncSyncDB>"

# async-leave-conf [8] (1) Recommended <DEFAULT>
class AsyncLeaveConf(AsyncMessage):
    MSG_NO = AsyncMessages.LEAVE_CONF
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.conf_no = ConfNo.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncLeaveConf %d>" % (self.conf_no, )

# async-login [9] (1) Recommended <DEFAULT>
class AsyncLogin(AsyncMessage):
    MSG_NO = AsyncMessages.LOGIN

    def __init__(self, person_no, session_no):
        self.person_no = person_no
        self.session_no = session_no

    def to_json(self):
        d = AsyncMessage.to_json(self)
        d['person_no'] = self.person_no
        d['session_no'] = self.session_no
        return d

    def __str__(self):
        return "<AsyncLogin %d (session: %d)>" % (self.person_no, self.session_no)

    @classmethod
    def parse(cls, conn):
        obj = cls(PersNo.parse(conn), SessionNo.parse(conn))
        return obj

    @classmethod
    def from_json(cls, json_obj):
        obj = cls(json_obj['person_no'], json_obj['session_no'])
        return obj


# async-broadcast [10] Obsolete

# async-rejected-connection [11] (1) Recommended <DEFAULT>
class AsyncRejectedConnection(AsyncMessage):
    MSG_NO = AsyncMessages.REJECTED_CONNECTION
    @classmethod
    def parse(cls, conn):
        obj = cls()
        return obj

    def __str__(self):
        return "<AsyncRejectedConnection>"

# async-send-message [12] (1) Recommended <DEFAULT>
class AsyncSendMessage(AsyncMessage):
    MSG_NO = AsyncMessages.SEND_MESSAGE
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.recipient = ConfNo.parse(conn)
        obj.sender = PersNo.parse(conn)
        obj.message = String.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncSendMessage %d => %d: %s>" % (self.sender, self.recipient, self.message)

# async-logout [13] (1) Recommended <DEFAULT>
class AsyncLogout(AsyncMessage):
    MSG_NO = AsyncMessages.LOGOUT

    def __init__(self, person_no, session_no):
        self.person_no = person_no
        self.session_no = session_no

    def to_json(self):
        d = AsyncMessage.to_json(self)
        d['person_no'] = self.person_no
        d['session_no'] = self.session_no
        return d

    def __str__(self):
        return "<AsyncLogout %d (session: %s)>" % (self.person_no, self.session_no)

    @classmethod
    def parse(cls, conn):
        obj = cls(PersNo.parse(conn), SessionNo.parse(conn))
        return obj

    @classmethod
    def from_json(cls, json_obj):
        obj = cls(json_obj['person_no'], json_obj['session_no'])
        return obj

# async-deleted-text [14] (10) Recommended
class AsyncDeletedText(AsyncMessage):
    MSG_NO = AsyncMessages.DELETED_TEXT
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.text_no = TextNo.parse(conn)
        obj.text_stat = TextStat.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncDeletedText %d>" % (self.text_no,)

# async-new-text [15] (10) Recommended
class AsyncNewText(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_TEXT

    def __init__(self, text_no, text_stat):
        self.text_no = text_no
        self.text_stat = text_stat

    def to_json(self):
        d = AsyncMessage.to_json(self)
        d['text_no'] = self.text_no
        # TODO: d['text_stat'] = self.text_stat.to_json()
        return d

    def __str__(self):
        return "<AsyncNewText %d>" % (self.text_no,)

    @classmethod
    def parse(cls, conn):
        obj = cls(TextNo.parse(conn), TextStat.parse(conn))
        return obj

    @classmethod
    def from_json(cls, json_obj):
        obj = cls(json_obj['text_no'], None)
        #TODO: cls.text_stat = TextStat.from_json(json_obj['text_stat'])
        return obj

# async-new-recipient [16] (10) Recommended
class AsyncNewRecipient(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_RECIPIENT
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.text_no = TextNo.parse(conn)
        obj.conf_no = ConfNo.parse(conn)
        obj.type = Int32.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncNewRecipient %d: %d>" % (self.text_no, self.conf_no)

# async-sub-recipient [17] (10) Recommended
class AsyncSubRecipient(AsyncMessage):
    MSG_NO = AsyncMessages.SUB_RECIPIENT
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.text_no = TextNo.parse(conn)
        obj.conf_no = ConfNo.parse(conn)
        obj.type = Int32.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncSubRecipient %d: %d>" % (self.text_no, self.conf_no)

# async-new-membership [18] (10) Recommended
class AsyncNewMembership(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_MEMBERSHIP
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.person_no = PersNo.parse(conn)
        obj.conf_no = ConfNo.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncNewMembership %d: %d>" % (self.person_no, self.conf_no)

# async-new-user-area [19] (11) Recommended
class AsyncNewUserArea(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_USER_AREA
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.person_no = PersNo.parse(conn)
        obj.old_user_area = TextNo.parse(conn)
        obj.new_user_area = TextNo.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncNewUserArea %d: %d => %d>" % (
            self.person_no, self.old_user_area, self.new_user_area)

# async-new-presentation [20] (11) Recommended
class AsyncNewPresentation(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_PRESENTATION
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.conf_no = ConfNo.parse(conn)
        obj.old_presentation = TextNo.parse(conn)
        obj.new_presentation = TextNo.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncNewPresentation %d: %d => %d>" % (
            self.conf_no, self.old_presentation, self.new_presentation)

# async-new-motd [21] (11) Recommended
class AsyncNewMotd(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_MOTD
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.conf_no = ConfNo.parse(conn)
        obj.old_motd = TextNo.parse(conn)
        obj.new_motd = TextNo.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncNewMotd %d: %d => %d>" % (
            self.conf_no, self.old_motd, self.new_motd)

# async-text-aux-changed [22] (11) Recommended
class AsyncTextAuxChanged(AsyncMessage):
    MSG_NO = AsyncMessages.TEXT_AUX_CHANGED
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.text_no = TextNo.parse(conn)
        obj.deleted = ArrayAuxItem.parse(conn)
        obj.added = ArrayAuxItem.parse(conn)
        return obj

    def __str__(self):
        return "<AsyncTextAuxChanged %d>" % (self.text_no,)


async_dict = {
    AsyncMessages.NEW_TEXT_OLD: AsyncNewTextOld,
    AsyncMessages.NEW_NAME: AsyncNewName,
    AsyncMessages.I_AM_ON: AsyncIAmOn,
    AsyncMessages.SYNC_DB: AsyncSyncDB,
    AsyncMessages.LEAVE_CONF: AsyncLeaveConf,
    AsyncMessages.LOGIN: AsyncLogin,
    AsyncMessages.REJECTED_CONNECTION: AsyncRejectedConnection,
    AsyncMessages.SEND_MESSAGE: AsyncSendMessage,
    AsyncMessages.LOGOUT: AsyncLogout,
    AsyncMessages.DELETED_TEXT: AsyncDeletedText,
    AsyncMessages.NEW_TEXT: AsyncNewText,
    AsyncMessages.NEW_RECIPIENT: AsyncNewRecipient,
    AsyncMessages.SUB_RECIPIENT: AsyncSubRecipient,
    AsyncMessages.NEW_MEMBERSHIP: AsyncNewMembership,
    AsyncMessages.NEW_USER_AREA: AsyncNewUserArea,
    AsyncMessages.NEW_PRESENTATION: AsyncNewPresentation,
    AsyncMessages.NEW_MOTD: AsyncNewMotd,
    AsyncMessages.TEXT_AUX_CHANGED: AsyncTextAuxChanged,
    }
