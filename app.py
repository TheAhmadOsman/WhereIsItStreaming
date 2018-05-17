from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import Required, InputRequired, Email, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from justwatch import JustWatch
import json
import query


app = Flask(__name__)
app.config['SECRET_KEY'] = "CS330FinalProject!"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[
        InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80)])

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class SearchCriteria(FlaskForm):
    search = StringField("", validators=[
                         InputRequired(), Length(max=30)])


def streaming(title="the matrix"):
    just_watch = JustWatch(country='US')
    results = just_watch.search_for_item(query='the matrix')

    providers = {2:  "iTunes", 10:  "Youtube", 68:  "Microsoft",
                 15:  "Hulu", 8:  "Netflix", 7:  "Vudu", 3:  "Google Play"}

    dct = {"rent": [], "buy": []}
    for item in results["items"][0]["offers"]:
        try:
            dct2 = {}
            dct2["provider"] = providers[item["provider_id"]]
            dct2["price"] = item["retail_price"]
            dct2["url"] = item["urls"]["standard_web"]
            dct[item["monetization_type"]].append(dct2)
        except:
            continue

    return dct


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('main'))
        else:
            return render_template('failed.html')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = Users(username=form.username.data,
                         email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/main", methods=['GET', 'POST'])
@login_required
def main():
    films = query.randomMovies()

    if len(films) >= 20:
        print(len(films))
        for item in films:
            if len(item["title"]) > 15:
                item["title"] = item["title"][:14] + "..."
    form = SearchCriteria()
    if form.validate_on_submit():
        search = str(form.search.data)
        films = query.returnFilm(search)
        if len(films) == 0:
            msg = "No results found for %s" % (search)
            return render_template("main.html", form=form)
        return render_template("main.html", films=films, form=form)
    return render_template("main.html", films=films, form=form)


@app.route("/movie", methods=["GET", "POST"])
@login_required
def movie():
    form = SearchCriteria()
    if form.validate_on_submit():
        search = str(form.search.data)
        films = query.returnFilm(search)
        if len(films) == 0:
            msg = "No results found for %s" % (search)
            return render_template("main.html", form=form)
        return render_template("main.html", films=films, form=form)

    movieid = int(request.args["id"])
    film = query.returnOneFilm(movieid)
    cast = query.returnCast(movieid)
    crew = query.returnCrew(movieid)
    ratings = ""
    ratings = query.returnRatings(movieid)
    return render_template("movie.html", form=form, film=film, cast=cast, crew=crew, ratings=ratings)


@app.route("/liked", methods=["GET", "POST"])
@login_required
def liked():
    form = SearchCriteria()
    if form.validate_on_submit():
        search = str(form.search.data)
        films = query.returnFilm(search)
        if len(films) == 0:
            msg = "No results found for %s" % (search)
            return render_template("main.html", form=form)
        return render_template("main.html", films=films, form=form)

    return render_template("liked.html", form=form)


@app.route("/viewed", methods=["GET", "POST"])
@login_required
def viewed():
    form = SearchCriteria()
    if form.validate_on_submit():
        search = str(form.search.data)
        films = query.returnFilm(search)
        if len(films) == 0:
            msg = "No results found for %s" % (search)
            return render_template("main.html", form=form)
        return render_template("main.html", films=films, form=form)

    return render_template("viewed.html")


@app.route("/searched", methods=["GET", "POST"])
@login_required
def searched():
    form = SearchCriteria()
    if form.validate_on_submit():
        search = str(form.search.data)
        films = query.returnFilm(search)
        if len(films) == 0:
            msg = "No results found for %s" % (search)
            return render_template("main.html", form=form)
        return render_template("main.html", films=films, form=form)

    return render_template("searched.html")


@app.route("/about", methods=["GET", "POST"])
@login_required
def about():
    form = SearchCriteria()
    if form.validate_on_submit():
        search = str(form.search.data)
        films = query.returnFilm(search)
        if len(films) == 0:
            msg = "No results found for %s" % (search)
            return render_template("main.html", form=form)
        return render_template("main.html", films=films, form=form)

    return render_template("about.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
