from flask import jsonify
from http import HTTPStatus
from requests.exceptions import RequestException, Timeout, ConnectionError
from datetime import datetime
from models import db, FavoriteMovie
from external_api import ExternalApi, ExternalApiV1


class ApiInterface:
    """
    A class that provides methods for interacting with the external API 
    and managing the user's favorite movies.
    
    This class acts as a singleton and allows fetching popular movies, 
    adding/removing movies to/from favorites, and rating favorite movies.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Creates a new instance of the ApiInterface class, ensuring it's a singleton.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            ApiInterface: The singleton instance of ApiInterface.
        """
        if not cls._instance:
            cls._instance = super(ApiInterface, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, external_api: ExternalApi) -> None:
        """
        Initializes the ApiInterface with an instance of ExternalApi and sets up 
        virtual cache and the last cache update timestamp.

        Args:
            external_api (ExternalApi): An instance of the ExternalApi class to fetch movie data.
        """
        self.external_api = external_api
        self.virtual_cache = {
            'page': 0,
            'results': [],
            'total_pages': 0,
            'total_results': 0
        }
        self.last_cache_update = 0

    def get_popular_movies(self) -> tuple:
        """
        Retrieves popular movies either from cache or by calling the external API.

        If the cache is recent (less than 30 seconds old), it returns the cached data.
        Otherwise, it fetches new data from the external API and updates the cache.

        Returns:
            tuple: A tuple containing the response JSON and the HTTP status code.
        """
        if datetime.now().timestamp() - self.last_cache_update < 30:
            return jsonify(self.virtual_cache), HTTPStatus.OK
        try:
            response = self.external_api.get_popular_movies()
            if response.status_code == HTTPStatus.OK:
                try:
                    response_json = response.json()
                    if not isinstance(response_json, dict) or 'results' not in response_json:
                        print('Error: Response structure is invalid')
                    else:
                        self.virtual_cache = response_json
                        self.last_cache_update = datetime.now().timestamp()
                except ValueError:
                    print('Error: Failed to parse JSON response')
            else:
                print(f'Error {response.status_code}: {response.text}')
        except Timeout:
            print('The request has timed out.')
        except ConnectionError:
            print('Connection error, please check your network.')
        except RequestException as e:
            print(f'An error occurred with the request: {e}')
        except Exception as e:
            print(f'An unexpected error has occurred: {e}')
        finally:
            return jsonify(self.virtual_cache), HTTPStatus.OK

    def add_to_favorite_movies(self, movie_id: int) -> tuple:
        """
        Adds a movie to the user's list of favorite movies.

        If the movie is not already in the favorites list, it fetches the movie's 
        details from the external API and adds it to the favorites database.

        Args:
            movie_id (int): The ID of the movie to add to the favorites.

        Returns:
            tuple: A tuple containing a message and the HTTP status code.
        """
        movie = FavoriteMovie.query.filter_by(movie_id=movie_id).first()
        if not movie:
            try:
                response = self.external_api.get_movie_detail(movie_id)
                if response.status_code == 200:
                    favorite_movie = FavoriteMovie(
                        user_id = 1,
                        movie_id = movie_id,
                        movie_name = response.json()['title'],
                        rating = 0,
                        created_at = datetime.strptime(response.json()['release_date'], '%Y-%m-%d')
                    )
                    db.session.add(favorite_movie)
                    db.session.commit()
                    message = 'Movie added successfully.'
                    status_code = HTTPStatus.OK
                else:
                    message = 'Movie not added to favorites because status code.'
                    status_code = HTTPStatus.BAD_REQUEST
                    print(f'{message}')
            except Timeout:
                message = 'The request to the external api has timed out.'
                status_code = HTTPStatus.REQUEST_TIMEOUT
                print(f'{message}')
            except ConnectionError:
                message = 'Connection error.'
                status_code = HTTPStatus.NOT_FOUND
                print(f'{message}')
            except RequestException as e:
                message = f'An error occurred with the request: {e}'
                status_code = HTTPStatus.BAD_REQUEST
                print(f'{message}')
            except Exception as e:
                message = f'An unexpected error has occurred: {e}'
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                print(f'{message}')
            finally:
                return jsonify({"message": f'{message}'}), status_code
        return jsonify({"message": "Movie already exists in favorites"}), HTTPStatus.OK

    def remove_from_favorite_movies(self, movie_id: int, user_id:int = 1) -> tuple:
        """
        Removes a movie from the user's list of favorite movies.

        Args:
            movie_id (int): The ID of the movie to remove from the favorites.
            user_id (int, optional): The ID of the user (default is 1).

        Returns:
            tuple: A tuple containing a message and the HTTP status code.
        """
        favorite_movie = FavoriteMovie.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if not favorite_movie:
            return jsonify({'error': 'Favorite movie not found for this user'}), HTTPStatus.NOT_FOUND
        db.session.delete(favorite_movie)
        db.session.commit()

        return jsonify({'message': 'Movie removed from favorites'}), HTTPStatus.OK

    def rate_favorite_movie(self, movie_id: int, rating: int) -> tuple:
        """
        Updates the rating for a movie in the user's list of favorite movies.

        Args:
            movie_id (int): The ID of the movie to rate.
            rating (int): The rating to assign to the movie.

        Returns:
            tuple: A tuple containing a message and the HTTP status code.
        """
        favorite_movie = FavoriteMovie.query.filter_by(user_id=1, movie_id=movie_id).first()
        if not favorite_movie:
            return jsonify({"error": "Favorite movie not found for this user"}), HTTPStatus.NOT_FOUND
        favorite_movie.rating = rating
        db.session.commit()

        return jsonify({"message": "Movie rating updated successfully."}), HTTPStatus.OK

    def get_favorite_movies(self) -> tuple:
        """
        Retrieves the list of the user's favorite movies.

        Returns:
            tuple: A tuple containing the list of favorite movies and the HTTP status code.
        """
        favorite_movies = db.session.query(FavoriteMovie).all()
        favorite_movies_json = list()
        for favorite_movie in favorite_movies:
            movie_data = {
                'id': favorite_movie.id,
                'user_id': favorite_movie.user_id,
                'movie_id': favorite_movie.movie_id,
                'rating': favorite_movie.rating,
                'created_at': favorite_movie.created_at.isoformat()
            }
            favorite_movies_json.append(movie_data)
        return jsonify(favorite_movies_json), HTTPStatus.OK

    def clear_favorite_movies(self, user_id: int = 1) -> tuple:
        """
        Clears all favorite movies for a specific user.

        Args:
            user_id (int, optional): The ID of the user (default is 1).

        Returns:
            tuple: A tuple containing a message and the HTTP status code.
        """
        try:
            db.session.query(FavoriteMovie).filter_by(user_id=user_id).delete()
            db.session.commit()
            message = 'All FavoriteMovie records have been deleted.'
            print(f'{message}')
            return jsonify({'message': message}), HTTPStatus.OK
        except Exception as e:
            db.session.rollback()
            message = f'Error deleting FavoriteMovie records: {e}'
            print(f'{message}')
            return jsonify({'error': message}), HTTPStatus.INTERNAL_SERVER_ERROR
