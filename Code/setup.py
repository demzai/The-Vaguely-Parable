"""
Generates a stand-alone .exe file of the project when run
"""


from cx_Freeze import setup, Executable

base = None

executables = [Executable("Main.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {
        'packages': packages,
    },
}

setup(
    name='The_Vaguely_Parable',
    options=options,
    version='1.0.0',
    packages=[''],
    url='',
    license='',
    author='Student',
    author_email='',
    description='',
    executables=executables,
    requires=['cx_Freeze', 'gtts']
)
