"""
Wrapper module for running commands from source code (rather than endpoints)
"""

def command_liner(name, cli):
    '''Wrapper for running {0} from source.'''.format(name)

    msg = (
        '''
When used with Python 3, {0} requires the locale to be unicode.
Any of the above unicode definitions are acceptable.

To set the locale to be unicode, try:

$ export LC_ALL=en_US.utf8
$ {0} [ARGS]

Alternately, you should be able to specify the locale on the command-line:

$ LC_ALL=en_US.utf8 {0} [ARGS]

Be sure to substitute your unicode variant for en_US.utf8

'''.format(name))
    print(msg)
