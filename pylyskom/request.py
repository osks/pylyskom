# -*- coding: utf-8 -*-

from . import kom


class Requests(object):
    """Used as an enum.
    """
    (AcceptAsync,
     AddMember,
     ChangeConference,
     CreateConf,
     CreatePerson,
     CreateText,
     Disconnect,
     GetCollateTable,
     GetConfStat,
     GetMarks,
     GetMembership,
     GetMembership11,
     GetPersonStat,
     GetText,
     GetTextStat,
     GetUconfStat,
     GetUnreadConfs,
     LocalToGlobal,
     LocalToGlobalReverse,
     Login,
     Logout,
     LookupZName,
     MarkAsRead,
     MarkAsUnread,
     MarkText,
     QueryReadTexts,
     QueryReadTexts11,
     ReZLookup,
     SetClientVersion,
     SetConnectionTimeFormat,
     SetUnread,
     SetUserArea,
     SubMember,
     UnmarkText,
     UserActive,
     WhoAmI) = range(36) # UPDATE WHEN ADDING/REMOVING VALUES.
    # range() is used to make sure that each "enum type" get a different value


_kom_request_to_class = {
    Requests.AcceptAsync: kom.ReqAcceptAsync,
    Requests.AddMember: kom.ReqAddMember,
    Requests.ChangeConference: kom.ReqChangeConference,
    Requests.CreateConf: kom.ReqCreateConf,
    Requests.CreatePerson: kom.ReqCreatePerson,
    Requests.CreateText: kom.ReqCreateText,
    Requests.Disconnect: kom.ReqDisconnect,
    Requests.GetCollateTable: kom.ReqGetCollateTable,
    Requests.GetConfStat: kom.ReqGetConfStat,
    Requests.GetMarks: kom.ReqGetMarks,
    Requests.GetMembership11: kom.ReqGetMembership11,
    Requests.GetMembership: kom.ReqGetMembership11,
    Requests.GetPersonStat: kom.ReqGetPersonStat,
    Requests.GetText: kom.ReqGetText,
    Requests.GetTextStat: kom.ReqGetTextStat,
    Requests.GetUconfStat: kom.ReqGetUconfStat,
    Requests.GetUnreadConfs: kom.ReqGetUnreadConfs,
    Requests.LocalToGlobal: kom.ReqLocalToGlobal,
    Requests.LocalToGlobalReverse: kom.ReqLocalToGlobalReverse,
    Requests.Login: kom.ReqLogin,
    Requests.Logout: kom.ReqLogout,
    Requests.LookupZName: kom.ReqLookupZName,
    Requests.MarkAsRead: kom.ReqMarkAsRead,
    Requests.MarkAsUnread: kom.ReqMarkAsUnread,
    Requests.MarkText: kom.ReqMarkText,
    Requests.QueryReadTexts11: kom.ReqQueryReadTexts11,
    Requests.QueryReadTexts: kom.ReqQueryReadTexts11,
    Requests.ReZLookup: kom.ReqReZLookup,
    Requests.SetClientVersion: kom.ReqSetClientVersion,
    Requests.SetConnectionTimeFormat: kom.ReqSetConnectionTimeFormat,
    Requests.SetUnread: kom.ReqSetUnread,
    Requests.SubMember: kom.ReqSubMember,
    Requests.SetUserArea: kom.ReqSetUserArea,
    Requests.UnmarkText: kom.ReqUnmarkText,
    Requests.UserActive: kom.ReqUserActive,
    Requests.WhoAmI: kom.ReqWhoAmI,
    # ... todo ...
}

class RequestFactory(object):
    def __init__(self, mapping):
        self.mapping = mapping

    def new(self, request):
        assert request in self.mapping
        return self.mapping[request]

default_request_factory = RequestFactory(_kom_request_to_class)
