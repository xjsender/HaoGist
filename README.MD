# Gist Plugin for Sublime
As you know, there already has a <a href="https://github.com/condemil/Gist">sublime gist plugin</a>, however, there is no cache handler and it seems the author already stop to develop on it, so I decide to develop this gist plugin.

## Installation
This plugin is hosted on [package control](https://sublime.wbond.net/packages/HaoGist)

You should upgrade package control to v3.0, because just v3.0 support dependencies.json feature, if you didn't do it, plugin will use the build-in requests.

## Configuration
* After plugin is installed, you **must** set your gist token, you can open this settings file by entering ```HaoGist: Settings User``` in the command palette.

* User setting sample:
```javascript
{
    // OSX workspace is different with windows,
    // In OSX, workspace should be: 
    // "/Users/<UserName>/workspace/gist-workspace"
    // If workspace is empty, it will be set as {packages_path}/User/HaoGist
    "workspace": "c:/workspace/gist-workspace",
    "token": ""
}
```

### How to open command palette?
* Via menu item in ```Tools > Command Palette```
* Via press ```ctrl+shift+p``` in windows or ```command+shift+p``` in osx

### How to get gist token?
* [Via Web](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)
* Via curl:
    - curl -v -u USERNAME -X POST https://api.github.com/authorizations --data "{\"scopes\":[\"gist\"], \"note\": \"Sublime HaoGist Plugin\"}"

### How to use this plugin to CRUD on gist:

#### Command Palette
* Input ```HaoGist: ``` in command palette, you will see gist commands
    - refresh_gist_workspace
    - reload_gist_cache
    - clear_gist_cache
    - open_gist
    - create_gist
    - rename_gist
    - update_gist
    - update_gist_description
    - refresh_gist
    - delete_gist
    - open_gist_in_browser
    - release_note
    - about_hao_gist

#### Context Menu
Open your context menu in any open view, you will see the commands of this plugin

# Dependency Lib
+ [requests](https://github.com/kennethreitz/requests)