import os
import json

try:
    import requests
except:
    from .. import requests

from .lib import util

GIST_BASE_URL = "https://api.github.com/%s"

class GistApi(object):
    """Gist API wrapper"""

    def __init__(self, token):
        self.res = None
        self._token = token
        self.settings = util.get_settings()
        self.proxies = self.settings["http_proxies"]
        self.headers = {
            "Accept": "application/json",
            "Authorization": "token %s" % self._token
        }

    def list(self, force=False):
        """Return a list of Gist objects."""

        try:
            # https://github.com/sanusart/gists-backup/blob/master/bkp.js#L25
            # If we don't add the per_page parameter, we can't get all gists
            # However, this is not mentioned in the gist API document
            self.res = requests.get(GIST_BASE_URL % "gists?per_page=1000", 
                headers=self.headers, proxies=self.proxies)
        except requests.exceptions.RequestException as e:
            if self.settings["debug_mode"]:
                print ("requests request exception: " + str(e))
            return
        return self.res

    def get(self, url):
        try:
            self.res = requests.get(url, headers=self.headers, proxies=self.proxies)
        except requests.exceptions.RequestException as e:
            if self.settings["debug_mode"]:
                print ("requests request exception: " + str(e))
            return
        return self.res

    def retrieve(self, raw_url):
        self.headers["Accept"] = "application/text"
        try:
            self.res = requests.get(raw_url, headers=self.headers, proxies=self.proxies)
            self.res.encoding = "utf-8"
        except requests.exceptions.RequestException as e:
            if self.settings["debug_mode"]:
                print ("requests request exception: " + str(e))
            return
        return self.res

    def post(self, post_url, params):
        """POST to the web form"""
        
        try:
            self.res = requests.post(post_url, data=json.dumps(params), 
                headers=self.headers, proxies=self.proxies)
        except requests.exceptions.RequestException as e:
            if self.settings["debug_mode"]:
                print ("requests request exception: " + str(e))
            return
        return self.res

    def patch(self, patch_url, params):
        """POST to the web form"""

        try:
            self.res = requests.patch(patch_url, data=json.dumps(params), 
                headers=self.headers, proxies=self.proxies)
        except requests.exceptions.RequestException as e:
            if self.settings["debug_mode"]:
                print ("requests request exception: " + str(e))
            return
        return self.res

    def delete(self, url):
        try:
            self.res = requests.delete(url, headers=self.headers, proxies=self.proxies)
        except requests.exceptions.RequestException as e:
            if self.settings["debug_mode"]:
                print ("requests request exception: " + str(e))
            return
        return self.res