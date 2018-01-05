from testcase.decorators import testcase
# ======================================


@testcase
def test_1():
    print("I'm test_1")
# _____________________________


@testcase
def test_2():
    print("I'm test_2")
# _____________________________


def test_3():
    print("I'm test_3")
# _____________________________


if __name__ == '__main__':
    from testcase.decorators import testcases_registry
    print("Registry: {}".format(testcases_registry))
