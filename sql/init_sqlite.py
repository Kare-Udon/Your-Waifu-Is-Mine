import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS twitter_users (id INTEGER PRIMARY KEY, name TEXT, url TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS pixiv_users (id INTEGER PRIMARY KEY, name TEXT, url TEXT)")
conn.commit
conn.close()