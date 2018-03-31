"""
This module is for testing bracket pairings within a given string
Tested with Python 3.5.4
>>> resolveCodeBrackets('#Testy(1, #Fire(4, ") fly["))')
[[0, 'code', ['#Testy']], [1, 'code', ['1', '#Fire']], [2, 'code', ['4']], [3, 'string', ') fly[']]
>>> resolveCodeBrackets('#Testy(1, "yup"')
Traceback (most recent call last):
 ...
ValueError: Invalid bracketing in code - [False, 3, ['(', '"', '"'], ['(', '"', '"']]
"""


# Dependencies
import re


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


def getBracketHierarchy(brackets, texts):
    """
    # Takes a list of brackets and text, and assigns a bracket depth and type to that text
    :param brackets:
    :param texts:
    :return [hierarchical depth, code or string, original text]:
    >>> getBracketHierarchy(['(', '(', '"', '"', ')', ')'], \
    ['#Testy', '', '1, #Fire', '', '4, ', '', ') fly[', '', '', ''])
    [[0, 'code', ['#Testy']], [1, 'code', ['1', '#Fire']], [2, 'code', ['4']], [3, 'string', ') fly[']]
    >>> getBracketHierarchy(['(', '"', '"', '(', '"', '"', ')', ')'], \
    ['#test', '', '4,', '', 'lo', '', ', #hel', '', '', '5', '', '', ''])
    [[0, 'code', ['#test']], [1, 'code', ['4']], [2, 'string', 'lo'], [1, 'code', ['#hel']], [3, 'string', '5']]
    """
    stack = []
    bracket_num = 0
    hierarchy = 0
    breakdown = []
    # For each text...
    for text in texts:
        # If a bracket...
        if text == '':
            # If an opening bracket...
            if brackets[bracket_num] in opening and \
                    (stack.__len__() is 0 or \
                     brackets[bracket_num] != bracket_pairs[stack[-1]][0]):
                stack.append(brackets[bracket_num])
                hierarchy = hierarchy + 1
            # If a closing bracket...
            else:
                stack.pop()
                hierarchy = hierarchy - 1
            bracket_num = bracket_num + 1
        else:
            # If no brackets, or inside a parenthesis, then text is code
            if stack.__len__() is 0 or bracket_pairs[stack[-1]][1] is 0:
                text_type = 'code'
                # Remove excess whitespace
                text = "".join(text.split())
                # Breakdown into comma separated values
                text = [x for x in text.split(',') if x != '']
                breakdown = breakdown + [[hierarchy, text_type, text]]
            # Otherwise, it is a string
            else:
                text_type = 'string'
                breakdown = breakdown + [[hierarchy, text_type, text]]
    return breakdown


def resolveCodeBrackets(code):
    """
    Converts the code snippet into a list of elements
    :param code:
    :return:
    """
    regexp = getRegexFromList(opening + closing)
    patterns = re.findall(regexp, str(code))
    anti_patterns = (re.findall('[^' + regexp + ']*', str(code)))[:-1]
    code_breakdown = doBracketsMatch(patterns, anti_patterns)
    if code_breakdown[0] is False:
        raise ValueError('Invalid bracketing in code - ' + str(code_breakdown))
    else:
        return getBracketHierarchy(code_breakdown[2], code_breakdown[1])


# Testing prompt
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    while False:
        print("Please enter an example code for testing:")
        string = input()
        results = resolveCodeBrackets(string)
        print(str(results) + '\n')
