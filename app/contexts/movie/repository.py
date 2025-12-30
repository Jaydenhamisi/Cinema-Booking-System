# app/contexts/movie/repository.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Movie

class MovieRepository:
    """Repository for Movie aggregate."""

    def get_by_id(self, db: Session, movie_id: int):
        """Get movie by ID."""
        return db.get(Movie, movie_id)

    def get_by_title(self, db: Session, title: str):
        """Get movie by title."""
        return db.scalars(
            select(Movie).where(Movie.title == title)
        ).first()

    def list_all(self, db: Session, active_only: bool = True):
        """List all movies, optionally filtering by active status."""
        stmt = select(Movie)
        if active_only:
            stmt = stmt.where(Movie.is_active == True)
        return db.scalars(stmt).all()

    def create(self, db: Session, movie: Movie):
        """Create a new movie."""
        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie

    def save(self, db: Session, movie: Movie):
        """Update existing movie."""
        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie

    def delete(self, db: Session, movie: Movie):
        """Delete a movie."""
        db.delete(movie)
        db.commit()