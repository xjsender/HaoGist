import sublime, sublime_plugin
import os
import json
import requests

from .api import Gist
from .lib import util
from .lib.panel import Printer
from .api import GIST_BASE_URL as base_url


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
        gist = Gist(settings["token"])
        gists = gist.list(force=True)
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
        gist = Gist(self.settings["token"])
        _gists = gist.list()

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

        gist = Gist(self.settings["token"])
        res = gist.post(post_url, data)

        if res.status_code < 399 and "id" in res.json():
            # Write file to workspace
            file_name = self.settings["workspace"] + "/" + self.filename
            with open(file_name, "wb") as fp:
                fp.write(self.content.encode("utf-8"))

            # Write cache to .cache/gists.json
            util.add_gists_to_cache([res.json()])

            # Success message
            Printer.get("log").write("%s is update successfully" % self.filename)

    def is_enabled(self):
        self.content = self.view.substr(self.view.sel()[0])

        if not self.content:
            self.content = self.view.substr(sublime.Region(0, self.view.size()))

        if not self.content:
            return False

        return True

class UpdateGist(sublime_plugin.TextCommand):
    def run(self, edit):
        self.settings = util.get_settings()

        body = open(self.view.file_name(), encoding="utf-8").read()
        path_url = ""
        payload = {
            "files": {
                self.filename: {
                    "content": body
                }
            }
        }

        gist = Gist(self.settings["token"])
        filep, _gist = gist.get_gist_by_filename(self.filename)

        res = gist.patch(_gist["url"], payload)
        if res.status_code < 399 and "id" in res.json():
            Printer.get("log").write("%s is update successfully" % self.filename)

    def is_enabled(self):
        if not self.view or not self.view.file_name(): return False

        base, self.filename = os.path.split(self.view.file_name())

        return True

class RefreshGist(sublime_plugin.TextCommand):
    def run(self, edit):
        self.settings = util.get_settings()
        gist = Gist(self.settings["token"])
        filep, _gist = gist.get_gist_by_filename(self.filename)

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
        gist = Gist(self.settings["token"])
        filep, _gist = gist.get_gist_by_filename(self.filename)
        util.open_with_browser(_gist["html_url"])

    def is_enabled(self):
        if not self.view or not self.view.file_name(): return False

        base, self.filename = os.path.split(self.view.file_name())

        return True

class DeleteGist(sublime_plugin.TextCommand):
    def run(self, edit):
        self.settings = util.get_settings()
        gist = Gist(self.settings["token"])
        filep, _gist = gist.get_gist_by_filename(self.filename)

        res = gist.delete(_gist["url"])
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
