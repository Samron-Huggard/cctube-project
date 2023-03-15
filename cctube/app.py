import flask
import secrets
import main
from keys import client_id
from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)



@app.route("/")
def index():
    print("in index")

    if main.authorized is False:
        main.authorized = True
        return flask.redirect(main.authorization_url)

    # try:
    #     credentials = session["token"]
    #
    # except KeyError:
    #     return redirect(url_for('login'))

    authorization_response = flask.request.url
    main.flow.fetch_token(authorization_response=authorization_response)
    session["token"] = main.flow.credentials.token
    credentials = main.flow.credentials
    main.youtube = main.create_client(credentials=credentials)

    return render_template("index.html")


@app.route('/results', methods=["GET", "POST"])
def down_trans_up():
    main.get_captions(request.form["video_id"])
    return render_template("success.html")


@app.route('/login')
def login():
    print("in login")
    main.flow.redirect_uri = url_for('authorize')
    return flask.redirect(main.authorization_url)


@app.route("/authorize")
def authorize():
    print("in authorize")
    authorization_response = flask.request.url
    main.flow.fetch_token(authorization_response=authorization_response, client_id=client_id)
    token = main.flow.credentials.token
    session["token"] = token
    return redirect(url_for('index'))

