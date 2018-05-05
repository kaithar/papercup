import logging

logger = None

def init():
  global logger
  from papercup import main, config
  logger = logging.getLogger('papercup.main')
  logger.setLevel(logging.DEBUG)
  from papercup.drivers.logging.stdout import handler as stdout_handler
  sh = stdout_handler(config.get("papercup", "name") or "Unknown_Application")
  logging.getLogger('').addHandler(sh)
  logging.getLogger('').setLevel(logging.INFO)
