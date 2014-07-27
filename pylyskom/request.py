# -*- coding: utf-8 -*-

import requests

# TODO: this file is pretty much not needed (but it is still used)
# after the refactorings.


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
    Requests.AcceptAsync: requests.ReqAcceptAsync,
    Requests.AddMember: requests.ReqAddMember,
    Requests.ChangeConference: requests.ReqChangeConference,
    Requests.CreateConf: requests.ReqCreateConf,
    Requests.CreatePerson: requests.ReqCreatePerson,
    Requests.CreateText: requests.ReqCreateText,
    Requests.Disconnect: requests.ReqDisconnect,
    Requests.GetCollateTable: requests.ReqGetCollateTable,
    Requests.GetConfStat: requests.ReqGetConfStat,
    Requests.GetMarks: requests.ReqGetMarks,
    Requests.GetMembership11: requests.ReqGetMembership11,
    Requests.GetMembership: requests.ReqGetMembership11,
    Requests.GetPersonStat: requests.ReqGetPersonStat,
    Requests.GetText: requests.ReqGetText,
    Requests.GetTextStat: requests.ReqGetTextStat,
    Requests.GetUconfStat: requests.ReqGetUconfStat,
    Requests.GetUnreadConfs: requests.ReqGetUnreadConfs,
    Requests.LocalToGlobal: requests.ReqLocalToGlobal,
    Requests.LocalToGlobalReverse: requests.ReqLocalToGlobalReverse,
    Requests.Login: requests.ReqLogin,
    Requests.Logout: requests.ReqLogout,
    Requests.LookupZName: requests.ReqLookupZName,
    Requests.MarkAsRead: requests.ReqMarkAsRead,
    Requests.MarkAsUnread: requests.ReqMarkAsUnread,
    Requests.MarkText: requests.ReqMarkText,
    Requests.QueryReadTexts11: requests.ReqQueryReadTexts11,
    Requests.QueryReadTexts: requests.ReqQueryReadTexts11,
    Requests.ReZLookup: requests.ReqReZLookup,
    Requests.SetClientVersion: requests.ReqSetClientVersion,
    Requests.SetConnectionTimeFormat: requests.ReqSetConnectionTimeFormat,
    Requests.SetUnread: requests.ReqSetUnread,
    Requests.SubMember: requests.ReqSubMember,
    Requests.SetUserArea: requests.ReqSetUserArea,
    Requests.UnmarkText: requests.ReqUnmarkText,
    Requests.UserActive: requests.ReqUserActive,
    Requests.WhoAmI: requests.ReqWhoAmI,
    # ... todo ...
}

class RequestFactory(object):
    def __init__(self, mapping):
        self.mapping = mapping

    def new(self, request):
        assert request in self.mapping
        return self.mapping[request]

default_request_factory = RequestFactory(_kom_request_to_class)
