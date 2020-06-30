"""Utilities for models to inherit or use"""
from flask import abort
from http import HTTPStatus


def get_object_or_404(model, mid):
    """Get an object by id or return a 404 not found response

    Args:
        model (object): object's model class
        mid (int): object's id

    Returns:
        object: returned from query

    Raises:
        404: if one object is returned from query

    """
    obj = model.query.get(mid)
    if obj:
        return obj
    else:
        abort(404)
