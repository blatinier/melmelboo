#!/usr/bin/env python
import os
import requests
import sqlite3
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import conf


if __name__ == "__main__":
    ghost = sqlite3.connect(conf.BLOG_DB_PATH)
    ghost_cur = ghost.cursor()
    api_url = "https://www.melmelboo-voyage.fr/blog/ghost/api/v0.1/"
    endpoint = "posts/"
    qs = {"limit": 5,
          "order": "published_at desc",
          "filter": "status:published",
          "include": "tags",
          "client_id": conf.GHOST_ID,
          "client_secret": conf.GHOST_SECRET}
    posts = requests.get(api_url + endpoint, params=qs)
    tag_voyage = 43
    for post in posts.json()['posts']:
        if post['tags'] and any(tag['slug'] == "melmelboo" for tag in post['tags']):
            ghost_cur.execute("SELECT COUNT(*) FROM posts WHERE title = ?", (post['title'], ))
            res = ghost_cur.fetchone()
            if not res[0]:
                art_uuid = str(uuid.uuid4())
                ghost_cur.execute("""
                                  INSERT INTO posts(uuid, title, slug, markdown, html, image,
                                                    status, language, author_id,
                                                    created_at, created_by,
                                                    updated_at, updated_by,
                                                    published_at, published_by)
                                  VALUES(?, ?, ?, ?, ?, ?,
                                         ?, ?, ?,
                                         ?, ?,
                                         ?, ?,
                                         ?, ?)""",
                                  (art_uuid, post['title'], post['slug'], post['markdown'], post['html'], post['image'],
                                   "published", "fr_FR", 1,
                                   post['created_at'], 1,
                                   post['updated_at'], 1,
                                   post['published_at'], 1))
                post_id = ghost_cur.lastrowid
                ghost_cur.execute("""INSERT INTO posts_tags(post_id, tag_id)
                                  VALUES(?, ?)""", (post_id, tag_voyage))
                ghost.commit()
    ghost.close()
