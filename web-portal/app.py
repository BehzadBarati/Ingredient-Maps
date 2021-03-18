# Authur: Behzad Barati
# 
# Inspired by followings: 
# https://github.com/fenna/dashboard_ok_web
# https://www.youtube.com/watch?v=Z1RJmh_OqeA&t=269s
# https://www.youtube.com/watch?v=aWN1CqMtzIE&t=613s 

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#Create a Flask instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql:///user.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rec = db.Column(db.String(200), nullable=False)
    ner = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        recipe_name = request.form['rec']
        ner_name = request.form['ner']
        new_task = Todo(rec = recipe_name, ner=ner_name)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There is an issue in adding recipe'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks= tasks)

app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['search_string']
        search = "%{0}%".format(search_value)
        #results = Todo.query.order_by(Todo.date_created).all()
        results = Todo.query.filter(Todo.rec.like(search)).all()
        print(results)
        return render_template('index.html', tasks = results)
    else:
        return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    recipe_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(recipe_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There is a problem in deleting that recipe"


if __name__ == "__main__":
    app.run(debug=True)