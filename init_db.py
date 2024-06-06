import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("database.db")

with open('scheme.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
           )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
           )

cur.execute("INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@blog.com', generate_password_hash('123456'), True)
           )

connection.commit()
connection.close()
