import sqlite3
import os
from flask import Flask, render_template, make_response, request, url_for, flash, redirect, g
from DataBase import DataBase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

DATABASE = '/tmp/database.db'
DEBUG = True
SECRET_KEY = 'gadsgsf123&81230><asd,'
MAX_CONTENT_LENGTH = 1024*1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'database.db')))
path_to_save_images = os.path.join(app.root_path, 'static', 'img')
app.config['MAIL_SERVER'] = 'smtp.mail.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'elizavetka.manakova02@mail.ru'
app.config['MAIL_PASSWORD'] = 'ye1EbqfYnpdtPgayBKT6'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = DataBase(db)


login_manager = LoginManager(app)


@login_manager.user_loader  # Загрузка пользователя
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'], check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.route("/get_all_users")
@login_required
def get_all_users():
    res = dbase.getAllUsers()
    return render_template(
        'all_users.html',
        data=res,
        user_name=current_user.get_name(),
        is_admin=int(current_user.get_admin())
    )


@app.route('/register', methods=['POST', 'GET'])
@login_required
def register():
    if request.method == "POST":
        if request.form['psw'] == request.form['psw2']:
            res = dbase.addUser(
                request.form['name'], request.form['email'], request.form['psw'])
            if res:
                return redirect(url_for('get_all_users'))
    return render_template('register.html', is_admin=int(current_user.get_admin()))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and (user['psw'] == request.form['psw']):
            userLogin = UserLogin().create(user)
            login_user(userLogin)
            return redirect(url_for('post_admin'))

        elif not user:
            flash('Пользователь не найден', category='error')
    return render_template("login.html", menu=dbase.getMenu())


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/")
def index():
    path1 = url_for('static', filename='img/ruk.jpg')
    path6 = url_for('static', filename='img/photo-1461749280684-dccba630e2f6.jpeg')
    path7 = url_for('static', filename='img/photo-1478432780021-b8d273730d8c.jpeg')
    path8 = url_for('static', filename='img/photo-1485579149621-3123dd979885.jpeg')
    path9 = url_for('static', filename='img/photo-1496065187959-7f07b8353c55.jpeg')
    path10 = url_for('static', filename='img/photo-1496171367470-9ed9a91ea931.jpeg')
    
    is_admin = None
    if str(current_user.is_authenticated) != 'False':
        is_admin = int(current_user.get_admin())
    else:
        is_admin = None
    return render_template(
        'index.html',
        res = dbase.getNewsJSON(),
        tecnol=dbase.getTechnJSON(),
        posts=dbase.getJSON(),
        path1=path1,
        path6=path6,
        path7=path7,
        path8=path8,
        pat9=path9,
        path10=path10,
      
        auth_user=str(current_user.is_authenticated),
        is_admin=is_admin
    )

