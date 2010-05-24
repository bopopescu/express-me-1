#!/usr/bin/env python
# -*- coding: utf-8 -*-

'Html Snippet'

import widget

title = 'Any HTML'
description = 'Display any HTML snippet'

class Widget(widget.WidgetModel):
    '''
    Show any html snippet.
    '''

    def load(self):
        html = r'<div><a href="http://feeds.feedburner.com/expressme"><img src="http://feeds.feedburner.com/~fc/expressme?bg=66FFCC&amp;fg=333333&amp;anim=0" height="26" width="88" style="border:0" alt="" /></a></div>'
        return {
                'title' : '',
                'content' : html
        }
