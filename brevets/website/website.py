import logging
import flask
import requests
import json
from urllib.parse import urlparse, urljoin
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, PasswordField, SubmitField, validators
from passlib.apps import custom_app_context as pwd_context
from flask import session

class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password = PasswordField('Password', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a password."),
        validators.InputRequired(u"Forget something?")])
    remember = BooleanField('Remember me')
    submit = SubmitField("Log In")

class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password = PasswordField('Password', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a password."),
        validators.InputRequired(u"Forget something?")])
    submit = SubmitField("Register")

def is_safe_url(target):
    """
    :source: https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


class User(UserMixin):
    def __init__(self, username, token):
        self.username = username
        self.token = token

    @property
    def id(self):
        return self.username

    def verify_password(self, password):
        return pwd_context.verify(password, self.token)

    @classmethod
    def new_user(cls, username, password):
        token = pwd_context.encrypt(password) #hash password and convert into token
        return cls(username, token)


app = Flask(__name__)
app.secret_key = "hello123#$5!"

app.config.from_object(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"


#return username id
@login_manager.user_loader
def load_user(username):
    url = 'http://restapi:5000/getUser/' + username
    r = requests.get(url)
    #check if user exists
    app.logger.debug("*"*50)
    app.logger.debug(r.text)
    app.logger.debug("*"*50)
    j = r.json()
    app.logger.debug(type(j))
    app.logger.debug(j)
    if not j: 
        return None
    app.logger.debug('username: %s, type: %s', username, type(username))
    u = User(j['username'], j['token']) #typeError: 'str' object not callable
    return u #load user


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', current_user=current_user)


@app.route('/listAll')
def listAll():
    dtype = request.args.get('json_or_csv', default='json')
    top = request.args.get('top').strip()
    url = 'http://restapi:5000/listAll/' + dtype
    if top != "":
        try:
            top=int(top)
        except ValueError as verr:
            abort(400, str(verr))
        url += f"?top={top}"
    r = requests.get(url)
    return flask.jsonify({"result": r.text})


@app.route('/listOpenOnly')
def listOpenOnly():
    dtype = request.args.get('json_or_csv', default='json')
    top = request.args.get('top').strip()
    url = 'http://restapi:5000/listOpenOnly/' + dtype
    if top != "":
        try:
            top=int(top)
        except ValueError as verr:
            abort(400, str(verr))
        url += f"?top={top}"
    r = requests.get(url)
    app.logger.debug(r)
    return flask.jsonify({"result": r.text})


@app.route('/listCloseOnly')
def listCloseOnly():
    dtype = request.args.get('json_or_csv', default='json')
    top = request.args.get('top').strip()
    url = 'http://restapi:5000/listCloseOnly/' + dtype
    if top != "":
        try:
            top=int(top)
        except ValueError as verr:
            abort(400, str(verr))
        url += f"?top={top}"
    r = requests.get(url)
    return flask.jsonify({"result": r.text})


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm(request.form)
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form:
        # Login and validate the user.
        # session['username'] = request.form['username']
        username = form.username.data
        password = form.password.data
        user = load_user(username)
        if not user:
            #redirect to registration page FIXME
            return flask.redirect("/register")
        if not user.verify_password(password):
            flash("Sorry, but you could not log in.")
        else:
            # user should be an instance of `User` class
            login_user(user)
            remember = flask.request.form.get("remember", "false") == "true"
            flask.flash('Logged in successfully.')
            flask.flash("I'll remember you") if remember else None

            next_ = flask.request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            if not is_safe_url(next_):
                return flask.abort(400)

            return flask.redirect(next_ or flask.url_for('index'))
    return flask.render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        # Login and validate the user.
        username = form.username.data
        password = form.password.data
        user = load_user(username)
        if user:
            flash("Username taken.")
        else:
            #encrypt password and make user object
            user = User.new_user(username, password)
            create_user(user)

            next_ = flask.request.args.get('next')
            return flask.redirect(next_ or flask.url_for('index'))
    return flask.render_template('register.html', form=form)

def create_user(user):
    url = 'http://restapi:5000/createUser/'
    r = requests.post(url, {"username": user.username, "token": user.token})

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    # remove the username from the session if it's there
    # session.pop('username', None)
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)