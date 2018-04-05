"""
# Contains the standard functions callable from the narrative files and databases
"""

# Dependencies
import time
import functools
import Globals as glbl
import Database_Management as dm
import Code_Interpreter as ci
import Extract_Narrative as en


# ///////////////////////////////////////////////////////
# /// HELPER FUNCTIONS
# ///////////////////////////////////////////////////////

# Add this files set of functions onto the functions list
def addFunctionsToMap():
    """
    # Adds the functions present within this file to the map of available functions to the user
    :return:
    >>> addFunctionsToMap()
    <function addition at
    """
    glbl.map_function.update({
        '###': [listSelect, True],
        '#segment': [listSelect, True],
        '#+': [addition, False],
        '#-': [subtraction, False],
        '#*': [multiplication, False],
        '#/': [division, False],
        '#%': [remainder, False],
        '#prev': [getPreviousAddress, False],
        '#&': [reference, False],
        '#forget': [popAddressStack, False],
        '#code': [getLastResult, False],
        '#quit': [endTheProgram, False],
        '#auto': [noUserChoice, False],
        '#delay': [delay, False],
        '#interrupt_start_local': [turnLocalInterruptsOn, False],
        '#interrupt_stop_local': [turnLocalInterruptsOff, False],
        '#interrupt_start_global': [turnGlobalInterruptsOn, False],
        '#interrupt_stop_global': [turnGlobalInterruptsOff, False],
        '#bracket': [bracketResolution, False],
        '#ignore': [ignoreNarrativeState, False]
    })

    # Provide an output for the doctest
    if __name__ == '__main__':
        print(str(glbl.map_function['#+'])[:21])
    return


def rememberParameters(f):
    """
    Aids a function in logging the parameters that have been passed to it previously
    Treats a function as an objects and gives it the variable "stack" to store parameters in at its own discretion
    :param f:
    :return:
    """

    @functools.wraps(f)
    def func(*args):
        """
        Function to be decorated
        :param args:
        :return:
        """
        func.stack += [args[0]]

        # If the first node is faulty, then ignore the whole thing and reset
        if func.stack[0][:3] != '###':
            func.stack = []

        # If a start and end '###' have been found, run the code and reset the stack
        elif len(listSelect.stack) > 3 and listSelect.stack[-1][:3] == '###':
            return_value = f(*args)
            func.stack = []
            return return_value
        return None

    func.stack = []
    return func


def countCalls(f):
    """
    Aids a function in keeping tabs on how many times it has been called
    Treats a function as an objects and gives it the variable "count" which auto-increments on each call
    :param f:
    :return:
    """

    @functools.wraps(f)
    def func(*args):
        """
        Function to be decorated
        :param args:
        :return:
        """
        func.count += 1
        return f(*args)

    func.count = 0
    return func


# ///////////////////////////////////////////////////////
# /// DEFAULT FUNCTIONS
# ///////////////////////////////////////////////////////

