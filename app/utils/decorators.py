
from functools import wraps
from fastapi import HTTPException
from typing import Callable
from bson import ObjectId
from typing import Type, Dict


def check_existence(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = None
        try:
            result = await func(*args, **kwargs)
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(status_code=404, detail=str(e))
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return result
    return wrapper


def validate_object_id(func):
    @wraps(func)
    async def wrapper(id: str, *args, **kwargs):
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID")
        return await func(id, *args, **kwargs)
    return wrapper


def convert_id_to_str(cls: Type):
    def decorator(func):
        @wraps(func)
        def wrapper(type_dict: Dict[str, str]):
            if 'id' in type_dict:
                type_dict['_id'] = str(type_dict.pop('id'))
            if '_id' in type_dict:
                type_dict['_id'] = str(type_dict['_id'])
            class_type = cls(**type_dict)
            return func(class_type)
        return wrapper
    return decorator
