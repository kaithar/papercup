import os, sys
import tornado.ioloop
import tornado.web
import tornado.autoreload
from pid import PidFile, PidFileAlreadyRunningError, PidFileAlreadyLockedError
import time
import logging

import papercup.config as config

static_path = None

routes = []
timers = []

import papercup.logs as logs

def main():
    global routes, static_path, timers
    sys.path.append(os.getcwd())

    config.load()

    logs.init()
    logger = logs.logger

    logger.info("")
    logger.info("")
    logger.info("################### !!! LOG BEGINS !!! ######################")
    logger.info("")
    logger.info("")
    logger.info("Initializing " + config.get("papercup", "name") + "...")

    logger.info("Config:")
    import pprint
    pprint.pprint(config.config_data)
    logger.info("")

    baseguess = os.getcwd()

    pidfile = config.get('papercup', 'pidfile')
    if (pidfile[0] == '/'):
        piddir = os.path.dirname(pidfile)
        pidfile = os.path.basename(pidfile)
    else:
        piddir = baseguess
    logger.info("")
    logger.info("Writing pid file: %s/%s"%(piddir, pidfile))
    pf_handler = PidFile(pidname=pidfile, piddir=piddir)

    passed = False
    for _ in range(0,10):
        try:
            pf_handler.create()
            tornado.autoreload.add_reload_hook(pf_handler.close)
            passed = True
            break
        except PidFileAlreadyRunningError:
            logger.info("Pid file already running, retrying...")
            time.sleep(0.5)
        except PidFileAlreadyLockedError:
            logger.info("Pid file already locked, retrying...")
            time.sleep(0.5)
    if not passed:
        logger.info("Giving up")
        return

    logger.info("")
    config.init_modules()

    import traceback
    import fnmatch
    from importlib import import_module
    import inspect
    from papercup import handlers
    client = None
    sentry_client = None

    logger.info("")
    logger.info("Base routes...")
    routes = []
    from papercup import handlers
    for route, c, tkwargs in handlers.routes:
      routes.append(tornado.web.URLSpec(route, c, tkwargs, None))

    route_text = "Base Routes:\n"
    for k in routes:
        if isinstance(k, tornado.web.URLSpec):
            cname = getattr(k.handler_class,"unbound_repr", None)
            if cname:
                cname = cname()
            else:
                cname = k.handler_class
            route_text += "  -- URLSpec(%-25s\t%s, kwargs=%r, name=%r)\n"%(
                        "%r,"%k.regex.pattern, cname, k.kwargs, k.name)
        else:
            route_text += "  -- %s\n"%str(k)
    logger.info(route_text)

    application = tornado.web.Application(routes, **config.get('papercup', 'tornado'))
    application.sentry_client = sentry_client
    application.listen(config.get('papercup', 'port'), xheaders=config.get('papercup', 'tornado', 'xheaders'))

    # Tornado requires a settings entry for 'static_path' in order to make use of its static_url() method within template files, even though a separate handler was defined above.  However just adding the setting to the config, even though it's not used, will allow access to proper caching behavior.
    application.settings['static_path'] = static_path

    logger.info("")
    logger.info("Running...")
    logger.info("")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    import papercup.main
    papercup.main.main()