# #segment
# noinspection PyUnusedLocal
@rememberParameters
def listSelect(line_contents):
    """
    # A simple switch case function
    :param line_contents:
    :return :
    """
    # Resolve the variable being compared against
    code_type = en.findCodeLines([str(listSelect.stack[1][0])])[0]
    if code_type == 'Code' or code_type == 'Variable' or code_type == 'Container':
        variable = ci.interpretParameters([str(listSelect.stack[1][0])])[0]
    else:
        variable = listSelect.stack[1][0]

    # For each case statement, compare to the state variable
    num_cases = len(listSelect.stack)-1
    selected_case = -1
    for i in range(2, num_cases):
        case = listSelect.stack[i]

        # Ignore faulty cases
        if len(case) is not 2 and len(case) is not 3:
            print("WARNING - FAULTY CASE: " + str(case))
            continue

        # If a default case has been presented at the end:
        if i is num_cases-1 and isinstance(case[0], str) is True and case[0] == 'else':
            selected_case = i
            break

        # If testing a numerical value over a range:
        elif (isinstance(variable, int) or isinstance(variable, float)) and \
                isinstance(case[0], str) and len(str(case[0]).split('<')) is 2:
            # Get the ranges and check for their validity and truth value
            check_range = ci.interpretParameters(case[0].split('<'))
            if (isinstance(check_range[0], int) or isinstance(check_range[0], float)) and \
                    (isinstance(check_range[1], int) or isinstance(check_range[1], float)) and \
                    check_range[0] <= variable < check_range[1]:
                selected_case = i
                break

        # All other tests should be equalities over same-typed values
        elif type(variable) == type(case[0]) and variable == case[0]:
            selected_case = i
            break

    # Resolve based on the selection, defaulting to None if no valid selection was made
    if selected_case is -1:
        print('WARNING - NO VALID CASES FOUND')
        return None
    elif len(listSelect.stack[selected_case]) is 3 and code_type != 'Variable':
        print('WARNING - INVALID CASE DETECTED: ' + str(listSelect.stack[selected_case]))
        return None
    else:
        # If a valid triplet found, replace the variable with the presented contents
        if len(listSelect.stack[selected_case]) is 3:
            ci.interpretCode(str(listSelect.stack[1][0]) + \
                             '(' + str(listSelect.stack[selected_case][1]) + ')')
        # Return the selected switch-case value
        return listSelect.stack[selected_case][-1]


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


# #prev
@countCalls
def getPreviousAddress():
    """
    Gets the address of the last narrative element visited
    :return:
    """
    return glbl.address_stack[-getPreviousAddress.count-1]


# #&
def reference(referenced_address):
    """
    # References a file and returns the list of addresses that can be reached from there
    # Ignores all calls to "prev"
    :param referenced_address:
    :return:
    """
    # @todo check for bugs - no, SERIOUSLY check for bugs!
    calls_to_previous = getPreviousAddress.count
    address_list = dm.getFromMap(referenced_address, glbl.database)
    return_list = []
    delayed = []

    # Look at the addresses pointed to & parse them
    for address in address_list:
        returned_value = dm.parseDatabaseEntry([address_list[address], address])
        if isinstance(returned_value, dict):
            returned_value = [returned_value]
        else:
            returned_value = [[returned_value, address[1]]]

        # Referenced addresses have a lower priority than current addresses, so delay their assimilation
        if len(address_list[address]) > 1 and address_list[address][:2] == '#&':
            delayed += [returned_value]
            continue

        # Add on the processed value
        return_list += returned_value

        # Ensure the #prev counter doesn't creep
        getPreviousAddress.count = calls_to_previous

    # @todo test whether this actually works as expected!
    # Add on the delayed entries
    for address in delayed:
        return_list += address

    return return_list


# #forget
def popAddressStack():
    """
    # Forgets the current address
    # Useful for narrative points where nothing happens
    :return:
    """
    glbl.address_stack.pop()
    return


# #code
def getLastResult():
    """
    # Gets the last value returned from any of the functions in this python file
    :return:
    """
    return glbl.last_function_result


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
    glbl.do_auto_select = True
    return


# #delay
def delay(delay_time):
    """
    # Wait and do nothing until the time delay (in seconds) is finished
    :param delay_time:
    :return:
    """
    # @todo - make this into an interrupt based timer!
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
    """
    Resolves the contents of parentheses (a) -> a
    :param contents:
    :return:
    """
    return contents


# #ignore
def ignoreNarrativeState(state_to_be_ignored):
    """
    # Appends a state (e.g. "look_around") to the ignore list
    :param state_to_be_ignored:
    :return:
    """
    # @todo ensure that this can run from csv / database files!
    glbl.ignore_addresses += [state_to_be_ignored]
    return


addFunctionsToMap()
if __name__ == '__main__':
    import doctest

    doctest.testmod()
