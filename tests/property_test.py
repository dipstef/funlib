from funlib.cached import cached_property


class Number(object):

    def __init__(self, number):
        self._number = number

    @cached_property
    def number(self):
        return self._number

    def get(self):
        return self._number


def main():
    n1 = Number(10)
    assert n1.number is 10
    assert n1.get() is 10

    n2 = Number(11)
    assert n2.number is 11
    assert n2.get() is 11

if __name__ == '__main__':
    main()
