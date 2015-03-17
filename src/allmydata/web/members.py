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


class Login(rend.Page):

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
        try:
            s = client.getServiceNamed("storage")
        except KeyError:
            s = None
    #    self.child_storage = storage.StorageStatus(s, self.client.nickname)
        self.child_uri = URIHandler(client,web_adminpass)

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


    # FIXME: This code is duplicated in root.py and introweb.py.
    def data_rendered_at(self, ctx, data):
        return time.strftime(TIME_FORMAT, time.localtime())

    def data_version(self, ctx, data):
        return get_package_versions_string()

    def data_import_path(self, ctx, data):
        return str(allmydata)
    def render_my_nodeid(self, ctx, data):
        tubid_s = "TubID: "+self.client.get_long_tubid()
        return T.td(title=tubid_s)[self.client.get_long_nodeid()]
    def data_my_nickname(self, ctx, data):
        return self.client.nickname


