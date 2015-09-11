# Design of HTTP process #

when an HTTP request come in:

all static file request are served by AppEngine itself, which includes:

```
# static files under root:

- url: /static
  static_dir: static

# static files for each app:

- url: /([^/].*)/static
  static_dir: \1/static
```

the dynamic requests are served by dispatcher.py:

```
- url: /.*
  script: dispatcher.py
```

dispatcher.py will handle all dynamic request follows the rule:

extract app name from first path-element:

`/<appname>/other-path...`

is app name exist?

NO: raise 404 error

YES: dispatch to script: `/<appname>/app.py`:

```
import config # apps = ('core', 'auth', 'admin', 'widget', 'blog', 'wiki', 'forum')

class Dispatcher(webapp.RequestHandler):
    def get(self):
        self.dispatch('get')

    def post(self):
        self.dispatch('post')

    @HttpErrorHandler
    def dispatch(self, method):
        bind_thread(self.request, self.response)
        appname = get_app(url)
        import appname.app as app
        handler = locate(app.export, url)
        if method=='get':
            handler.get()
        elif method=='post':
            handler.post()
        else:
            raise HTTPMethodNotAllowedError()

application = webapp.WSGIApplication([('/.*', Dispatcher)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
```

each `/<appname>/app.py` contains handler classes:

```
export = ('/post/$/$', 'Post', '/create/$', 'create')

class Post(object):
    def get(self, userId, postId):
        pass

class Create(object):
    def post(self, userId):
        pass
```

the returning results:

  * None: HTTP request handled, no further process is needed;
  * string: As HTML response string, send to browser;
  * ('template-path', model): Rendered by Django template.

when Raise HTTP Error:

  * HTTPNotFoundError: 404 error
  * HTTPRedirectError: 302 redirect
  * HTTPError: show error page