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
# Функция main()
# ----------------------------------------------------------------
# Создаем главную функцию
def main():
    # ----------------------------------------------------------------
    # Подгрузка пользователей
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
    # Оброботчик всех товаров
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
    # Оброботчик покупки
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция
    @app.route('/buy/<int:id>')
    def buy(id):
        # Создаем session
        db_sess = db_session.create_session()
        # Вызваем из базы днных нужные нам данные
        news = db_sess.query(News).filter(News.id == id)
        # Выводим эти данные
        return render_template("buy.html", title='Покупка', news=news)

    # ----------------------------------------------------------------
    # Оброботчик регистрации
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция
    @app.route('/register', methods=['GET', 'POST'])
    # Функция регистрации
    def reqister():
        form = RegisterForm()
        # проверка на заполненность всех форм
        if form.validate_on_submit():
            # проверка паролей
            if form.password.data != form.password_again.data:
                #если есть ошибка, то не даем идти дальше
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            # Создаем session
            db_sess = db_session.create_session()
            # Вызваем из базы днных нужные нам данные и проверяем если таокй челлвек или нет
            if db_sess.query(User).filter(User.email == form.email.data).first():
                #возвращаем, что такой пользователь уже есть
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                surname=form.name.data,
                email=form.email.data,
                about=form.about.data
            )
            #ставим пароль
            user.set_password(form.password.data)
            #добавляем пользователя
            db_sess.add(user)
            #  коментим базу данных
            db_sess.commit()
            # переводим на страницу логина
            return redirect('/login')
        #переводим на регистрацию
        return render_template('register.html', title='Регистрация', form=form)

    # ----------------------------------------------------------------
    #обработчик удаления
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и удаляля товары

    @app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def news_delete(id):
        # Создаем session
        db_sess = db_session.create_session()
        # Вызываем из базы данных нужные нам данные
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        #если есть товар, то удаляем
        if news:
            # удаляем товар
            db_sess.delete(news)
            # комментим базу данных
            db_sess.commit()
        else:
            # если нет товара, то ошибка 404
            abort(404)
        # Возвращаем мои товары
        return redirect('/my_tovar')

    # ----------------------------------------------------------------
    # обработчик редактирования
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и мы могли редактировать товар
    @app.route('/red/<int:id>', methods=['GET', 'POST'])
    @login_required
    # функция редактирования
    def edit_news(id):
        # Вызываем форму редактирования
        form = NewsForm()
        # проверяем если метод get
        if request.method == "GET":
            # Создаем session
            db_sess = db_session.create_session()
            # Вызваем из базы днных нужные нам данные
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
            # Если есть товар:
            if news:
                # Ставим название
                form.title.data = news.title
                # Ставим описание
                form.content.data = news.content
                # Ставим цену
                form.cena.data = news.cena
            # Если товара нет:
            else:
                # Ошибка 404
                abort(404)
        # Если все формы заполненны
        if form.validate_on_submit():
            # Создаем session
            db_sess = db_session.create_session()
            # Вызываем из базы данных нужные нам данные
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
            # если такая новость есть
            if news:
                # ставим новое название
                news.title = form.title.data
                # ставим новое описание
                news.content = form.content.data
                # ставим новые цены
                shena = form.cena.data
                # если в цене буквы
                if not shena.isdigit():
                    # просим ввести только цифры
                    return render_template('red.html', title='Редактирование товара',
                                           form=form, message='Ведите цену цифрами')

                # вводим новое описание
                news.content = form.content.data
                # ставим новую цену
                news.cena = form.cena.data
                # комментим
                db_sess.commit()
                # выводим новые товары
                return redirect('/my_tovar')
            # если нет, то
            else:
                # выводим 404
                abort(404)
        # возвращение товара
        return render_template('red.html',
                               title='Редактирование товара',
                               form=form
                               )

    # ----------------------------------------------------------------
    # функция логина
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
    # функция выхода
    # ----------------------------------------------------------------

    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и мы могли выйти
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    # ----------------------------------------------------------------
    # функция на готовность покупки
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и мы аокупаем
    @app.route('/ready')
    def ready():
        return render_template('ready.html')

    # ----------------------------------------------------------------
    # ПАСХАЛКА!!!!!!
    # ----------------------------------------------------------------
    # C помощью декоратора делаем так чтоб при открыти на сайте вызывалась эта фукнкция и открывалсь пасхалка
    @app.route('/pashalka')
    def pashalka():
        return render_template('pashalka.html')

    # ----------------------------------------------------------------
    # вкладка мои товары
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
    # Добавление новых товаров
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
                # шифрование названия фото
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
                # Шифруем название фото
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
