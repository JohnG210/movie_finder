from pydoc import cli
from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import firestore
import csv
import numpy as np
import pandas as pd
app = Flask(__name__)

# Use a service account.
cred = credentials.Certificate('temporal-tensor-362216-ce8e831dd5d8.json')
app_fs = firebase_admin.initialize_app(cred)
db = firestore.client()

# Firestore load functions
def loadPerson(db):
    users_ref = db.collection(u'sales_person')
    docs = users_ref.stream()
    for doc in docs:
        a = 1
    name = doc.to_dict()
    # name = name['name']
    return name

def loadSales(db):
    users_ref = db.collection(u'sales')
    docs = users_ref.stream()
    sales = []
    for doc in docs:
        sales.append(doc.to_dict())
    return sales

def loadClients(db):
    users_ref = db.collection(u'clients')
    docs = users_ref.stream()
    for doc in docs:
        a = 1
    clients = doc.to_dict()
    # clients = clients['clients']
    return clients

def importCsvWatchedData(file):
    with open(file, newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=',', quotechar='|')
        row_idx = 0
        data_out = []
        for row in data:
            if row_idx == 0:
                headers = row
            else:
                data_out.append(row)
            row_idx = row_idx + 1
    return pd.DataFrame(data_out, columns=headers)  

def importCsvData(file):
    with open(file, newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=',', quotechar='|')
        row_idx = 0
        data_out = []
        for row in data:
            if row_idx == 0:
                row[0] = 'pic'
                headers = row
            else:
                row[0] = 'https://lh3.googleusercontent.com/1x5fLPAQpaacJLrbzhtAI8VK6IkIwLe1hErnsTuhbOu9VW5UNaCF9ecM7HuTtu2ZRYpixIB80ROCw1CSEuzaF0Gm8iED4YZVLg=w843'
                # row[1] = int(row[1])
                row[6] = float(row[6])
                data_out.append(row)
            row_idx = row_idx + 1
    return pd.DataFrame(data_out, columns=headers)  

# Load in firestore data
# current_id = 2
# sales_person = loadPerson(db)
# sales = loadSales(db)
# clients = loadClients(db)
movies = {}
movies['1000'] = importCsvData('IMDB top 1000.csv')
movies['50'] = importCsvData('IMDB top 50.csv')
movies['10'] = importCsvData('IMDB top 10.csv')
user = ''
other_user = ''
all_users= ['john', 'violet']
watchedData = importCsvWatchedData('watched_data.csv')

# ROUTES
@app.route('/')
def hello_world():
    return render_template('welcome.html', user=user) 

@app.route('/render-1000')
def change_to_1000():
    setCurrentDb('1000')
    return render_template('show_movies.html', movies_list=movies['current'].to_dict(), other_user=other_user, user=user, cur_db='IMDB Top 1000') 

@app.route('/render-10')
def change_to_10():
    setCurrentDb('10')
    return render_template('show_movies.html', movies_list=movies['current'].to_dict(), other_user=other_user, user=user, cur_db='IMDB Top 10') 

@app.route('/render-50')
def change_to_50():
    setCurrentDb('50')
    return render_template('show_movies.html', movies_list=movies['current'].to_dict(), other_user=other_user, user=user, cur_db='IMDB Top 50') 


@app.route('/find')
def showMovies():
    if 'current' not in movies.keys():
        setCurrentDb('50')
    else:
        movies['current'] = sortByWatched(movies['current'], watchedData)
    return render_template('show_movies.html', movies_list=movies['current'].to_dict(), other_user=other_user, user=user, cur_db='IMDB Top 10') 

def setCurrentDb(desired_db):
    global movies
    global watchedData
    temp = movies[desired_db]
    temp = sortByWatched(temp, watchedData)
    movies['current'] = temp


def sortByWatched(movies_data, watched):
    movies_data['num_users_seen'] = 0
    movies_data['users_seen'] = ''
    watched = watched[np.isin(watched, [user, other_user]).any(axis=1)]
    for mi, movie in movies_data.iterrows():
        for i, seen in watched.iterrows():
            if seen['movie_id'] == movie['Rank'] or seen['movie_id'] == str(movie['Rank']):
                movies_data['num_users_seen'][mi] = movies_data['num_users_seen'][mi] + 1
                movies_data['users_seen'][mi] = f"{movies_data['users_seen'][mi]}{seen['user']},"
    movies_data["Rank"] = pd.to_numeric(movies_data["Rank"])
    movies_data = movies_data.sort_values(by=['Rank'])
    movies_data['Rank'] = movies_data['Rank'].astype(str)
    movies_data = movies_data.reset_index(drop=True)
    movies_data["Rank"] = pd.to_numeric(movies_data["Rank"])
    movies_data = movies_data.sort_values(by=['num_users_seen','Rank'])
    movies_data = movies_data.reset_index(drop=True)
    movies_data['Rank'] = movies_data['Rank'].astype(str)
    return movies_data

@app.route('/movie/<id>')
def show_movie(id):
    global movies
    id = int(id)
    movie = movies['current'][id-1:id]
    movie = movie.reset_index(drop=True)
    return render_template('movie_template.html', movie=movie.to_dict(), user=user) 

# AJAX FUNCTIONS
# ajax for people.js
@app.route('/change_guest', methods=['POST'])
def guestChanged():
    global other_user
    json_data = request.get_json()
    other_user = json_data
    return jsonify(other_user = other_user)

@app.route('/change_user', methods=['POST'])
def userChanged():
    global user
    json_data = request.get_json()
    user = json_data
    return jsonify(user = user)

@app.route('/movie/watch_movie', methods=['POST'])
def watched_movie():
    global watchedData
    movie_id = request.get_json()
    if not ((watchedData['user'] == user) & (watchedData['movie_id'] == movie_id)).any():
        temp = pd.DataFrame([[user, movie_id]], columns=['user', 'movie_id'])  
        watchedData = watchedData.append(temp, ignore_index = True) 
    if not ((watchedData['user'] == other_user) & (watchedData['movie_id'] == movie_id)).any():
        temp = pd.DataFrame([[other_user, movie_id]], columns=['user', 'movie_id'])  
        watchedData = watchedData.append(temp, ignore_index = True) 
    return jsonify(movie_id = movie_id)

if __name__ == '__main__':
   app.run(debug = True)




