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
