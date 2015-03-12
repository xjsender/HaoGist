import sublime, sublime_plugin
import os

from . import requests
from .gistapi import Gist, Gists
from .lib import util


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



        


