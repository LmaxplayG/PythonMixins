from __init__ import *

def test():
    flag = "flag"
    del flag
    print('before')
    print('after')

@Mixin(target=test, at=Head())
def testHead():
    print('head', locals())

@Mixin(target=test, at=Return())
def testReturn():
    print('ret', locals())

@Mixin(target=test, at=Opcode('DELETE_FAST'))
def testOpcode():
    print('opcode', locals())

@Mixin(target=test, at=Match.after(lambda: print('before')))
def testMatch():
    print('match')

import os
def custom_print(s):
    print('here', s)

@Mixin(target=os.getenv, at=Return(), globals=dict(custom_print=custom_print))
def getEnvMixin(key):
    custom_print(key)
