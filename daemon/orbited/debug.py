import traceback
import sys


def debug(*args):
    return
    if len(args) == 1:
        print args[0]
    else:
        print args
#    print data
    
    
    
def tbinfo():
    return traceback.print_stack()
    try:
        raise Exception("TBINFO")
    except:
        a,b,tb = sys.exc_info()
        traceback.print_tb(tb)
        return
    