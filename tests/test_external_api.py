"Tests for external API Module"
import unittest
from unittest.mock import patch, MagicMock
from http import HTTPStatus
from app.external_api import ExternalApiV1


class TestExternalApiV1(unittest.TestCase):
    def setUp(self):
        self.api = ExternalApiV1()

    @patch('requests.get')
    def test_get_popular_movies_success(self, mock_get):
        response_data = {'results': [{'title': 'Test Movie'}]}
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_response.status_code = HTTPStatus.OK
        mock_get.return_value = mock_response
        response = self.api.get_popular_movies()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(response.json(), response_data)

    @patch('requests.get')
    def test_get_popular_movies_exception(self, mock_get):
        mock_get.side_effect = Exception('Network error')
        with self.assertRaises(Exception):
            response = self.api.get_popular_movies()

    @patch('requests.get')
    def test_get_popular_movies_retry(self, mock_get):
        response_data = {'results': [{'title1': 'Test Movie1'}, {'title2': 'Test Movie2'}]}
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_response.status_code = HTTPStatus.OK
        mock_get.side_effect = [Exception('Network error'),
                                Exception('Network error'),
                                Exception('Network error'),
                                Exception('Network error'),
                                mock_response]
        response = self.api.get_popular_movies()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertDictEqual(response.json(), response_data)
        self.assertEqual(mock_get.call_count, 5)

    @patch('requests.get')
    def test_get_movie_detail_success(self, mock_get):
        response_data = {'title': 'Test Movie'}
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_response.status_code = HTTPStatus.OK
        mock_get.return_value = mock_response
        response = self.api.get_popular_movies()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['title'], 'Test Movie')

    @patch('requests.get')
    def test_get_movie_detail_retry(self, mock_get):
        response_data = {'title': 'Test Movie'}
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_response.status_code = HTTPStatus.OK
        mock_get.side_effect = [Exception('Network error'),
                                Exception('Network error'),
                                mock_response]
        response = self.api.get_movie_detail()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['title'], 'Test Movie')
        self.assertEqual(mock_get.call_count, 3)

    @patch('requests.get')
    def test_get_movie_detail_exception(self, mock_get):
        mock_get.side_effect = Exception('Network error')
        with self.assertRaises(Exception):
            response = self.api.get_movie_detail()


if __name__ == '__main__':
    unittest.main()
