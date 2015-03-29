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
from allmydata.web import storage,root
from allmydata.web.common import abbreviate_size, getxmlfile, WebError, \
     get_arg, RenderMixin, get_format, get_mutable_type, TIME_FORMAT



sessions={}
class Logout(RenderMixin, rend.Page):
    # I live at /uri . There are several operations defined on /uri itself,
    # mostly involved with creation of unlinked files and directories.

    def __init__(self, client):
        rend.Page.__init__(self, client)
        self.client = client

    def render_GET(self, ctx):
        req = IRequest(ctx)
        sess=ISession(ctx)
        sessions[sess]['logged']=0

        there = url.URL.fromContext(ctx)
        there = there.clear("../")

        return there



class URIHandler(RenderMixin, rend.Page):
    # I live at /uri . There are several operations defined on /uri itself,
    # mostly involved with creation of unlinked files and directories.

    def __init__(self, client, web_adminpass):
        rend.Page.__init__(self, client)
        self.client = client
        self.web_adminpass=web_adminpass

        self.session={}

    def render_GET(self, ctx):
        req = IRequest(ctx)
        uri = get_arg(req, "uri", None)
        if uri is None:
            raise WebError("GET /uri requires uri=")
        there = url.URL.fromContext(ctx)
        there = there.clear("uri")
        # I thought about escaping the childcap that we attach to the URL
        # here, but it seems that nevow does that for us.
        there = there.child(uri)
        return there

    def render_PUT(self, ctx):
        req = IRequest(ctx)
        # either "PUT /uri" to create an unlinked file, or
        # "PUT /uri?t=mkdir" to create an unlinked directory
        t = get_arg(req, "t", "").strip()
        if t == "":
            file_format = get_format(req, "CHK")
            mutable_type = get_mutable_type(file_format)
            if mutable_type is not None:
                return unlinked.PUTUnlinkedSSK(req, self.client, mutable_type)
            else:
                return unlinked.PUTUnlinkedCHK(req, self.client)
        if t == "mkdir":
            return unlinked.PUTUnlinkedCreateDirectory(req, self.client)
        errmsg = ("/uri accepts only PUT, PUT?t=mkdir, POST?t=upload, "
                  "and POST?t=mkdir")
        raise WebError(errmsg, http.BAD_REQUEST)

    def render_POST(self, ctx):
        # "POST /uri?t=upload&file=newfile" to upload an
        # unlinked file or "POST /uri?t=mkdir" to create a
        # new directory
        req = IRequest(ctx)
        session=ISession(ctx)
        login = get_arg(req, "login", "").strip()
        password= get_arg(req, "password", "").strip()
        w=req.getSession()
        
        try:
            self.session[w]
        except:
            self.session[w]={}
            self.session[w]['logged']=0


        if(self.session[w]['logged']==0):
            if(login=='admin' and password==self.web_adminpass):
                self.session[w]['user']='admin'
                self.session[w]['logged']=1
                req.redirect('test')
                there=url.URL.fromContext(ctx).parentdir()
                there=there.clear()
                there=there.child("test")
            else:
                there=url.URL.fromContext(ctx).parentdir()
                there=there.child("")

        else:
            there=url.URL.fromContext(ctx).parentdir()
            there=there.child("")
        
        global sessions
        sessions=self.session      
        return there 
        

        #raise WebError(errmsg, http.BAD_REQUEST)

    def childFactory(self, ctx, name):
        # 'name' is expected to be a URI
        try:
            node = self.client.create_node_from_uri(name)
            return directory.make_handler_for(node, self.client)
        except (TypeError, AssertionError):
            raise WebError("'%s' is not a valid file- or directory- cap"
                           % name)

