from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Movie



class MovieRepository:

    def get_by_id(self, db: Session, movie_id: int):
        return db.get(Movie, movie_id)



    def get_by_title(self, db: Session, title: str):
        return db.scalars(
            select(Movie).where(Movie.title == title)
        ).first()



    def list_all(self, db: Session, active_only: bool = True):
        stmt = select(Movie)
        if active_only:
            stmt = stmt.where(Movie.is_active == True)
        return db.scalars(stmt).all()



    def create(self, db: Session, movie: Movie):
        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie



    def delete(self, db: Session, movie: Movie):
        db.delete(movie)
        db.commit()
        return True
