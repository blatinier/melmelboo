import os
import os.path
import shutil
import sqlite3
from whoosh.index import create_in
import whoosh.fields as fields

from utils.progress import progress
from utils.cleaner import clean_string
from databases import get_melmelboo_connection


class BlogIndexer:

    def __init__(self, index_name, index_dir):
        self.index_name = index_name
        self.index_dir = index_dir

    def get_schema(self):
        return fields.Schema(post_id=fields.ID(stored=True),
                             tags=fields.KEYWORD(commas=True),
                             title=fields.TEXT(stored=True),
                             text=fields.TEXT)

    def init_index(self):
        print("Drop index")
        shutil.rmtree(self.index_dir)
        os.mkdir(self.index_dir)
        print("Create fresh index")
        self.index = create_in(self.index_dir, self.get_schema(),
                               indexname=self.index_name)

    def index_document(self, index, doc):
        writer = self.index.writer()
        writer.add_document(**doc)
        writer.commit()

    def index_blog(self):
        ghost = get_melmelboo_connection()
        with ghost.cursor() as ghost_cur:
            ghost_cur.execute("SELECT id, title, published_at, html "
                              "FROM posts WHERE status='published' "
                              "ORDER BY published_at DESC")
            posts = [{"post_id": str(post[0]),
                      "title": post[1],
                      "text": clean_string(post[3])}
                     for post in ghost_cur.fetchall()]
            total_cnt = len(posts)
            print("Index %d posts" % total_cnt)
            for i, post in enumerate(posts):
                ghost_cur.execute("SELECT t.name FROM tags t "
                                  "LEFT JOIN posts_tags pt ON pt.tag_id=t.id "
                                  "WHERE pt.post_id=%s", str(post['post_id']))
                tags = [tag[0] for tag in ghost_cur.fetchall()]
                post["tags"] = ",".join(tags)
                suffix = post["title"][:25]
                progress(i, total_cnt, suffix)
                self.index_document(self.index_name, post)
        ghost.close()
        print("\nFinished indexing posts")
