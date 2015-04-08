import sublime
import os
import json
import webbrowser

def get_gists_cache(settings):
    cache_dir = os.path.join(settings["workspace"], ".cache", "gists.json")
    if not os.path.isfile(cache_dir): return
    return json.loads(open(cache_dir).read())

def add_gists_to_cache(gists):
    """Add gist the caches"""
    
    settings = get_settings()
    outputdir = os.path.join(settings["workspace"], ".cache")
    cachedir = os.path.join(outputdir, "gists.json")

    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
        
    with open(outputdir + "/gists.json", "w") as fp:
        fp.write(json.dumps(gists, indent=4))

def get_settings():
    """ Load settings from sublime-settings"""
    
    settings = {}
    s = sublime.load_settings("HaoGist.sublime-settings")
    settings["token"] = s.get("token")
    settings["workspace"] = s.get("workspace")
    settings["file_exclude_patterns"] = s.get("file_exclude_patterns", {})
    settings["debug_mode"] = s.get("debug_mode", False)
    settings["auto_update_on_save"] = s.get("auto_update_on_save", True)
    settings["hide_workspace_in_sidebar"] = s.get("hide_workspace_in_sidebar", False)
    settings["folder_exclude_patterns"] = s.get("folder_exclude_patterns", [])
    settings["default_chrome_path"] = s.get("default_chrome_path", "")
    settings["delay_seconds_for_hiding_panel"] = s.get("delay_seconds_for_hiding_panel", 1)

    return settings

def open_with_browser(show_url, use_default_chrome=True):
    """ Utility for open file in browser

    Arguments:

    * use_default_browser -- optional; if true, use chrome configed in settings to open it
    """

    settings = get_settings()
    browser_path = settings["default_chrome_path"]
    if not use_default_chrome or not os.path.exists(browser_path):
        webbrowser.open_new_tab(show_url)
    else:
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(browser_path))
        webbrowser.get('chrome').open_new_tab(show_url)

def close_view_by_filename(file_name):
    view = get_view_by_file_name(file_name)
    if view:
        sublime.active_window().focus_view(view)
        sublime.active_window().run_command("close")

def get_view_by_name(view_name):
    """Get view by view name

    Arguments:

    * view_name -- name of view in sublime

    Returns:

    * view -- sublime open tab
    """
    view = None
    for v in sublime.active_window().views():
        if not v.name(): continue
        if v.name() == view_name:
            view = v

    return view

def get_view_by_file_name(file_name):
    """
    Get the view in the active window by the view_name

    Arguments:

    * view_id: view name

    Returns:

    * return: view
    """

    view = None
    for v in sublime.active_window().views():
        if not v.file_name(): continue
        if file_name in v.file_name():
            view = v

    return view

def get_view_by_id(view_id):
    """
    Get the view in the active window by the view_id

    * view_id: id of view
    * return: view
    """

    view = None
    for v in sublime.active_window().views():
        if not v.id(): continue
        if v.id() == view_id:
            view = v

    return view
    
def show_workspace_in_sidebar(settings):
    """Add new project folder to workspace
       Just Sublime Text 3 can support this method
    """

    # Don't show the workspace in the sidebar
    if settings["hide_workspace_in_sidebar"]: return

    # Just ST3 supports, ST2 is not
    workspace = settings["workspace"]
    file_exclude_patterns = settings["file_exclude_patterns"]
    folder_exclude_patterns = settings["folder_exclude_patterns"]
    project_data = sublime.active_window().project_data()
    if not project_data: project_data = {}
    folders = []
    if "folders" in project_data:
        folders = project_data["folders"]

    # If the workspace is already exist in project data,
    # just update the patters, if not, add the workspace to it
    for folder in folders:
        # Parse windows path to AS-UNIX
        if "\\" in folder : folder = folder.replace("\\", "/")
        if "\\" in workspace : workspace = workspace.replace("\\", "/")

        if folder["path"] == workspace:
            folder["file_exclude_patterns"] = file_exclude_patterns;
            folder["folder_exclude_patterns"] = folder_exclude_patterns
        else:
            folders.append({
                "path": workspace,
                "file_exclude_patterns": file_exclude_patterns,
                "folder_exclude_patterns": folder_exclude_patterns
            })
    else:
        folders.append({
            "path": workspace,
            "file_exclude_patterns": file_exclude_patterns,
            "folder_exclude_patterns": folder_exclude_patterns
        })

    project_data["folders"] = folders
    sublime.active_window().set_project_data(project_data)
