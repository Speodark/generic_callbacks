from functools import wraps
from dash import Input, Output, ctx
import ast
import vaex
import ast
import pandas as pd
from pprint import pprint
import dash
from dash import Input, Output, ALL, ctx, no_update
from .callback_functions import *

class Filter_Manager:
    def __init__(self):
        self._inputs = []
        self._outputs = []
        self._filter_functions = {}
        self._generate_component_functions = {}
        self._initiated = False
        self._df = None


    @property
    def df(self):
        return self._df


    @df.setter
    def df(self, new_df):
        self._df = new_df
    
    
    def start(self, df):
        if not self._initiated:
            self.df = df
            dash.callback(
                *[*self._outputs,*self._inputs]
            )(self.dashboard_update)

    
    def register_component_generator(self, _type):
        assert not self._initiated, "You cannot register components generators after initiating the callback!"
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
        assert not self._initiated, "You cannot register filter functions after initiating the callback!"
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
        assert not self._initiated, "You cannot register Inputs or Outputs after initiating the callback!"
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


    def dashboard_update(self, *args):
        # Get a list of all the types
        types = set(list(self._filter_functions.keys()) + list(self._generate_component_functions.keys()))
        # Create a dictionary with type as a key and empty dict as a value
        type_dict = {key: {} for key in types}
 

        # Update type_dict using the inputs_list
        update_type_dict_from_input_list(ctx.inputs_list, type_dict, args)
        # Update type_dict using the outputs_list and creating types_with_output_no_input list for 
        (
            types_with_output_no_input, 
            ordered_output_type_list
        ) = update_type_dict_from_output_list(ctx.outputs_list, type_dict, self._filter_functions)


        # we need to save the order with the empty outputs in order to return the components in the right order
        # because of that we create a new list for the ordrered output type list which will be used
        # to know which inputs dont have an output
        output_type_list = [
            output for output in ordered_output_type_list if output != "empty"
        ]


        # create a list of all the input and output types where the first types are the ones that doesnt have an output
        # because those who doesn't have an output only filter and don't change.
        # meaning i don't need to create multiple df so they won't effect themselfs
        input_type_list = list(type_dict.keys())
        input_without_output_types = list(set(input_type_list) - set(output_type_list))

        
        # remove all ids that appear in generate_component_functions and not in output_type_list from input_without_output_types
        # types that have output but do not appear in dashboard
        dont_have_output = list(set(self._generate_component_functions.keys()) - set(output_type_list))
        for output_type in dont_have_output:
            if output_type in input_without_output_types:
                input_without_output_types.remove(output_type)


        # This list will be ordered in order to optimize the df filtering
        # First the types that have an input and no output, means i only have to filter the main df
        # Second the output_type_list which have both the components with input and outputs 
        # Third will be the components that have an output but not an input
        # and components with only outputs 
        type_list = input_without_output_types.copy()
        type_list.extend(output_type_list)

        
        # Get the types that have an output and not an input to be last in the list
        # for optimization, we won't need to filter their dataframes because all the filters
        # has been done
        for component_type in types_with_output_no_input:
            type_list.remove(component_type)
        type_list.extend(types_with_output_no_input)


        # for each input type we go over all input types again and filter by them except for the current input_type.
        filtered_df = self.df
        individual_filtered_df = {}


        for component_type in type_list:

            # For each component/type we create an individual df depends on the sitation
            # 1: the type is does not filter we only need to create one df for all the components
            # 2: the type is does filter so we need to create df for each component in the type so
            #    we each component won't filter itself
            # 3: the type does not have an output, means we don't create a df because we don't create a component.
            create_df_for_individual_components(
                component_type,
                input_without_output_types,
                self._filter_functions,
                individual_filtered_df,
                type_dict,
                filtered_df
            )


            if component_type in self._filter_functions.keys():

                # Here we filter components that have both input and output, taking care they don't filter themself in the process
                components_input_and_output_filter(
                    component_type,
                    input_without_output_types,
                    individual_filtered_df,
                    self._filter_functions,
                    type_dict
                )
            
                # Filter the df by all the components for the next input type
                # note only this part of the code will run if the type only has an input and not output
                filtered_df = self._filter_functions[component_type](
                    df=filtered_df, data=type_dict[component_type]
                )

        # Creating the outputs list
        outputs = []
        for output_type in ordered_output_type_list:
            # if the output is empty (does not exsist in the dashboard) we need to append an empty list
            if output_type == "empty":
                outputs.append([]) # Switch to no_update
            else: 

                # If the component has an input and output, the generate function will get (dfs, components_data)
                # If the component has only an output, the generate function will get (df, components_data)
                components_of_type = self._generate_component_functions[output_type](
                    individual_filtered_df[output_type],
                    type_dict[output_type]
                )
                # check if components is a nested list (lists inside a list)
                # Happens if the components require more than 1 output to update like 
                # date_picker_range and range_sliders then we need to add to the list each component output
                is_nested = any(isinstance(component_arg, list) for component_arg in components_of_type)

                # if its a nested list we need to appened each arg individually
                # else we need to append all the components
                if is_nested:
                    for component in components_of_type:
                        outputs.append(component)
                else:
                    outputs.append(components_of_type)
        # returning the outputs Finishing the callback
        return outputs
