import sqlite3
import datetime


class DataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM posts'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            # print ('Ошибка чтения из бд')
            return False
        return []

    def getJSON(self):
        sql = '''SELECT * FROM posts'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                blocks_list = [dict(ix) for ix in res]
                return blocks_list
        except:
            # print ('Ошибка чтения из бд')
            return False
        return []

    def getTechnJSON(self):
        sql = '''SELECT * FROM technologies'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                blocks_list = [dict(ix) for ix in res]
                return blocks_list
        except:
            # print ('Ошибка чтения из бд')
            return False
        return []

    def addPost(self, title, content, user, status):
        try:
            today = datetime.datetime.today()
            tm = today.strftime("%d/%m/%Y")

            self.__cur.execute(
                "INSERT INTO posts VALUES(NULL, ?, ?, ?, ?, ?)", (tm, title, content, status, user))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД" + str(e))
            return False
        return True

    def addTech(self, summary, content):
        try:
            self.__cur.execute(
                "INSERT INTO technologies VALUES(NULL, ?, ?)", (summary, content))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления технологии в БД" + str(e))
            return False
        return True
    
    def addNew(self, content, img, summary):
        try:
            self.__cur.execute(
                "INSERT INTO news VALUES(NULL, ?, ?, ?)", (content, img, summary))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления новости в БД" + str(e))
            return False
        return True
    

    def updateStatus(self, title, content, status, id):
        try:
            self.__cur.execute(
                f"UPDATE posts SET title=?, content=?, status=? WHERE id=?", (title, content, status, id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления новости в БД: " + str(e))
            return False
        return True
    
    def updateUser(self, name, email, psw, id):
        try:
            self.__cur.execute(
                f"UPDATE users SET name=?, email=?, psw=? WHERE id=?", (name, email, psw, id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД: " + str(e))
            return False
        return True

    def updateTechn(self, title, content, id):
        try:
            self.__cur.execute(
                f"UPDATE technologies SET summary=?, content=? WHERE id=?", (title, content, id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления технологии в БД: " + str(e))
            return False
        return True
    
    def updateNewAndImg(self, content, img, summary, id):
        try:
            self.__cur.execute(
                f"UPDATE news SET content=?, img=?, summary=? WHERE id=?", (content, img, summary, id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления технологии в БД: " + str(e))
            return False
        return True
    
    def updateNew(self, content, summary, id):
        try:
            self.__cur.execute(
                f"UPDATE news SET content=?, summary=? WHERE id=?", (content,  summary, id ))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления технологии в БД: " + str(e))
            return False
        return True

    def getPost(self, postId):
        try:
            self.__cur.execute(
                f"SELECT title, content FROM posts WHERE id = {postId} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            # print("Ошибка получения статьи из БД "+str(e))
            return False
        return (False, False)

    def getNewsJSON(self):
        sql = '''SELECT * FROM news'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                blocks_list = [dict(ix) for ix in res]
                return blocks_list
        except:
            # print ('Ошибка чтения из бд')
            return False
        return []


    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(
                f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}' ")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False
            self.__cur.execute(
                "INSERT INTO users VALUES(NULL, ?, ?, ?, ?)", (name, email, hpsw, 0))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД "+str(e))
            return False
        return True
    
    def delUser(self, user_id):
        self.__cur.execute(
                f"DELETE FROM users WHERE id = {user_id}")
        self.__db.commit()
        return True
    
    def delPost(self, post_id):
        self.__cur.execute(
                f"DELETE FROM posts WHERE id = {post_id}")
        self.__db.commit()
        return True
    
    def getUser(self, user_id):
        try:
            self.__cur.execute(
                f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения из БД "+str(e))
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(
                f"SELECT * FROM users WHERE email= '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))
        return False

    def getAllUsers(self):
        try:
            self.__cur.execute(f"SELECT * FROM users")
            res = self.__cur.fetchall()
            print(res)
            if res:
                blocks_list = [dict(ix) for ix in res]
                print(blocks_list)
                return blocks_list

        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))
        return False

    def getUserPostsJSON(self, userId):
        try:
            self.__cur.execute(
                f"SELECT created, title, content, status FROM posts WHERE author = {userId} ")
            res = self.__cur.fetchall()
            if res:
                blocks_list = [dict(ix) for ix in res]
                return blocks_list
        except sqlite3.Error as e:
            return False
        return ()

