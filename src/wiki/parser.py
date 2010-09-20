#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Parse wiki to html.

Syntax:

italic:       __italic__
bold:         **bold**
code:         ``code``
block code:   {{{code}}}
strikeout:    ~~strikeout~~

= Heading =
== Level 2 ==
=== Level 3 ===
==== Level 4 ====
===== Level 5 =====
====== Level 6 ======

Dividers:
---- Four or more dashes on a line by themeselves results in a horizontal rule.

Lists:
The following is:
  * A list
  * Of bulleted items
    # This is a numbered sublist
    # Which is done by indenting further

 * This is also a list
 * With a single leading space

Internal wiki links:
[[Title description is here]]
[[Title]]

Links to anchors within a page:
Each heading defines a HTML anchor with the same name as the heading, but with spaces replaced by underscores.

[[Title#Anchor]]

Links to external pages
External links always start with 'http://' or 'https://', and description follows or omitted:

[[http://www.microsoft.com]]
[[http://www.google.com Search with Google]]

Links to images:
If external links end with '.png', '.jpg' or '.gif', links are turn to image:

[[http://code.google.com/images/code_sm.png]]

If the image is produced by a server-side script, you may need to add a nonsense query string parameter to the end so that the URL ends with a supported image filename extension.

[[http://chart.apis.google.com/chart?chs=200x125&chd=t:48.14,33.79,19.77|83.18,18.73,12.04&cht=bvg&nonsense=something_that_ends_with.png]]

Tables:

|| Year || Temperature (low) || Temperature (high) ||
|| 1900 || -10 || 25 ||
|| 1910 || -15 || 30 ||
|| 1920 || -10 || 32 ||

Comments is the same as HTML:
<!-- this is a comment -->

To be implemented:

Videos:

<wiki:video url="http://www.youtube.com/watch?v=3LkNlTNHZzE"/>

super script: ^^super^^script
sub script:   ,,sub,,script
'''

import re
import StringIO
import urllib

__author__ = 'Michael Liao (askxuefeng@gmail.com)'

class TocHolder(object):

    def __init__(self, max):
        self.max = max

    def __str__(self):
        return '<!-- To be replaced with toc (max=%d) -->' % (self.max,)

sym_pair_dict = {
        '__' : ('<i>', '</i>'),
        '**' : ('<b>', '</b>'),
        '``' : ('<code>', '</code>'),
        '~~' : ('<s>', '</s>'),
}

wiki_sym = re.compile(r'(\_\_|\*\*|\`\`|\~\~|\[\[)')

#wiki_summary = re.compile(r'^\#summary .*$')
wiki_toc = re.compile(r'^ *\<wiki\:toc( +max\_depth\=[\"|\'](?P<max>[1-6])[\"|\'])? *(\/\> *|> *\<\/wiki\:toc\>) *$')
wiki_heading = re.compile(r'^(\={1,6}) +(.+) +(\={1,6})$')
wiki_list_ul = re.compile(r'^( *)\* .*$')
wiki_list_ol = re.compile(r'^( *)\# .*$')
wiki_hr = re.compile(r'^ *\-\-\-\-\-* *$')
wiki_empty = re.compile(r'^ *$')

def valid_title(title):
    '''
    Convert title to a valid title.
    '''
    if isinstance(title, unicode):
        title = title.encode('utf8')
    return urllib.quote(title.strip().replace(' ', '_'), safe='')

def __parse_link(text, is_exist):
    '''
    Convert '[[text]]' to a http link '<a href=xxx>link</a>'.
    '''
    links = text.strip().split(' ', 1)
    link = links[0]
    title = links[0]
    if len(links)==2:
        title = links[1].strip()
    if link.startswith('http://') or link.startswith('https://'):
        # external link:
        return '<a href="%s" title="%s" target="_blank" class="wiki-link-external">%s</a>' % (link, title, title)
    if link.startswith('mailto:'):
        # email link:
        if title==link:
            title = link[7:]
        return '<a href="%s" title="%s" class="wiki-link-email">%s</a>' % (link, title, title)
    # internal link:
    vars = (valid_title(link), title, title)
    return is_exist(link) \
            and '<a href="/wiki/page/%s" title="%s" class="wiki-link">%s</a>' % vars \
            or '<a href="/wiki/edit?title=%s" title="Edit %s" class="wiki-link-edit">%s</a>' % vars

def parse(wikicontent, is_exist):
    buffer = ['<!-- parsed wiki page -->']
    headings = []
    f = StringIO.StringIO(wikicontent)
    last_indent = 0
    pre = False
    has_p = False
    for line in f:
        line = line.rstrip('\n').rstrip('\r')
        # is heading:
        m = wiki_heading.match(line)
        if m is not None:
            if has_p:
                has_p = False
                buffer.append('</p>')
            if len(m.group(1))==len(m.group(3)):
                n = len(m.group(1))
                title = m.group(2)
                href = valid_title(title)
                headings.append((n, title, href,))
                buffer.append('<a name="%s"></a><h%d class="wiki-heading">%s</h%d>' % (href, n, title, n))
            else:
                # invalid heading
                buffer.append(line)
            continue
        # is toc:
        m = wiki_toc.match(line)
        if m is not None:
            if has_p:
                has_p = False
                buffer.append('</p>')
            max = 6
            ms = m.group('max')
            if ms is not None:
                max = int(ms)
            buffer.append(TocHolder(max))
            continue
        # is seperator line:
        m = wiki_hr.match(line)
        if m is not None:
            if has_p:
                has_p = False
                buffer.append('</p>')
            buffer.append('<hr class="wiki-hr" />')
            continue
        # empty line?
        m = wiki_empty.match(line)
        if m is not None:
            if has_p:
                has_p = False
                buffer.append('</p>')
            continue
        # parse line:
        if not has_p:
            has_p = True
            buffer.append('<p class="wiki-p">')
        stack = []
        while True:
            m = wiki_sym.search(line)
            if m is None:
                buffer.append(line)
                break
            buffer.append(line[:m.start()])
            sym = m.group(1)
            if sym in sym_pair_dict:
                # it is __, **, ~~:
                if stack and stack[-1]==sym:
                    # should pop up:
                    stack.pop()
                    buffer.append(sym_pair_dict[sym][1])
                else:
                    # should push:
                    stack.append(sym)
                    buffer.append(sym_pair_dict[sym][0])
                line = line[m.end():]
            elif sym=='[[':
                # parse link
                end_of_link = line.find(']]', m.end())
                link = end_of_link==(-1) and line[m.end():] or line[m.end():end_of_link]
                buffer.append(__parse_link(link, is_exist))
                if end_of_link==(-1):
                    break
                line = line[end_of_link+2:]
                if not line:
                    break
        # fix stack:
        while stack:
            sym = stack.pop()
            buffer.append(sym_pair_dict[sym][1])
        buffer.append('\n')

    if has_p:
        buffer.append('</p>')
    # replace toc:
    for index, item in enumerate(buffer):
        if isinstance(item, TocHolder):
            buffer[index] = __parse_toc(headings)
            break
    return ''.join(buffer)

def __parse_toc(headings):
    '''
    parse headings in list which starts with '<!--@Heading%d %s-->'
    
    Args:
        headings: list object contains tuple (depth, title, href).
    
    Returns:
        String of HTML with headings.
    '''
    buffer = [r'<div class="wiki-toc"><div class="wiki-toc-header">Content</div><div class="wiki-toc-content">']
    last = 0
    for n, title, href in headings:
        if n>last:
            buffer.append('<ol>' * (n-last))
        elif n<last:
            buffer.append('</ol>' * (last-n))
        last = n
        buffer.append('<li><a href="#%s">%s</a></li>'% (href, title))
    buffer.append('</ol>' * last)
    buffer.append('</div></div>')
    return ''.join(buffer)

if __name__=='__main__':
    s = u'''
<wiki:toc max_depth="2" /> 

ach pragma line begins with a pound-sign (#) and the
pragma name, followed by a value.

'''
    print parse('this is __italic__ font')
    print parse('this is **bold** font')
    print parse('this is ~~strike words~~ here')
    print parse('this is ``python code`` and a **__bold and italic__** haha!')
    print parse('this is a bad **__bold and italic**__ haha!')

    print parse('this is a [[http://www.google.com Search with Google]] haha!')
    print parse('this is a [[http://www.google.com]] haha!')

    print parse('this is a [[Google Search with Google]] haha!')
    print parse('this is a [[MS Search with Microsoft]] haha!')
    print parse('this is a [[MS    Search with Microsoft   ]] haha!')
    print parse('this is a [[Google]] haha!')
    print parse('this is a [[MS]] haha!')
    print parse(u'this is a [[谷歌 Welcome to 谷歌]] haha!')
    print parse('this is a bad [[http://www.google.com Search with Google')
    print parse('this is a bad [[Google')
    print parse('this is a bad [[MS')
    print parse('this is a not well-formed **[[ http://www.google.com Search with Google ]]** format')

    print parse(' <wiki:toc max_depth="4" /> \n **haha**')

    ss = [
          '<wiki:toc/>',
          '<wiki:toc />',
          '<wiki:toc  />',
          ' <wiki:toc  /> ',

          '<wiki:toc max_depth="3"/>',
          '<wiki:toc max_depth="3" />',
          '<wiki:toc max_depth=\'3\'/>',
          '<wiki:toc max_depth=\'3\' />',

          '<wiki:toc max_depth="3"></wiki:toc>',
          '<wiki:toc max_depth="3" ></wiki:toc>',
          '<wiki:toc max_depth=\'3\'></wiki:toc>',
          '<wiki:toc max_depth=\'3\' ></wiki:toc>  ',

          '<wiki:toc max_depth="3"> </wiki:toc>',
          '<wiki:toc max_depth="3" > </wiki:toc>',
          '<wiki:toc max_depth=\'3\'> </wiki:toc>',
          '<wiki:toc max_depth=\'3\' > </wiki:toc>',

          '<wiki:toc></wiki:toc>',
          '<wiki:toc ></wiki:toc>',
          '<wiki:toc> </wiki:toc>',
          '<wiki:toc > </wiki:toc>',

          '<wiki:toc > <wiki:toc>',
          '<wiki:toc > < /wiki:toc>',
          '<wiki:toc > </ wiki:toc>',
          '<wiki:toc >',
          ' <wiki:toc></wiki:toc> ok'
    ]
    for s in ss:
        m = wiki_toc.match(s)
        if m is not None:
            max = 6
            ms = m.group('max')
            if ms is not None:
                max = int(ms)
            print 'max =', max,
        print str(m is not None) + ' --> ' + s 

    print parse('''
first line
    
second and 
third and 
fourth


end

----
copyright & announcement
    ''')