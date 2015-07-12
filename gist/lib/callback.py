import os
import json
import sublime

from . import util
from .panel import Printer

def refresh_gist(res, options):
    # Get file_full_name
    file_full_name = options["fileFullName"]
    base, filename = os.path.split(file_full_name)

    settings = util.get_settings()
    with open(file_full_name, "wb") as fp:
        fp.write(res.content)

    show_message("%s update succeed" % filename)

def open_gist(res, options):
    filename = options["fileName"]
    settings = util.get_settings()

    workspace = settings["workspace"]
    if not os.path.exists(workspace):
        os.makedirs(workspace)

    file_full_name = os.path.join(workspace, filename)
    with open(file_full_name, "wb") as fp:
        fp.write(res.text.encode("utf-8"))

    # Then open the file
    view = sublime.active_window().open_file(file_full_name)
    view.settings().set("options", options)

def delete_gist(res, options):
    # When delete current open gist, we need to delete the gist
    # and close the open view
    if "fileFullName" in options:
        file_full_name = options["fileFullName"]
        base, filename = os.path.split(file_full_name)

        settings = util.get_settings()

        # Close corresponding view by file full name
        util.close_view_by_filename(file_full_name)

        # Remove file name
        os.remove(file_full_name)

        show_message("%s delete succeed" % filename)
    else:
        filename = options["fileName"]
        show_message("Gist %s is delete successfully" % filename)

    # Reload gist cache
    sublime.active_window().run_command('choose_gist', {
        "read_cache": False
    })

def create_gist(res, options):
    # Get filename and content
    filename = options["fileName"]
    content = options["content"]

    # Get settings
    settings = util.get_settings()

    # Write file to workspace
    file_full_name = settings["workspace"] + "/" + filename
    with open(file_full_name, "wb") as fp:
        fp.write(content.encode("utf-8"))

    # Open created gist
    gist = res.json()
    view = sublime.active_window().open_file(file_full_name)
    view.settings().set("options", {
        "gist": gist,
        "fileName": filename,
        "fileProperty": gist["files"][filename]
    })

    # Success message
    show_message("%s is created successfully" % filename)

    # Reload gist cache
    sublime.active_window().run_command('choose_gist', {
        "read_cache": False
    })

def update_gist(res, options):
    # Get file_full_name
    file_full_name = options["fileFullName"]
    base, filename = os.path.split(file_full_name)
    show_message("%s is update successfully" % filename)

    # Reload gist cache
    sublime.active_window().run_command('choose_gist', {
        "read_cache": False
    })

def update_to_gist(res, options):
    # Show message to output panel
    show_message("%s is update successfully" % options["fileName"])

    # Reload gist cache
    sublime.active_window().run_command('choose_gist', {
        "read_cache": False
    })

def add_file_to_gist(res, options):
    # Show message to output panel
    show_message("%s is added to %s successfully" % (
        options["fileName"], options["gistName"]
    ))

    # Reload gist cache
    sublime.active_window().run_command('choose_gist', {
        "read_cache": False
    })

def delete_file_from_gist(res, options):
    # Show message to output panel
    show_message("%s is deleted from %s successfully" % (
        options["fileName"], options["gistName"]
    ))

    # Reload gist cache
    sublime.active_window().run_command('choose_gist', {
        "read_cache": False
    })

def rename_gist(res, options):
    # Get file_full_name
    old_file_full_name = options["fileFullName"]
    old_filename = options["old_filename"]
    new_filename = options["new_filename"]

    # Get settings
    settings = util.get_settings()

    # Close corresponding view by file full name
    util.close_view_by_filename(old_file_full_name)

    # Rename 
    new_file_full_name = os.path.join(settings["workspace"], new_filename)
    os.rename(old_file_full_name, new_file_full_name)
    view = sublime.active_window().open_file(new_file_full_name)
    view.settings().set("options", options["options"])

    show_message("%s is renamed to %s successfully" % (
        old_filename, new_filename
    ))

    # Reload gist cache
    sublime.active_window().run_command('choose_gist', {
        "read_cache": False
    })

def update_description(res, options):
    file_full_name = options["fileFullName"]
    base, filename = os.path.split(file_full_name)
    desc = options["desc"]

    show_message("Description of %s is changed to %s successfully" % (
        filename, desc
    ))

    # Reload gist cache
    sublime.active_window().run_command('choose_gist', {
        "read_cache": False
    })

def add_gists_to_cache(res, options):
    util.add_gists_to_cache(res.json())

    if "show_message" in options and options["show_message"]:
        show_message("Gists cache reloading succeed")

def show_message(msg):
    settings = util.get_settings()
    Printer.get("gist_log").write(msg)
    sublime.set_timeout_async(Printer.get("gist_log").hide_panel, 
        settings["delay_seconds_for_hiding_panel"] * 1000)