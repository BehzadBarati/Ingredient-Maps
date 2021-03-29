# Authur: Behzad Barati

from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from appfunctions import *
import pandas as pd

# Create a Flask instance
app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    df = pd.DataFrame()
    if request.method == 'POST':
        searched_recipe = request.form['searched_recipe']
        exact = request.form['exact_search']
        searched_ner = request.form['searched_ner']
        if len(searched_ner):
            result, df = queryOnRecipeNer(searched_recipe, searched_ner, exact)
        else:    
            result, df = queryOnRecipe(searched_recipe, exact)
        minimal_wordcloud(result, 2)
        return render_template('searchResult.html', resultDetails = df)
    return render_template('index.html', resultDetails = df)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == "__main__":
    app.run(debug=True)



#@app.route('/searchResult/<keyword>')
#def search(keyword):
#    connection = sqlite3.connect(currentDirectory + "\database\\\\recipe.db")
#    cursor = connection.cursor()
#    query1 = "SELECT R.ID, R.tag_value FROM recipe R WHERE R.tag_value LIKE '%{0}%';".format(keyword)
#    resultValue = cursor.execute(query1)
#    resultDetails = resultValue.fetchall()
#    return render_template('searchResult.html', resultDetails = resultDetails)


#@app.route('/delete/<int:id>')
#def delete(id):
#    recipe_to_delete = Todo.query.get_or_404(id)
#    try:
#        db.session.delete(recipe_to_delete)
#        db.session.commit()
#        return redirect('/')
#    except:
#        return "There is a problem in deleting that recipe"


#@app.route('/', methods=['POST', 'GET'])
#def index():
#    if request.method == 'POST':
#        search_string = request.form['search_string']
#        return redirect(url_for('search', keyword = search_string))
#    return render_template('index.html', , resultDetails = resultDetails)


# Create a Form class
#class searchForm (FlaskForm):
#    searched_recipe = StringField("what recipe are you looking for?", validators=[DataRequired()])
#    searched_ner = StringField("what ingredient are you looking for?")
#    search = SubmitField("Search")
    
