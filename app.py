from flask import Flask, Blueprint, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku

from forms import ArticleForm, EditArticleForm, RemoveArticleForm

import sys
from copy import copy
import json

app = Flask(__name__, static_url_path="/static")
app.secret_key = "lkj()984kljl;:LKJF?.a<faskdjkl"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

heroku = Heroku(app)
db = SQLAlchemy(app)

class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text())
    date = db.Column(db.Text())
    author = db.Column(db.Text())
    image = db.Column(db.Text())
    caption = db.Column(db.Text())
    location = db.Column(db.Text())
    article = db.Column(db.Text())

    def __repr__(self):
        return self.title

    def __init__(self, data):
        self.title = data['title']
        self.date = data['date']
        self.author = data['author']
        self.image = data['image']
        self.caption = data['caption']
        self.location = data['location']
        self.article = data['article']

#managing articles in the database
manager = Blueprint("manager", __name__, template_folder='templates')
def get_credential_name():
    return "test"
def get_credential_password():
    return "test"

@manager.route("/manage/", methods=["GET", "POST"])
def manage():
    return render_template("/manage.html")

@manager.route("/view_articles/")
def view_articles():
    data = Article.query.order_by(Article.id).all()
    return render_template("view_articles.html", articles=data)

@manager.route("/add_article/", methods=["GET", "POST"])
def add_article():
    form = ArticleForm()
    if form.validate_on_submit():
        if form.name.data != get_credential_name() or form.password.data != get_credential_password():
            return render_template("/add_article.html", form=form)
        indata = Article(form.data)
        data = copy(indata.__dict__)
        del data["_sa_instance_state"]
        try:
            db.session.add(indata)
            db.session.commit()
        except Exception as e:
            print("\n FAILED entry: {}\n".format(json.dumps(data)))
            print(e)
            sys.stdout.flush()
            return redirect(url_for("manager.errors", errors="\n FAILED entry: {}\n".format(json.dumps(data))))
        return redirect(url_for("manager.success"))
    return render_template("/add_article.html", form=form)

@manager.route("/edit_article/", methods=["GET", "POST"])
def edit_article():
    form = EditArticleForm()
    if form.validate_on_submit():
        if form.name.data != get_credential_name() or form.password.data != get_credential_password():
            return render_template("/edit_article.html", form=form)
        try:
            article = Article.query.get(form.id.data)
            for key in form.data:
                if key != "id" and key != "csrf_token" and form[key].data != "" and form[key].data != None:
                    setattr(article, key, form[key].data)
            db.session.commit()
        except Exception as e:
            print("\n FAILED entry: {}\n".format(json.dumps(form.data)))
            print(e)
            sys.stdout.flush()
            return redirect(url_for("manager.errors", errors="\n FAILED entry: {}\n".format(json.dumps(form.data))))
        return redirect(url_for("manager.success"))
    return render_template("/edit_article.html", form=form)

@manager.route("/remove_article/", methods=["GET", "POST"])
def remove_article():
    form = RemoveArticleForm()
    if form.validate_on_submit():
        if form.name.data != get_credential_name() or form.password.data != get_credential_password():
            return render_template("/remove_article.html", form=form)
        try:
            article = Article.query.get(form.id.data)
            db.session.delete(article)
            decrements = Article.query.filter(Article.id > form.id.data).order_by(Article.id.asc())
            for item in decrements:
                item.id -= 1
            db.session.commit()
        except Exception as e:
            print("\n FAILED entry: {}\n".format(json.dumps(form.data)))
            print(e)
            sys.stdout.flush()
            return redirect(url_for("manager.errors", errors="\n FAILED entry: {}\n".format(json.dumps(form.data))))
        return redirect(url_for("manager.success"))
    return render_template("/remove_article.html", form=form)

@manager.route("/success/", methods=["GET"])
def success():
    return render_template("/success.html")

@manager.route("/errors/", methods=["GET"])
def errors():
    problems = request.args.get("errors")
    return render_template("/errors.html", errors=problems)

app.register_blueprint(manager)

if __name__ == '__main__':
    app.debug = True
    app.run()
