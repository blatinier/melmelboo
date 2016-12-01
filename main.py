#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

from flask import render_template, request, redirect
from flask_mail import Message

from bootstrap import application, mail
from forms import ContactForm


@application.route("/", methods=['GET'])
def home():
    return redirect("/blog")


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
    ghost = sqlite3.connect("/var/www/melmelboo/blog/content/data/ghost.db")
    ghost_cur = ghost.cursor()
    # Get charlie au fil des mois
    ghost_cur.execute("SELECT title, image FROM posts WHERE id IN "
                      "(SELECT post_id FROM posts_tags WHERE tag_id=38) "
                      "ORDER BY published_at DESC")
    charlie_month = list(ghost_cur.fetchall())
    # Get gaspard au fil des mois
    ghost_cur.execute("SELECT title, image FROM posts WHERE id IN "
                      "(SELECT post_id FROM posts_tags WHERE tag_id=42) "
                      "ORDER BY published_at DESC")
    gaspard_month = list(ghost_cur.fetchall())
    # Get projet 52 - 2015
    ghost_cur.execute("SELECT title, image FROM posts WHERE id IN "
                      "(SELECT post_id FROM posts_tags WHERE tag_id=36) "
                      "AND strftime('%Y', published_at)='2015'"
                      "ORDER BY published_at DESC")
    p52_2015 = list(ghost_cur.fetchall())
    # Get projet 52 - 2016
    ghost_cur.execute("SELECT title, image FROM posts WHERE id IN "
                      "(SELECT post_id FROM posts_tags WHERE tag_id=36) "
                      "AND strftime('%Y', published_at)='2016'"
                      "ORDER BY published_at DESC")
    p52_2016 = list(ghost_cur.fetchall())
    return render_template('projects.html', charlie_month=charlie_month,
                           p52_2015=p52_2015, p52_2016=p52_2016,
                           gaspard_month=gaspard_month)
