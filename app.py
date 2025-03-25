from flask import Flask, render_template, request, redirect, url_for
import requests
from moviweb_app.datamanager.sqlite_data_manager import SQLiteDataManager, db, User, Movie

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

data_manager = SQLiteDataManager(app)
OMDB_API_KEY = "345317ed"

# OMDb API fetch function
def fetch_movie_data(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                return {
                    "title": data.get("Title"),
                    "director": data.get("Director", "Unknown"),
                    "year": int(data.get("Year", 0)),
                    "rating": float(data.get("imdbRating", 0)),
                    "poster_url": data.get("Poster", None)
                }
        return None
    except requests.RequestException as e:
        print(f"OMDb API error: {str(e)}")
        return None
    except ValueError as e:
        print(f"Data parsing error: {str(e)}")
        return None

# Home route
@app.route('/')
def home():
    try:
        # Fetch the top 6 movies by rating
        featured_movies = Movie.query.order_by(Movie.rating.desc()).limit(6).all()
        return render_template('home.html', featured_movies=featured_movies)
    except Exception as e:
        print(f"Error fetching featured movies: {str(e)}")
        return render_template('home.html', featured_movies=[])

# Users List route
@app.route('/users')
def list_users():
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return render_template('500.html'), 500

# User Movies route
@app.route('/users/<int:user_id>')
def user_movies(user_id):
    try:
        user = db.session.get(User, user_id)
        if not user:
            return render_template('404.html'), 404
        movies = data_manager.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)
    except Exception as e:
        return render_template('500.html'), 500

# Add User route
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            return "Username is required", 400
        try:
            data_manager.add_user(username)
            return redirect(url_for('list_users'))
        except Exception as e:
            return render_template('500.html'), 500
    return render_template('add_user.html')

# Add Movie route
@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    try:
        user = db.session.get(User, user_id)
        if not user:
            return render_template('404.html'), 404
        if request.method == 'POST':
            title = request.form.get('title')
            if not title:
                return "Title is required", 400
            movie_data = fetch_movie_data(title)
            if movie_data:
                data_manager.add_movie(
                    user_id,
                    movie_data['title'],
                    movie_data['director'],
                    movie_data['year'],
                    movie_data['rating'],
                    poster_url=movie_data['poster_url']
                )
            else:
                data_manager.add_movie(
                    user_id,
                    title,
                    request.form.get('director', 'Unknown'),
                    int(request.form.get('year', 0)),
                    float(request.form.get('rating', 0)),
                    poster_url=None
                )
            return redirect(url_for('user_movies', user_id=user_id))
        return render_template('add_movie.html', user=user)
    except Exception as e:
        return render_template('500.html'), 500

# Update Movie route
@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    try:
        user = db.session.get(User, user_id)
        movie = db.session.get(Movie, movie_id)
        if not user or not movie or movie.user_id != user_id:
            return render_template('404.html'), 404
        if request.method == 'POST':
            title = request.form.get('title')
            if not title:
                return "Title is required", 400
            director = request.form.get('director', 'Unknown')
            try:
                year = int(request.form.get('year', 0))
                rating = float(request.form.get('rating', 0))
            except ValueError as e:
                return "Year and rating must be numbers", 400
            data_manager.update_movie(movie_id, title, director, year, rating)
            return redirect(url_for('user_movies', user_id=user_id))
        return render_template('update_movie.html', user=user, movie=movie)
    except Exception as e:
        return render_template('500.html'), 500

# Delete Movie route
@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    try:
        user = db.session.get(User, user_id)
        movie = db.session.get(Movie, movie_id)
        if not user or not movie or movie.user_id != user_id:
            return render_template('404.html'), 404
        data_manager.delete_movie(movie_id)
        return redirect(url_for('user_movies', user_id=user_id))
    except Exception as e:
        return render_template('500.html'), 500

# Delete User Route
@app.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    try:
        user = db.session.get(User, user_id)
        if not user:
            return render_template('404.html'), 404
        data_manager.delete_user(user_id)
        return redirect(url_for('list_users'))
    except Exception as e:
        return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)