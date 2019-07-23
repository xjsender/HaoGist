# Gist Plugin for Sublime Text
As you know, there already has a [sublime gist plugin](https://github.com/condemil/Gist), however, there is no cache handler and it seems the author already stop to develop on it, so I decide to develop this gist plugin.

## Installation
This plugin is hosted on [package control](https://packagecontrol.io/packages/HaoGist)

You should upgrade package control to v3.0, because just v3.0 support dependencies.json feature, if you didn't do it, plugin will use the build-in requests.

## Change Logs:
+ <a href="https://github.com/xjsender/HaoGist/blob/master/HISTORY.rst" target="_blank">Change Logs</a>

## Configuration
* After plugin is installed, you **must** set your gist token, you can open this settings file by entering `HaoGist: Settings User` in the command palette.

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
* Via menu item in `Tools > Command Palette`
* Via press `ctrl+shift+p` in windows or `command+shift+p` in osx

### How to get gist token?

#### web
* [Via Web](https://github.com/settings/tokens/new?scopes=gist,&description=SublimeText+HaoGist+plugin)
* Paste the token in the settings section under the token option.

#### API

Here's a command you can run from your terminal to generate a token via curl:

    curl -i -u USERNAME https://api.github.com/authorizations --data '{"scopes":["gist"],"note":"SublimeText HaoGist plugin"}'

Where `USERNAME` is your Github username. Save the token generated and paste it in the settings section under the token option.

If OTP is enabled on your account, this will return 401 error code, use:

    curl -i -u USERNAME -H "X-GitHub-OTP: OTPCODE" https://api.github.com/authorizations --data '{"scopes":["gist"],"note":"SublimeText 2/3 Gist plugin"}'

Where `OTPCODE` is the code your authenticator app shows you.

### How to use this plugin to CRUD on gist:

#### Command Palette
* Input `HaoGist: ` in command palette, you will see gist commands
    - choose_gist
    - open_gist
    - delete_exist_gist
    - open_gist_in_browser
    - update_content_to_gist
    - add_file_to_gist
    - delete_file_from_gist
    - create_gist
    - rename_gist
    - update_gist_description
    - update_gist
    - refresh_gist
    - delete_gist
    - clear_gist_cache
    - open_current_gist_in_browser
    - release_note
    - about_hao_gist

#### Context Menu
Open your context menu in any open view, you will see the commands of this plugin

## Dependency Lib
+ [requests](https://github.com/kennethreitz/requests)