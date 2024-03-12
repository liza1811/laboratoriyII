import sqlite3

from werkzeug.security import generate_password_hash


def create_user(name, email, psw):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT INTO users (name, email, psw, is_admin) VALUES (?, ?, ?, ?)',
              (name, email, psw, 1))
    conn.commit()
    conn.close()


create_user('Елизавета', 'admin@mail.ru', 'admin')
