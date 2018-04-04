"""
# Takes in a code and interprets its meaning.
Traceback (most recent call last):
 ...
ValueError: Invalid bracketing in code - [False, 3, ['(', '"', '"'], ['(', '"', '"']]
"""
# @todo write test scripts


# Dependencies
import Bracket_Testing as bt
import Globals as glbl
from inspect import signature


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
        elif to_type == 'string':
            return [True, str(string)]
    except ValueError:
        return [False, None]
    finally:
        del string, to_type


def interpretParameters(parameters, is_segment=False):
    """
    # Scans through each parameter presented and converts it to the correct variable type
    :param parameters: list
    :param is_segment: bool
    :return:
    """
    # print('\t\t' + str(parameters))  # -----------------------------------------------------------------------------
    # If nothing to do, do nothing
    if parameters is None or parameters.__len__() is 0:
        return None

    formatted_parameters = []
    # For each parameter:
    for param in parameters:
        # If a list, then there's more code to be checked out
        if isinstance(param, list):
            formatted_parameters = formatted_parameters + [interpretCode(param)]
        # If a string beginning with '#', then there's a variable to be resolved
        elif isinstance(param, str) and param[0] == '#':
            formatted_parameters = formatted_parameters + [interpretCode(bt.convertCodeToList(param))]
        # If not a string, then there's a problem
        elif isinstance(param, str) is False:
            raise ValueError("ERROR - " + str(param) + " IS NOT A VALID PARAMETER TYPE - " + str(type(param)))
        # If parameter is meant to be a string, then leave as a string without the quotes
        elif param[0] == '"' and param[-1] == '"':
            formatted_parameters = formatted_parameters + [param[1:-1]]
        # Otherwise, attempt to determine it type
        # Valid types remaining are bool, int, and float... if those fail default to an error or string?
        else:
            to_type = 'int'
            while attemptConversion(param, to_type)[0] is False:
                if to_type == 'int':
                    to_type = 'float'
                elif to_type == 'float':
                    to_type = 'bool'
                elif is_segment is True:  # Some segment options may need further processing!
                    to_type = 'string'
                else:
                    raise ValueError("ERROR - " + str(param) + " CANNOT BE CONVERTED. is_segment = " + str(is_segment))
            formatted_parameters = formatted_parameters + [attemptConversion(param, to_type)[1]]

    return formatted_parameters


def interpretCode(code):
    """
    # Interprets the code and performs the necessary functions
    :param code:
    :return:
    """
    # print(str(code) + ' - ' + str(type(code)))  # ------------------------------------------------------------------
    if isinstance(code, str):
        code = bt.convertCodeToList(code)
    elif not isinstance(code, list):
        raise ValueError("ERROR - INVALID CODE: " + str(code))
    # print('\t' + str(code))  # -------------------------------------------------------------------------------------
    # If the code is poorly formatted, then raise an exception
    """
    # Interprets the code and throws errors when something obvious is wrong
    :param code:
    :return:
    """
    if code.__len__() is not 2 or \
            isinstance(code[0], str) is False or \
            isinstance(code[1], list) is False or \
            code[0].__len__() <= 1 or \
            code[0][0] != '#':
        raise ValueError("ERROR - " + str(code) + " IS INCORRECT CODE!")

    # Interpret parameters first
    parameters = interpretParameters(code[1], code[0] == '#segment')
    # print('\t\t\t' + str(parameters))  # ---------------------------------------------------------------------------

    # Then perform the function
    # If code name starts with a capital letter, then it refers to a variable
    if code[0][1] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        # If the variable exists and no parameters were passed, then retrieve & return the value
        if parameters is None or parameters.__len__() is 0:
            if code[0] not in glbl.map_variable:
                raise ValueError("ERROR - " + str(code[0]) + " WAS NOT FOUND!\n" + str(glbl.map_variable))
            else:
                glbl.last_function_result = glbl.map_variable[code[0]]
        # Otherwise store the values
        elif parameters.__len__() is 1:
            glbl.map_variable.update({code[0]: parameters[0]})
            glbl.last_function_result = None
        else:
            raise ValueError("ERROR - " + str(code) + " CONTAINS TOO MANY PARAMETERS TO BE STORED!")
        return glbl.last_function_result

    # If code does not start with a capital letter, then it refers to a function
    else:
        # If code isn't in the list of predefined functions, then raise an exception
        if code[0] not in glbl.map_function:
            raise ValueError("ERROR - " + str(code[0]) + " IS NOT A VALID COMMAND!\n" + str(glbl.map_function))

        # Resolve len(None) = DNE bug
        if glbl.map_function[code[0]][1] is True:
            if parameters is None:
                parameters = '###'
            parameters = [parameters]
            len_param = 1
        elif parameters is None:
            len_param = 0
        else:
            len_param = len(parameters)
        if signature(glbl.map_function[code[0]][0]).parameters is None:
            len_fun = 0
        else:
            len_fun = len(signature(glbl.map_function[code[0]][0]).parameters)

        # If there aren't enough parameters for the function, then raise an exception
        if len_param is not len_fun:
            raise ValueError("ERROR - " + str(code) + " DOES NOT CONTAIN " + \
                             str(len(signature(glbl.map_function[code[0]][0]).parameters)) + " PARAMETERS!")
        # Otherwise, get the function and perform it
        else:
            result = glbl.callFunction(code[0], parameters)
            # print('\t\t\t' + str(code) + ' - ' + str(parameters) + ' - ' + str(result))  # -------------------------
            return result


def parseContainerCode(container_text, container_codes):
    """
    Takes a textual container in and converts the code segments into text
    :param container_text:
    :param container_codes:
    :return:
    """
    # [type, text, [codes]]

    # For each code:
    for code in container_codes:
        # If the code was found within the text, then split it, else raise an exception
        if len(container_text.split(code, 1)) is not 2:
            raise ValueError("ERROR - CODE NOT FOUND WITHIN STRING!")
        else:
            # Insert the result of the code in its place
            code_split = container_text.split(code, 1)
            code_split[0] += str(interpretCode(code))
            container_text = code_split[0] + code_split[1]
    return container_text


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # Convert the code into a list
    print(str(interpretCode('#Testy("Hello ")')))
    print(str(glbl.map_variable))
    print(str(interpretCode('#+(#Testy,"World!!!")')))
    print(str(interpretCode('#delay(0.1)')))
    print(str(interpretCode(' # + ( # * ( "a" , 5\t  ) , # * ( "gh" , 1 ) ) ')))
    print(str(glbl.last_function_result))

