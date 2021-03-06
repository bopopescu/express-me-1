#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao (askxuefeng@gmail.com)'

'''
Web MVC framework for AppEngine/WebOb.
'''

import re
import time
import urllib
import inspect
import logging

from google.appengine.ext import webapp

from framework import ApplicationError
from framework import view

import interceptor
import theme

COOKIE_EXPIRES_MIN = 86400
COOKIE_EXPIRES_MAX = 31536000

class WebError(ApplicationError):
    pass

class NotFoundError(WebError):
    pass

class Context(dict):
    '''
    Web application context as a dict.
    '''
    def __getattr__(self, name):
        if self.has_key(name):
            return self[name]
        raise AttributeError('\'%s\' object has no attribute \'%s\'' % (self.__class__.__name__, name))

    def __setattr__(self, name, value):
        self[name] = value

class Dispatcher(webapp.RequestHandler):
    '''
    Entry point of MVC tier. It handles URL with '/appname/apppath'. 
    The app name of root URL ('/') is 'index'.
    '''

    def get(self):
        '''
        Override super.get to handle GET request.
        '''
        self._service('get')

    def post(self):
        '''
        Override super.post to handle POST request.
        '''
        self._service('post')

    def _service(self, method):
        '''
        Handle HTTP request of 'get' or 'post'.
        Args:
            method: string 'get' or 'post'.
        '''
        path = self.request.path;
        if path=='/':
            return self._handle_app(method, 'index', '/')
        n = path.find('/', 1)
        if n==(-1):
            n = len(path)
        appname = path[1:n]
        apppath = path[len(appname)+1:]
        if not apppath.startswith('/'):
            apppath = '/' + apppath
        return self._handle_app(method, appname, apppath)

    def _handle_app(self, method, appname, apppath):
        '''
        Handle request with specific app.
        Args:
            method: string 'get' or 'post'.
            appname: app name, the same as package name.
            apppath: URL that excludes the appname in prefix. For example, apppath of '/blog/view/123' is '/view/123'.
        '''
        logging.info(r'Handle app "%s", path=%s' % (appname, apppath))
        for func in self._get_mapping(method, appname):
            r = func.matches(apppath)
            if r is not None:
                # decode url parameter:
                args = [urllib.unquote(arg) for arg in r]
                # prepare environment as varkw:
                kw = {
                        'environ' : self.request.environ,
                        'headers' : self.request.headers,
                        'cookies' : self.request.cookies,
                        'request' : self.request,
                        'response' : self.response,
                        'context' : Context(
                                get_argument=lambda argument_name, default_value=None: self.request.get(argument_name, default_value),
                                get_arguments=lambda argument_name: self.request.get_all(argument_name),
                                arguments=lambda: self.request.arguments(),
                                get_cookie=lambda name: self._get_cookie(name),
                                set_cookie=lambda name, value, max_age=-1, path='/', secure=False: self._set_cookie(name, value, max_age, path, secure),
                                delete_cookie=lambda name, path='/', secure=False: self._set_cookie(name, 'deleted', 0, path, secure)
                        )
                }
                # global interceptor:
                interceptor.intercept(kw)
                # app interceptor:
                app_inter = __import__(appname, fromlist=['interceptor']).interceptor
                app_inter.intercept(kw)
                if func.has_varkw():
                    result = func(*args, **kw)
                else:
                    result = func(*args)
                return self._response(kw, appname, result);
        # 404 error:
        self._error(404)

    def _response(self, kw, appname, result):
        '''
        Handle result and send response.
        Args:
            appname: app name.
            result: result object that can be None, basestring or dict.
        '''
        if result is None:
            return
        if isinstance(result, basestring):
            return self._render_string(result)
        if isinstance(result, dict):
            return self._render_template(kw, appname, result)

    def _render_template(self, kw, appname, model):
        '''
        Render a template using the given model.
        
        Args:
            model: model as dict.
        '''
        use_theme = model.get('__theme__', False)==True
        if use_theme:
            t = theme.render(appname, model, **kw)
        else:
            t = view.render(appname, model)
        content_type = model.get('__content_type__')
        if content_type:
            self.response.content_type = content_type
        self.response.out.write(t)

    def _render_string(self, result):
        '''
        Render string.
        Args:
            result: string treated as HTML or special content like 'redirect:/'.
        '''
        if result.startswith('redirect:'):
            return self._error(301, result[9:])
        if result.startswith('json:'):
            self.request.headers['Content-Type'] = 'application/json'
            self.response.out.write(result[5:])
            return
        self.response.out.write(result)

    def _get_mapping(self, method, appname):
        '''
        Get list of functions that matches the method and appname.
        Args:
            method: 'get' or 'post'.
            appname: name of app.
        Returns:
            dict, url as key, function as value.
        '''
        attr = 'support_' + method
        mod = __import__(appname, fromlist=['controller']).controller
        all = [getattr(mod, f) for f in dir(mod)]
        return [func for func in all if callable(func) and getattr(func, attr, False)]

    def _error(self, code, extra=None):
        '''
        Send HTTP error response.
        Args:
            code: HTTP code as int.
            extra: additional message based on code.
        '''
        self.response.set_status(code)
        if code==301 or code==302:
            self.response.headers['Location'] = extra
            return
        if code==404:
            self.response.out.write(extra or '404 Not Found')
            return
        if extra:
            self.response.out.write(extra)

    def _set_cookie(self, name, value, max_age=-1, path='/', secure=False):
        '''
        Set cookie by name, value, max_age, path and secure.
        
        Args:
            name: cookie name.
            value: cookie value.
            max_age: cookie age in seconds, if 0, cookie will be deleted immediately, if <0, ignored. Default to -1.
            path: cookie path, default to '/'.
            secure: if cookie is secure, default to False.
        '''
        cookie = name + '=' + value + '; path=' + path
        if max_age>=0:
            cookie += time.strftime('; expires=%a, %d-%b-%Y %H:%M:%S GMT', time.gmtime(time.time() + max_age))
        if secure:
            cookie += '; secure'
        self.response.headers.add_header('Set-Cookie', cookie)

    def _get_cookie(self, name):
        '''
        Get cookie value of specified cookie name.
        
        Args:
            name: cookie name.
        Returns:
            Cookie value.
        '''
        if name in self.request.cookies:
            return self.request.cookies[name]
        return None

    def handle_exception(self, exception, debug_mode):
        logging.exception('Unhandled exception caught by framework.web.Dispatcher.handle_exception()')
        html = r'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>An error occurred</title>
