import sublime, sublime_plugin
from .gist.lib import util

class HaoGistEvent(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        settings = util.get_settings();
        if settings["workspace"] not in view.file_name(): return
        if settings.get('auto_update_on_save'):
            view.run_command('update_gist')