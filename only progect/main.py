# ----------------------------------------------------------------
# Основные импорты
# ----------------------------------------------------------------
# Импортируем os
import os
# Импортируем uuid
import uuid
# Импортируем random, choice
from random import random, choice
#  Импортирем из flask раздел Flask, redirect, render_template, request, flash, abort
from flask import Flask, redirect, render_template, request, flash, abort
#  Импортирем из flask_login раздел login_user, login_required, logout_user, current_user
from flask_login import login_user, login_required, logout_user, current_user
# Импортирем secure_filename из werkzeug.utils
from werkzeug.utils import secure_filename
# Импортирем LoginForm
from forms.login import LoginForm
# Импортирем LoginManager из flask_login
from flask_login import LoginManager
# Импортирем db_session
from data import db_session
# Импортирем RegisterForm
from forms.user import RegisterForm
# Импортирем User
from data.users import User
# Импортирем NewsForm
from forms.new_tovar import NewsForm
# Импортирем adressForm
from forms.adress import adressForm
# Импортирем News
from data.tovar import News
# Импортирем Adr
from data.adres import Adr
# ----------------------------------------------------------------
#  Основные переменные
# ----------------------------------------------------------------

# Создаем app
app = Flask(__name__)
# Выставляем app config
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# Сделаем все расширени которы могут быть доступнее
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
# Вызываем login_manager
login_manager = LoginManager()
# Инициирум app
login_manager.init_app(app)
# ----------------------------------------------------------------
#  Функция allowef_file
# ----------------------------------------------------------------
# Создаем функцию allowed_file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# ----------------------------------------------------------------
#
# ----------------------------------------------------------------
# Создаем главную функцию
def main():
    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    #  Вызываем базу данных
    db_session.global_init("only progect/db/all.sqlite")
    # Подгружем пользоватлей
    @login_manager.user_loader
    # Создаем функцию load_user
    def load_user(user_id):
        # Создаем session
        db_sess = db_session.create_session()
        # Возвращем пользователей
        return db_sess.query(User).get(user_id)

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция
    @app.route('/')
    def index():
        # Создаем session
        db_sess = db_session.create_session()
        # Вызваем из базы днных нужные нам данные
        news = db_sess.query(News)
        # print(news)
        return render_template("index.html", news=news, title='Velociraptor     Village')

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция
    @app.route('/buy/<int:id>')
    def buy(id):
        # Создаем session
        db_sess = db_session.create_session()
        # Вызваем из базы днных нужные нам данные
        news = db_sess.query(News).filter(News.id == id, News.user == current_user)
        return render_template("buy.html", title='Покупка', news=news)

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция
    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            # Создаем session
            db_sess = db_session.create_session()
            # Вызваем из базы днных нужные нам данные и проверяем если таокй челлвек или нет
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

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и удаляля товары

    @app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def news_delete(id):
        # Создаем session
        db_sess = db_session.create_session()
        # Вызваем из базы днных нужные нам данные
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            db_sess.delete(news)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/my_tovar')

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и мы могли редактировать товар
    @app.route('/red/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_news(id):
        form = NewsForm()
        if request.method == "GET":
            # Создаем session
            db_sess = db_session.create_session()
            # Вызваем из базы днных нужные нам данные
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
            if news:
                form.title.data = news.title
                form.content.data = news.content
                form.cena.data = news.cena
            else:
                abort(404)
        if form.validate_on_submit():
            # Создаем session
            db_sess = db_session.create_session()
            # Вызваем из базы днных нужные нам данные
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
            if news:
                news.title = form.title.data
                news.content = form.content.data
                shena = form.cena.data
                if not shena.isdigit():
                    return render_template('red.html', title='Редактирование товара',
                                           form=form, message='Ведите цену цифрами')

                news.content = form.content.data
                news.cena = form.cena.data
                db_sess.commit()
                return redirect('/my_tovar')
            else:
                abort(404)
        return render_template('red.html',
                               title='Редактирование новости',
                               form=form
                               )

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и можно было залогиниться
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            # Создаем session
            db_sess = db_session.create_session()
            # Вызваем из базы днных нужные нам данные
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------

    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и мы могли выйти
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и мы аокупаем
    @app.route('/ready')
    def ready():
        return render_template('ready.html')

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и открывалсь пасхалка
    @app.route('/pashalka')
    def pashalka():
        return render_template('pashalka.html')

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и отображались мои товары
    @app.route('/my_tovar')
    def my_tovar():
        # Создаем session
        db_sess = db_session.create_session()
        # Вызваем из базы днных нужные нам данные
        news = db_sess.query(News).filter(News.user == current_user)
        return render_template("my_tovar.html", title='Мои товары', news=news)

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и мы могли создать свой новый товар
    @app.route('/new_tovar', methods=['GET', 'POST'])
    @login_required
    def add_news():
        form = NewsForm()
        # Создаем session
        db_sess = db_session.create_session()
        # Проверяем все ли поля запоннины
        if form.validate_on_submit():
            # Создаем session
            db_sess = db_session.create_session()
            # Вызываем News
            news = News()

            # filename = secure_filename(file.filename)
            # image.save(os.path.join("static/img", filename))
            # Добавляем в базу данных название товара
            news.title = form.title.data
            # Добываем цену товара
            shena = form.cena.data
            # Если в цене есть буквы то
            if not shena.isdigit():
                # Просим вести его цифрами
                return render_template('new_tovar.html', title='Добавление товара',
                                       form=form, message='Ведите цену цифрами')
            # Добавляем в базу данных описание товара
            news.content = form.content.data
            # Добавляем в базу данных цену
            news.cena = form.cena.data
            # print(form.cena.data)
            # Добавляем в базу данных автора
            current_user.news.append(news)
            # Запращиваем файл
            file = request.files['file']
            # Проверяем и если все ок то
            if file and allowed_file(file.filename):
                # ----------------------------------------------------------------
                #
                # ----------------------------------------------------------------
                chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
                password = ''
                for n in range(1):
                    for i in range(25):
                        password += choice(chars)
                filename = secure_filename(file.filename)
                # Сохраняем фото
                file.save(os.path.join('only progect/static/img', filename))
                # print(filename)
                # Шифрум название фото
                k = password + '.' + filename.rsplit('.', 1)[0].lower()
                # print(k)
                # Пременоваваем файт
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
        return render_template('new_tovar.html', title='Добавление товара',
                                form=form)

    # app.run()


# Запускаем наше приложение
if __name__ == '__main__':
    # Вызываем функцию main
    main()
    # Запускаем сайт
    app.run(port=8000, host='127.0.0.1')
