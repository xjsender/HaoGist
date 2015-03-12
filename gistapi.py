import os
import json
from . import requests
from datetime import datetime

from .lib import util

GIST_BASE_URL = "https://api.github.com/%s"

class Gist(object):
    def __init__(self, id="", json="", username="", token=""):
        self.id = id
        self._json = json
        self._username = username
        self._token = token

        # Map given repo id to gist id if none exists
        
        if self._json:
            self.id = self._json['id']

        self.url = url = GIST_BASE_URL % "gists/%s" % self.id
        self.post_url = GIST_BASE_URL % 'gists/%s' % self.id
        self.comments  = []

    def __getattribute__(self, name):
        """Get attributes, but only if needed."""

        # Only make external API calls if needed
        if name in ('owner', 'description', 'created_at', 'public',
                    'files', 'filenames', 'id', 'comments'):
            if not hasattr(self, '_meta'):
                self._meta = self._get_meta()

        return object.__getattribute__(self, name)

    def _get_meta(self):
        """Fetch Gist metadata."""

        # Use json data provided if available
        if self._json:
            _meta = self._json
            setattr(self, 'id', _meta['id'])
        else:
            # Fetch Gist metadata
            _meta_url = GIST_BASE_URL % "gists/%s" % self.id
            headers = {"Authorization" : "token %s" % self._token}
            _meta = requests.get(_meta_url, headers=headers).json()

        for key, value in _meta.items():
            if key == 'files':
                # Remap file key from API.
                setattr(self, 'filenames', value)
                
                # Store the {current_name: original_name} mapping.
                setattr(self, '_renames', dict((fn, fn) for fn in value))

            elif key == 'public':
                # Attach booleans
                setattr(self, key, value)

            elif key == 'created_at':
                # Attach datetime
                setattr(self, 'created_at', datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ'))
                
            elif key == 'comments':
                pass
                # _comments_url = _meta["comments_url"]
                # headers = {"Authorization" : "token %s" % self._token}
                # result = requests.get(_comments_url, headers=headers).json()

                # _comments = []
                # for comment in result:
                #     c = GistComment().from_api(comment)
                #     _comments.append(c)
                #     setattr(self, 'comments', _comments)

            elif isinstance(value, str):
                setattr(self, key, value.encode('utf-8') if value else "")

            else:
                setattr(self, key, value)
                
        return _meta

    def _post(self, params, headers={"Accept": "application/json"}):
        """POST to the web form (internal method)."""
        r = requests.post(self.post_url, params, headers=headers)

        return r.status_code, r.json()

    def reset(self):
        """Clear the local cache."""
        if hasattr(self, '_files'):
            del self._files
        if hasattr(self, '_meta'):
            del self._meta

    def auth(self, username, token):
        """Set credentials."""
        self._username = username
        self._token = token

    def delete(self, headers={"Accept": "application/json"}):
        r = requests.delete(self.url, headers)

        return r.status_code, r.json()

    def rename(self, from_name, to_name):
        """Rename a file."""
        if from_name not in self.files:
            raise KeyError('File %r does not exist' % from_name)
        if to_name in self.files:
            raise KeyError('File %r already exist' % to_name)
        self.files[to_name] = self.files.pop(from_name)
        try:
            self._renames[to_name] = self._renames.pop(from_name)
        except KeyError:
            # New file
            pass

    def save(self):
        """Upload the changes to Github."""
        params = {
            '_method': 'put',
            'login': self._username or USERNAME,
            'token': self._token or TOKEN,
        }
        names_map = self._renames
        original_names = names_map.values()
        index = len(original_names)
        for fn, content in self.files.items():
            ext = os.path.splitext(fn)[1] or '.txt'
            try:
                orig = names_map.pop(fn)
            except KeyError:
                # Find a unique filename
                while True:
                    orig = 'gistfile%s' % index
                    index += 1
                    if orig not in original_names:
                        break
            params.update({
                'file_name[%s]' % orig: fn,
                'file_ext[%s]' % orig: ext,
                'file_contents[%s]' % orig: content,
            })
        code, msg = self._post(params=params)
        if code == 200:  # OK
            # If successful, clear the cache
            self.reset()
        return code, msg

class Gists(object):
    """Gist API wrapper"""

    def __init__(self, name, token):
        # Token-based Authentication is unnecessary, gist api still in alpha
        self.gists = self.fetch_by_user(name, token)

    def fetch_by_user(self, name, token):
        """Return a list of public Gist objects owned by
        the given GitHub username."""

        # Read cache
        settings = util.get_settings()
        cache_dir = os.path.join(settings["workspace"], ".cache", "gists.json")
        gists = None
        if os.path.isfile(cache_dir):
            gists = json.loads(open(cache_dir).read())
            return [Gist(json=g, token=token) for g in gists]

        _url = GIST_BASE_URL % "users/%s/gists" % name
        headers = {"Authorization" : "token %s" % token}
        gists = requests.get(_url, headers=headers).json()

        # Return a list of Gist objects
        return [Gist(json=g, token=token) for g in gists]

    def get_gist_by_id(self, gist_id):
        if isinstance(gist_id, str):
            gist_id = gist_id.encode("utf-8")

        for g in self.gists:
            if gist_id == g.id:
                return g

class GistComment(object):
    """Gist comments."""
    
    def __init__(self): 
        self.body = None
        self.created_at = None
        self.url = None
        self.id = None
        self.updated_at = None
        self.user = None

    def __repr__(self):
        return '<gist-comment %s>' % self.id

    @staticmethod
    def from_api(jsondict):
        """Returns new instance of GistComment containing given api dict."""
        comment = GistComment()
        
        comment.body = jsondict.get('body', None)
        comment.created_at = datetime.strptime(jsondict.get('created_at'), '%Y-%m-%dT%H:%M:%SZ')
        comment.url = jsondict.get('url', None)
        comment.id = jsondict.get('id', None)
        comment.updated_at = datetime.strptime(jsondict.get('updated_at'), '%Y-%m-%dT%H:%M:%SZ')
        comment.user = jsondict.get('user', None)
        
        return comment
