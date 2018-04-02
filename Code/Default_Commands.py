"""
# Contains the standard functions callable from the narrative files and databases
"""


# Dependencies
import time
import Globals


# Add this files set of functions onto the functions list
def addFunctionsToMap():
    """
    # Adds the functions present within this file to the map of available functions to the user
    :return:
    >>> addFunctionsToMap()
    <function addition at
    """
    Globals.map_function.update({
        '###': listSelect,
        '#+': addition,
        '#-': subtraction,
        '#*': multiplication,
        '#/': division,
        '#%': remainder,
        '#&': reference,
        '#code': getLastResult,
        '#prev': getPreviousAddress,
        '#quit': endTheProgram,
        '#auto': noUserChoice,
        '#delay': delay,
        '#interrupt_start_local': turnLocalInterruptsOn,
        '#interrupt_stop_local': turnLocalInterruptsOff,
        '#interrupt_start_global': turnGlobalInterruptsOn,
        '#interrupt_stop_global': turnGlobalInterruptsOff,
        '#bracket': bracketResolution
    })

    # Provide an output for the doctest
    if __name__ == '__main__':
        print(str(Globals.map_function['#+'])[:21])
    return


# ###
def listSelect(selection_variable, cases, results):
    """
    # A simple switch case function
    :param selection_variable:
    :param cases:
    :param results:
    """
    # @todo insert code
    return


# #+
def addition(variable1, variable2):
    """
    # Sums together two variables of approximately the same type if they're numerical, strings, or lists
    :param variable1:
    :param variable2:
    :return:
    >>> addition(1, 1)
    2
    >>> addition(1.0, 1)
    2.0
    >>> addition(1, 1.5)
    2.5
    >>> addition(2.0, 3.5)
    5.5
    >>> addition('hello ', 'world!')
    'hello world!'
    >>> addition([1], ['one'])
    [1, 'one']
    >>> addition(1, 'one')
    """
    if (isinstance(variable1, int) and isinstance(variable2, int)) or \
            (isinstance(variable1, float) and isinstance(variable2, int)) or \
            (isinstance(variable1, int) and isinstance(variable2, float)) or \
            (isinstance(variable1, float) and isinstance(variable2, float)) or \
            (isinstance(variable1, str) and isinstance(variable2, str)) or \
            (isinstance(variable1, list) and isinstance(variable2, list)):
        return variable1 + variable2
    else:
        return None


# #-
def subtraction(variable1, variable2):
    """
    # Subtracts two variables of numerical type from each other
    :param variable1:
    :param variable2:
    :return:
    >>> subtraction(1, 1)
    0
    >>> subtraction(1.0, 1)
    0.0
    >>> subtraction(1, 1.5)
    -0.5
    >>> round(subtraction(1.8, 1.7),2)
    0.1
    >>> subtraction(1, 'one')
    """
    if (isinstance(variable1, int) and isinstance(variable2, int)) or \
            (isinstance(variable1, float) and isinstance(variable2, int)) or \
            (isinstance(variable1, int) and isinstance(variable2, float)) or \
            (isinstance(variable1, float) and isinstance(variable2, float)):
        return variable1 - variable2
    else:
        return None


# #*
def multiplication(variable1, variable2):
    """
    # Multiplies two variables of valid types together
    :param variable1:
    :param variable2:
    :return:
    >>> multiplication(1, 1)
    1
    >>> multiplication(1.0, 1)
    1.0
    >>> multiplication(2, 1.5)
    3.0
    >>> multiplication(5.5, 3.5)
    19.25
    >>> multiplication('hey ', 2)
    'hey hey '
    >>> multiplication(2, 'hey ')
    'hey hey '
    >>> multiplication([1], 2)
    [1, 1]
    >>> multiplication(3, [1])
    [1, 1, 1]
    >>> multiplication('one', 'one')
    >>> multiplication([1], 'one')
    >>> multiplication('one', [1])
    >>> multiplication([1], [1])
    """
    if (isinstance(variable1, int) and isinstance(variable2, int)) or \
            (isinstance(variable1, float) and isinstance(variable2, int)) or \
            (isinstance(variable1, int) and isinstance(variable2, float)) or \
            (isinstance(variable1, float) and isinstance(variable2, float)) or \
            (isinstance(variable1, int) and isinstance(variable2, str)) or \
            (isinstance(variable1, str) and isinstance(variable2, int)) or \
            (isinstance(variable1, int) and isinstance(variable2, list)) or \
            (isinstance(variable1, list) and isinstance(variable2, int)):
        return variable1 * variable2
    else:
        return None


