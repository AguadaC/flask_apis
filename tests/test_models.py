import unittest
from app.app import create_app, db
from app.models import FavoriteMovie
from app.config import TestingConfig
from datetime import datetime


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Configuramos la aplicación para pruebas
        app = create_app(TestingConfig())
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Crear las tablas de la base de datos antes de cada prueba
        db.create_all()

    def tearDown(self):
        # Limpiar la base de datos después de cada prueba
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_favorite_movie(self):
        # Crear un objeto de película favorito
        new_favorite_movie = FavoriteMovie(user_id=1, movie_id=101, movie_name='test_movie', rating=4.5, created_at=datetime.now())
        db.session.add(new_favorite_movie)
        db.session.commit()

        # Verificar que se haya creado correctamente
        favorite_movie = FavoriteMovie.query.filter_by(user_id=1, movie_id=101).first()
        self.assertIsNotNone(favorite_movie)
        self.assertEqual(favorite_movie.rating, 4.5)

    def test_movie_not_in_database(self):
        # Intentar obtener una película que no existe
        favorite_movie = FavoriteMovie.query.filter_by(user_id=999, movie_id=999).first()
        self.assertIsNone(favorite_movie)



if __name__ == '__main__':
    unittest.main()
