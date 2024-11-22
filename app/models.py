from app import db


class FavoriteMovie(db.Model):
    __tablename__ = 'favorite_movies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    movie_name = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'FavoriteMovie movie_name={self.movie_name}, rating={self.rating}'
