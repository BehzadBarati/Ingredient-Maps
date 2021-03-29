# Inspired by followings: 
# https://github.com/fenna/dashboard_ok_web
# https://www.youtube.com/watch?v=Z1RJmh_OqeA&t=269s
# https://www.youtube.com/watch?v=aWN1CqMtzIE&t=613s
# https://www.youtube.com/watch?v=6L3HNyXEais&t=125s

import os
import sqlite3
import pandas as pd
from PIL import Image
from wordcloud import WordCloud

currentDirectory = os.path.dirname(os.path.abspath(__file__))

def queryOnRecipe(searched_recipe, exact_search):
    
    #Inputs: keywords for searaching in recipes, boolean to indicate type of search
    #Output: list of tuples as result, grouped dataframe on recipes 
    
    if exact_search == '1':
        query = f"""SELECT R.ID, R.tag_value, N.tag_value 
                FROM recipe R 
                JOIN recipe_ner RN ON R.ID = RN.recipe_id
                JOIN ner N ON RN.ner_id = N.ID
                WHERE R.tag_value LIKE '%{searched_recipe}%';"""
    else:
        query = f"""SELECT R.ID, R.tag_value, N.tag_value 
                FROM recipe R 
                JOIN recipe_ner RN ON R.ID = RN.recipe_id
                JOIN ner N ON RN.ner_id = N.ID
                WHERE R.tag_value LIKE '%{searched_recipe.split(' ')[0]}%'"""
        if len(searched_recipe.split(' ')) > 1:
            for i in searched_recipe.split(' ')[1:]:
                query += f""" AND R.tag_value LIKE '%{i}%'"""
        query += """;"""

    print(query)
    connection = sqlite3.connect(currentDirectory + "\database\\\\recipe.db")
    cursor = connection.cursor()
    resultValue = cursor.execute(query)
    result = resultValue.fetchall()
    df = pd.DataFrame(result, columns=['recipe_id', 'recipe_name', 'ner_name'])
    df = df.groupby(['recipe_id', 'recipe_name'])['ner_name'].apply(list).reset_index()
    return result, df


def queryOnRecipeNer(searched_recipe, searched_ner, exact_search):
    
    #Inputs: keywords for searaching in recipes, boolean to indicate type of search
    #Output: list of tuples as result, grouped dataframe on recipes 
    
    # generate first query to find recipe ID match criteria

    if exact_search == '1':
        query1 = f"""SELECT R.ID 
                FROM recipe R 
                WHERE R.tag_value LIKE '%{searched_recipe}%'"""
    else:
        query1 = f"""SELECT R.ID 
                FROM recipe R 
                WHERE R.tag_value LIKE '%{searched_recipe.split(' ')[0]}%'"""
        if len(searched_recipe.split(' ')) > 1:
            for i in searched_recipe.split(' ')[1:]:
                query1 += f""" AND R.tag_value LIKE '%{i}%'"""
    
    query1 += f''' INTERSECT
                SELECT RN.recipe_id
                FROM recipe_ner RN
                JOIN ner N ON RN.ner_id = N.ID
                WHERE N.tag_value LIKE '%{searched_ner}%'
                '''
    #if len(searched_ner.split(' ')) > 1:
    #    for i in searched_ner.split(' ')[1:]:
    #        query1 += f"""AND N.tag_value LIKE '%{i}%'"""

    print(query1)
    connection = sqlite3.connect(currentDirectory + "\database\\\\recipe.db")
    cursor = connection.cursor()

    # generate second query
    query2 = f"""SELECT R.ID, R.tag_value, N.tag_value 
                FROM recipe R 
                JOIN recipe_ner RN ON R.ID = RN.recipe_id
                JOIN ner N ON RN.ner_id = N.ID
                WHERE R.ID IN ({query1});"""
    print(query2)

    # generate final results
    resultValue2 = cursor.execute(query2)
    result2 = resultValue2.fetchall()

    df = pd.DataFrame(result2, columns=['recipe_id', 'recipe_name', 'ner_name'])
    df = df.groupby(['recipe_id', 'recipe_name'])['ner_name'].apply(list).reset_index()
    return result2, df


# For creating word clouds, I used WordCloud library which was imported before.
def minimal_wordcloud(result, column):
    """
    Generate a simple wordcloud similar to: 
    https://www.kaggle.com/paultimothymooney/explore-recipe-nlg-dataset/data.
    The only import required is: from wordcloud import WordCloud
    """
    text = " ".join(row[column] for row in result)
    print(text[:100])
    wordcloud = WordCloud(background_color="white").generate(text)
    image = wordcloud.to_image()
    image.save("static/images/graph.png", "")