import sublime
import os
import json

def add_caches(caches):
    """Keep the caches"""
    
    settings = get_settings()
    outputdir = settings["workspace"]+"/.cache"
    if not os.path.exists(outputdir): 
        os.makedirs(outputdir)

    fp = open(outputdir + "/gists.json", "w")
    fp.write(json.dumps(dict(caches), indent=4))
    fp.close()

def get_settings():
    """ Load settings from sublime-settings"""
    
    settings = {}
    s = sublime.load_settings("HaoGist.sublime-settings")
    settings["username"] = s.get("username")
    settings["token"] = s.get("token")
    settings["workspace"] = s.get("workspace")
    settings["file_exclude_patterns"] = s.get("file_exclude_patterns", {})
    settings["folder_exclude_patterns"] = s.get("folder_exclude_patterns", [])

    return settings

def show_workspace_in_sidebar(settings):
    """Add new project folder to workspace
       Just Sublime Text 3 can support this method
    """

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
