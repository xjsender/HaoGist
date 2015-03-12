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

        self.headers = {"Accept": "application/json"}
        if self._token:
            self.headers["Authorization"] = "token %s" % self._token

        # Map given repo id to gist id if none exists
        
        if self._json:
            self.id = self._json['id']

        self.open_url = "https://gist.github.com/%s" % self.id
        self.url = url = GIST_BASE_URL % "gists/%s" % self.id
        self.post_url = GIST_BASE_URL % 'gists'
        self.patch_url = GIST_BASE_URL % 'gists/%s' % self.id
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
                setattr(self, key, value if value else "")

            else:
                setattr(self, key, value)
                
        return _meta

    def get(self):
        return requests.get(self.url, headers=self.headers)

    def retrieve(self, raw_url):
        return requests.get(raw_url, headers=self.headers)

    def post(self, params):
        """POST to the web form (internal method)."""
        
        return requests.post(self.post_url, data=json.dumps(params), 
            headers=self.headers)

    def patch(self, params):
        """POST to the web form (internal method)."""

        return requests.patch(self.patch_url, data=json.dumps(params), 
            headers=self.headers)

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

    def delete(self):
        return requests.delete(self.url, headers=self.headers)

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
        if os.path.isfile(cache_dir):
            gists = json.loads(open(cache_dir).read())
            return [Gist(json=g, token=token) for g in gists]

        _url = GIST_BASE_URL % "users/%s/gists" % name
        headers = {"Authorization" : "token %s" % token}
        gists = requests.get(_url, headers=headers).json()

        # Return a list of Gist objects
        return [Gist(json=g, token=token) for g in gists]

    def get_gist_by_id(self, gist_id):
        for g in self.gists:
            if gist_id == g.id:
                return g

    def get_gist_by_filename(self, fn):
        for g in self.gists:
            for filename in g.filenames:
                if filename == fn:
                    return g.filenames[filename], g

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
