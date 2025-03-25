import unittest
from flask import url_for
from app import app, data_manager, db, User, Movie
import os

class MovieWebAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        self.user_id = data_manager.add_user("testuser")
        self.movie_id = data_manager.add_movie(self.user_id, "Test Movie", "Test Director", 2023, 8.5)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Route Functionality Tests
    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the MovieWeb App!', response.data)

    def test_users_route(self):
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data)

    def test_user_movies_route(self):
        response = self.app.get(f'/users/{self.user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Movie', response.data)

    def test_add_user_route_get(self):
        response = self.app.get('/add_user')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add New User', response.data)

    def test_add_movie_route_get(self):
        response = self.app.get(f'/users/{self.user_id}/add_movie')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add Movie for testuser', response.data)

    def test_update_movie_route_get(self):
        response = self.app.get(f'/users/{self.user_id}/update_movie/{self.movie_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Update Test Movie', response.data)

    # Data Persistence Test
    def test_data_persistence(self):
        new_user_id = data_manager.add_user("persistuser")
        new_movie_id = data_manager.add_movie(new_user_id, "Persist Movie", "Persist Director", 2024, 9.0)
        user = db.session.get(User, new_user_id)
        movie = db.session.get(Movie, new_movie_id)
        self.assertIsNotNone(user, "User should exist in the database")
        self.assertEqual(user.username, "persistuser")
        self.assertIsNotNone(movie, "Movie should exist in the database")
        self.assertEqual(movie.title, "Persist Movie")

    # Edge Case Tests
    def test_user_movies_invalid_user(self):
        response = self.app.get('/users/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404 - Page Not Found', response.data)

    def test_update_movie_invalid_movie(self):
        response = self.app.get(f'/users/{self.user_id}/update_movie/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404 - Page Not Found', response.data)

    def test_delete_movie_invalid_movie(self):
        response = self.app.get(f'/users/{self.user_id}/delete_movie/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404 - Page Not Found', response.data)

    # Form Validation Tests
    def test_add_user_empty_form(self):
        response = self.app.post('/add_user', data={})
        self.assertEqual(response.status_code, 400)  # Expect 400 for invalid input
        self.assertIn(b'Username is required', response.data)

    def test_add_movie_empty_title(self):
        response = self.app.post(f'/users/{self.user_id}/add_movie', data={})
        self.assertEqual(response.status_code, 400)  # Expect 400 for invalid input
        self.assertIn(b'Title is required', response.data)

    def test_update_movie_empty_title(self):
        response = self.app.post(
            f'/users/{self.user_id}/update_movie/{self.movie_id}',
            data={'director': 'New Director', 'year': '2023', 'rating': '8.0'}
        )
        self.assertEqual(response.status_code, 400)  # Expect 400 for invalid input
        self.assertIn(b'Title is required', response.data)

    # Successful Form Submission Tests
    def test_add_user_success(self):
        response = self.app.post('/add_user', data={'username': 'newuser'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'newuser', response.data)

    def test_add_movie_success(self):
        response = self.app.post(
            f'/users/{self.user_id}/add_movie',
            data={'title': 'New Movie', 'director': 'New Director', 'year': '2024', 'rating': '7.5'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Movie', response.data)

    def test_update_movie_success(self):
        response = self.app.post(
            f'/users/{self.user_id}/update_movie/{self.movie_id}',
            data={'title': 'Updated Movie', 'director': 'Updated Director', 'year': '2025', 'rating': '9.0'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated Movie', response.data)

    def test_delete_movie_success(self):
        response = self.app.get(f'/users/{self.user_id}/delete_movie/{self.movie_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Test Movie', response.data)

if __name__ == '__main__':
    unittest.main()