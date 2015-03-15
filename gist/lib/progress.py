import sublime


class ThreadProgress():

    """
    Animates an indicator, [=   ], in the status area while a thread runs
    :param thread:
        The thread to track for activity
    :param message:
        The message to display next to the activity indicator
    :param _callback:
        The message to display once the thread is complete
    """

    def __init__(self, api, thread, message, _callback, _callback_options={}):
        self.api = api
        self.thread = thread
        self.message = message
        self._callback = _callback
        self._callback_options = _callback_options
        self.addend = 1
        self.size = 12
        sublime.set_timeout(lambda: self.run(0), 100)

    def run(self, i):
        if not self.thread.is_alive():
            if hasattr(self.thread, 'result') and not self.thread.result:
                sublime.status_message('')
                return

            res = self.api.res
            if not res or res.status_code > 399:
                print (res.text)
                return

            # Invoke _callback
            self._callback(res, self._callback_options)
                
            return

        before = i % self.size
        after = (self.size - 1) - before

        sublime.status_message('%s [%s=%s]' % (self.message, ' ' * before, ' ' * after))

        if not after:
            self.addend = -1
        if not before:
            self.addend = 1
        i += self.addend

        sublime.set_timeout(lambda: self.run(i), 100)