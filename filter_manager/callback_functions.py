# gets the dictionary of dictionaries of all the Inputs type and values
# the value of type_dict will look like this:
# type_dict = {
#   type: {
#     full_id_1: {
#       property1: value,
#       property2: value
#     }
#   }
# }
def update_type_dict_from_input_list(inputs_list, type_dict, args):
    for callback_input_index, callback_input in enumerate(inputs_list):
        # If we have components.
        if callback_input:
            for component_index, component in enumerate(callback_input):
                component_type = component["id"]["type"]
                component_id = str(component["id"])
                if type_dict[component_type].get(component_id, None) is not None:
                    type_dict[component_type][component_id][component["property"]] = args[callback_input_index][component_index]
                else:
                    type_dict[component_type][component_id] = {
                        component["property"]: args[callback_input_index][component_index]
                    }
    
    # return type_dict


# adds dictionaries of all outputs type and values that doesn't have an input to the type_dict
# the value is null because there are no args for output
# Also creates the variable types_with_output_no_input used later in the filtering section and for optimization
def update_type_dict_from_output_list(outputs_list, type_dict, filter_functions):
    types_with_output_no_input = []
    ordered_output_type_list = []
    for callback_output in outputs_list:
        # Adds empty for the ordered_output_type_list incase the component doesnt exists on the dashboard
        if not callback_output:
            ordered_output_type_list.append("empty")
        else:
            for component in callback_output:
                component_type = component["id"]["type"]
                component_id = str(component["id"])
                # if the type is not in the ordered_output_type_list add it
                if component_type not in ordered_output_type_list:
                    ordered_output_type_list.append(component_type)

                if component_type not in filter_functions.keys():
                    if component_type not in types_with_output_no_input:
                        types_with_output_no_input.append(component_type)

                    if type_dict[component_type].get(component_id, None) is not None:
                        type_dict[component_type][component_id][
                            component["property"]
                        ] = ""
                    else:
                        type_dict[component_type][component_id] = {
                            component["property"]: ""
                        }
    return types_with_output_no_input, ordered_output_type_list



def create_df_for_individual_components(
    component_type, 
    input_without_output_types, 
    filter_functions, 
    individual_filtered_df,
    type_dict,
    filtered_df
):
    # if the component has an output create a dictionary for the type and value a copy of filtered_df
    # for each component in the type
    if component_type not in input_without_output_types:
        if component_type in filter_functions.keys():
            # create the type in the dictioanry
            individual_filtered_df[component_type] = {}
            # for each different input component in that specific type create a key and copy the filtered_df
            for key in type_dict[component_type].keys():
                individual_filtered_df[component_type][key] = filtered_df
        else:
            # If its not a filter component it will be the last elements in the list and will
            # use the last filtered dataframe for all its components.
            individual_filtered_df[component_type] = filtered_df


def components_input_and_output_filter(
    component_type,
    input_without_output_types,
    individual_filtered_df,
    filter_functions,
    type_dict
):
    # checking the input has an output if it does then we need to create a df for each component in the type
    # and filter all of the exsisting dfs, and for each df we need to not filter by itself.
    # Example: if we filter a barchart by its chosen value we will not be able to deselect the filter.
    if component_type not in input_without_output_types:
        # filter each filtered df by all the different components by the type components
        for filtered_df_type in individual_filtered_df.keys():
            for filtered_df_key in individual_filtered_df[
                filtered_df_type
            ].keys():
                # update the df to the filtered one by the component filter function
                # The filtering function is the one in the component_type key.
                individual_filtered_df[filtered_df_type][
                    filtered_df_key
                ] = filter_functions[component_type](
                    df=individual_filtered_df[filtered_df_type][
                        filtered_df_key
                    ],
                    data=type_dict[component_type],
                    active_id=filtered_df_key,
                )