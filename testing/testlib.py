from colorama import Fore, Back, Style

passed_tests = 0
num_tests = 0
current_test_name = "None"
failed_test = False

def test(name: str = ""):
    def wrapper(func):
        nonlocal name

        if name == "":
            name = func.__name__
        global num_tests
        print(Fore.BLUE + "Running test: " + Fore.CYAN + name.ljust(20) + Fore.RESET)
        num_tests += 1
        global current_test_name
        current_test_name = func.__name__
        try:
            func()
        except Exception as e:
            print(Fore.RED + "Test " + current_test_name + " failed: " + str(e) + Fore.RESET)
            global failed_test
            failed_test = True
        global passed_tests
        if not failed_test:
            passed_tests += 1
            print(Fore.BLUE + "Passed test : " + Fore.CYAN + name + Fore.RESET)
    return wrapper

class Expect:
    def __init__(self, actual):
        self.actual = actual

    def toBe(self, value):
        if self.actual == value:
            return
        else:
            print(Fore.RED + "Failed in test: " + current_test_name + " with actual: " + str(self.actual) + " and expected: " + str(value) + Fore.RESET)
            print("Expected: " + str(value))
            print("Actual: " + str(self.actual))
            global failed_test
            failed_test = True

    def toNotBe(self, value):
        if self.actual != value:
            return
        else:
            print(Fore.RED + "Failed in test: " + current_test_name + " with actual: " + str(self.actual) + " and expected: " + str(value) + Fore.RESET)
            print("Expected: " + str(value))
            print("Actual: " + str(self.actual))
            global failed_test
            failed_test = True

    def toBeTrue(self):
        self.toBe(True)
    
    def toBeFalse(self):
        self.toBe(False)

    def __str__(self):
        return str(self.actual)

def exitTests():
    print(Fore.BLUE + "Passed " + str(passed_tests) + " out of " + str(num_tests) + " tests" + Fore.RESET)
    exit(0)