#  Импортирем из flask раздел Flask
import os
import uuid
from random import random, choice

from flask import Flask, redirect, render_template, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from forms.login import LoginForm
from flask_login import LoginManager
from data import db_session
from forms.user import RegisterForm
from data.users import User
from forms.new_tovar import NewsForm
from data.tovar import News


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
login_manager = LoginManager()
login_manager.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def main():
    db_session.global_init("only progect/db/all.sqlite")

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)
    @app.route('/')
    def index():
        db_sess = db_session.create_session()
        news = db_sess.query(News)
        return render_template("index.html", news=news)

    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                surname=form.name.data,
                email=form.email.data,
                about=form.about.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    @app.route('/new_tovar', methods=['GET', 'POST'])
    @login_required
    def add_news():
        form = NewsForm()
        db_sess = db_session.create_session()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            news = News()

            # filename = secure_filename(file.filename)
            # image.save(os.path.join("static/img", filename))
            news.title = form.title.data
            shena = form.cena.data
            if not shena.isdigit():
                return render_template('new_tovar.html', title='Добавление новости',
                                       form=form, message='Ведите цену цифрами')

            news.content = shena
            news.cena = form.cena.data
            # print(form.cena.data)
            current_user.news.append(news)
            file = request.files['file']
            if file and allowed_file(file.filename):
                chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
                password = ''
                for n in range(1):
                    for i in range(25):
                        password += choice(chars)
                filename = secure_filename(file.filename)
                file.save(os.path.join('only progect/static/img', filename))
                k = password + '.' + filename.rsplit('.', 1)[1].lower()
                # print(k)
                os.rename(f'only progect/static/img/{filename}', f'only progect/static/img/{k}')
                # print('upload_image filename: ' + filename)
                flash('Image successfully uploaded and displayed below')
                news.filename = k
                db_sess.merge(current_user)
                db_sess.commit()
                return redirect('/')
        # if request.method == 'POST':
            # This will be executed on POST request.
            # file = request.files['file']
            # filename = secure_filename(file.filename)
            # file.save(os.path.join('static/img', filename))
        # flash('Image successfully uploaded and displayed below')
        # flash('Chena')
        return render_template('new_tovar.html', title='Добавление новости',
                                form=form)

    # app.run()



if __name__ == '__main__':
    main()
    app.run(port=8000, host='127.0.0.1')
