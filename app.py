from flask import Flask, render_template, request, redirect, url_for
import requests
from datamanager.sqlite_data_manager import SQLiteDataManager, db, User, Movie

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

data_manager = SQLiteDataManager(app)
OMDB_API_KEY = "345317ed"

# OMDb API fetch function
def fetch_movie_data(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            return {
                "title": data.get("Title"),
                "director": data.get("Director", "Unknown"),
                "year": int(data.get("Year", 0)),
                "rating": float(data.get("imdbRating", 0))
            }
    return None

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Users List route
@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)

# User Movies route
@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return "User not found", 404
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user=user, movies=movies)

# Add User route
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            data_manager.add_user(username)
            return redirect(url_for('list_users'))
        return "Username is required", 400
    return render_template('add_user.html')

# Add Movie route
@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return "User not found", 404
    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            movie_data = fetch_movie_data(title)
            if movie_data:
                data_manager.add_movie(
                    user_id,
                    movie_data['title'],
                    movie_data['director'],
                    movie_data['year'],
                    movie_data['rating']
                )
            else:
                # Fallback to manual if API fails
                data_manager.add_movie(
                    user_id,
                    title,
                    request.form.get('director', 'Unknown'),
                    int(request.form.get('year', 0)),
                    float(request.form.get('rating', 0))
                )
            return redirect(url_for('user_movies', user_id=user_id))
        return "Title is required", 400
    return render_template('add_movie.html', user=user)

# Update Movie route
@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    user = db.session.get(User, user_id)
    movie = db.session.get(Movie, movie_id)
    if not user or not movie or movie.user_id != user_id:
        return "User or movie not found", 404
    if request.method == 'POST':
        title = request.form.get('title')
        director = request.form.get('director')
        year = int(request.form.get('year', 0))
        rating = float(request.form.get('rating', 0))
        if title:
            data_manager.update_movie(movie_id, title, director, year, rating)
            return redirect(url_for('user_movies', user_id=user_id))
        return "Title is required", 400
    return render_template('update_movie.html', user=user, movie=movie)

# Delete Movie route
@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    user = db.session.get(User, user_id)
    movie = db.session.get(Movie, movie_id)
    if not user or not movie or movie.user_id != user_id:
        return "User or movie not found", 404
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))

if __name__ == '__main__':
    with app.app_context():
        if not data_manager.get_all_users():
            user_id = data_manager.add_user("alice")
            data_manager.add_movie(user_id, "The Matrix", "Wachowski", 1999, 8.7)
    app.run(debug=True)