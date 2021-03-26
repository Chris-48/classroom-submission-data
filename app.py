from flask import render_template
from flask import Flask
from flask import request
from flask_session import Session
from tempfile import mkdtemp


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    
    if request.method == "POST":
        pass
    else:
        return render_template("index.html")