class FileHandler(rend.Page):
    # I handle /file/$FILECAP[/IGNORED] , which provides a URL from which a
    # file can be downloaded correctly by tools like "wget".

    def __init__(self, client):
        rend.Page.__init__(self, client)
        self.client = client

    def childFactory(self, ctx, name):
        req = IRequest(ctx)
        if req.method not in ("GET", "HEAD"):
            raise WebError("/file can only be used with GET or HEAD")
        # 'name' must be a file URI
        try:
            node = self.client.create_node_from_uri(name)
        except (TypeError, AssertionError):
            # I think this can no longer be reached
            raise WebError("'%s' is not a valid file- or directory- cap"
                           % name)
        if not IFileNode.providedBy(node):
            raise WebError("'%s' is not a file-cap" % name)
        return filenode.FileNodeDownloadHandler(self.client, node)

    def renderHTTP(self, ctx):
        raise WebError("/file must be followed by a file-cap and a name",
                       http.NOT_FOUND)

class IncidentReporter(RenderMixin, rend.Page):
    def render_POST(self, ctx):
        req = IRequest(ctx)
        log.msg(format="User reports incident through web page: %(details)s",
                details=get_arg(req, "details", ""),
                level=log.WEIRD, umid="LkD9Pw")
        req.setHeader("content-type", "text/plain")
        return "An incident report has been saved to logs/incidents/ in the node directory."

SPACE = u"\u00A0"*2

class Login(rend.Page):

    addSlash = True

    docFactory = getxmlfile("welcome.xhtml")

    #def createSession(self, ctx):
    #   self.session=ISession(ctx)

    def __init__(self, client, clock=None,web_adminpass=None):
        rend.Page.__init__(self, client)
        self.client = client

        # If set, clock is a twisted.internet.task.Clock that the tests
        # use to test ophandle expiration.
        self.child_operations = operations.OphandleTable(clock)
        try:
            s = client.getServiceNamed("storage")
        except KeyError:
            s = None
    #    self.child_storage = storage.StorageStatus(s, self.client.nickname)
        self.child_uri = URIHandler(client,web_adminpass)
        self.child_logout = Logout(client)

        self.child_cap = URIHandler(client,web_adminpass)
        self.session={}
     #   self.child_file = FileHandler(client)
        self.child_test=root.Root(client)

     #   self.child_named = FileHandler(client)
      #  self.child_status = status.Status(client.get_history())
      #  self.child_statistics = status.Statistics(client.stats_provider)
        static_dir = resource_filename("allmydata.web", "static")
        for filen in os.listdir(static_dir):
            self.putChild(filen, nevow_File(os.path.join(static_dir, filen)))

    def child_helper_status(self, ctx):
        # the Helper isn't attached until after the Tub starts, so this child
        # needs to created on each request
        return status.HelperStatus(self.client.helper)

    child_report_incident = IncidentReporter()
    #child_server # let's reserve this for storage-server-over-HTTP

    # FIXME: This code is duplicated in root.py and introweb.py.
    def data_rendered_at(self, ctx, data):
        return time.strftime(TIME_FORMAT, time.localtime())

    def data_version(self, ctx, data):
        session=ISession(ctx)
        req=IRequest(ctx)
        #session=createSession(ctx)
        self.session[req.getSession()]={}
        self.session[req.getSession()]['logged']=0

        req=IRequest(ctx)
    #    self.webadmin=root.Root(self.client)
        #req.redirect('welcomeadmin')
        return get_package_versions_string()

    def data_import_path(self, ctx, data):
        return str(allmydata)
    def render_my_nodeid(self, ctx, data):
        tubid_s = "TubID: "+self.client.get_long_tubid()
        return T.td(title=tubid_s)[self.client.get_long_nodeid()]
    def data_my_nickname(self, ctx, data):
        return self.client.nickname
    
    def data_logout(self,ctx,data):
        pass


def checkLogin(session_id, ctx , group):
    global sessions
    req=IRequest(ctx)
    try:
       logged=sessions[session_id]['logged']
       user=sessions[session_id]['user']
    except:
       logged=0
       user=''
       return False
    

    if(user=='admin'):
        return True
