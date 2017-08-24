# routing
import tornado.web
import tornado.websocket
from concurrent.futures import ThreadPoolExecutor
import os
import pystache
import traceback
import papercup

routes = []

def handle_url(route, target_kwargs=None):
  def handle_url_inner(cls):
    routes.append((route, cls, target_kwargs))
    return cls
  return handle_url_inner

try:
    from raven.contrib.tornado import SentryMixin
except:
    class SentryMixin(object):
        pass

class template_base(SentryMixin):
    # search_dirs=[os.path.join(
    #             config.papercup['base'],
    #             config.papercup['project'],
    #             "templates"),]
    # Singletons
    executor = ThreadPoolExecutor(max_workers=50)
    watched_files = []
    renderer = pystache.Renderer()
    loader = pystache.loader.Loader()
    locator = pystache.locator.Locator()

    def adjusted_url(self):
        url = self.request.full_url()
        if ("X-Forwarded-Proto" in self.request.headers):
            url = url.replace(
                    "http://",
                    "{}://".format(self.request.headers["X-Forwarded-Proto"]))
        return url

class request_base(template_base):
    pass

class Request_handler(tornado.web.RequestHandler, request_base):
    @classmethod
    def unbound_repr(cls):
        return "<Handler "+cls.__module__.split('.')[-1]+"."+cls.__name__+">"

    def initialize(self):
      if papercup.Session:
        self.session = papercup.Session(self)

class Static_handler(tornado.web.StaticFileHandler, request_base):
  pass

class Websocket_handler(tornado.websocket.WebSocketHandler, request_base):
    @classmethod
    def unbound_repr(cls):
        return "<Websocket "+cls.__module__.split('.')[-1]+"."+cls.__name__+">"

    def open(self):
      if papercup.Session:
        self.session = papercup.Session(self, read_only=True)
        #if not privs_good(self, None):
        #    self.write_message("Not authed: %s"%(repr(self.session['user.id'])))
        #    self.close()
      self.on_open()

import logging

class Periodic_handler(template_base):
    def _callback(self):
        logger = logging.getLogger('papercup.periodic')
        try:
            logger.info("Running periodic callback: %s" % str(self))
            self.run()
        except:
            logger.error("Exception in runner!", exc_info=1)