</head>
<body style="font-family: 'Helvetica Neue', Arial, Helvetica, sans-serif;">
  <div style="margin:3px auto; width:640px;">
    <div style="padding:12px 6px; border-bottom:solid 1px #ccc">
      <a href="http://www.expressme.org/" target="_blank"><img src="/static/image/expressme.gif" width="326" height="60" border="0" /></a>
    </div>
    <div style="padding:0px 12px">
      <h3 style="line-height:40px">We are sorry but an unexpected error occurred...</h3>
    </div>
    <div style="padding:12px">%s: %s</div>
    <div style="padding:12px">See logs for more details.</div>
    <div style="line-height:40px; text-align:center; border-top:solid 1px #ccc"><a href="http://www.expressme.org/" target="_blank">ExpressMe</a> copyright&copy;2010, all rights reserved.</div>
  </div>
</body>
</html>
''' % (exception.__class__.__name__, exception.message or '(no message)')
        self.response.out.write(html)

def _matches(pattern, raw_mapping, url):
    '''
    Return match result by given pattern and url.
    Args:
        pattern: pattern as string.
        raw_mapping: True if using raw regular expression, otherwise False.
        url: to-be-tested url.
    Returns:
        A tuple as matched result (maybe empty tuple), or None if not matched.
    '''
    if raw_mapping:
        p = re.compile('^' + pattern + '$')
    else:
        p = re.compile('^' + re.escape(pattern).replace(r'\$', '([^/]*)') + '$')
    m = p.match(url)
    if m is not None:
        return m.groups()
    return None

def _has_varkw(func):
    '''
    Return True if function has kw args. False otherwise.
    Args:
        func: Function reference.
    Returns:
        True or False.
    '''
    # get args spec: (arg_names, varargs, varkw, defaults)
    argsspec = inspect.getargspec(func)
    return argsspec[2] is not None

def get(pattern):
    '''
    decorator of @get() that support get only
    
    Args:
        pattern: string like '/$/$.html', default value: None
    
    Returns:
        decorated function.
    '''
    def execute(f):
        def _wrapper(*args, **kw):
            return f(*args, **kw)
        _wrapper.pattern = pattern
        _wrapper.support_get = True
        _wrapper.support_post = False
        _wrapper.raw_mapping = False
        _wrapper.__name__ = f.__name__
        _wrapper.matches = lambda url: _matches(_wrapper.pattern, _wrapper.raw_mapping, url)
        _wrapper.has_varkw = lambda: _has_varkw(f)
        return _wrapper
    return execute

def post(pattern):
    '''
    decorator of @post() that support post only
    
    Args:
        pattern: string like '/$/$.html', default value: None
    
    Returns:
        decorated function.
    '''
    def execute(f):
        def wrapper(*args, **kw):
            return f(*args, **kw)
        wrapper.pattern = pattern
        wrapper.support_get = False
        wrapper.support_post = True
        wrapper.raw_mapping = False
        wrapper.__name__ = f.__name__
        wrapper.matches = lambda url: _matches(wrapper.pattern, wrapper.raw_mapping, url)
        wrapper.has_varkw = lambda: _has_varkw(f)
        return wrapper
    return execute

def mapping(pattern):
    '''
    decorator of @mapping() that support get and post
    
    Args:
        pattern: string like '/$/$.html', default value: None
    
    Returns:
        decorated function.
    '''
    def execute(f):
        def wrapper(*args, **kw):
            return f(*args, **kw)
        wrapper.pattern = pattern
        wrapper.support_get = True
        wrapper.support_post = True
        wrapper.raw_mapping = False
        wrapper.__name__ = f.__name__
        wrapper.matches = lambda url: _matches(wrapper.pattern, wrapper.raw_mapping, url)
        wrapper.has_varkw = lambda: _has_varkw(f)
        return wrapper
    return execute

def raw_mapping(pattern):
    '''
    decorator of @raw_mapping() that support get and post. 
    WARNING: for regular express expert only! 
    
    The regular expression MUST NOT start with '^' and end with '$'.
    
    Args:
        url: regular expression string.
    
    Returns:
        decorated function.
    '''
    def execute(f):
        def wrapper(*args, **kw):
            return f(*args, **kw)
        wrapper.pattern = pattern
        wrapper.support_get = True
        wrapper.support_post = True
        wrapper.raw_mapping = True
        wrapper.__name__ = f.__name__
        wrapper.matches = lambda url: _matches(wrapper.pattern, wrapper.raw_mapping, url)
        wrapper.has_varkw = lambda: _has_varkw(f)
        return wrapper
    return execute
