import os
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

    Printer.get("log").write("%s update succeed" % filename)
    sublime.set_timeout_async(Printer.get("log").hide_panel, 
        settings["delay_seconds_for_hiding_panel"] * 1000)

def open_gist(res, options):
    filename = options["filename"]
    settings = util.get_settings()

    workspace = settings["workspace"]
    if not os.path.exists(workspace):
        os.makedirs(workspace)
    
    # Show workspace in the sidebar
    util.show_workspace_in_sidebar(settings)

    res.encoding = "utf-8"
    file_full_name = os.path.join(workspace, filename)
    with open(file_full_name, "wb") as fp:
        fp.write(res.text.encode("utf-8"))

    # Then open the file
    sublime.active_window().open_file(file_full_name)

def delete_gist(res, options):
    # Get file_full_name
    file_full_name = options["file_full_name"]
    base, filename = os.path.split(file_full_name)

    settings = util.get_settings()

    view = util.get_view_by_file_name(file_full_name)
    if view:
        sublime.active_window().focus_view(view)
        sublime.active_window().run_command("close")
    os.remove(file_full_name)
    Printer.get("log").write("%s delete succeed" % filename)
    sublime.set_timeout_async(Printer.get("log").hide_panel, 
        settings["delay_seconds_for_hiding_panel"] * 1000)

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
    Printer.get("log").write("%s is created successfully" % filename)
    sublime.set_timeout_async(Printer.get("log").hide_panel, 
        settings["delay_seconds_for_hiding_panel"] * 1000)

def update_gist(res, options):
    # Get file_full_name
    file_full_name = options["file_full_name"]
    base, filename = os.path.split(file_full_name)

    settings = util.get_settings()

    Printer.get("log").write("%s is update successfully" % filename)
    sublime.set_timeout_async(Printer.get("log").hide_panel, 
        settings["delay_seconds_for_hiding_panel"] * 1000)