# #/
def division(variable1, variable2):
    """
    # Divides two numerically typed variables
    :param variable1:
    :param variable2:
    :return:
    >>> division(1, 1)
    1.0
    >>> division(1.0, 1)
    1.0
    >>> division(-1, 2.0)
    -0.5
    >>> division(3.2, 2.0)
    1.6
    >>> division(1.0, 0.0)
    >>> division(1, 'one')
    """
    if ((isinstance(variable1, int) and isinstance(variable2, int)) or \
            (isinstance(variable1, float) and isinstance(variable2, int)) or \
            (isinstance(variable1, int) and isinstance(variable2, float)) or \
            (isinstance(variable1, float) and isinstance(variable2, float))) and \
            (variable2 is not 0) and (variable2 != 0.0):
        return variable1 / variable2
    else:
        return None


# #%
def remainder(variable1, variable2):
    """
    # Finds the remainder after division between two numerically typed variables
    :param variable1:
    :param variable2:
    :return:
    >>> remainder(1, 1)
    0
    >>> remainder(1.0, 1)
    0.0
    >>> remainder(1, 1.5)
    1.0
    >>> round(remainder(3.2, 2.0), 2)
    1.2
    >>> remainder(1.0, 0.0)
    >>> remainder(1, 'one')
    """
    if ((isinstance(variable1, int) and isinstance(variable2, int)) or \
            (isinstance(variable1, float) and isinstance(variable2, int)) or \
            (isinstance(variable1, int) and isinstance(variable2, float)) or \
            (isinstance(variable1, float) and isinstance(variable2, float))) and \
            (variable2 is not 0) and (variable2 != 0.0):
        return variable1 % variable2
    else:
        return None


# #&
def reference(referenced_address):
    """
    # References a file and returns the list of addresses that can be reached from there
    # Ignores all calls to "prev"
    :param referenced_address:
    :return:
    """
    # @todo insert code
    return


# #code
def getLastResult():
    """
    # Gets the last value returned from any of the functions in this python file
    :return:
    """
    return Globals.last_function_result


# #prev
def getPreviousAddress():
    """
    Gets the address of the last narrative element visited
    :return:
    """
    return Globals.addresses[0]


# #quit
def endTheProgram():
    """
    # Literally ends the program
    :return:
    """
    quit(0)


# #auto
def noUserChoice():
    """
    # Do not allow the user to select a new narrative path, just pick the first option
    :return:
    """
    # @todo insert code
    return


# #delay
def delay(delay_time):
    """
    # Wait and do nothing until the time delay (in seconds) is finished
    :param delay_time:
    :return:
    """
    time.sleep(delay_time)
    return


# #interrupt_start_local
def turnLocalInterruptsOn():
    """
    # Allow looking for interrupts specific to the current narrative file
    :return:
    """
    # @todo insert code
    return


# #interrupt_stop_local
def turnLocalInterruptsOff():
    """
    # Prevent looking for interrupts specific to the current narrative file
    :return:
    """
    # @todo insert code
    return


# #interrupt_start_global
def turnGlobalInterruptsOn():
    """
    # Allow looking for interrupts general to the entire story
    :return:
    """
    # @todo insert code
    return


# #interrupt_stop_global
def turnGlobalInterruptsOff():
    """
    # Prevent looking for interrupts general to the entire story
    :return:
    """
    # @todo insert code
    return


# #bracket
def bracketResolution(contents):
    # @todo insert code
    return contents


addFunctionsToMap()
if __name__ == '__main__':
    import doctest
    doctest.testmod()
