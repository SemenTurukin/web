from flask import Flask, render_template, request, redirect
from cloudipsp import Api, Checkout
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data.users import User
from data import db_session, Item
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user
import telebot
import random


ID = "1058673144"
TOKEN = "1711327567:AAEUeEZ98N0T_zdei8XAECaXPxl1hy_NpG4"
app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)


login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/')
def index():
    db_sess = db_session.create_session()
    items = db_sess.query(Item.Item).all()
    return render_template('index.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/buy/<int:id>')
@login_required
def item_buy(id):
    db_sess = db_session.create_session()
    item = db_sess.query(Item.Item).all()

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    sum = 0
    for i in item:
        sum += i.price
    data = {
        "currency": "RUB",
        "amount": str(sum) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    number = random.randint(1, 10000)
    order_number("Заказ с номером " + str(number) + " оплачен")
    return redirect(url)


@app.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        db_ses = db_session.create_session()
        item = Item.Item(title=title, price=price)

        try:
            db_ses.add(item)
            db_ses.commit()
            return redirect('/')
        except:
            return "Получилась ошибка"
    else:
        return render_template('create.html')


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

def order_number(text):
    bot.send_message(ID, text)


if __name__ == "__main__":
    db_session.global_init("db/product.db")
    app.run()