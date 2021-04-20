# Inspired by followings: 
# https://github.com/fenna/dashboard_ok_web
# https://www.youtube.com/watch?v=Z1RJmh_OqeA&t=269s
# https://www.youtube.com/watch?v=aWN1CqMtzIE&t=613s
# https://www.youtube.com/watch?v=6L3HNyXEais&t=125s

import os
import sqlite3
import numpy as np
import pandas as pd
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt


currentDirectory = os.path.dirname(os.path.abspath(__file__))

def DBInitializer():

    #Inputs: None ()
    #Output: None (make views/index for DB, view name:view_table1)

    connection = sqlite3.connect(currentDirectory + "\database\\\\recipe.db")
    cursor = connection.cursor()

    query1 = f"""CREATE INDEX IF NOT EXISTS iNer ON ner(ID);"""
    cursor.execute(query1)

    query2 = f"""CREATE INDEX IF NOT EXISTS iRecipe ON recipe(ID);"""
    cursor.execute(query2)

    query3 = f"""CREATE INDEX IF NOT EXISTS iStep ON step(ID);"""
    cursor.execute(query3)

    query4 = f"""CREATE VIEW IF NOT EXISTS view_table1 AS
                SELECT R.ID, R.tag_value AS Recipes, N.tag_value AS Ingredients 
                FROM recipe R 
                JOIN recipe_ner RN ON R.ID = RN.recipe_id
                JOIN ner N ON RN.ner_id = N.ID;"""
    cursor.execute(query4)


def queryOnRecipe(searched_recipe, exact_search):
    
    #Inputs: keywords for searaching in recipes, boolean to indicate type of search
    #Output: list of tuples as result, grouped dataframe on recipes 
    
    if exact_search == '1':
        query = f"""SELECT *
                FROM view_table1
                WHERE Recipes LIKE '%{searched_recipe}%';"""
    else:
        query = f"""SELECT *
                FROM view_table1
                WHERE Recipes LIKE '%{searched_recipe.split(' ')[0]}%'"""
        if len(searched_recipe.split(' ')) > 1:
            for i in searched_recipe.split(' ')[1:]:
                query += f""" AND Recipes LIKE '%{i}%'"""
        query += """;"""

    print(query)
    connection = sqlite3.connect(currentDirectory + "\database\\\\recipe.db")
    cursor = connection.cursor()
    resultValue = cursor.execute(query)
    result = resultValue.fetchall()
    df = pd.DataFrame(result, columns=['ID', 'Recipes', 'Ingredients'])
    df = df.groupby(['ID', 'Recipes'])['Ingredients'].apply(list).reset_index()
    
    return result, df


def queryOnRecipeNer(searched_recipe, searched_ner, exact_search):
    
    #Inputs: keywords for searaching in recipes, boolean to indicate type of search
    #Output: list of tuples as result, grouped dataframe on recipes 
    
    # generate first query to find recipe ID match criteria

    if exact_search == '1':
        query1 = f"""SELECT ID 
                FROM view_table1 
                WHERE Recipes LIKE '%{searched_recipe}%'"""
    else:
        query1 = f"""SELECT ID 
                FROM view_table1 
                WHERE Recipes LIKE '%{searched_recipe.split(' ')[0]}%'"""
        if len(searched_recipe.split(' ')) > 1:
            for i in searched_recipe.split(' ')[1:]:
                query1 += f""" AND Recipes LIKE '%{i}%'"""
    
    query1 += f'''
                AND Ingredients LIKE '%{searched_ner}%' ;
                '''
    
    connection = sqlite3.connect(currentDirectory + "\database\\\\recipe.db")
    cursor = connection.cursor()
    resultValue1 = cursor.execute(query1)
    result1 = resultValue1.fetchall()
    result1 = tuple(sum(result1, ()))

    # generate second query
    query2 = f"""SELECT *
                FROM view_table1 
                WHERE ID IN {result1};"""

    print(query2)

    # generate final results
    cursor = connection.cursor()
    resultValue2 = cursor.execute(query2)
    result2 = resultValue2.fetchall()
    df = pd.DataFrame(result2, columns=['ID', 'Recipes', 'Ingredients'])
    df = df.groupby(['ID', 'Recipes'])['Ingredients'].apply(list).reset_index()
    
    return result2, df


def searchsummary(l, df):

    # a function for processing dataframe. output is a list of items as follow:
    # 0: what we were looking for
    # 1: Number of found recipes
    # 2: recipe with max ingredients
    # 3: recipe with min ingredients
    
    summary = []
    #0
    summary.append(l)
    #1
    summary.append(df.shape[0])
    field_length = df['Ingredients'].astype(str).map(len)
    #2
    summary.append(df.loc[field_length.argmax(), 'ID'])
    #3
    summary.append(df.loc[field_length.argmin(), 'ID'])
    return summary


def minimal_wordcloud(result, column):
    # For creating word clouds, I used WordCloud library which was imported before.

    """
    Generate a simple wordcloud similar to: 
    https://www.kaggle.com/paultimothymooney/explore-recipe-nlg-dataset/data.
    The only import required is: from wordcloud import WordCloud
    """
    text = " ".join(row[column] for row in result)
    print(text[:100])
    if len(text) > 0:
        wordcloud = WordCloud(background_color="white").generate(text)
        image = wordcloud.to_image()
        image.save("static/images/graph.png", "")