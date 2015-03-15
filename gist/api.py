import os
import json
import requests

from .lib import util

GIST_BASE_URL = "https://api.github.com/%s"

class GistApi(object):
    """Gist API wrapper"""

    def __init__(self, token):
        self.res = None
        self._token = token
        self.headers = {
            "Accept": "application/json",
            "Authorization": "token %s" % self._token
        }

    def list(self, force=False):
        """Return a list of Gist objects."""

        # Read cache
        settings = util.get_settings()
        cache_dir = os.path.join(settings["workspace"], ".cache", "gists.json")
        if not force and os.path.isfile(cache_dir):
            return json.loads(open(cache_dir).read())

        # If no cache, just request server
        url = GIST_BASE_URL % "gists"
        _gists = requests.get(url, headers=self.headers).json()
        return _gists

    def get(self, url):
        self.res = requests.get(url, headers=self.headers)
        return self.res

    def retrieve(self, raw_url):
        self.res = requests.get(raw_url, headers=self.headers)

    def post(self, post_url, params):
        """POST to the web form"""
        
        print (params)
        self.res = requests.post(post_url, data=json.dumps(params), 
            headers=self.headers)
        return self.res

    def patch(self, patch_url, params):
        """POST to the web form"""

        self.res = requests.patch(patch_url, data=json.dumps(params), 
            headers=self.headers)
        return self.res

    def delete(self, url):
        self.res = requests.delete(url, headers=self.headers)
        return self.res
