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
from flask_socketio import SocketIO, send, emit
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

formatter = logging.Formatter(
    "[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] >> %(process)d %(message)s"
)

file_handler = RotatingFileHandler(
    "/home/ymadmin/YourManager/log/YourManager.log",
    maxBytes=256 * 1024 * 1024,
    backupCount=2,
)
file_handler.setFormatter(formatter)

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

app = Flask(__name__, static_folder="templates/")
app.config["SECRET_KEY"] = "manager"
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)
socketio = SocketIO(app)


@app.route("/")
def index():
    # logger.info(f'connect : {request.environ["HTTP_X_FORWARDED_FOR"]}')
    # logger.info(f"{request.host}")
    return render_template("index.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")


@socketio.on("my event")
def handle_my_custom_event(data):
    logger.info(f"received message: {data}")


@socketio.on("login")
def login(data):
    password = data["password"]
    logger.info(f"password : {password}")
    if password == "4321":
        logger.info("pass")
        return emit("redirect", {"url": url_for("chat")})
    return emit("redirect", {"url": url_for("index")})


if __name__ == "__main__":
    socketio.run(app)
