# Customisation de l'interpreteur python
import sys
try:
    sys.setdefaultencoding('utf-8')
except AttributeError:
    pass
del sys
