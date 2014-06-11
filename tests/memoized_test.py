from funlib.decorator import property_decorator
from funlib.cached import cached, memoized


def _test_class():

    class A(object):
        @cached
        def fibonacci(self, n):
            print 'Fibonacci', n
            if n in (0, 1):
                return n
            return self.fibonacci(n - 1) + self.fibonacci(n - 2)

        @property_decorator(cached)
        def two(self):
            print 'Computing Two'
            return 2

    a = A()
    assert a.fibonacci.__name__ == 'fibonacci'

    assert 2 == a.two
    assert 2 == a.two

    a.fibonacci(10)
    a.fibonacci(10)


def _test_function():

    @memoized
    def fibonacci(n):
        print 'Fibonacci', n
        if n in (0, 1):
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    print fibonacci(10)
    print fibonacci(10)
    print fibonacci(n=10)
    print fibonacci(n=10)


def main():
    _test_class()
    print
    _test_function()

if __name__ == '__main__':
    main()