@app.route('/send_mail', methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':
        msg = Message("Обратная связь", sender='elizavetka.manakova02@mail.ru', recipients=[request.form['email']])
        msg.body = request.form['text']
        mail.send(msg)
    return render_template('mail.html')


@app.route('/post_admin', methods=["POST", "GET"])
@login_required
def post_admin():
    data = None
    if int(current_user.get_admin()) == 1:
        data = dbase.getJSON()
        if request.method == "POST":
            res = dbase.updateStatus(
                request.form['title'], 
                request.form['content'], 
                request.form['status'], 
                request.form['id']
            )
            return redirect(url_for('post_admin'))
    else:
        data = dbase.getUserPostsJSON(current_user.get_id())

    res = dbase.getAllUsers()
    return render_template(
        "post_admin.html",
        posts=data,
        res=res,
        user_name=current_user.get_name(),
        is_admin=int(current_user.get_admin())
    )


@app.route("/add_post", methods=["POST", "GET"])
@login_required
def addPost():
    if request.method == "POST":
        res = None
        if int(current_user.get_admin()) == 1:
            res = dbase.addPost(
                request.form['title'], request.form['content'], current_user.get_id(), 'public')
        else:
            res = dbase.addPost(
                request.form['title'], request.form['content'], current_user.get_id(), 'draft')
        if not res:
            flash('Ошибка добавления статьи', category='error')
        else:
            flash('Статья добавлена успешно', category='success')
            return redirect(url_for('post_admin'))
    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/update_status", methods=["POST", "GET"])
@login_required
def updateStatus():
    tmp = None
    menu = None
    if int(current_user.get_admin()) == 1:
        tmp = 'admin.html'
        menu = dbase.getJSON()
        if request.method == "POST":
            res = dbase.updateStatus(
                request.form['title'], request.form['content'], request.form['status'], request.form['id'])
            if not res:
                flash('Ошибка обновления статуса', category='error')
            else:
                flash('Статус успешно обновлен', category='success')
    else:
        tmp = 'error_admin.html'
    return render_template(tmp, menu=menu)


@app.route("/tech_admin", methods=["POST", "GET"])
@login_required
def tech_admin():
    if request.method == "POST":
        res = dbase.updateTechn(
            request.form['summary'], request.form['content'], request.form['id'])
        if not res:
            flash('Ошибка добавления статьи', category='error')
        else:
            flash('Статья добавлена успешно', category='success')
    return render_template(
        'technol_admin.html',
        posts=dbase.getTechnJSON(),
        user_name=current_user.get_name(),
        is_admin=int(current_user.get_admin())
    )


@app.route("/add_tech", methods=["POST", "GET"])
@login_required
def addTech():
    if request.method == "POST":
        res = None
        if int(current_user.get_admin()) == 1:
            res = dbase.addTech(request.form['summary'], request.form['content'])     
        if not res:
            flash('Ошибка добавления статьи', category='error')
        else:
            flash('Статья добавлена успешно', category='success')
            return redirect(url_for('tech_admin')) 
    return render_template('add_tech.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/news_admin", methods=['GET'])
@login_required
def news_admin():
    if int(current_user.get_admin()) == 1:
        res = dbase.getNewsJSON()
        return render_template(
            "news_admin.html", 
            posts=res,
            user_name=current_user.get_name(),
            is_admin=int(current_user.get_admin())
        )
    
@app.route("/update_user/<int:pk>", methods=["POST", "GET"])
def update_user(pk):
    if request.method == "POST":
        res = dbase.updateUser(
            request.form['name'],
            request.form['email'],
            request.form['psw'],
            pk
        )
        if not res:
            flash('Ошибка добавления статьи', category='error')
        else:
            flash('Статья добавлена успешно', category='success')
        return redirect(url_for('get_all_users'))
    return render_template(
            'update_user.html',
            post = dbase.getUser(pk),
            is_admin=int(current_user.get_admin())
        )

@app.route("/del_user/<int:pk>", methods=['GET'])
def del_user(pk):
    res = dbase.delUser(pk)
    return redirect(url_for('get_all_users')) 

@app.route("/del_post/<int:pk>", methods=['GET'])
def del_post(pk):
    res = dbase.delPost(pk)
    return redirect(url_for('post_admin')) 

@app.route("/add_new", methods=["POST", "GET"])
@login_required
def addNew():
    if request.method == "POST":
        res = None
        if int(current_user.get_admin()) == 1:
            content = request.form['content']
            summary = request.form['summary']
            file = request.files['img']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(path_to_save_images, filename)
                imgpath = "/static/img/"+filename
                file.save(save_path)
            res = dbase.addNew(content, imgpath, summary)
        if not res:
            flash('Ошибка добавления новости', category='error')
        else:
            flash('Новость добавлена успешно', category='success')
            return redirect(url_for('news_admin')) 
    return render_template('add_new.html')


@app.route("/updateNew", methods=['POST'])
@login_required
def updateNew():
    if int(current_user.get_admin()) == 1:
        new_id = request.form['id']
        content = request.form['content']
        summary = request.form['summary']
        print(content, summary)
        file = request.files['img']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(path_to_save_images, filename)
            imgpath = "/static/img/"+filename
            file.save(save_path)
        if file:
            dbase.updateNewAndImg(content, imgpath, summary, new_id)
        else:
            dbase.updateNew(content,summary, new_id)
        return redirect(url_for('news_admin'))


if __name__ == "__main__":
    app.run(debug=True)

""" 
4) Обратный запрос 

5) Адаптив
6) Деплой 

"""
