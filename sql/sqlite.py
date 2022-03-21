from cgi import test
import re
import sqlite3

class database: 
    def __init__(self):
        self.conn = sqlite3.connect('data.db')
        self.c = self.conn.cursor()
    
    # type: 0-twitter 1-pixiv
    def add_user(self, type, id, name):
        if type == 0:
            self.c.execute("SELECT id FROM twitter_users WHERE id=?", (id,))
            if len(list(self.c)) == 0:
                self.c.execute("INSERT INTO twitter_users (id, name) VALUES (?, ?)", (id, name))
            else:
                return False
        elif type == 1:
            self.c.execute("SELECT id FROM pixiv_users WHERE id=?", (id,))
            if len(list(self.c)) == 0:
                self.c.execute("INSERT INTO pixiv_users (id, name) VALUES (?, ?)", (id, name))
            else:
                return False
        self.conn.commit()
        self.conn.close()
        
    def del_user(self, type, id):
        if type == 0:
            self.c.execute("SELECT id FROM twitter_users WHERE id=?", (id,))
            if len(list(self.c)) == 0:
                self.c.execute("DELETE FROM twitter_users WHERE id=?", (id,))
            else:
                return False
        elif type == 1:
            self.c.execute("SELECT id FROM pixiv_users WHERE id=?", (id,))
            if len(list(self.c)) == 0:
                self.c.execute("DELETE FROM pixiv_users WHERE id=?", (id,))
            else:
                return False
        self.conn.commit()
        self.conn.close()