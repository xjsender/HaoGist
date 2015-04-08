import sublime, sublime_plugin
import os
import json
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
                    break

        # If not exists, just disable command
        if not self._gist: return False

        return True

class HaoGistEvent(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        settings = util.get_settings();
        if settings["workspace"] not in view.file_name(): return
        if settings.get('auto_update_on_save'):
            view.run_command('update_gist')

class RefreshGistWorkspace(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(RefreshGistWorkspace, self).__init__(*args, **kwargs)

    def run(self):
        settings = util.get_settings()
        util.show_workspace_in_sidebar(settings)

    def is_visible(self):
        self.settings = util.get_settings()

        return not self.settings["hide_workspace_in_sidebar"]

class ReloadGistCache(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(ReloadGistCache, self).__init__(*args, **kwargs)

    def run(self):
        settings = util.get_settings()
        api = GistApi(settings["token"])
        thread = threading.Thread(target=api.list, args=(True, ))
        thread.start()
        ThreadProgress(api, thread, 'Reloading Gist Cache', 
            callback.add_gists_to_cache, _callback_options={
                "show_message": True
            }
        )

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
        
        _gists = util.get_gists_cache(self.settings)
        if _gists: return self.choose_gist(_gists)

        # If there is no cache
        thread = threading.Thread(target=api.list)
        thread.start()
        ThreadProgress(api, thread, 'List All Gist', 
            self.choose_gist, _callback_options={}
        )

    def choose_gist(self, res, options={}):
        # Keep the gists to cache
        if not isinstance(res, list): 
            _gists = res.json()
        else:
            _gists = res
        util.add_gists_to_cache(_gists)

        # Show the filenames in the quick panel
        self.files = []
        self.files_settings = {}
        for _gist in _gists:
            for key, value in _gist["files"].items():
                description = _gist["description"]
                self.files.append(["%s" % (key), description if description else ""])
                self.files_settings["%s" % (key)] = value

        self.files = sorted(self.files)
        self.window.show_quick_panel(self.files, self.on_done)

    def on_done(self, index):
        if index == -1: return
        filep = self.files_settings[self.files[index][0]]

        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.retrieve, args=(filep["raw_url"], ))
        thread.start()
        ThreadProgress(api, thread, 'Opening Gist %s' % filep["filename"], 
            callback.open_gist, _callback_options={
                "filename": filep["filename"]
            }
        )

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
        ThreadProgress(api, thread, 'Creating Gist %s' % self.filename, 
            callback.create_gist, _callback_options={
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

class RenameGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        self.old_filename = self.filename
        sublime.active_window().show_input_panel('Input New Name:', 
            self.old_filename, self.on_input_name, None, None)

    def on_input_name(self, input):
        if not input: 
            sublime.error_message("File name can't be empty")
            return

        self.new_filename = input

        body = open(self.view.file_name(), encoding="utf-8").read()
        data = {
            "files": {
                self.old_filename: {
                    "filename": self.new_filename,
                    "content": body
                }
            }
        }

        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.patch, args=(self._gist["url"], data, ))
        thread.start()
        ThreadProgress(api, thread, 'Renaming Gist from %s to %s' % (
                self.old_filename, 
                self.new_filename
            ),
            callback.rename_gist, _callback_options={
                "old_filename": self.old_filename,
                "new_filename": self.new_filename,
                "file_full_name": self.file_full_name
            }
        )

class UpdateGistDescription(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.active_window().show_input_panel('Input New Description:', 
            "", self.on_input_name, None, None)

    def on_input_name(self, input):
        if not input: 
            sublime.error_message("File Description can't be empty")
            return

        self.desc = input

        body = open(self.view.file_name(), encoding="utf-8").read()
        data = {
            "description": self.desc,
            "files": {
                self.filename: {
                    "content": body
                }
            }
        }

        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.patch, args=(self._gist["url"], data, ))
        thread.start()
        ThreadProgress(api, thread, 'Update Gist Description',
            callback.update_description, _callback_options={
                "file_full_name": self.file_full_name,
                "desc": self.desc
            }
        )

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
            callback.update_gist, _callback_options={
                "file_full_name": self.file_full_name
            }
        )

class RefreshGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.retrieve, args=(self.filep["raw_url"], ))
        thread.start()
        ThreadProgress(api, thread, 'Refreshing Gist %s' % self.filename, 
            callback.refresh_gist, _callback_options={
                "file_full_name": self.file_full_name
            }
        )

class DeleteGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.delete, args=(self._gist["url"], ))
        thread.start()
        ThreadProgress(api, thread, 'Deleting Gist %s' % self.filename, 
            callback.delete_gist, _callback_options={
                "file_full_name": self.file_full_name
            }
        )

class OpenGistInBrowser(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        util.open_with_browser(self._gist["html_url"])

class ReleaseNote(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(ReleaseNote, self).__init__(*args, **kwargs)

    def run(self):
        util.open_with_browser("https://github.com/xjsender/HaoGist/blob/master/HISTORY.rst")

class AboutHaoGist(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(AboutHaoGist, self).__init__(*args, **kwargs)

    def run(self):
        util.open_with_browser("https://github.com/xjsender/HaoGist")

