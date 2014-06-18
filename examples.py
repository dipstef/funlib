from funlib.decorator import decorator, property_decorator, Decorator


@decorator
def add(fun, value=2):
    def add_fun(*args, **kwargs):
        return fun(*args, **kwargs) + value
    return add_fun


class add2(Decorator):

    def _decorate(self, fun, args, kwargs):
        return fun(*args, **kwargs) + 2


class add(Decorator):
    def __init__(self, value=2):
        self._value = value

    def _decorate(self, fun, args, kwargs):
        return fun(*args, **kwargs) + self._value


@add2
def five():
    return 3

@add
def seven():
    return 5


@add(value=3)
def eight():
    return 5

assert five() is 5
assert seven() is 7
assert eight() is 8


class Numbers(object):
    @add
    def nine(self):
        return 7

    @add(value=3)
    def ten(self):
        return 7

numbers = Numbers()
assert numbers.nine() is 9
assert numbers.ten() is 10


property_plus_2 = property_decorator(add)
property_plus_3 = property_decorator(add(value=3))


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


class add5(add):
    def __init__(self):
        super(add5, self).__init__(value=5)


@add5
def seven():
    return 2

assert seven() is 7