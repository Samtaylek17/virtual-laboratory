name = 'quizzer'

from .quizz import ActivityMagic

def load_ipython_extension(ipython):
    ipython.register_magics(ActivityMagic)