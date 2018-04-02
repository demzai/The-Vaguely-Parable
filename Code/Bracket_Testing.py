"""
This module is for testing bracket pairings within a given string
It also converts a given code string into a pair of values [function name, function parameter list]
Tested with Python 3.5.4
"""


# Dependencies
import re
import ast


# Global Variables
# Provide opening and closing patterns, along with their priorities & whether a priority is nestable
opening = ['"', '(']
closing = ['"', ')']
priority = [1, 0]
nestable = {0: True, 1: False}
bracket_pairs = dict(zip(opening + closing, \
                         [[(closing + opening)[i], (priority + priority)[i]] \
                          for i in range(0, opening.__len__() * 2)]))


def getRegexFromList(listOfPatterns):
    """
    Generate the search term for the regular expression
    :param listOfPatterns:
    :return:
    >>> getRegexFromList(['"', '<--', '##', 'test'])
    '(\\\\t\\\\e\\\\s\\\\t|\\\\<\\\\-\\\\-|\\\\#\\\\#|\\\\")'
    """
    # Longer patterns first to prevent false negatives
    search_terms = sorted(listOfPatterns, key=len, reverse=True)
    regex = ""
    for term in search_terms:
        for char in str(term):
            regex = regex + '\\' + char  # Search for all characters literally
        regex = regex + '|'  # Search pattern = (a|b|c)
    return '(' + regex[:-1] + ')'  # Remove excess '|' and add brackets


def subNthOccurrence(target, replacement, nth_item, values):
    """
    Finds the nth occurrence of a list entry and replaces it
    :param target: occurrence to search for
    :param replacement: value to replace the occurrence with
    :param nth_item: the number of occurrences to go before replacement
    :param values: the list of values to search through
    :return: an updated list containing the replacement
    >>> subNthOccurrence('', ')', 2, ['3', '', 'hello', '', '', 'world'])
    ['3', '', 'hello', ')', '', 'world']
    """
    # If n is larger than the list, then no replacement can occur
    if nth_item >= values.__len__():
        return values

    count = 0
    for i in range(0, values.__len__()):
        if values[i] == target:
            count = count + 1
            if count == nth_item:
                values[i] = replacement
    # If not found, then ignore
    return values


def mergeNonSeparated(separator, values):
    """
    Take a list of values, and merge together the elements which don't have a separator between them
    :param separator: Value in need of being between other values
    :param values: List of values
    :return: Updated list of values
    >>> mergeNonSeparated('', ['', '', '', ')', '', '', '-'])
    ['', '', '', ')', '', '', '-']
    >>> mergeNonSeparated('', ['', ')', '', ']', '[', ''])
    ['', ')', '', '][', '']
    """
    updated_values = []
    stack = []
    for i in range(0, values.__len__()):
        if values[i] != separator:
            stack.append(values[i])
        if values[i] == separator or i is values.__len__()-1:
            if stack.__len__() is not 0:
                result = ''
                for var in stack:
                    result = result + str(var)
                updated_values = updated_values + [result]
            if values[i] == separator:
                updated_values = updated_values + ['']
            stack = []
    return updated_values


def doBracketsMatch(list_of_brackets, other_text=None):
    """
    Determine if brackets match up
    :param list_of_brackets: List of bracket patterns to be processed
    :param other_text: Text surrounding the bracket patterns
    :return [bool, list or int, list]:
    >>> doBracketsMatch(['"', ')', '"', ']', '['])
    [True, ['', ')', '', ']['], ['"', '"']]
    >>> doBracketsMatch(['"', ')', '"', '[', ']', ')'])
    [False, 6, ['"', ')', '"', '[', ']', ')'], ['"', '"', ')']]
    """

    # Create placeholders in case the additional text is unavailable
    if other_text is None:
        # noinspection PyUnusedLocal
        other_text = ['' for i in range(0, list_of_brackets.__len__())]

    stack = []
    endBrackets = []
    num_ignored = 0
    for i in range(0, list_of_brackets.__len__()):
        bracket = list_of_brackets[i]
        # Check empty stack conditions
        if stack.__len__() is 0:
            # Check for openings first to catch quotes
            if bracket in opening:
                stack.append(bracket)
                endBrackets.append(bracket)
            elif bracket in closing:
                endBrackets.append(bracket)
                return [False, i + 1, list_of_brackets, endBrackets]
            else:
                other_text = subNthOccurrence('', bracket, i + 1 - num_ignored, other_text)
                num_ignored = num_ignored + 1
                continue
        # Check for a matching bracket
        elif bracket == bracket_pairs[stack[-1]][0]:
            stack.pop()
            endBrackets.append(bracket)
        # Ignore cases:
        #  - False positives
        #  - Lower priority brackets
        #  - Equal priority brackets if nesting is not allowed
        elif bracket not in bracket_pairs or \
                bracket_pairs[bracket][1] < bracket_pairs[stack[-1]][1] or \
                (bracket_pairs[bracket][1] == bracket_pairs[stack[-1]][1] and \
                    not nestable[bracket_pairs[bracket][1]]):
            other_text = subNthOccurrence('', bracket, i + 1 - num_ignored, other_text)
            num_ignored = num_ignored + 1
            continue
        # New open bracket
        elif bracket in opening:
            stack.append(bracket)
            endBrackets.append(bracket)
        # Otherwise, unpaired close bracket
        else:
            endBrackets.append(bracket)
            return [False, i + 1, list_of_brackets, endBrackets]
    # If stack isn't empty, then there is an unpaired open bracket
    if stack.__len__() is not 0:
        return [False, list_of_brackets.__len__(), list_of_brackets, endBrackets]
    else:
        return [True, mergeNonSeparated('', other_text), endBrackets]


