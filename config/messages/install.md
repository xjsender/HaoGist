You should upgrade package control to v3.0, because just v3.0 support dependencies.json feature

This Gist plugin support cache, after this plugin is installed, you must set your own gist token and workspace.

If you want to know more detail on how to set them, you can goto https://github.com/xjsender/HaoGist

How to get gist token?
* [Via Web](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)
* [Via curl]
```bash
curl -v -u USERNAME -X POST https://api.github.com/authorizations --data "{\"scopes\":[\"gist\"], \"note\": \"Sublime HaoGist Plugin\"}"
```

