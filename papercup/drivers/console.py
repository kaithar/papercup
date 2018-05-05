requires = ['papercup.drivers.sqlalchemy']

import os
from papercup import handlers
from spinalbrace import auth
import papercup.drivers.sqlalchemy as db
from papercup.templating import use_template

staticpath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'static')
title = 'Console'

styles = []
scripts = []

@handlers.handle_url("/console(?:/.*)?")
class console_handler(handlers.Request_handler):
  search_dirs = [staticpath]
  @db.bind_session
  @auth.require_user
  @use_template('console.mustache')
  def get(self):
    return {
      'title': title,
      'styles': styles,
      'scripts': scripts
    }
