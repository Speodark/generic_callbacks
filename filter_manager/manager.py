from functools import wraps
from dash import Input, Output
import ast


class Filter_Manager:
    def __init__(self):
        self._inputs = []
        self._outputs = []
        self._filter_functions = {}
        self._generate_component_functions = {}
        self._initiated = False

    
    def start(self):
        if not self._initiated:
            pass

    
    def register_component_generator(self, _type):
        assert isinstance(_type, str), "The type should be a string."

        if _type in self._generate_component_functions:
            raise Exception("The type is already registered in the _generate_component_functions.")

        def decorator(func):
            nonlocal _type
            self._generate_component_functions[_type] = func
            
            @wraps(func)
            def wrapper(*args, **kwrags):
                result = func(*args, **kwrags)

                return result
            
            return wrapper
        return decorator


    def register_filter_functions(self, _type):
        assert isinstance(_type, str), "The type should be a string."

        if _type in self._filter_functions:
            raise Exception("The type is already registered in the _filter_functions.")

        def decorator(func):
            nonlocal _type
            self._filter_functions[_type] = func
            
            @wraps(func)
            def wrapper(*args, **kwrags):
                result = func(*args, **kwrags)

                return result
            
            return wrapper
        return decorator


    def register_inputs_outputs(self, *args):
        for arg in args:
            assert isinstance(arg, Input) or isinstance(arg, Output), "You can only register Inputs or Outputs."
            id_dict = ast.literal_eval(arg.to_dict()['id'])
            assert id_dict.get('type',False), "You have to specifiy a type!"
            assert id_dict.get('id',False), "You have to specifiy an id!"
            assert self._generate_component_functions.get(id_dict['type'], False) or \
                   self._filter_functions.get(id_dict['type'], False), \
                   'You have to register the type in either the filter_functions or generate_component_functions\nBefore you add its Inputs and Outputs'
        
        for arg in args:
            if isinstance(arg, Input):
                self._inputs.append(arg)
            else:
                self._outputs.append(arg)
