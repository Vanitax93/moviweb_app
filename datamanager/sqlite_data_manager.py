from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    movies = db.relationship('Movie', backref='user', lazy=True, cascade="all, delete-orphan")

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    director = db.Column(db.String(80))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    poster_url = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class SQLiteDataManager:
    def __init__(self, app):
        db.init_app(app)

    def get_all_users(self):
        return User.query.all()

    def get_user_movies(self, user_id):
        return Movie.query.filter_by(user_id=user_id).all()

    def add_user(self, username):
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        return new_user.id

    def add_movie(self, user_id, title, director, year, rating, poster_url=None):
        movie = Movie(
            user_id=user_id,
            title=title,
            director=director,
            year=year,
            rating=rating,
            poster_url=poster_url
        )
        db.session.add(movie)
        db.session.commit()
        return movie.id

    def update_movie(self, movie_id, title, director, year, rating):
        movie = db.session.get(Movie, movie_id)
        if movie:
            movie.title = title
            movie.director = director
            movie.year = year
            movie.rating = rating
            db.session.commit()

    def delete_movie(self, movie_id):
        movie = db.session.get(Movie, movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()

    def delete_user(self, user_id):
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()