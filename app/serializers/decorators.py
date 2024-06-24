from functools import wraps
from typing import Type


def convert_id_to_str(cls: Type):
    def decorator(func):
        @wraps(func)
        def wrapper(user_dict):
            if '_id' in user_dict:
                user_dict['_id'] = str(user_dict['_id'])
                user = cls(**user_dict)
            return func(user)
        return wrapper
    return decorator
