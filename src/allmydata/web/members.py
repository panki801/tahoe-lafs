import time, os

from twisted.internet import address
from twisted.web import http
from nevow import rend, url, tags as T,guard
from nevow.inevow import IRequest,ISession
from nevow.static import File as nevow_File # TODO: merge with static.File?
from nevow.util import resource_filename

import allmydata # to display import path
from allmydata import get_package_versions_string
from allmydata.util import log
from allmydata.interfaces import IFileNode
from allmydata.web import filenode, directory, unlinked, status, operations
from allmydata.web import storage
from allmydata.web.common import abbreviate_size, getxmlfile, WebError, \
     get_arg, RenderMixin, get_format, get_mutable_type, TIME_FORMAT

import dbtahoe,login




class URIHandler(RenderMixin, rend.Page):
    # I live at /uri . There are several operations defined on /uri itself,
    # mostly involved with creation of unlinked files and directories.

    def __init__(self, client):
        rend.Page.__init__(self, client)
        self.client = client
    
    def render_POST(self, ctx):
        # "POST /uri?t=upload&file=newfile" to upload an
        # unlinked file or "POST /uri?t=mkdir" to create a
        # new directory
        req = IRequest(ctx)
        session=req.getSession()
        if(login.checkLogin(session,ctx,0)==False):
         return "please logon on the system"

        action = get_arg(req, "action", "").strip()
        username = get_arg(req, "username", "").strip()
        fullname = get_arg(req, "fullname", "").strip()
        password= get_arg(req, "password", "").strip()
        DIR= get_arg(req, "DIR", "").strip()
        
        if(action=='addmember'):
         dbtahoe.add_member(username,fullname,password,DIR)

        there = url.URL.fromContext(ctx).parentdir()
        there = there.child("members")
        return there
         
 

class Members(rend.Page):

    addSlash = True

    docFactory = getxmlfile("members.xhtml")

    #def createSession(self, ctx):
    #   self.session=ISession(ctx)

    def __init__(self, client, clock=None,web_adminpass=None):
        rend.Page.__init__(self, client)
        self.client = client

        # If set, clock is a twisted.internet.task.Clock that the tests
        # use to test ophandle expiration.
        self.child_operations = operations.OphandleTable(clock)
        self.child_opr=URIHandler(client)
        try:
            self.members=dbtahoe.all_members()
        except:
            dbtahoe.createDB()
            self.members=dbtahoe.all_members()

        try:
            s = client.getServiceNamed("storage")
        except KeyError:
            s = None
    #    self.child_storage = storage.StorageStatus(s, self.client.nickname)
    #   self.child_named = FileHandler(client)
      #  self.child_status = status.Status(client.get_history())
      #  self.child_statistics = status.Statistics(client.stats_provider)
        static_dir = resource_filename("allmydata.web", "static")
        for filen in os.listdir(static_dir):
            self.putChild(filen, nevow_File(os.path.join(static_dir, filen)))


    # FIXME: This code is duplicated in root.py and introweb.py.
    def data_rendered_at(self, ctx, data):
        
        self.members=dbtahoe.all_members();
        return time.strftime(TIME_FORMAT, time.localtime())

    def data_version(self, ctx, data):
        req=IRequest(ctx)
       # global members

        if(login.checkLogin(req.getSession(),ctx, 0)==False):
            req.redirect('../')
        return get_package_versions_string()

    def data_import_path(self, ctx, data):
        return str(allmydata)
    def render_my_nodeid(self, ctx, data):
        tubid_s = "TubID: "+self.client.get_long_tubid()
        return T.td(title=tubid_s)[self.client.get_long_nodeid()]
    def data_my_nickname(self, ctx, data):
        return self.client.nickname
    
    def data_members(self,ctx,data):
      return self.members.fetchall()

    def render_members_row(self,ctx, data):

      ctx.fillSlots("username",data[0])
      ctx.fillSlots("full_name",data[1])
      D="N/A"
      if(data[2]!=None):
         D=data[2]

      ctx.fillSlots("last_logon",D)
      ctx.fillSlots("DIR",data[3])
      
      return ctx.tag

