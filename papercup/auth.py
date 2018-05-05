requires = []

from papercup import handlers
from functools import wraps

users_class = None

def get_context(handler):
  handler.user = None

def require_user( wrapfunc ):
  @wraps(wrapfunc)
  def inner( self, *args, **kwargs ):
    get_context(self)
    if not self.user:
      self.redirect('/')
      return
    return wrapfunc( self, *args, **kwargs )
  return inner
