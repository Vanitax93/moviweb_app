from abc import ABC, abstractmethod
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Abstract Base Class (Interface)
class DataManagerInterface(ABC):
    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        pass

    @abstractmethod
    def add_user(self, username):
        pass

    @abstractmethod
    def add_movie(self, user_id, title, director, year, rating):
        pass

    @abstractmethod
    def update_movie(self, movie_id, title, director, year, rating):
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        pass

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    movies = db.relationship('Movie', backref='user', lazy=True)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    director = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)

# SQLite Implementation
class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        db.init_app(app)
        # Create tables if they don't exist
        with app.app_context():
            db.create_all()

    def get_all_users(self):
        return User.query.all()

    def get_user_movies(self, user_id):
        return Movie.query.filter_by(user_id=user_id).all()

    def add_user(self, username):
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        return new_user.id

    def add_movie(self, user_id, title, director, year, rating):
        new_movie = Movie(
            user_id=user_id,
            title=title,
            director=director,
            year=year,
            rating=rating
        )
        db.session.add(new_movie)
        db.session.commit()
        return new_movie.id

    def update_movie(self, movie_id, title, director, year, rating):
        movie = Movie.query.get(movie_id)
        if movie:
            movie.title = title
            movie.director = director
            movie.year = year
            movie.rating = rating
            db.session.commit()
            return True
        return False

    def delete_movie(self, movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return True
        return False

