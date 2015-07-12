This Gist plugin support cache and thread progress, any of your gist operation will not block your action in sublime.

you can see the operation progress in the status bar, after operation is finished, you will see the operation result in the output panel, if no error happen, the output panel will be closed automatically 1.5 seconds after it is open.

After this plugin is installed, you must set your own gist token, if you want to know more detail on how to set them, you can goto https://github.com/xjsender/HaoGist

How to get gist token?
* [Via Web](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)
* Via curl:
    - curl -v -u xjsender -X POST https://api.github.com/authorizations --data "{\"scopes\":[\"gist\"], \"note\": \"Sublime HaoGist Plugin\"}"

How to use this plugin?
* Input ```HaoGist: ``` in command palette, you will see gist commands
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

