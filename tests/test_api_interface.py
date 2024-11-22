"Tests for API interface Module"
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from http import HTTPStatus
from requests.exceptions import RequestException, Timeout, ConnectionError
import io
from app.app import create_app, db
from app.models import FavoriteMovie
from app.config import TestingConfig
from app.external_api import ExternalApiV1
from app.api_interface import ApiInterface


class TestApiInterface(unittest.TestCase):
    def setUp(self):
        app = create_app(TestingConfig())
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch.object(ExternalApiV1, 'get_popular_movies')
    def test_get_popular_movies_success(self, mock_get_popular_movies):
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_json = {'results': [{'id': 1, 'title': 'Movie 1'}, {'id': 2, 'title': 'Movie 2'}]}
        mock_response.json.return_value = expected_json
        mock_get_popular_movies.return_value = mock_response
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.get_popular_movies()
        self.assertEqual(response[0].json, expected_json)
        self.assertEqual(api_interface.virtual_cache, expected_json)
        self.assertTrue(api_interface.last_cache_update <= datetime.now().timestamp())

    @patch.object(ExternalApiV1, 'get_popular_movies')
    def test_get_popular_movies_failure(self, mock_get_popular_movies):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_get_popular_movies.return_value = mock_response
        api_interface = ApiInterface(ExternalApiV1())
        expected_update = api_interface.last_cache_update

        # Exception
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.get_popular_movies()
            self.assertTrue('Error 500: Internal Server Error' in fake_out.getvalue())
        self.assertEqual(api_interface.virtual_cache, response[0].json)
        self.assertEqual(api_interface.last_cache_update,  expected_update)

    @patch.object(ExternalApiV1, 'get_popular_movies')
    def test_get_popular_movies_empty_response(self, mock_get_popular_movies):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_get_popular_movies.return_value = mock_response
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.get_popular_movies()
        self.assertEqual(api_interface.virtual_cache, {'results': []})
        self.assertTrue(api_interface.last_cache_update <= datetime.now().timestamp())

    @patch.object(ExternalApiV1, 'get_popular_movies')
    def test_get_get_popular_movies_exceptions(self, mock_get):
        mock_get.side_effect = [Exception('Test error'),
                                RequestException('Test error'),
                                ConnectionError,
                                Timeout]
        api_interface = ApiInterface(ExternalApiV1())
        expected_json = api_interface.virtual_cache

        # Exception
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.get_popular_movies()
            self.assertTrue('Test error' in fake_out.getvalue())
        self.assertEqual(response[0].json, expected_json)
        self.assertEqual(response[1], HTTPStatus.OK)

        # RequestException
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.get_popular_movies()
            self.assertTrue('Test error' in fake_out.getvalue())
        self.assertEqual(response[0].json, expected_json)
        self.assertEqual(response[1], HTTPStatus.OK)
        
        # ConnectionError
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.get_popular_movies()
            self.assertTrue('Connection error, please check your network.' in fake_out.getvalue())
        self.assertEqual(response[0].json, expected_json)
        self.assertEqual(response[1], HTTPStatus.OK)
        
        # Timeout
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.get_popular_movies()
            self.assertTrue('The request has timed out.' in fake_out.getvalue())
        self.assertEqual(response[0].json, expected_json)
        self.assertEqual(response[1], HTTPStatus.OK)

    @patch.object(ExternalApiV1, 'get_movie_detail')
    def test_add_to_favorite_movies_new_movie(self, mock_get_movie_detail):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'title': 'Test Movie',
            'release_date': '2023-01-01'
        }
        mock_get_movie_detail.return_value = mock_response
        api_interface = ApiInterface(ExternalApiV1())
        movie_id = 12345
        response = api_interface.add_to_favorite_movies(movie_id)
        self.assertEqual(response[0].json, {'message': 'Movie added successfully.'})
        self.assertEqual(response[1], HTTPStatus.OK)
        favorite_movie = FavoriteMovie.query.filter_by(movie_id=movie_id).first()
        self.assertIsNotNone(favorite_movie)
        self.assertEqual(favorite_movie.movie_name, 'Test Movie')
        self.assertEqual(favorite_movie.created_at, datetime.strptime('2023-01-01', '%Y-%m-%d'))

    @patch.object(ExternalApiV1, 'get_movie_detail')
    def test_add_to_favorite_movies_existing_movie(self, mock_get_movie_detail):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'title': 'Test Movie',
            'release_date': '2023-01-01'
        }
        mock_get_movie_detail.return_value = mock_response
        api_interface = ApiInterface(ExternalApiV1())
        movie_id = 12345
        new_favorite_movie = FavoriteMovie(
            user_id=1,
            movie_id=movie_id,
            movie_name='Test Movie',
            rating=0,
            created_at=datetime.strptime('2023-01-01', '%Y-%m-%d')
        )
        db.session.add(new_favorite_movie)
        db.session.commit()
        response = api_interface.add_to_favorite_movies(movie_id)
        self.assertEqual(response[0].json, {'message': 'Movie already exists in favorites'})
        self.assertEqual(response[1], HTTPStatus.OK)

    @patch.object(ExternalApiV1, 'get_movie_detail')
    def test_add_to_favorite_movies_api_failure(self, mock_get_movie_detail):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get_movie_detail.return_value = mock_response
        api_interface = ApiInterface(ExternalApiV1())
        movie_id = 67890
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.add_to_favorite_movies(movie_id)
            self.assertTrue('Movie not added to favorites because status code.' in fake_out.getvalue())
        self.assertEqual(response[0].json, {'message': 'Movie not added to favorites because status code.'})
        self.assertEqual(response[1], HTTPStatus.BAD_REQUEST)

    @patch.object(ExternalApiV1, 'get_movie_detail')
    def test_add_to_favorite_movies_invalid_response(self, mock_get_movie_detail):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'release_date': '2023-01-01'
        }
        mock_get_movie_detail.return_value = mock_response
        api_interface = ApiInterface(ExternalApiV1())
        movie_id = 112233
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.add_to_favorite_movies(movie_id)
            self.assertTrue("An unexpected error has occurred: 'title'" in fake_out.getvalue())
        self.assertEqual(response[0].json, {'message': "An unexpected error has occurred: 'title'"})
        self.assertEqual(response[1], HTTPStatus.INTERNAL_SERVER_ERROR)

    @patch.object(ExternalApiV1, 'get_movie_detail')
    def test_add_to_favorite_movies_exceptions(self, mock_get):
        mock_get.side_effect = [Exception('Test error'),
                                RequestException('Test error'),
                                ConnectionError,
                                Timeout]
        api_interface = ApiInterface(ExternalApiV1())
        movie_id = 112233

        # Exception
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.add_to_favorite_movies(movie_id)
            self.assertTrue('Test error' in fake_out.getvalue())
        self.assertEqual(response[0].json, {'message': 'An unexpected error has occurred: Test error'})
        self.assertEqual(response[1], HTTPStatus.INTERNAL_SERVER_ERROR)

        # RequestException
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.add_to_favorite_movies(movie_id)
            self.assertTrue('Test error' in fake_out.getvalue())
        self.assertEqual(response[0].json, {'message': 'An error occurred with the request: Test error'})
        self.assertEqual(response[1], HTTPStatus.BAD_REQUEST)
        
        # ConnectionError
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.add_to_favorite_movies(movie_id)
            self.assertTrue('Connection error.' in fake_out.getvalue())
        self.assertEqual(response[0].json, {'message': 'Connection error.'})
        self.assertEqual(response[1], HTTPStatus.NOT_FOUND)
        
        # Timeout
        with patch('sys.stdout', new = io.StringIO()) as fake_out:
            response = api_interface.add_to_favorite_movies(movie_id)
            self.assertTrue('The request to the external api has timed out.' in fake_out.getvalue())
        self.assertEqual(response[0].json, {'message': 'The request to the external api has timed out.'})
        self.assertEqual(response[1], HTTPStatus.REQUEST_TIMEOUT)

    def test_rate_favorite_movie_success(self):
        self.favorite_movie = FavoriteMovie(user_id=1, movie_id=100, movie_name="Test Movie", rating=0, created_at=datetime.now())
        db.session.add(self.favorite_movie)
        db.session.commit()
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.rate_favorite_movie(100, 4)
        self.assertEqual(response[1], HTTPStatus.OK)
        self.assertEqual(response[0].json['message'], "Movie rating updated successfully.")
        updated_movie = FavoriteMovie.query.filter_by(movie_id=100).first()
        self.assertEqual(updated_movie.rating, 4)

    def test_rate_favorite_movie_not_found(self):
        self.favorite_movie = FavoriteMovie(user_id=1, movie_id=100, movie_name="Test Movie", rating=0, created_at=datetime.now())
        db.session.add(self.favorite_movie)
        db.session.commit()
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.rate_favorite_movie(99, 4)
        self.assertEqual(response[1], HTTPStatus.NOT_FOUND)
        self.assertEqual(response[0].json['error'], "Favorite movie not found for this user")

    def test_get_favorite_movies(self):
        self.favorite_movie = FavoriteMovie(user_id=1, movie_id=100, movie_name="Test Movie", rating=4, created_at=datetime.now())
        db.session.add(self.favorite_movie)
        db.session.commit()
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.get_favorite_movies()
        self.assertEqual(response[1], HTTPStatus.OK)
        self.assertIsInstance(response[0].json, list)
        self.assertEqual(len(response[0].json), 1)
        self.assertEqual(response[0].json[0]['movie_id'], 100)
        self.assertEqual(response[0].json[0]['rating'], 4)

    def test_get_favorite_movies_empty(self):
        self.favorite_movie = FavoriteMovie(user_id=1, movie_id=100, movie_name="Test Movie", rating=4, created_at=datetime.now())
        db.session.add(self.favorite_movie)
        db.session.commit()
        FavoriteMovie.query.delete()
        db.session.commit()
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.get_favorite_movies()
        self.assertEqual(response[1], HTTPStatus.OK)
        self.assertEqual(response[0].json, [])

    def test_clear_favorite_movies_success(self):
        self.favorite_movie = FavoriteMovie(user_id=1, movie_id=100, movie_name="Test Movie", rating=4, created_at=datetime.now())
        db.session.add(self.favorite_movie)
        db.session.commit()
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.clear_favorite_movies(1)
        self.assertEqual(response[1], HTTPStatus.OK)
        self.assertEqual(response[0].json['message'], 'All FavoriteMovie records have been deleted.')
        favorite_movies = FavoriteMovie.query.all()
        self.assertEqual(len(favorite_movies), 0)

    def test_remove_from_favorite_movies_success(self):
        self.favorite_movie = FavoriteMovie(user_id=1, movie_id=100, movie_name="Test Movie", rating=4, created_at=datetime.now())
        db.session.add(self.favorite_movie)
        db.session.commit()
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.remove_from_favorite_movies(movie_id=100)
        self.assertEqual(response[1], HTTPStatus.OK)
        self.assertEqual(response[0].json['message'], "Movie removed from favorites")
        favorite_movie = FavoriteMovie.query.filter_by(user_id=1, movie_id=100).first()
        self.assertIsNone(favorite_movie)  # La película debería haber sido eliminada

    def test_remove_from_favorite_movies_not_found(self):
        self.favorite_movie = FavoriteMovie(user_id=1, movie_id=100, movie_name="Test Movie", rating=4, created_at=datetime.now())
        db.session.add(self.favorite_movie)
        db.session.commit()
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.remove_from_favorite_movies(movie_id=990)
        self.assertEqual(response[1], HTTPStatus.NOT_FOUND)
        self.assertEqual(response[0].json['error'], "Favorite movie not found for this user")

    def test_remove_from_favorite_movies_with_different_user(self):
        another_user_movie = FavoriteMovie(user_id=2, movie_id=100, movie_name="Test Movie", rating=4, created_at=datetime.now())
        db.session.add(another_user_movie)
        db.session.commit()
        api_interface = ApiInterface(ExternalApiV1())
        response = api_interface.remove_from_favorite_movies(movie_id=100, user_id=1)
        self.assertEqual(response[1], HTTPStatus.NOT_FOUND)
        self.assertEqual(response[0].json['error'], "Favorite movie not found for this user")
        favorite_movie = FavoriteMovie.query.filter_by(user_id=2, movie_id=100).first()
        self.assertIsNotNone(favorite_movie)


if __name__ == '__main__':
    unittest.main()
