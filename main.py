import os
import functools
import secrets
from passlib.hash import pbkdf2_sha256
from flask import (
    Flask,
    has_request_context,
    request,
    render_template,
    session,
    redirect,
    url_for,
)
from flask_session import Session
from flask_login import login_user, logout_user, current_user, LoginManager
from flask_socketio import SocketIO, send, emit, disconnect
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
import logging

from model.user import User
from form import RegisterationForm, LoginForm

import common

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
logger.addHandler(common.get_file_handler())

app = Flask(__name__, static_folder="templates/")
app.config["SECRET_KEY"] = os.urandom(24)
csrf = CSRFProtect(app)
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)
socketio = SocketIO(
    app,
    cors_allowed_origins="http://ec2-3-23-132-5.us-east-2.compute.amazonaws.com",
    manage_session=False,
)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user = User(user_id)
    user.load()
    return user


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


@app.route("/", methods=["GET", "POST"])
def index():
    logger.info(f'connect : {request.environ["HTTP_X_FORWARDED_FOR"]}')
    form = LoginForm()
    if form.validate_on_submit():

        user = User(
            form.data.get("user_id"),
            passwd_hash=form.data.get("password"),
        )

        if not user.check_user_exist():
            logger.info(f"{user.user_id} 로그인 실패(없는 아이디)")
            return render_template("index.html", form=form, response="존재하지 않는 아이디입니다.")

        if not pbkdf2_sha256.verify(
            user.passwd_hash + User.get_salt(user.user_id),
            User.get_passwd_hash(user.user_id),
        ):
            logger.info(f"{user.user_id} 로그인 실패(비밀번호 오류)")
            return render_template("index.html", form=form, response="비밀번호가 틀렸습니다.")

        logger.info(user.is_authenticated())

        logger.info(f"{user.user_id} 로그인 성공")
        login_user(user)

        return redirect("/chat")
    return render_template("index.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():

        salt = str(secrets.SystemRandom().getrandbits(128))

        user = User(
            form.data.get("user_id"),
            form.data.get("user_name"),
            pbkdf2_sha256.hash(form.data.get("password") + salt),
            salt,
        )

        if user.check_user_exist():
            logger.info(f"{user.user_id} was already registered.")
            return render_template("registeration.html", form=form)

        user.register()

        return redirect("/")

    return render_template("registeration.html", form=form)


@app.route("/chat")
@authenticated_only
def chat():
    user_data = {
        "user_id": current_user.user_id,
        "user_name": current_user.user_name,
        "email": current_user.email,
    }
    return render_template("chat.html", user=user_data)


@socketio.on("connect event")
@authenticated_only
def connect_event(data):
    logger.info(f"{data}")
    user_data = {
        "user_id": current_user.user_id,
        "user_name": current_user.user_name,
        "email": current_user.email,
    }
    socketio.emit("enter user", user_data, broadcast=True)


@socketio.on("send message")
@authenticated_only
def send_message_event(message):
    message = f"{current_user.user_name} : {message}"
    logger.info(f"received message: {message}")
    # 대화 저장 로직
    socketio.emit("broad message", message, broadcast=True)


@socketio.on("disconnect event")
@authenticated_only
def disconnect_event():
    logger.info(f"disconnect request.")
    user_data = {
        "user_id": current_user.user_id,
        "user_name": current_user.user_name,
        "email": current_user.email,
    }
    socketio.emit("quit user", user_data, broadcast=True)
    logout_user()
    return emit("disconnect event", {"url": url_for("index")})


@socketio.event
def disconnect():
    logger.warning("로그인 없이 접근하였습니다.")
    return emit("disconnect event", {"url": url_for("index")})


if __name__ == "__main__":
    socketio.run(app)
