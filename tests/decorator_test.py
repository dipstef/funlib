from funlib.decorator import Decorator, decorator, property_decorator


def _test(add):

    @add
    def sum_plus2(x, y):
        return x + y

    @add(value=5)
    def sum_plus5(x, y):
        return x + y

    def sum_times2_plus7(x, y):
        return sum_plus2(x, y) + sum_plus5(x, y)

    assert 5 == sum_plus2(1, 2)
    assert 8 == sum_plus5(1, 2)
    assert 13 == sum_times2_plus7(1, 2)

    property_plus = property_decorator(add)

    class Sum(object):

        @add
        def sum_plus2(self, x, y):
            return x + y

        @add(value=5)
        def sum_plus5(self, x, y):
            return x + y

        def sum_times2_plus7(self, x, y):
            return self.sum_plus2(x, y) + self.sum_plus5(x, y)

        @add
        def sum_times2_plus9(self, x, y):
            return self.sum_plus2(x, y) + self.sum_plus5(x, y)

        @add(value=3)
        def sum_times2_plus10(self, x, y):
            return self.sum_plus2(x, y) + self.sum_plus5(x, y)

        @property
        @add
        def four(self):
            return 2

        @property
        @add(value=2)
        def five(self):
            return 2

        @property_decorator(add(value=5))
        def seven(self):
            return 2

        @property_decorator(add)
        def nine(self):
            return 7

        @property_plus
        def eleven(self):
            return 9

        @property_plus(value=3)
        def twelve(self):
            return 9

        @property_plus(3)
        def ten(self):
            return 7

        @property
        def twenty(self):
            return self.nine + self.eleven

    sum = Sum()

    assert 5 == sum.sum_plus2(1, 2)
    assert 8 == sum.sum_plus5(1, 2)
    assert 13 == sum.sum_times2_plus7(1, 2)
    assert 15 == sum.sum_times2_plus9(1, 2)
    assert 16 == sum.sum_times2_plus10(1, 2)

    assert 4 == sum.four
    assert 7 == sum.seven
    assert 9 == sum.nine
    assert 11 == sum.eleven
    assert 12 == sum.twelve
    assert 10 == sum.ten
    assert 20 == sum.twenty


def _test_decorator_fun():
    @decorator
    def add(fun, value=2):
        def add_fun(*args, **kwargs):
            return fun(*args, **kwargs) + value
        return add_fun

    _test(add)


def _test_decorator_class():
    class add(Decorator):
        def __init__(self, value=2):
            self._value = value

        def __call__(self, *args, **kwargs):
            return self._fun(*args, **kwargs) + self._value

    _test(add)


def main():
    _test_decorator_class()
    _test_decorator_fun()

if __name__ == '__main__':
    main()