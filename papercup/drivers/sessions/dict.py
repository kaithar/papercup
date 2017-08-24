import uuid
import collections

def init():
    import papercup
    papercup.Session = Session

# WARNING! This driver doesn't persist sessions across restarts!

class Session(collections.MutableMapping):
    sessions = {}
    this_session = None
    def __init__(self, t_req, read_only=False):
        self.csid = t_req.get_secure_cookie('_csid') or uuid.uuid4().hex
        if isinstance(self.csid, bytes):
            self.csid = self.csid.decode()
        if not read_only:
            t_req.set_secure_cookie('_csid', self.csid)
        self.this_session = self.sessions.setdefault(self.csid, {})
    def __getitem__(self, key):
        s = self.this_session.get(key,None)
        return s
    def __setitem__(self, key, value):
        if type(key) is not str:
            raise KeyError("Key must be a string")
        self.this_session[key] = value
    def __delitem__(self, key):
        del self.this_session[key]
    def __len__(self):
        return len(self.this_session)
    def keys(self):
        return self.this_session.keys()
    def __iter__(self):
        for k in self:
            yield k
    def update(self, d):
        for k,v in list(d.items()):
            self[k] = v
