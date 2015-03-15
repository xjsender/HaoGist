import sublime, sublime_plugin
import os
import json
import requests
import threading

from .gist.api import GistApi
from .gist.api import GIST_BASE_URL as base_url
from .gist.lib import util
from .gist.lib import callback
from .gist.lib.progress import ThreadProgress
from .gist.lib.panel import Printer


class BaseGistView(object):
    """Base Class for Command with view"""
    def is_enabled(self):
        if not self.view or not self.view.file_name(): return False

        # Rad file_full_name and filename
        self.file_full_name = self.view.file_name()
        base, self.filename = os.path.split(self.file_full_name)

        # Read gists, if not exists, just disable related command
        self.settings = util.get_settings()
        cache_dir = os.path.join(self.settings["workspace"], ".cache", "gists.json")
        if not os.path.isfile(cache_dir): return False
        self._gists = json.loads(open(cache_dir).read())

        # Read related _gist
        self.filep, self._gist = None, None
        for g in self._gists:
            for key, value in g["files"].items():
                if key == self.filename:
                    self.filep, self._gist = g["files"][key], g

        # If not exists, just disable command
        if not self._gist: return False

        return True

class RefreshGistWorkspace(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(RefreshGistWorkspace, self).__init__(*args, **kwargs)

    def run(self):
        settings = util.get_settings()
        util.show_workspace_in_sidebar(settings)

class ReloadGistCache(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(ReloadGistCache, self).__init__(*args, **kwargs)

    def run(self):
        settings = util.get_settings()
        api = GistApi(settings["token"])
        gists = api.list(force=True)
        util.add_gists_to_cache(gists)

class ClearGistCache(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(ClearGistCache, self).__init__(*args, **kwargs)

    def run(self):
        settings = util.get_settings()
        cachedir = os.path.join(settings["workspace"], ".cache", "gists.json")
        try:
            os.remove(cachedir)
            Printer.get("log").write("Gist cache is cleared")
        except:
            Printer.get("error").write("Gist cache clear failed")

class OpenGist(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(OpenGist, self).__init__(*args, **kwargs)

    def run(self):
        self.settings = util.get_settings()
        api = GistApi(self.settings["token"])
        _gists = api.list()

        # Keep the gists to cache
        util.add_gists_to_cache(_gists)

        # Show the filenames in the quick panel
        self.files = []
        self.files_settings = {}
        for _gist in _gists:
            for key, value in _gist["files"].items():
                description = _gist["description"]
                self.files.append([key, description if description else ""])
                self.files_settings[key] = value

        self.files = sorted(self.files)
        self.window.show_quick_panel(self.files, self.on_done)

    def on_done(self, index):
        if index == -1: return

        file_settings = self.files_settings[self.files[index][0]]
        headers = {"Accept": "application/json; charset=UTF-8"}
        res = requests.get(file_settings["raw_url"], headers=headers)
        res.encoding = "utf-8"

        workspace = self.settings["workspace"]
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        
        # Show workspace in the sidebar
        util.show_workspace_in_sidebar(self.settings)

        file_name = os.path.join(workspace, file_settings["filename"])
        with open(file_name, "wb") as fp:
            fp.write(res.text.encode("utf-8"))

        # Then open the file
        sublime.active_window().open_file(file_name)

class CreateGist(sublime_plugin.TextCommand):
    def run(self, edit, public=False):
        self.public = public
        self.settings = util.get_settings()

        sublime.active_window().show_input_panel("Gist File Name: (Required)", 
            '', self.on_input_name, None, None)

    def on_input_name(self, filename):
        self.filename = filename

        sublime.active_window().show_input_panel('Gist Description: (optional):', 
            filename, self.on_input_descrition, None, None)

    def on_input_descrition(self, desc):
        post_url = base_url % "gists"
        data = {
            "description": desc,
            "public": self.public,
            "files": {
                self.filename : {
                    "content": self.content
                }
            }
        }

        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.post, args=(post_url, data, ))
        thread.start()
        ThreadProgress(api, thread, 'Refreshing Gist %s' % self.filename, 
            callback.create_gist, _callback_options = {
                "filename": self.filename,
                "content": self.content
            }
        )

    def is_enabled(self):
        self.content = self.view.substr(self.view.sel()[0])

        if not self.content:
            self.content = self.view.substr(sublime.Region(0, self.view.size()))

        if not self.content:
            return False

        return True

class UpdateGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        body = open(self.view.file_name(), encoding="utf-8").read()
        data = {
            "files": {
                self.filename: {
                    "content": body
                }
            }
        }

        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.patch, args=(self._gist["url"], data, ))
        thread.start()
        ThreadProgress(api, thread, 'Updating Gist %s' % self.filename, 
            callback.update_gist, _callback_options = {
                "file_full_name": self.file_full_name
            }
        )

class RefreshGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.retrieve, args=(self.filep["raw_url"], ))
        thread.start()
        ThreadProgress(api, thread, 'Refreshing Gist %s' % self.filename, 
            callback.refresh_gist, _callback_options = {
                "file_full_name": self.file_full_name
            }
        )

class OpenGistInBrowser(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        util.open_with_browser(self._gist["html_url"])

class DeleteGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.delete, args=(self._gist["url"], ))
        thread.start()
        ThreadProgress(api, thread, 'Deleting Gist %s' % self.filename, 
            callback.delete_gist, _callback_options = {
                "file_full_name": self.file_full_name
            }
        )
