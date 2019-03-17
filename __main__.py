from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def home():
    return render_template("Hello World!")


if __name__ == "__main__.py":
    app.run(debug=True)
