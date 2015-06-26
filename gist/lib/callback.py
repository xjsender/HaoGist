import os
import json
import sublime

from . import util
from .panel import Printer

def refresh_gist(res, options):
    # Get file_full_name
    file_full_name = options["file_full_name"]
    base, filename = os.path.split(file_full_name)

    settings = util.get_settings()
    with open(file_full_name, "wb") as fp:
        fp.write(res.content)

    show_message("%s update succeed" % filename)

def open_gist(res, options):
    filename = options["filename"]
    settings = util.get_settings()

    workspace = settings["workspace"]
    if not os.path.exists(workspace):
        os.makedirs(workspace)
    
    # Show workspace in the sidebar
    util.show_workspace_in_sidebar(settings)

    file_full_name = os.path.join(workspace, filename)
    with open(file_full_name, "wb") as fp:
        fp.write(res.text.encode("utf-8"))

    # Then open the file
    sublime.active_window().open_file(file_full_name)

def delete_gist(res, options):
    # Get file_full_name
    if "file_full_name" in options:
        file_full_name = options["file_full_name"]
        base, filename = os.path.split(file_full_name)

        settings = util.get_settings()

        # Close corresponding view by file full name
        util.close_view_by_filename(file_full_name)

        # Remove file name
        os.remove(file_full_name)

        show_message("%s delete succeed" % filename)
    else:
        show_message("Gist is delete successfully")

    # Reload gist cache
    sublime.active_window().run_command('reload_gist_cache')

def create_gist(res, options):
    # Get filename and content
    filename = options["filename"]
    content = options["content"]

    # Get settings
    settings = util.get_settings()

    # Write file to workspace
    file_full_name = settings["workspace"] + "/" + filename
    with open(file_full_name, "wb") as fp:
        fp.write(content.encode("utf-8"))

    # Write cache to .cache/gists.json
    util.add_gists_to_cache([res.json()])

    # Open created gist
    sublime.active_window().open_file(file_full_name)

    # Success message
    show_message("%s is created successfully" % filename)

    # Reload gist cache
    sublime.active_window().run_command('reload_gist_cache')

def update_gist(res, options):
    # Get file_full_name
    file_full_name = options["file_full_name"]
    base, filename = os.path.split(file_full_name)
    show_message("%s is update successfully" % filename)

    # Reload gist cache
    sublime.active_window().run_command('reload_gist_cache')

def rename_gist(res, options):
    # Get file_full_name
    old_file_full_name = options["file_full_name"]
    old_filename = options["old_filename"]
    new_filename = options["new_filename"]

    # Get settings
    settings = util.get_settings()

    # Close corresponding view by file full name
    util.close_view_by_filename(old_file_full_name)

    # Rename 
    new_file_full_name = os.path.join(settings["workspace"], new_filename)
    os.rename(old_file_full_name, new_file_full_name)
    sublime.active_window().open_file(new_file_full_name)

    show_message("%s is renamed to %s successfully" % (
        old_filename, new_filename
    ))

    # Reload gist cache
    sublime.active_window().run_command('reload_gist_cache')

def update_description(res, options):
    file_full_name = options["file_full_name"]
    base, filename = os.path.split(file_full_name)
    desc = options["desc"]

    show_message("Description of %s is changed to %s successfully" % (
        filename, desc
    ))

    # Reload gist cache
    sublime.active_window().run_command('reload_gist_cache')

def add_gists_to_cache(res, options):
    util.add_gists_to_cache(res.json())

    if "show_message" in options and options["show_message"]:
        show_message("Gists cache reloading succeed")

def show_message(msg):
    settings = util.get_settings()
    Printer.get("log").write(msg)
    sublime.set_timeout_async(Printer.get("log").hide_panel, 
        settings["delay_seconds_for_hiding_panel"] * 1000)
