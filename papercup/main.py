import os, sys
import tornado.ioloop
import tornado.web
import tornado.autoreload
from pid import PidFile, PidFileAlreadyRunningError, PidFileAlreadyLockedError
import time
import logging
import argparse

import papercup.config as config

static_path = None
args = None

routes = []
timers = []
exit_hooks = []

import papercup.logs as logs

def main():
    global args
    sys.path.append(os.getcwd())

    # Options are up first
    parser = argparse.ArgumentParser(description='Papercup main entrypoint', fromfile_prefix_chars='@')
    subparsers = parser.add_subparsers(title='commands', dest='cmd')
    parser_start = subparsers.add_parser('start', help='Start the papercup server')
    parser_revision = subparsers.add_parser('revision', help='Create a new alembic migration')
    parser_migrate = subparsers.add_parser('migrate', help='Run all pending migrations')
    parser_heads = subparsers.add_parser('heads', help='See alembic heads')
    parser_history = subparsers.add_parser('history', help='See alembic history')
    parser_upgrade = subparsers.add_parser('upgrade', help='Upgrade database tables')
    parser_downgrade = subparsers.add_parser('downgrade', help='Downgrade database tables')

    parser_revision.add_argument('-m', '--message', help='Message string for revision')
    parser_revision.add_argument('--init', help='Create a new root revision for a module', action='store_true')
    parser_revision.add_argument('--autogenerate', help='Try and guess about the changes wanted', action='store_true')
    parser_revision.add_argument('module', help='Module to add revision to')
    parser_heads.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser_history.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser_downgrade.add_argument('target', help='Target revision')
    
    parser.add_argument('-d', '--debug', help="Debugging stuff", action='store_true')
    args = parser.parse_args()
    if args.debug:
        print(args)

    config.load()

    logs.init()
    logger = logs.logger

    logger.info("")
    logger.info("")
    logger.info("################### !!! LOG BEGINS !!! ######################")
    logger.info("")
    logger.info("")
    logger.info("Initializing " + config.get("papercup", "name") + "...")

    if args.debug:
        logger.info("Config:")
        import pprint
        pprint.pprint(config.config_data)

    logger.info("")

    baseguess = os.getcwd()

    func = None
    func = {
        'start': start,
        None: start,
        'revision': revision,
        'heads': heads,
        'history': history,
        'upgrade': upgrade,
        'downgrade': downgrade,
    }.get(args.cmd, None)
    if not func:
        print('{} isn\' a known command'.format(args.cmd))
        return
    else:
        func(args, logger, baseguess)

def alembic_setup(logger):
    logger.info("")
    config.init_modules()
    usable_modules = config.config_data['papercup']['modules_by_name']
    alembic_modules = ['papercup']
    alembic_versions = [os.path.join(os.path.dirname(__file__), 'migrations', 'versions')]
    for m in config.config_data['papercup']['loaded_modules']:
        if hasattr(usable_modules[m], 'alembic'):
            alembic_modules.append(m)
            alembic_versions.append(usable_modules[m].alembic['versions'])
    from alembic.config import Config
    alembic_config = Config()
    alembic_config.set_main_option('script_location', os.path.join(os.path.dirname(__file__), 'migrations'))
    alembic_config.set_main_option('version_locations', ' '.join(alembic_versions))
    alembic_config.set_section_option('loggers', 'keys', 'root,sqlalchemy,alembic')
    alembic_config.set_section_option('handlers', 'keys', 'console')
    alembic_config.set_section_option('formatters', 'keys', 'generic')
    alembic_config.set_section_option('logger_root', 'level', 'WARN')
    alembic_config.set_section_option('logger_root', 'handlers', 'console')
    alembic_config.set_section_option('logger_root', 'qualname', '')
    alembic_config.set_section_option('logger_sqlalchemy', 'level', 'WARN')
    alembic_config.set_section_option('logger_sqlalchemy', 'handlers', '')
    alembic_config.set_section_option('logger_sqlalchemy', 'qualname', 'sqlalchemy.engine')
    alembic_config.set_section_option('logger_alembic', 'level', 'INFO')
    alembic_config.set_section_option('logger_alembic', 'handlers', '')
    alembic_config.set_section_option('logger_alembic', 'qualname', 'alembic')
    alembic_config.set_section_option('handler_console', 'class', 'StreamHandler')
    alembic_config.set_section_option('handler_console', 'args', '(sys.stderr,)')
    alembic_config.set_section_option('handler_console', 'level', 'NOTSET')
    alembic_config.set_section_option('handler_console', 'formatter', 'generic')
    alembic_config.set_section_option('formatter_generic', 'format', '%%(levelname)-5.5s [%%(name)s] %%(message)s')
    alembic_config.set_section_option('formatter_generic', 'datefmt', '%%H:%%M:%%S')
    #alembic_cfg.attributes['connection'] = connection
    return (usable_modules, alembic_modules, alembic_config)


def revision(args,logger, baseguess):
    usable_modules, alembic_modules, alembic_config = alembic_setup(logger)
    from alembic import command
    if args.init:
        if args.module not in alembic_modules:
            print('{} isn\'t a configured module.  You can create revisions on one of these: {}'.format(args.module, ', '.join(alembic_modules)))
            return
        command.revision(config=alembic_config, message=args.message, head='base', branch_label=args.module,
                         autogenerate=args.autogenerate,
                         version_path=usable_modules[args.module].alembic['versions'])
    else:
        command.revision(config=alembic_config, message=args.message, autogenerate=args.autogenerate,
                         head='{}@head'.format(args.module))

def heads(args,logger, baseguess):
    usable_modules, alembic_modules, alembic_config = alembic_setup(logger)
    from alembic import command
    command.heads(config=alembic_config, verbose=(args.verbose == True), resolve_dependencies=True)

def history(args,logger, baseguess):
    usable_modules, alembic_modules, alembic_config = alembic_setup(logger)
    from alembic import command
    command.history(config=alembic_config, verbose=(args.verbose == True))

def upgrade(args,logger, baseguess):
    usable_modules, alembic_modules, alembic_config = alembic_setup(logger)
    from alembic import command
    command.upgrade(config=alembic_config, revision='heads')

def downgrade(args,logger, baseguess):
    usable_modules, alembic_modules, alembic_config = alembic_setup(logger)
    from alembic import command
    command.downgrade(config=alembic_config, revision=args.target)


def start(args, logger, baseguess):
    global routes, static_path, timers
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
    config.prerun_modules()

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
    try:
        tornado.ioloop.IOLoop.instance().start()
    finally:
        for f in exit_hooks:
            f()


if __name__ == "__main__":
    import papercup.main
    papercup.main.main()
