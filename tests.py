from mixin import Mixin, Opcode, Head, Tail, Return, Match, Call
from testing.testlib import test, exitTests, Expect




@test(name="Match")
def testMatch():
    def matchTestFunc():
        x = 1
        return 1
    def toMatch():
        return 1
    @Mixin(matchTestFunc, at=Match(toMatch))
    def matchTestMixin():
        return 2
    
    Expect(matchTestFunc()).toBe(2)



@test(name="Head")
def testHead():
    def headTestFunc():
        return 1
    @Mixin(headTestFunc, at=Head())
    def headTestMixin():
        return 2
    
    Expect(headTestFunc()).toBe(2)



@test(name="Tail")
def testTail():
    def tailTestFunc():
        x = 1
        return x

    @Mixin(tailTestFunc, at=Tail())
    def tailTestMixin():
        return 2
    
    Expect(tailTestFunc()).toBe(2)



@test(name="Opcode")
def testOpcode():
    def opcodeTestFunc():
        x = 1
        return x

    @Mixin(opcodeTestFunc, at=Opcode('RETURN_VALUE'))
    def opcodeTestMixin():
        return 2
    
    Expect(opcodeTestFunc()).toBe(2)



@test(name="Return")
def testReturn():
    def returnTestFunc():
        return 1
    @Mixin(returnTestFunc, at=Return())
    def returnTestMixin():
        return 2
    
    Expect(returnTestFunc()).toBe(2)



@test(name="Call")
def testCall():
    def dummyFunc():
        return
    def callTestFunc():
        dummyFunc()
        return 1
    @Mixin(callTestFunc, at=Call())
    def callTestMixin():
        return 2
    
    Expect(callTestFunc()).toBe(2)



@test(name="Return.after")
def testAfter():
    def afterTestFunc():
        return 1
    @Mixin(afterTestFunc, at=Return().after())
    def afterTestMixin():
        return 2
    
    Expect(afterTestFunc()).toNotBe(2)



@test(name="Mixin property force_ret")
def testForceReturn():
    def forceReturnTestFunc():
        return 1
    @Mixin(forceReturnTestFunc, at=Head(), force_ret=True)
    def forceReturnTestMixin():
        return
    
    Expect(forceReturnTestFunc()).toBe(None)



@test(name="Mixin property globals")
def testGlobals():
    def returnsTrue():
        return True
    
    def globalsTestFunc():
        return False

    @Mixin(globalsTestFunc, at=Head(), globals={'rt': returnsTrue})
    def globalsTestMixin():
        return rt()

    Expect(globalsTestFunc()).toBe(True)



@test(name="Accessing local variables")
def testLocalVariables():
    def doesNothing():
        return

    def localTestFunc():
        x = 1
        doesNothing()
        def test():
            doesNothing()
        test()
        return x

    def xAssignDummy():
        x = 1

    @Mixin(localTestFunc, at=Match(lambda : doesNothing()))
    def localTestMixin():
        x = 2
    
    Expect(localTestFunc()).toBe(2)



@test(name="Accessing arguments")
def testArguments():
    def argumentTestFunc(x):
        return x

    @Mixin(argumentTestFunc, at=Head(), force_ret=True)
    def argumentTestMixin(x):
        return x + 1
    
    Expect(argumentTestFunc( 1)).toBe(2)
    Expect(argumentTestFunc( 2)).toBe(3)
    Expect(argumentTestFunc(-1)).toBe(0)
    Expect(argumentTestFunc(-2)).toBe(-1)
    Expect(argumentTestFunc(0.3)).toBe(1.3)



@test(name="Accessing arguments with default values")
def testArgumentsWithDefaultValues():
    def argumentTestFunc(x, y=1):
        return x + y

    @Mixin(argumentTestFunc, at=Head(), force_ret=True)
    def argumentTestMixin(x, y=1):
        return x + y + 1

    Expect(argumentTestFunc( 2)).toBe(4)
    Expect(argumentTestFunc( 2, 2)).toBe(5)
    Expect(argumentTestFunc(-2)).toBe(0)
    Expect(argumentTestFunc(-2, 2)).toBe(1)
    Expect(argumentTestFunc(0.3)).toBe(2.3)



@test(name="Accessing *args")
def testArgs():
    def argsTestFunc(*args):
        return args

    @Mixin(argsTestFunc, at=Head(), force_ret=True)
    def argsTestMixin(*args):
        return args + (1, 2, 3)
    
    Expect(argsTestFunc(1, 2, 3)).toBe((1, 2, 3, 1, 2, 3))
    Expect(argsTestFunc(1, 2, 3, 4)).toBe((1, 2, 3, 4, 1, 2, 3))
    Expect(argsTestFunc("a", "Hello World", "Fish")).toBe(("a", "Hello World", "Fish", 1, 2, 3))



@test(name="Accessing **kwargs")
def testKwargs():
    def kwargsTestFunc(**kwargs):
        return kwargs

    @Mixin(kwargsTestFunc, at=Head(), force_ret=True)
    def kwargsTestMixin(**kwargs):
        return dict(kwargs, **{'0': 0, '1': 1, '2': 2})
    
    Expect(kwargsTestFunc(a=1, b=2, c=3)).toBe({'a': 1, 'b': 2, 'c': 3, '0': 0, '1': 1, '2': 2})
    Expect(kwargsTestFunc(a=1, b=2, c=3, d=4)).toBe({'a': 1, 'b': 2, 'c': 3, 'd': 4, '0': 0, '1': 1, '2': 2})
    Expect(kwargsTestFunc(a="a", b="Hello World", c="Fish")).toBe({'a': "a", 'b': "Hello World", 'c': "Fish", '0': 0, '1': 1, '2': 2})



#! Look into this one
# @test(name="Reusing variables defined in another mixin")
# def testReuseVariables():
    # def reuseTestFunc():
        # return 1
# 
    # @Mixin(reuseTestFunc, at=Head())
    # def reuseTestMixin1():
        # x = 1
# 
    # @Mixin(reuseTestFunc, at=Return())
    # def reuseTestMixin2():
        # return x + 1
    # 
    # import dis
# 
    # dis.dis(reuseTestFunc)
    # 
    # Expect(reuseTestFunc()).toBe(2)



#! Need to fix this one
# @test(name="Match multiple")
# def testMatchMultiple():
    # i = 0
# 
    # def matchMultipleTestFunc():
        # nonlocal i
        # i += 1
        # i += 1
        # return i
# 
    # def matchMultipleToMatch():
        # i += 1
# 
    # @Mixin(matchMultipleTestFunc, at=Match(matchMultipleToMatch))
    # def matchMultipleTestMixin():
        # i += 1
    # 
    # Expect(matchMultipleTestFunc()).toBe(4)


exitTests()