import os
import json
import requests
from datetime import datetime

from .lib import util

GIST_BASE_URL = "https://api.github.com/%s"

class Gist(object):
    """Gist API wrapper"""

    def __init__(self, token):
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
        return requests.get(url, headers=self.headers)

    def retrieve(self, raw_url):
        return requests.get(raw_url, headers=self.headers)

    def post(self, post_url, params):
        """POST to the web form"""
        
        return requests.post(post_url, data=json.dumps(params), 
            headers=self.headers)

    def patch(self, patch_url, params):
        """POST to the web form"""

        return requests.patch(patch_url, data=json.dumps(params), 
            headers=self.headers)

    def delete(self, url):
        return requests.delete(url, headers=self.headers)

    def get_gist_by_id(self, gist_id):
        _gists = self.list()
        for _gist in self.list():
            if gist_id == _gist["id"]:
                return _gist

    def get_gist_by_filename(self, fn):
        _gists = self.list()
        for _gist in _gists:
            for key, value in _gist["files"].items():
                if key == fn:
                    return _gist["files"][key], _gist
