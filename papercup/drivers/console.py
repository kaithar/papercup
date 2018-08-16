requires = []

import os
from papercup import handlers
from papercup import auth
from papercup.templating import use_template

staticpath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'static')
title = 'Console'

styles = []
scripts = []

root_templates = "/static/papercup/root_templates.js"

@handlers.handle_url("/console(?:/.*)?")
class console_handler(handlers.Request_handler):
  search_dirs = [staticpath]
  @auth.require_user
  @use_template('console.mustache')
  def get(self):
    return {
      'title': title,
      'styles': styles,
      'scripts': scripts,
      'template_js': root_templates
    }
