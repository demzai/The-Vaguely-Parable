"""
# Takes in a code and interprets its meaning.
Traceback (most recent call last):
 ...
ValueError: Invalid bracketing in code - [False, 3, ['(', '"', '"'], ['(', '"', '"']]
"""


# Dependencies
import Bracket_Testing as bt


def attemptConversion(string, to_type):
    """
    # Attempts to convert a given string into either an integer, floating point variable or boolean
    :param string:
    :param to_type:
    :return:
    >>> attemptConversion('9', 'int')
    [True, 9]
    >>> attemptConversion('8.2', 'int')
    [False, None]
    >>> attemptConversion('True', 'int')
    [False, None]
    >>> attemptConversion('9', 'float')
    [True, 9.0]
    >>> attemptConversion('8.2', 'float')
    [True, 8.2]
    >>> attemptConversion('True', 'float')
    [False, None]
    >>> attemptConversion('9', 'bool')
    [False, None]
    >>> attemptConversion('8.2', 'bool')
    [False, None]
    >>> attemptConversion('True', 'bool')
    [True, True]
    >>> attemptConversion('False', 'bool')
    [True, False]
    """
    try:
        if to_type == 'int':
            return [True, int(string)]
        elif to_type == 'float':
            return [True, float(string)]
        elif to_type == 'bool':
            if string == 'True':
                return [True, True]
            elif string == 'False':
                return [True, False]
            else:
                return [False, None]
    except ValueError:
        return [False, None]
    finally:
        del string, to_type


def interpretParameters(parameters):
    """
    # Scans through each parameter presented and converts it to the correct variable type
    :param parameters:
    :return:
    """
    # If nothing to do, do nothing
    if parameters.__len__() is 0:
        return None

    formatted_parameters = []
    # For each parameter:
    for param in parameters:
        # If a list, then there's more code to be checked out
        if isinstance(param, list):
            formatted_parameters = formatted_parameters + [interpretCode(param)]
        # If not a string, then there's a problem
        elif isinstance(param, str) is False:
            raise ValueError("ERROR - " + str(param) + " IS NOT A VALID PARAMETER TYPE - " + str(type(param)))
        # If parameter is meant to be a string, then leave as a string without the quotes
        elif param[0] == '"' and param[-1] == '"':
            formatted_parameters = formatted_parameters + [param[1:-1]]
        # Otherwise, attempt to determine it type
        # Valid types remaining are bool, int, and float
        else:
            to_type = 'int'
            while attemptConversion(param, to_type)[0] is False:
                if to_type == 'int':
                    to_type = 'float'
                elif to_type == 'float':
                    to_type = 'bool'
                else:
                    raise ValueError("ERROR - " + str(param) + " CANNOT BE CONVERTED")
            formatted_parameters = formatted_parameters + [attemptConversion(param, to_type)[1]]

    return formatted_parameters


def interpretCode(code):
    # If the code is poorly formatted, then raise an exception
    if code.__len__() is not 2 or \
                    isinstance(code[0], str) is False or \
                    isinstance(code[1], list) is False or \
                    code[0].__len__() <= 1 or \
                    code[0][0] != '#':
        raise ValueError("ERROR - " + str(code) + " IS INCORRECT CODE!")

    # Interpret parameters first
    parameters = interpretParameters(code[1])

    # Then perform the function
    # If code name starts with a capital letter, then it refers to a variable
    if code[0][1] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        # If no parameters were passed, then retrieve & return the value
        if code[1].__len__() is 0:
            a = 1
        # Otherwise store the values
        else:
            a = 2
    # If code isn't in the list of predefined functions, then raise an exception
    elif False:
        raise ValueError("ERROR - " + str(code[0]) + " IS NOT A VALID COMMAND!")
    # If there aren't enough parameters for the function, then raise an exception
    elif False: # @todo change str(len(code)) to get the actual number of parameters
        raise ValueError("ERROR - " + str(code) + " DOES NOT CONTAIN " + str(len(code)) + " PARAMETERS")
    # Otherwise, get the function and perform it
    else:
        a = parameters
        # Store the returned value into #code
        # Return whatever the function returns
    return a


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # Convert the code into a list
    code_string = bt.convertCodeToList("#Testy")
    print(str(code_string))


