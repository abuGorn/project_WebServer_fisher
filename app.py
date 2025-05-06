from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import requests
import random
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json


app = Flask(__name__)

try:
    countries_data = requests.get("https://restcountries.com/v3.1/all").json()
    with open("countries.json", "w") as f:
        json.dump(countries_data, f)
except Exception as e:
    print(e)
    with open("countries.json", "r") as f:
        countries_data = json.load(f)

app.config['SECRET_KEY'] = 'laisjdlkasdlknaskjdblakjsdqwiuheo124k2h53l456-0ppk;lm2lk34nlklksdlkhsdlkf'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "/login"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    correct_answers = db.Column(db.Integer)
    incorrect_answers = db.Column(db.Integer)
    current_correct_answer = db.Column(db.String(50))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует.')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            password=generate_password_hash(password=password),
            correct_answers=0,
            incorrect_answers=0
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно!')
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template("register.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))

        flash('Неверное имя пользователя или пароль.')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.')
    return redirect(url_for('login'))


def generate_random_country():
    while True:
        try:
            random_country = random.choice(countries_data)
            name = random_country["translations"]["rus"]["common"]
            population = random_country["population"]
            area = random_country["area"]
            capital = random_country["capital"][0]

            current_user.current_correct_answer = name

            db.session.add(current_user)
            db.session.commit()
            return name, population, area, capital
        except Exception as e:
            pass


@app.route('/')
@login_required
def index():
    name, population, area, capital = generate_random_country()

    return render_template(
        'index.html',
        population=population,
        area=area,
        capital=capital,
        user=current_user
    )


@app.route('/capitals')
@login_required
def capitals():
    return render_template('capitals.html')


@app.route('/check_country_answer', methods=['POST'])
@login_required
def check_country_answer():
    data = request.json
    user_answer_text = data.get("user_answer_text")

    if user_answer_text.lower() == current_user.current_correct_answer.lower():
        name, population, area, capital = generate_random_country()
        current_user.correct_answers += 1
        db.session.add(current_user)
        db.session.commit()
        return jsonify(
            success=True,
            result={
                "answer_result": "правильно",
                "population": population,
                "area": area,
                "capital": capital,
            }
        )
    elif len(user_answer_text) >= 4 and user_answer_text.lower() in current_user.current_correct_answer.lower():
        correct_answer = current_user.current_correct_answer
        name, population, area, capital = generate_random_country()
        return jsonify(
            success=True,
            result={
                "answer_result": "близко",
                "population": population,
                "area": area,
                "capital": capital,
                "name": correct_answer
            }
        )
    else:
        current_user.incorrect_answers += 1
        db.session.add(current_user)
        db.session.commit()
        return jsonify(
            success=False
        )


@app.route('/user_dont_know', methods=['POST'])
@login_required
def user_dont_know():
    name, population, area, capital = generate_random_country()
    current_user.correct_answers -= 1
    db.session.add(current_user)
    db.session.commit()
    return jsonify(
        success=True,
        result={
            "population": population,
            "area": area,
            "capital": capital,
        }
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
