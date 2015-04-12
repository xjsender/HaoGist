.. :changelog:

Release History

---------------


0.1.8 (2015-04-12)
++++++++++++++++++
* Remove ``file_exclude_patterns`` setting
* Remove ``folder_exclude_patterns`` setting
* ``workspace`` setting can be empty, if it is empty, workspace will be set as {packages_path}/User/HaoGist


0.1.7 (2015-04-08)
++++++++++++++++++
* Deliver issue #2 for hiding workspace in sidebar


0.1.6 (2015-04-05)
++++++++++++++++++
* Add context menu items for all HaoGist commands
* Add message for ``reload_gist_cache`` command


0.1.5 (2015-04-04)
++++++++++++++++++
* Bug: In order to get all gists, add ``?per_page=1000`` to ``/gists`` list request


0.1.4 (2015-04-04)
++++++++++++++++++
* Deliver enhancement for issue #1


0.1.3 (2015-03-22)
++++++++++++++++++
* Catch requests request exception
* Add a new settings ``debug_mode`` to control whether output debug message


0.1.2 (2015-03-21)
++++++++++++++++++
* Add thread progress for ``list_gist`` part of ``open_gist``
* Correct progress message for ``create_gist``


0.1.1 (2015-03-20)
++++++++++++++++++
* Add a new command ``update_gist_description`` to update gist description
* Update README.MD


0.1.0 (2015-03-18)
++++++++++++++++++
* Add exception catch for network connection exception
* Rename ``about`` command to ``about_hao_gist`` in order to prevent conflict with other plugin


0.0.9 (2015-03-16)
++++++++++++++++++
* Add new ``rename_gist`` command
* Add new ``about`` command
* Add new ``release_note`` command
* Add thread process for gist list
* Reload gist cache after create, delete or rename operation on gist


0.0.8 (2015-03-16)
++++++++++++++++++
* Add requests dependencies, if not package control 3, just use the build-in requests


0.0.7 (2015-03-15)
++++++++++++++++++
* Add thread progress for ``open_gist``


0.0.6 (2015-03-15)
++++++++++++++++++
* Add thread progress for CRUD on gist
* Refactoring this plugin, add callback support to thread
* If CRUD succeed, just hide the panel after lots of seconds
* Add a ``delay_seconds_for_hiding_panel`` setting to control the panel hiding delay seconds


0.0.5 (2015-03-14)
++++++++++++++++++
* Add two commands for default setting and user setting for HaoGist
* Update README.MD
* Correct messages
* Add more detail in the install message


0.0.4 (2015-03-14)
++++++++++++++++++
* Fix install bug
* Fix ```cache``` bug


0.0.3 (2015-03-12)
++++++++++++++++++
* Remove ``user`` setting
* Remove dependency lib [gistapi]
* Enhancement for gist selection of ``open gist``
* Add a new module ``api.py``
* Add ``reload gist workspace`` command
* Add ``reload gist cache`` command


0.0.2 (2015-03-12)
++++++++++++++++++
* Add ``update gist`` command
* Add ``refresh gist`` command
* Add ``refresh gist`` command
* Add ``delete gist`` command
* Add ``create gist`` command
* Add ``clear gist cache`` command
* Add ``open gist in browser`` command


0.0.1 (2015-03-12)
++++++++++++++++++
* Optimize the cache feature


0.0.0 (2015-03-12)
++++++++++++++++++
* Birth!

* Frustration
* Conception