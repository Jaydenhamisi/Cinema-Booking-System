# app/contexts/movie/events.py

"""
Domain events emitted by MovieContext.
"""


def movie_created_event(movie_id: int) -> dict:
    return {
        "type": "movie.created",
        "payload": {
            "movie_id": movie_id,
        },
    }


def movie_updated_event(movie_id: int) -> dict:
    return {
        "type": "movie.updated",
        "payload": {
            "movie_id": movie_id,
        },
    }


def movie_deactivated_event(movie_id: int) -> dict:
    return {
        "type": "movie.deactivated",
        "payload": {
            "movie_id": movie_id,
        },
    }


def movie_deleted_event(movie_id: int) -> dict:
    return {
        "type": "movie.deleted",
        "payload": {
            "movie_id": movie_id,
        },
    }
