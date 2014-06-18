import time

from dated.date_time import seconds

from funlib.cached import cached, memoized, cached_property


def _test_class():

    class Numbers(object):
        @cached_property
        def two(self):
            print 'Computing Two'
            return 2

        @cached(expiration=seconds(1))
        def fibonacci(self, n):
            print 'Fibonacci', n
            if n in (0, 1):
                return n
            return self.fibonacci(n - 1) + self.fibonacci(n - 2)

    a = Numbers()
    assert a.fibonacci.__name__ == 'fibonacci'
    assert 2 == a.two
    assert 2 == a.two

    a.fibonacci(10)
    print 'Cached', a.fibonacci(10)
    time.sleep(1)
    print 'Expired'
    a.fibonacci(10)

    print a.fibonacci.get(10)


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