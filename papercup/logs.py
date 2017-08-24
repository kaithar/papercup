
import logging

logger = None

def init():
  global logger
  logger = logging.getLogger('papercup.main')
  logger.setLevel(logging.DEBUG)
  #from papercup.drivers.logging.stdout import handler as stdout_handler
  #sh = stdout_handler(config.papercup.get("project", "Unknown_Application"))
  #logging.getLogger('').addHandler(sh)
  logging.getLogger('').setLevel(logging.INFO)
