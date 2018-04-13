"""
# Global values used throughout the program
"""


# Location of the start directory of the narrative and database files
start_directory = "Story Segments/"


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
interrupt_addresses = [{'$Interrupt': '4/01'}]
error_addresses = [{'$User_Error': '4/05'}, {'$Creator_Error': '4/06'}, {'$Silence': '4/07'}]
constant_addresses = [{'restart': '4/04'}, {'wake_up': '4/02'}]
next_addresses = {}
ignore_addresses = []
file_locales = []
do_auto_select = False
is_reading = False


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
        last_function_result = map_function[function_code][0](*parameters)
    elif isinstance(function_code, str) and \
            isinstance(parameters, type(None)):
        last_function_result = map_function[function_code][0]()
    else:
        raise ValueError("ERROR - INVALID INPUTS " + \
                         str(type(function_code)) + str(function_code) + ' - ' + \
                         str(type(parameters)) + str(parameters))
    return last_function_result


# noinspection PyPep8
import Default_Commands


Default_Commands.addFunctionsToMap()


