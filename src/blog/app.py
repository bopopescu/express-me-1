#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao (askxuefeng@gmail.com)'

'''
Blog app that display blog posts.
'''

from exweb import get
from exweb import post
from exweb import context
from exweb import HttpForbiddenError

import manage
import blog

@get('/')
def get_posts():
    '''
    show all public posts of blog
    '''
    posts = blog.BlogPost.all().filter('post_state =', 0).filter('post_static =', False).order('-post_date').fetch(100)
    return { 'title' : 'Posts', 'posts' : posts, 'feed' : __get_feed() }

@get('/p/$')
def get_posts_by_page(page):
    '''
    show public posts of blog at specified page.
    '''
    posts = blog.BlogPost.all().filter('post_state =', 0).filter('post_static =', False).order('-post_date').fetch(100)
    return { 'title' : 'Posts', 'posts' : posts, 'feed' : __get_feed() }

@get('/tag/$')
def posts_by_tag(tag_key):
    tag = blog.BlogTag.get(tag_key)
    posts = blog.BlogPost.all().filter('post_state =', 0).filter('post_tags =', tag.tag_name).filter('post_static =', False).order('-post_date').fetch(100)
    return { 'title' : tag.tag_nicename, 'tag' : tag, 'posts' : posts, 'feed' : __get_feed() }

@get('/cat/$')
def posts_by_cat(cat_key):
    cat = blog.BlogCategory.get(cat_key)
    posts = blog.BlogPost.all().filter('post_state =', 0).filter('post_category =', cat).filter('post_static =', False).order('-post_date').fetch(100)
    return { 'title' : cat.category_name, 'category' : cat, 'posts' : posts, 'feed' : __get_feed() }

@get('/post/$')
def get_post(id):
    '''
    Show a single post.
    
    Args:
        id: post id as string.
    '''
    p = blog.get_post(id)
    return {
            'title' : p.post_title,
            'post' : p,
            'comments' : manage.get_comments(id),
            'feed' : __get_feed()
    }

@get('/page/$')
def get_page(id):
    '''
    Show a single page.
    
    Args:
        id: page id as string.
    '''
    p = blog.get_page(id)
    return { 'title' : p.post_title, 'page' : p, 'feed' : __get_feed() }

def __get_feed():
    ''' get feed url and title '''
    url = manage.get_setting('blog_setting', 'feed_proxy', '/blog/feed')
    title = manage.get_setting('blog_setting', 'feed_title', 'Rss Feed')
    return { 'url' : url, 'title' : title }

@post('/comment')
def make_comment():
    ''' make a comment on a post or page '''
    form = context.form
    id = form.get('id')
    post = blog.get_post(id)
    if not post.comment_allow:
        raise HttpForbiddenError()
    ref = str(post.key())
    name = form.get('name', '')
    link = form.get('link', '')
    content = form.get('content')
    content = '<p>' + '</p><p>'.join(content.split('\n')) + '</p>'
    key = str(manage.create_comment(ref, content, name, link).key())
    return 'redirect:/blog/post/%s#%s' % (ref, key)

@get('/feed')
def feed():
    '''
    Generate rss feed.
    '''
    host = context.request.host_url
    title = manage.get_setting('blog_setting', 'feed_title', 'Rss Feed')
    description = manage.get_setting('blog_setting', 'feed_desc', 'Subscribe Rss Feed')
    hub = 'http://pubsubhubbub.appspot.com'
    link = 'http://feeds.feedburner.com/expressme'
    max = 20
    posts = blog.get_posts(limit=max)
    response = context.response
    response.content_type = 'application/rss+xml'
    response.charset = 'utf8'
    out = response.out
    out.write(r'''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:slash="http://purl.org/rss/1.0/modules/slash/">
<channel><atom:link rel="hub" href="''')
    out.write(hub)
    out.write('"/><title>')
    out.write(title)
    out.write('</title><link>')
    out.write(link)
    out.write('</link><description>')
    out.write(description)
    out.write('</description><generator>expressme.org</generator><language>en</language>\n')
    for post in posts:
        out.write('<item><title>')
        out.write(post.post_title)
        out.write('</title><link>')
        out.write(host)
        out.write('/blog/post/')
        out.write(str(post.key()))
        out.write('</link><dc:creator>')
        out.write(post.post_owner.user_nicename)
        out.write('</dc:creator><pubDate>')
        out.write(__format_rss_date(post.post_date))
        out.write('</pubDate><description><![CDATA[')
        out.write(post.post_content)
        out.write(']]></description></item>\n')
    out.write('</channel></rss>')

def __format_rss_date(dt):
    # format: Sun, 07 Feb 2010 20:56:30
    return dt.strftime('%a, %d %b %Y %H:%M:%S')
