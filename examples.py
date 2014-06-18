from funlib.decorator import decorator, property_decorator, Decorator


@decorator
def add(fun, value=2):
    def add_fun(*args, **kwargs):
        return fun(*args, **kwargs) + value
    return add_fun


class plus2(Decorator):

    def _decorate(self, fun, args, kwargs):
        return fun(*args, **kwargs) + 2

@plus2
def five():
    return 3

assert five() is 5


class plus2(Decorator):
    def __init__(self, plus=0):
        self._value = 2 + plus

    def _decorate(self, fun, args, kwargs):
        return fun(*args, **kwargs) + self._value

@plus2
def seven():
    return 5

@plus2(plus=1)
def eight():
    return 5

assert seven() is 7
assert eight() is 8


class Numbers(object):
    @plus2
    def nine(self):
        return 7

    @plus2(plus=3)
    def ten(self):
        return 5

numbers = Numbers()
assert numbers.nine() is 9
assert numbers.ten() is 10


property_plus_2 = property_decorator(plus2)
property_plus_3 = property_decorator(plus2(plus=1))


class Numbers(object):
    @property_plus_2
    def eleven(self):
        return 9

    @property_plus_3
    def twelve(self):
        return 9

numbers = Numbers()
assert numbers.eleven is 11
assert numbers.twelve is 12


class plus5(plus2):
    def __init__(self):
        super(plus5, self).__init__(plus=3)


@plus5
def seven():
    return 2

assert seven() is 7