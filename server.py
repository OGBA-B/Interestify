from flask import Flask, json, jsonify, render_template, request
from flask_cors import CORS

import apitesting as api

app = Flask(
    __name__, static_folder="./client/build/static", template_folder="./client/build"
)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html", token="Sample Token")


@app.route("/search/<search_term>")
def search_tweets(search_term=None):
    return jsonify(api.get_popular_tweets(search_term))


@app.route("/followers/<screen_name>")
def get_followers(screen_name=None):
    return jsonify(api.get_followers(screen_name))


@app.route("/asearch/<screen_name>")
def test(screen_name=None):
    value = request.get_json()
    return str(value["name"])


if __name__ == "__main__":
    app.run(debug=True)
