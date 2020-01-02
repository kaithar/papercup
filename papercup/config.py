import json
from boltons.iterutils import remap, get_path, default_enter
import copy
import os
from importlib import import_module
import traceback

config_data = None

def load():
  global config_data
  # Our defaults
  baseguess = os.getcwd()
  base = {
    "papercup": {
      "name": "Papercup container",
      "request_modules": [],
      'base': baseguess,
      'port': 8080,
      'tornado': {
        "xsrf_cookies": False,
        "debug": False,
        "xheaders": False,
        "cookie_secret": ""
      },
      'ssl' : {
          "use_ssl" : False,
          "certfile" : os.path.join(baseguess, "main_module_name.crt"),
          "keyfile" : os.path.join(baseguess, "main_module_name.key")
      },
      'pidfile': "papercup.pid"
    }
  }

  merge_config = None
  config_file = None
  def _dmerge(p,k,v):
    try:
      return (k, v if isinstance(v,dict) else get_path(merge_config, p+(k,)))
    except:
      return (k, v)
  def _dover_enter(p,k,v):
    ret = default_enter(p,k,v)
    if k == None:
      return ret
    try:
      n = get_path(config, p)
      if (k not in n):
        n[k] = v
        return (ret[0],False)
    except:
      pass
    return ret
  # Try loading the config file
  try:
    with open(os.path.join(baseguess, 'config.json'), 'r') as conf:
      merge_config = config_file = json.load(conf)
      base = remap(base, _dmerge)
  except Exception as e:
    print("Failed config.json")
    print(traceback.format_exc())
    pass
  config = copy.deepcopy(base)
  # load modules to check for requirements
  try_modules = []
  usable_modules = {}
  requested = copy.copy(base['papercup']['request_modules'])
  attempting = []
  failed = []

  def _attempt_reqs(mod):
    if (mod in failed):
      raise Exception("Already failed {}".format(mod))
    needs = [mod]
    attempting.append(mod)
    m = import_module(mod)
    usable_modules[mod] = m
    if hasattr(m, 'requires') and isinstance(m.requires, list):
      for r in m.requires:
        if (r not in attempting and r not in try_modules):
          needs = _attempt_reqs(r) + needs
    return needs

  for mod in requested:
    mod = str(mod)
    try:
      attempting = []
      chain = _attempt_reqs(mod)
      try_modules += chain
    except:
      print("While testing "+mod)
      failed += attempting
      raise

  # load for real
  for mod in try_modules:
    try:
      m = usable_modules[mod]
      if hasattr(m,"config_defaults"):
        merge_config = m.config_defaults
        remap(merge_config, enter=_dover_enter)
    except:
        raise
        print("While trying "+mod)

  # remerge config file if we have one
  if (config_file):
    merge_config = config_file
    config = remap(config, _dmerge)

  # set the modules info...
  config['papercup']['loaded_modules'] = try_modules
  config['papercup']['modules_by_name'] = dict([(k, usable_modules[k]) for k in try_modules])

  config_data = config

  return config

def init_modules():
  from papercup import logs
  logger = logs.logger
  usable_modules = config_data['papercup']['modules_by_name']

  # No guarentees on the order init() gets called in
  for m in config_data['papercup']['loaded_modules']:
    if hasattr(usable_modules[m], 'init'):
      logger.info("Initialising driver: %s from %s"%(m, usable_modules[m].__name__))
      usable_modules[m].init()

  for m in config_data['papercup']['loaded_modules']:
    if hasattr(usable_modules[m], 'post_init'):
      logger.info("Post Initialising driver: %s from %s"%(m, usable_modules[m].__name__))
      usable_modules[m].post_init()

def prerun_modules():
  from papercup import logs
  logger = logs.logger
  usable_modules = config_data['papercup']['modules_by_name']

  # No guarentees on the order this gets called in either
  for m in config_data['papercup']['loaded_modules']:
    if hasattr(usable_modules[m], 'prerun'):
      logger.info("Pre-run function for driver: %s from %s"%(m, usable_modules[m].__name__))
      usable_modules[m].prerun()


def get(*args):
  try:
    return get_path(config_data, args)
  except:
    return None

if __name__ == "__main__":
  from pprint import pprint
  pprint(load())
  init_modules()
