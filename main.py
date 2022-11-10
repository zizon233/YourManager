import os
import functools
import datetime
from pytz import timezone
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
import logging

from model.user import User
from model.room import Room
import model.chat
from form import RegisterationForm, LoginForm

import common

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
logger.addHandler(common.get_file_handler())

app = Flask(__name__, static_folder="templates/")
app.config["SECRET_KEY"] = os.urandom(24)
csrf = CSRFProtect(app)
SESSION_TYPE = "redis"
PERMANENT_SESSION_LIFETIME = 600
app.config.from_object(__name__)
Session(app)
socketio = SocketIO(
    app,
    cors_allowed_origins="http://3.132.24.2",
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
            disconnect2()
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

        if not common.verify_hash(
            user.passwd_hash + User.get_salt(user.user_id),
            User.get_passwd_hash(user.user_id),
        ):
            logger.info(f"{user.user_id} 로그인 실패(비밀번호 오류)")
            return render_template("index.html", form=form, response="비밀번호가 틀렸습니다.")

        logger.info(f"{user.user_id} 로그인 성공")
        login_user(user)

        return redirect("/chat")
    return render_template("index.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():

        passwd_hash, salt = common.make_hash(form.data.get("password"))

        user = User(
            form.data.get("user_id"),
            form.data.get("user_name"),
            passwd_hash,
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
    room_id = b"\xdf\x1f<[\xac\x91G]\x8e\xc3\x17\xc1E\xc5\xc6\xbf"
    room_message = model.chat.get_all_message(room_id)
    socketio.emit("room message", room_message)


@socketio.on("send message")
@authenticated_only
def send_message_event(message):
    current_time = datetime.datetime.now(timezone("Asia/Seoul")).strftime(
        "%Y-%m-%d %H:%M"
    )
    send_message = f"[{current_time}] {current_user.user_name} : {message}"
    logger.info(f"received message: {send_message}")
    model.chat.insert_new_message(
        current_time,
        current_user.user_id,
        b"\xdf\x1f<[\xac\x91G]\x8e\xc3\x17\xc1E\xc5\xc6\xbf",
        message,
    )
    socketio.emit("broad message", send_message, broadcast=True)


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
    logger.warning("test 종료되었습니다.")
    return emit("disconnect event", {"url": url_for("index")})


@socketio.event
def disconnect2():
    logger.warning("접근이 종료되었습니다.")
    return emit("disconnect event", {"url": url_for("index")})


# react-native
@socketio.on("react connect event")
def react_connect(data):
    logger.info(f"react connect.")


if __name__ == "__main__":
    socketio.run(app)
