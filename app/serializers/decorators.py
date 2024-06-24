from functools import wraps
from typing import Type, Dict


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
