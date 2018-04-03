"""
# Global values used throughout the program
"""


# Location of the start directory of the narrative and database files
start_directory = "../Story Segments/"


# Provide opening and closing patterns, along with their priorities & whether a priority is nestable
opening = ['"', '(']
closing = ['"', ')']
priority = [1, 0]
nestable = {0: True, 1: False}
bracket_pairs = dict(zip(opening + closing, \
                         [[(closing + opening)[i], (priority + priority)[i]] \
                          for i in range(0, opening.__len__() * 2)]))


# State machine variables
database = {}
address_stack = []
next_addresses = []
file_locales = []


# Volatile variables, functions and function results
map_variable = {}
map_function = {}
last_function_result = None


# Master function used to call the default commands
def callFunction(function_code, parameters):
    """
    # Calls the function pointed to by the function code, using the parameters provided
    :param function_code: string
    :param parameters: list
    :return:
    """
    global last_function_result
    if isinstance(function_code, str) and \
            isinstance(parameters, list):
        last_function_result = map_function[function_code](*parameters)
    elif isinstance(function_code, str) and \
            isinstance(parameters, type(None)):
        last_function_result = map_function[function_code]()
    else:
        raise ValueError("ERROR - INVALID INPUTS " + str(function_code) + " AND " + str(parameters))
    return last_function_result


# noinspection PyPep8
import Default_Commands


Default_Commands.addFunctionsToMap()

