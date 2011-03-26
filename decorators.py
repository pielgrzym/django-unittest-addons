from django.contrib.auth.models import User

def login(method):
    def l(self):
        username = self._default_user[0]
        password = self._default_user[1]

        logged_in = self.client.login(username=username, password=password)
        self.failUnlessEqual(logged_in, True)

        method_results = method(self, *args, **kwargs)
        self.client.logout()
        return method_results
    return l
