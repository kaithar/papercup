import redis
import uuid
import pickle
import papercup.config as config
import collections

def init():
    import papercup
    papercup.Session = Session

def post_init():
    try:
        Session.prefix = config.get('papercup','redis','host')
    except:
        pass
    if Session.prefix == None:
        Session.prefix = config.get('papercup','name').replace(' ','_')

config_defaults = {
    'papercup': {
        'redis': {
            'host': None,
            'prefix': None
        }
    }
}

class Session(collections.MutableMapping):
    _key_expiry_time = (60*60)*24*7
    prefix = None
    def __init__(self, t_req, read_only=False):
        self.redis = redis.StrictRedis(host=config.get('papercup','redis','host'))
        self.csid = t_req.get_secure_cookie('_csid') or uuid.uuid4().hex
        if isinstance(self.csid, bytes):
            self.csid = self.csid.decode()
        if not read_only:
            t_req.set_secure_cookie('_csid', self.csid)
    def _key_format(self, key):
        return '%s.sessions.%s.%s'%(self.prefix, self.csid, key)
    def __getitem__(self, key):
        k = self._key_format(key)
        s = self.redis.get(k)
        if s:
            self.redis.expire(k, self._key_expiry_time)
            return pickle.loads(s)
        return s
    def __setitem__(self, key, value):
        if type(key) is not str:
            raise KeyError("Key must be a string")
        self.redis.setex(self._key_format(key),
                         self._key_expiry_time,
                         pickle.dumps(value))
    def __delitem__(self, key):
        self.redis.delete(self._key_format(key))
    def __len__(self):
        return len(self.redis.keys(self._key_format('*')))
    def keys(self):
        blank_key = self._key_format('')
        return [
            x.replace(blank_key, '')
            for x in self.redis.keys(self._key_format('*')) ]
    def __iter__(self):
        for k in list(self.keys()):
            yield k
    def update(self, d):
        for k,v in list(d.items()):
            self[k] = v
