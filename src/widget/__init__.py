#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao (askxuefeng@gmail.com)'

'''
Widget definition
'''

import os

class SettingClass(type):
    ' Meta-class for initializing Setting '
    pass

def get_widgets():
    '''
    Get all widgets available in ExpressMe.
    
    Args:
      None
    
    Returns:
      Dict that contains module name (short name) as key and module as value.
    '''
    root = os.path.split(os.path.dirname(__file__))[0]
    widget_root = os.path.join(root, 'widget')
    widgets = os.listdir(widget_root)
    valid_widgets = [w for w in widgets if __is_valid_widget(widget_root, w)]
    dict = {}
    for w in valid_widgets:
        dict[w] = __import__('widget.' + w, fromlist=[w])
    return dict

def __is_valid_widget(widget_root, widget):
    dir = os.path.join(widget_root, widget)
    return os.path.isdir(dir) and os.path.isfile(os.path.join(dir, '__init__.py'))

class WidgetSetting(object):

    __slots__ = ('key', 'required', 'name', 'description', 'is_password')

    def __init__(self, key, required, name, description='', is_password=False):
        self.key = key
        self.required = required
        self.name = name
        self.description = description
        self.is_password = is_password

    def validate(self, value):
        pass

class WidgetModel(object):

    def handle_request(self, request, response, parameters):
        '''
        Handle a AJAX request that makes a Widget can interact with users.
        
        NOTE that the HTTP request is initiate from widget's HTML snippets by JavaScript, 
        and unlike the normal app-dispatcher-handler, HTTP response must be handled and 
        any returning value will be ignored.
        '''
        out = response.out
        out.write('<html><head><title>Widget Debug</title></head><body><p>Request: %s</p><p>Method: %s</p><p>Parameters:</p>' % (request.url, request.method.lower()))
        if parameters and len(parameters)>0:
            for key, value in parameters.iteritems():
                out.write('<p>&nbsp;&nbsp;%s = %s</p>' % (key, value))
        else:
            out.write('<p>&nbsp;&nbsp;<i>None</i></p>')
        out.write('</body></html>')

    def load(self):
        return {
                'title' : 'Widget Title',
                'content' : 'Widget Content in <strong>HTML</strong> format'
        }

    def render(self, data):
        title = ''
        if 'title' in data:
            title = data['title']
        content = ''
        if 'content' in data:
            content = data['content']
        buffer = ['<div class="widget" id="']
        buffer.append(self.__class__.__module__.replace('.', '_'))
        buffer.append('">')
        if title:
            buffer.append('<h3 class="widget-title">')
            buffer.append(title)
            buffer.append('</h3>')
        buffer.append('<div class="widget-content">')
        buffer.append(content)
        buffer.append('</div></div>')
        return ''.join(buffer)