def resolveCodeBrackets(code):
    """
    Converts the code snippet into a list of elements
    :param code:
    :return:
    >>> resolveCodeBrackets('#Testy(1, #Fire(4, ") fly["))')
    [True, ['#Testy', '', '1, #Fire', '', '4, ', '', ') fly[', '', '', ''], ['(', '(', '"', '"', ')', ')']]
    >>> resolveCodeBrackets('#Testy(1, "yup"')
    Traceback (most recent call last):
     ...
    ValueError: Invalid bracketing in code - [False, 3, ['(', '"', '"'], ['(', '"', '"']]
    """
    regexp = getRegexFromList(opening + closing)
    patterns = re.findall(regexp, str(code))
    anti_patterns = (re.findall('[^' + regexp + ']*', str(code)))[:-1]
    code_breakdown = doBracketsMatch(patterns, anti_patterns)
    if code_breakdown[0] is False:
        raise ValueError('Invalid bracketing in code - ' + str(code_breakdown))
    else:
        return code_breakdown


def updateStack(stack, bracket):
    """
    Given a new bracket, keep track of what the currently open one is
    :param stack:
    :param bracket:
    :return:
    >>> updateStack([], '(')
    ['(']
    >>> updateStack([None], '(')
    [None, '(']
    >>> updateStack(['('], '(')
    ['(', '(']
    >>> updateStack(['('], ')')
    []
    >>> updateStack([], '"')
    ['"']
    >>> updateStack(['"'], '"')
    []
    >>> updateStack([], 'INCORRECT')
    Traceback (most recent call last):
     ...
    ValueError: Invalid bracketing in code - "INCORRECT" is not a valid bracket
    >>> updateStack([], ')')
    Traceback (most recent call last):
     ...
    ValueError: Unpaired close bracket detected - ")"
    """
    if bracket not in bracket_pairs:
        raise ValueError('Invalid bracketing in code - "' + str(bracket) + '" is not a valid bracket')
    elif stack.__len__() > 0 and stack[-1] is not None and bracket == bracket_pairs[stack[-1]][0]:
        stack.pop()
    elif bracket in opening:
        stack.append(bracket)
    else:
        raise ValueError('Unpaired close bracket detected - "' + str(bracket) + '"')
    return stack


def convertCodeToList(code):
    """
    # Takes a code in and returns a list pair [function name, function parameters]
    :param code:
    :return:
    >>> convertCodeToList('#T(1, #F(4, "8 _ 8", "&") )')
    ['#T', ['1', ['#F', ['4', '"8 _ 8"', '"&"']]]]
    >>> convertCodeToList("#T (\t ( ( \t(1, (2) \t) )\t ) )")
    ['#T', [['#bracket', [['#bracket', [['#bracket', ['1', ['#bracket', ['2']]]]]]]]]]
    >>> convertCodeToList("#Testy")
    ['#Testy', []]
    """
    result = resolveCodeBrackets(code)

    text = result[1]
    brackets = result[2]
    stack = [None]

    # Resolve whitespace and quotes
    for i in range(0, text.__len__()):
        # If not a bracket...
        if text[i] != '':
            # If not a string...
            if stack[-1] != '"':
                # Remove whitespace
                text[i] = ''.join(str(text[i]).split())
                # Add quotes around comma separated values
                text[i] = str(text[i]).replace(',', '","')
            # If a string...
            else:
                # Add delimited quotes around the string
                text[i] = '\\"' + str(text[i]) + '\\"'
            # Ensure all csv's, and only csv's, are quoted properly
            text[i] = '"' + str(text[i]) + '"'
            text[i] = str(text[i]).replace('"",', ',')
            text[i] = str(text[i]).replace(',""', ',')
        # If a bracket...
        else:
            # Update the stack
            updateStack(stack, brackets[0])
            brackets = brackets[1:]

    new_text = []
    brackets = result[2]
    stack = [None]

    # Resolve comma separation and brackets
    for i in range(0, text.__len__()):
        # If not a bracket...
        if text[i] != '':
            # If not a string...
            if stack[-1] != '"' and text[i] != '""':
                # Split into comma separated values and reinsert individually
                values = str(text[i]).split(',')
                for value in values:
                    new_text.append(value)
                    new_text.append(',')
                new_text.pop()
            # If a string...
            elif stack[-1] == '"':
                new_text.append(text[i])
        # If a bracket...
        else:
            # If an opening parenthesis, '('...
            if brackets[0] == '(' and new_text.__len__() is not 0:
                # If previous entry wasn't a comma, empty, or an opening bracket...
                if new_text[-1] != ',' and new_text[-1] != '' and new_text[-1][-1] != '[':
                    new_text[-1] = '[' + new_text[-1] + ',['
                else:
                    new_text.append('["#bracket",[')
            # If an closing parenthesis, ')'...
            elif brackets[0] == ')':
                new_text.append(']]')
            # Update the stack
            updateStack(stack, brackets[0])
            brackets = brackets[1:]

    # Convert to a single string
    string_list = ""
    for i in new_text:
        string_list = string_list + str(i)

    # Resolve 0-brackets condition
    if string_list[0] != '[':
        string_list = '[' + string_list + ',[]]'

    return ast.literal_eval(string_list)


# Testing prompt
if __name__ == '__main__':
    import doctest
    doctest.testmod()
