import sublime, sublime_plugin
import os
import json

from . import requests
from .gistapi import Gist, Gists
from .lib import util
from .lib.panel import Printer


class OpenGist(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(OpenGist, self).__init__(*args, **kwargs)

    def run(self):
        self.settings = util.get_settings()
        gi = Gists(self.settings["username"], self.settings["token"])

        self.files = []
        self.files_settings = {}
        caches = []
        for gist in gi.gists:
            caches.append(gist._json)
            for key, value in gist.filenames.items():
                self.files.append(key)
                self.files_settings[key] = value

        # Keep the caches
        util.add_caches(caches)

        self.files = sorted(self.files)
        self.window.show_quick_panel(self.files, self.on_done)

    def on_done(self, index):
        if index == -1: return

        file_settings = self.files_settings[self.files[index]]
        headers = {"Accept": "application/json; charset=UTF-8"}
        res = requests.get(file_settings["raw_url"], headers=headers)
        res.encoding = "UTF-8"

        workspace = self.settings["workspace"]
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        
        # Show workspace in the sidebar
        util.show_workspace_in_sidebar(self.settings)

        file_name = os.path.join(workspace, file_settings["filename"])
        with open(file_name, "wb") as fp:
            fp.write(res.text.encode("UTF-8"))

        # In windows, new file is not shown in the sidebar, 
        # we need to refresh the sublime workspace to show it
        sublime.active_window().run_command("refresh_folder_list")

        # Then open the file
        sublime.active_window().open_file(file_name)

class UpdateGist(sublime_plugin.TextCommand):
    def run(self, edit):
        self.settings = util.get_settings()
        gi = Gists(self.settings["username"], self.settings["token"])
        filep, gist = gi.get_gist_by_filename(self.filename)

        body = open(self.view.file_name(), encoding="utf-8").read()
        payload = {
            "files": {
                self.filename: {
                    "content": body
                }
            }
        }

        res = gist.post(payload)

        if res.status_code < 399 and "id" in res.json():
            Printer.get("log").write("%s is update successfully" % self.filename)

    def is_enabled(self):
        if not self.view or not self.view.file_name(): return False

        base, self.filename = os.path.split(self.view.file_name())

        return True

class RefreshGist(sublime_plugin.TextCommand):
    def run(self, edit):
        self.settings = util.get_settings()
        gi = Gists(self.settings["username"], self.settings["token"])
        filep, gist = gi.get_gist_by_filename(self.filename)

        res = gist.retrieve(filep["raw_url"])
        if res.status_code < 399:
            with open(self.view.file_name(), "wb") as fp:
                fp.write(res.content)
            Printer.get("log").write("%s update succeed" % self.filename)
        else:
            Printer.get("error").write("%s update failed" %  (self.filename, json.dumps(res.json)))

    def is_enabled(self):
        if not self.view or not self.view.file_name(): return False

        base, self.filename = os.path.split(self.view.file_name())

        return True

class OpenGistInBrowser(sublime_plugin.TextCommand):
    def run(self, edit):
        self.settings = util.get_settings()
        gi = Gists(self.settings["username"], self.settings["token"])
        filep, gist = gi.get_gist_by_filename(self.filename)

        util.open_with_browser(gist.open_url)

    def is_enabled(self):
        if not self.view or not self.view.file_name(): return False

        base, self.filename = os.path.split(self.view.file_name())

        return True

class DeleteGist(sublime_plugin.TextCommand):
    def run(self, edit):
        self.settings = util.get_settings()
        gi = Gists(self.settings["username"], self.settings["token"])
        filep, gist = gi.get_gist_by_filename(self.filename)

        res = gist.delete()
        if res.status_code < 399:
            view = util.get_view_by_file_name(self.file_name)
            if view:
                sublime.active_window().focus_view(view)
                sublime.active_window().run_command("close")
            os.remove(self.file_name)
            Printer.get("log").write("%s delete succeed" % self.filename)
        else:
            print (res.json())
            Printer.get("error").write("%s delete failed, due to " % (self.filename, str(res.content)))

    def is_enabled(self):
        if not self.view or not self.view.file_name(): return False
        self.file_name = self.view.file_name()
        base, self.filename = os.path.split(self.file_name)

        return True
