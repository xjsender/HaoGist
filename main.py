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
        if not self.view or not self.view.file_name(): 
            return False

        # Rad file_full_name and filename
        self.fileFullName = self.view.file_name()
        self.settings = util.get_settings()

        # Get options settings of this view
        self.options = self.view.settings().get("options")
        if not self.options: return False

        self.fileName = self.options["fileName"]
        self.fileProperty = self.options["fileProperty"]
        self.gist = self.options["gist"]

        self.gist_id = self.gist["id"]
        self.html_url = self.gist["html_url"]
        self.gist_url = self.gist["url"]
        self.raw_url = self.fileProperty["raw_url"]

        return True

class ChooseGist(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(ChooseGist, self).__init__(*args, **kwargs)

    def run(self, read_cache=True, include_files=True, callback_command=None):
        self.include_files = include_files
        self.callback_command = callback_command
        self.settings = util.get_settings()
        if not self.settings["token"]:
            message = "Your own token is empty, please set it by " +\
                "HaoGist > Settings > User Settings in the context menu"
            return Printer.get("gist_error").write(message)

        # Read gist from cache if read_cache flag is true
        if read_cache:
            _gists = util.get_gists_cache(self.settings)
            if _gists: return self.choose_gist(_gists)

        api = GistApi(self.settings["token"])
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
        _gists = sorted(_gists, key=lambda k: k['updated_at'], reverse=True)
        util.add_gists_to_cache(_gists)

        # If no callback command, it will just refresh cache
        if self.callback_command:
            # Show the filenames in the quick panel
            self.items = []
            self.items_property = {}
            for _gist in _gists:
                if not self.include_files:
                    description = _gist["description"]
                    if not description:
                        description = "gist:%s" % _gist["id"]

                    self.items.append(description)
                    self.items_property[description] = {
                        "gist": _gist
                    }
                else:
                    # Get gist description
                    description = _gist["description"]
                    if not description:
                        description = "gist:%s" % _gist["id"]

                    files_number = len(_gist["files"])
                    if files_number > 1:
                        self.items.append(description)

                    # Add gist files to items
                    gist_items_property = []
                    for key, value in _gist["files"].items():
                        if files_number > 1:
                            key = "%s%s" % (" " * 4, key)
                        self.items.append(key)
                        self.items_property[key] = [{
                            "fileName": key.strip(),
                            "fileProperty": value,
                            "gist": _gist
                        }]
                        gist_items_property.extend(self.items_property[key])

                    # Populate items_property
                    self.items_property[description] = gist_items_property

            self.window.show_quick_panel(self.items, self.on_done, 
                sublime.MONOSPACE_FONT)

    def on_done(self, index):
        if index == -1: return

        for item in self.items_property[self.items[index]]:
            self.window.run_command(self.callback_command, {
                "options": item
            })

class OpenGist(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(OpenGist, self).__init__(*args, **kwargs)

    def run(self, options={}):
        if "fileName" not in options:
            return

        filename = options["fileName"]
        fileProperty = options["fileProperty"]
        _gist = options["gist"]

        settings = util.get_settings()
        api = GistApi(settings["token"])
        thread = threading.Thread(target=api.retrieve, args=(fileProperty["raw_url"], ))
        thread.start()
        ThreadProgress(api, thread, 'Opening Gist %s' % filename.strip(), 
            callback.open_gist, _callback_options=options
        )

class DeleteExistGist(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(DeleteExistGist, self).__init__(*args, **kwargs)

    def run(self, options={}):
        if "gist" not in options:
            return

        filename = options["fileName"]
        _gist = options["gist"]

        settings = util.get_settings()
        api = GistApi(settings["token"])
        thread = threading.Thread(target=api.delete, args=(_gist["url"], ))
        thread.start()
        ThreadProgress(api, thread, 'Deleting Gist %s' % filename, 
            callback.delete_gist, _callback_options={
                "fileName": filename
            }
        )

class OpenGistInBrowser(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(OpenGistInBrowser, self).__init__(*args, **kwargs)

    def run(self, options={}):
        if "gist" not in options:
            return
        
        _gist = options["gist"]
        util.open_with_browser(_gist["html_url"])

class UpdateContentToGist(sublime_plugin.TextCommand):
    def run(self, edit, options):
        if "gist" not in options:
            return

        # Get filename and gist from chosen options
        filename = options["fileName"]
        _gist = options["gist"]

        # Prepare data for update
        data = {
            "files": {
                filename: {
                    "content": self.selection
                }
            }
        }

        settings = util.get_settings()
        api = GistApi(settings["token"])
        thread = threading.Thread(target=api.patch, args=(_gist["url"], data, ))
        thread.start()
        ThreadProgress(api, thread, 'Updating Gist %s' % filename,
            callback.update_to_gist, _callback_options={
                "fileName": filename
            }
        )

    def is_enabled(self):
        self.selection = self.view.substr(self.view.sel()[0])

        if not self.selection:
            self.selection = self.view.substr(sublime.Region(0, self.view.size()))

        if not self.selection:
            return False

        return True

class AddFileToGist(sublime_plugin.TextCommand):
    def run(self, edit, options={}):
        self.gist = options["gist"]

        # Get gist description, if no description,
        # use "gist:<gist_id>" instead
        gist_description = self.gist["description"]
        if not gist_description:
            gist_description = "gist:%s" % self.gist["id"]

        message = "Input fileName to be added into %s" % gist_description
        sublime.active_window().show_input_panel(message, 
            "", self.on_input_name, None, None)

    def on_input_name(self, filename):
        if not filename:
            message = "FileName is required, do you want to try again?"
            if not sublime.ok_cancel_dialog(message, "Yes?"): return
            sublime.active_window().show_input_panel("Gist File Name: (Required)", 
                '', self.on_input_name, None, None)
            return

        data = {
            "files": {
                filename: {
                    "content": self.selection
                }
            }
        }

        settings = util.get_settings()
        api = GistApi(settings["token"])
        thread = threading.Thread(target=api.patch, args=(self.gist["url"], data, ))
        thread.start()

        description = self.gist["description"]
        if not description:
            description = "gist:%s" % self.gist["id"]
        ThreadProgress(api, thread, 'Adding %s to Gist %s' % (filename, description),
            callback.add_file_to_gist, _callback_options={
                "fileName": filename,
                "gistName": description
            }
        )

    def is_enabled(self):
        self.selection = self.view.substr(self.view.sel()[0])

        if not self.selection:
            self.selection = self.view.substr(sublime.Region(0, self.view.size()))

        if not self.selection:
            return False

        return True

class DeleteFileFromGist(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super(DeleteFileFromGist, self).__init__(*args, **kwargs)

    def run(self, options={}):
        if "gist" not in options:
            return

        self.options = options
        self.gist = options["gist"]
        self.fileNames = self.gist["files"]

        self.items = []
        for key, value in self.fileNames.items():
            self.items.append(key)

        self.window.show_quick_panel(self.items, self.on_done)

    def on_done(self, index):
        if index == -1: return

        self.fileName = self.items[index]
        data = {
            "files": {
                self.fileName: None
            }
        }

        settings = util.get_settings()
        api = GistApi(settings["token"])
        thread = threading.Thread(target=api.patch, args=(self.gist["url"], data, ))
        thread.start()

        description = self.gist["description"]
        if not description:
            description = "gist:%s" % self.gist["id"]
        ThreadProgress(api, thread, 'Delete %s from Gist %s' % (self.fileName, description),
            callback.delete_file_from_gist, _callback_options={
                "fileName": self.fileName,
                "gistName": description
            }
        )

class CreateGist(sublime_plugin.TextCommand):
    def run(self, edit, public=False):
        self.public = public
        self.settings = util.get_settings()

        sublime.active_window().show_input_panel("Gist File Name: (Required)", 
            '', self.on_input_name, None, None)

    def on_input_name(self, filename):
        if not filename:
            message = "FileName is required, do you want to try again?"
            if not sublime.ok_cancel_dialog(message, "Yes?"): return
            sublime.active_window().show_input_panel("Gist File Name: (Required)", 
                '', self.on_input_name, None, None)
            return

        self.fileName = filename

        sublime.active_window().show_input_panel('Gist Description: (optional):', 
            filename.split(".")[0], self.on_input_descrition, None, None)

    def on_input_descrition(self, desc):
        post_url = base_url % "gists"
        data = {
            "description": desc,
            "public": self.public,
            "files": {
                self.fileName : {
                    "content": self.selection
                }
            }
        }

        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.post, args=(post_url, data, ))
        thread.start()
        ThreadProgress(api, thread, 'Creating Gist %s' % self.fileName, 
            callback.create_gist, _callback_options={
                "fileName": self.fileName,
                "content": self.selection
            }
        )

    def is_enabled(self):
        self.selection = self.view.substr(self.view.sel()[0])

        if not self.selection:
            self.selection = self.view.substr(sublime.Region(0, self.view.size()))

        if not self.selection:
            return False

        return True

class RenameGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        self.old_filename = self.fileName
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
        thread = threading.Thread(target=api.patch, args=(self.gist_url, data, ))
        thread.start()
        ThreadProgress(api, thread, 'Renaming Gist from %s to %s' % (
                self.old_filename, 
                self.new_filename
            ),
            callback.rename_gist, _callback_options={
                "old_filename": self.old_filename,
                "new_filename": self.new_filename,
                "fileFullName": self.fileFullName,
                "options": self.options
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
                self.fileName: {
                    "content": body
                }
            }
        }

        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.patch, args=(self.gist_url, data, ))
        thread.start()
        ThreadProgress(api, thread, 'Update Gist Description',
            callback.update_description, _callback_options={
                "fileFullName": self.fileFullName,
                "desc": self.desc
            }
        )

class UpdateGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        if self.fileName in globals():
            thread = globals()[self.fileName]
            if thread and thread.is_alive():
                return

        body = open(self.view.file_name(), encoding="utf-8").read()
        data = {
            "files": {
                self.fileName: {
                    "content": body
                }
            }
        }

        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.patch, args=(self.gist_url, data, ))
        thread.start()
        ThreadProgress(api, thread, 'Updating Gist %s' % self.fileName, 
            callback.update_gist, _callback_options={
                "fileFullName": self.fileFullName
            }
        )

        globals()[self.fileName] = thread

class RefreshGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.retrieve, args=(self.raw_url, ))
        thread.start()
        ThreadProgress(api, thread, 'Refreshing Gist %s' % self.fileName, 
            callback.refresh_gist, _callback_options={
                "fileFullName": self.fileFullName
            }
        )

class DeleteGist(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        api = GistApi(self.settings["token"])
        thread = threading.Thread(target=api.delete, args=(self.gist_url, ))
        thread.start()
        ThreadProgress(api, thread, 'Deleting Gist %s' % self.fileName, 
            callback.delete_gist, _callback_options={
                "fileFullName": self.fileFullName
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
            Printer.get("gist_log").write("Gist cache is cleared")
        except:
            Printer.get("gist_error").write("Gist cache clear failed")

class OpenCurrentGistInBrowser(BaseGistView, sublime_plugin.TextCommand):
    def run(self, edit):
        util.open_with_browser(self.html_url)

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
