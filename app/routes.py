from flask import request
from flask import jsonify
from http import HTTPStatus
from .api_interface import ApiInterface
from .external_api import ExternalApiV1


def register_routes(app, db):
    @app.route('/health')
    def health_check():
        """
        Endpoint for health check.

        Returns a simple status message to indicate that the server is running.

        Returns:
            JSON response: A dictionary with the key 'status' and value 'ok'.
        """
        return jsonify({"status": "ok"})

    # TODO: refactor into Blueprint 'movies'
    @app.route('/get_popular_movies', methods=['GET'])
    def get_popular_movies():
        """
        Fetches popular movies from the external API.

        Calls the external API and returns the data about popular movies,
        either from cache or by making an API request.

        Returns:
            JSON response: Data about popular movies in the cache or from the API.
        """
        return ApiInterface(ExternalApiV1()).get_popular_movies()

    # TODO: refactor into Blueprint 'favorites'
    @app.route('/get_favorite_movies', methods=['GET'])
    def get_favorite_movies():
        """
        Fetches the list of the user's favorite movies.

        Returns a list of movies marked as favorites for the user.

        Returns:
            JSON response: A list of favorite movies.
        """
        return ApiInterface(ExternalApiV1()).get_favorite_movies()

    @app.route('/add_to_favorite_movies/<int:movie_id>', methods=['POST'])
    def add_to_favorite_movies(movie_id):
        """
        Adds a movie to the user's favorite movies list.

        Fetches movie details from the external API and adds the movie to
        the favorites list in the database.

        Args:
            movie_id (int): The ID of the movie to be added to favorites.

        Returns:
            JSON response: A message indicating whether the movie was added successfully.
        """
        return ApiInterface(ExternalApiV1()).add_to_favorite_movies(movie_id=movie_id)

    @app.route('/remove_from_favorite_movies/<int:movie_id>', methods=['DELETE'])
    def remove_from_favorite_movies(movie_id):
        """
        Removes a movie from the user's favorite movies list.

        Args:
            movie_id (int): The ID of the movie to be removed from favorites.

        Returns:
            JSON response: A message indicating whether the movie was removed successfully.
        """
        return ApiInterface(ExternalApiV1()).remove_from_favorite_movies(movie_id=movie_id)

    # TODO: refactor into Blueprint 'reviews'
    @app.route('/update_review/<int:movie_id>', methods=['PUT'])
    def update_review(movie_id):
        """
        Updates the rating for a favorite movie.

        Accepts a JSON body with a 'rating' field and updates the rating for the
        specified movie.

        Args:
            movie_id (int): The ID of the movie to update the rating.

        Returns:
            JSON response: A message indicating whether the rating was updated successfully or errors.
        """
        data = request.get_json()

        if 'rating' not in data:
            return jsonify({"error": "Rating is required"}), HTTPStatus.BAD_REQUEST

        rating = data['rating']
        if rating < 0 or rating > 5:
            return jsonify({"error": "Rating must be between 0 and 5"}), HTTPStatus.BAD_REQUEST

        api_interface = ApiInterface(ExternalApiV1())
        return api_interface.rate_favorite_movie(movie_id=movie_id, rating=rating)

    # TODO: refactor into Blueprint 'admin'
    @app.route('/clear_favorite_movies/<int:user_id>', methods=['DELETE'])
    def clear_favorite_movies(user_id):
        """
        Clears all favorite movies for a specific user.

        Args:
            user_id (int): The ID of the user whose favorites are to be cleared.

        Returns:
            JSON response: A message indicating whether the favorites were cleared successfully.
        """
        return ApiInterface(ExternalApiV1()).clear_favorite_movies(user_id=user_id)
