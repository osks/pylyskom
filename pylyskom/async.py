# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.

from .datatypes import (
    Array,
    AuxItem,
    String,
    ConfNo,
    TextNo,
    PersonNo,
    Int32,
    TextStat,
    SessionNo,
    WhoInfo)


class AsyncMessages(object):
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

class AsyncMessage(object):
    MSG_NO = None
    @classmethod
    def parse(cls, conn):
        """Parses the message from the connection and returns a new
        instance of the parsed message."""
        raise NotImplementedError()

# async-new-text-old [0] (1) Obsolete (10) <DEFAULT>
class AsyncNewTextOld(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_TEXT_OLD
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.text_no = TextNo.parse(conn)
        obj.text_stat = TextStat.parse(conn, old_format=1)
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

# async-i-am-on [6] Recommended
class AsyncIAmOn(AsyncMessage):
    MSG_NO = AsyncMessages.I_AM_ON
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.info = WhoInfo.parse(conn)
        return obj

# async-sync-db [7] (1) Recommended <DEFAULT>
class AsyncSyncDB(AsyncMessage):
    MSG_NO = AsyncMessages.SYNC_DB
    @classmethod
    def parse(cls, conn):
        obj = cls()
        return obj

# async-leave-conf [8] (1) Recommended <DEFAULT>
class AsyncLeaveConf(AsyncMessage):
    MSG_NO = AsyncMessages.LEAVE_CONF
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.conf_no = ConfNo.parse(conn)
        return obj

# async-login [9] (1) Recommended <DEFAULT>
class AsyncLogin(AsyncMessage):
    MSG_NO = AsyncMessages.LOGIN
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.person_no = PersonNo.parse(conn)
        obj.session_no = SessionNo.parse(conn)
        return obj

# async-broadcast [10] Obsolete

# async-rejected-connection [11] (1) Recommended <DEFAULT>
class AsyncRejectedConnection(AsyncMessage):
    MSG_NO = AsyncMessages.REJECTED_CONNECTION
    @classmethod
    def parse(cls, conn):
        obj = cls()
        return obj

# async-send-message [12] (1) Recommended <DEFAULT>
class AsyncSendMessage(AsyncMessage):
    MSG_NO = AsyncMessages.SEND_MESSAGE
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.recipient = ConfNo.parse(conn)
        obj.sender = PersonNo.parse(conn)
        obj.message = String.parse(conn)
        return obj

# async-logout [13] (1) Recommended <DEFAULT>
class AsyncLogout(AsyncMessage):
    MSG_NO = AsyncMessages.LOGOUT
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.person_no = PersonNo.parse(conn)
        obj.session_no = SessionNo.parse(conn)
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

# async-new-text [15] (10) Recommended
class AsyncNewText(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_TEXT
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.text_no = TextNo.parse(conn)
        obj.text_stat = TextStat.parse(conn)
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

# async-new-membership [18] (10) Recommended
class AsyncNewMembership(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_MEMBERSHIP
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.person_no = PersonNo.parse(conn)
        obj.conf_no = ConfNo.parse(conn)
        return obj

# async-new-user-area [19] (11) Recommended
class AsyncNewUserArea(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_USER_AREA
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.person_no = PersonNo.parse(conn)
        obj.old_user_area = TextNo.parse(conn)
        obj.new_user_area = TextNo.parse(conn)
        return obj

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

# async-text-aux-changed [22] (11) Recommended
class AsyncTextAuxChanged(AsyncMessage):
    MSG_NO = AsyncMessages.TEXT_AUX_CHANGED
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.text_no = TextNo.parse(conn)
        obj.deleted = Array(AuxItem).parse(conn)
        obj.added = Array(AuxItem).parse(conn)
        return obj

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
