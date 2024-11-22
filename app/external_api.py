from abc import ABC, abstractmethod
import requests
from tenacity import retry, wait_exponential, stop_after_attempt
from .settings import API_TOKEN, POPULAR_MOVIES_URL


class ExternalApi(ABC):

    @abstractmethod
    def get_popular_movies(self):
        pass

    @abstractmethod
    def get_movie_detail(self):
        pass


class ExternalApiV1(ExternalApi):
    @retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(5),
    reraise=True
    )
    def get_popular_movies(self,
                           include_adult: str = 'false',
                           include_video: str = 'false',
                           language: str = 'en-US',
                           page: str = '1',
                           sort_by: str = 'popularity.desc') -> requests.Response:
        """
        Fetch popular movies from the API.

        Args:
            include_adult (str): Whether to include adult content (default: 'false').
            include_video (str): Whether to include videos (default: 'false').
            language (str): The language of the results (default: 'en-US').
            page (str): The page of results to fetch (default: '1').
            sort_by (str): The sorting criterion (default: 'popularity.desc').

        Returns:
            requests.Response: The response object containing the popular movies data.

        """
        params = {
        'include_adult': include_adult,
        'include_video': include_video,
        'language': language,
        'page': page,
        'sort_by': sort_by
        }

        headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'accept': 'application/json'
        }

        response = requests.get(url=POPULAR_MOVIES_URL, params=params, headers=headers)
        return response

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def get_movie_detail(self, movie_id: int = 912649) -> requests.Response:
        """
        Fetch details of a specific movie from the API.

        Args:
            movie_id (int): The ID of the movie to fetch details for (default: 912649).

        Returns:
            requests.Response: The response object containing the movie details data.

        """
        url = f'https://api.themoviedb.org/3/movie/{movie_id}'

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f'Bearer {API_TOKEN}',
        }

        response = requests.get(url, headers=headers)
        return response
