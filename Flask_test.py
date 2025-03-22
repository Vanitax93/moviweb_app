from flask import Flask
from Interface import SQLiteDataManager, db, User, Movie

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

data_manager = SQLiteDataManager(app)

# Test routes
@app.route('/')
def home():
    return """
    <h1>MoviWeb Test Page</h1>
    <ul>
        <li><a href="/test_add">Test Adding Data</a></li>
        <li><a href="/test_users">Test Get Users</a></li>
        <li><a href="/test_movies">Test Get Movies</a></li>
    </ul>
    """

@app.route('/test_add')
def test_add():
    try:
        user_id = data_manager.add_user("testuser1")
        movie_id = data_manager.add_movie(user_id, "The Matrix", "Wachowski", 1999, 8.0)
        return f"Added user ID: {user_id} and movie ID: {movie_id}"
    except Exception as e:
        return f"Error adding data: {str(e)}"

@app.route('/test_users')
def test_users():
    try:
        users = data_manager.get_all_users()
        output = "<h2>Users:</h2><ul>"
        for user in users:
            output += f"<li>ID: {user.id}, Username: {user.username}</li>"
        output += "</ul>"
        return output
    except Exception as e:
        return f"Error getting users: {str(e)}"

@app.route('/test_movies')
def test_movies():
    try:
        users = data_manager.get_all_users()
        if not users:
            return "No users found."
        user_id = users[0].id
        movies = data_manager.get_user_movies(user_id)
        output = f"<h2>Movies for User {user_id}:</h2><ul>"
        for movie in movies:
            output += f"<li>ID: {movie.id}, Title: {movie.title}, Director: {movie.director}, Year: {movie.year}, Rating: {movie.rating}</li>"
        output += "</ul>"
        return output
    except Exception as e:
        return f"Error getting movies: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)