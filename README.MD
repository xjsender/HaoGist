# Gist Plugin for Sublime
As you know, there already has a <a href="https://github.com/condemil/Gist">sublime gist plugin</a>, however, there is no cache handler and it seems the author already stop to develop on it, so I decide to develop this gist plugin.

## Installation
This plugin will be hosted on [package control](https://sublime.wbond.net/packages/HaoGist) in the soon later.

## Configuration
* After plugin is installed, you should set your own gist workspace in your user settings, you can open this settings file by entering ```HaoGist: Settings User``` in the command palette.

* User setting sample:
```javascript
{
    "workspace": "c:/workspace/gist-workspace",
    "token": ""
}
```

### How to open command palette?
* Via menu item in ```Tools > Command Palette```
* Via press ```ctrl+shift+p``` in windows or ```command+shift+p``` in osx

### How to get gist token?
* [Via Web](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)
* Via curl
```bash
curl -v -u USERNAME -X POST https://api.github.com/authorizations --data "{\"scopes\":[\"gist\"], \"note\": \"Sublime HaoGist Plugin\"}"
```

# Dependency Lib
+ [requests](https://github.com/kennethreitz/requests)