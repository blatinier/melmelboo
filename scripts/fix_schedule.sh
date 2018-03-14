#!/usr/bin/env bash
sqlite3 /home/camille/ghost-melmelboo/blog/content/data/ghost.db "update posts set status='published' where published_at < datetime('now', 'localtime') and status='scheduled'"
