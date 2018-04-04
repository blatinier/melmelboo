#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
from flask import render_template, request, redirect
from flask_mail import Message
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import MultifieldParser

import conf
from bootstrap import application, mail
from databases import get_melmelboo_connection
from forms import ContactForm
from utils.cleaner import clean_string


def excerpt(text):
    text = clean_string(text)
    return " ".join(text.split(" ")[:45])


@application.route("/", methods=['GET'])
def home():
    return redirect(conf.BLOG_PATH)


@application.route("/contact-me", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == "GET":
        return render_template('contact.html', form=form,
                               current='contact')
    elif request.method == "POST":
        if not form.validate():
            return render_template('contact.html', form=form,
                                   current='contact')
        else:
            pass
            msg = Message("[Melmelboo] %s" % form.name.data,
                          sender=form.email.data,
                          reply_to=form.email.data,
                          recipients=['benoit@latinier.fr',
                                      'camille.demoment@gmail.com'])
            msg.body = """
From: %s <%s>
Website: %s
%s
""" % (form.name.data, form.email.data, form.website.data, form.message.data)
            mail.send(msg)
            return render_template('contact.html', form=form,
                                   success=True, current='contact')


@application.route("/projects", methods=['GET'])
def projects():
    ghost = get_melmelboo_connection()
    with ghost.cursor() as ghost_cur:
        # Get projet 52 - 2015
        ghost_cur.execute("SELECT title, feature_image FROM posts WHERE id IN "
                          "(SELECT post_id FROM posts_tags WHERE tag_id='5ac410167526de286e2664a7') "
                          "AND YEAR(published_at)='2015'"
                          "ORDER BY published_at DESC")
        p52_2015 = list(ghost_cur.fetchall())
        # Get projet 52 - 2016
        ghost_cur.execute("SELECT title, feature_image FROM posts WHERE id IN "
                          "(SELECT post_id FROM posts_tags WHERE tag_id='5ac410167526de286e2664a7') "
                          "AND YEAR(published_at)='2016'"
                          "ORDER BY published_at DESC")
        p52_2016 = list(ghost_cur.fetchall())
    ghost.close()
    return render_template('projects.html',
                           p52_2015=p52_2015, p52_2016=p52_2016)


@application.route("/search/", defaults={'page': 1})
@application.route("/search/<int:page>")
def search(page):
    search = request.args['q']
    storage = FileStorage(conf.INDEX_DIR)
    index = storage.open_index(indexname=conf.INDEX_NAME)
    qp = MultifieldParser(['title', 'text', 'tags'], schema=index.schema)
    q = qp.parse(search)
    results = []
    with index.searcher() as searcher:
        results = searcher.search_page(q, page, pagelen=conf.PAGE_SIZE)
        # Get real posts
        post_ids = ",".join(["'%s'" % p['post_id'] for p in results])
        if post_ids:
            ghost = get_melmelboo_connection()
            with ghost.cursor() as ghost_cur:
                ghost_cur.execute("SELECT title, feature_image, html, slug "
                                  "FROM posts WHERE id IN (%s)" % post_ids)
                posts = [{'type': "post",
                          'title': i[0],
                          'image': i[1],
                          'excerpt': excerpt(i[2]),
                          'url': "/blog/" + i[3]} for i in ghost_cur.fetchall()]
            ghost.close()
        else:
            posts = []
    return render_template("search.html", posts=posts, search=search)
