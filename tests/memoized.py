import time

from dated.timedelta import seconds

from funlib.cached import cached, cached_property


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

    numbers = Numbers()

    print numbers.fibonacci
    assert numbers.fibonacci.__name__ == 'fibonacci'
    assert 2 == numbers.two
    assert 2 == numbers.two

    numbers.fibonacci(10)

    assert numbers.fibonacci.in_cache(10) is 55
    time.sleep(1)
    assert not numbers.fibonacci.in_cache(10)
    cached_result = numbers.fibonacci.memoized(10)
    assert cached_result.is_expired()

    numbers.fibonacci(10)

    #print numbers.fibonacci.memoized(10)


def _test_function():

    @cached
    def fibonacci(n):
        if n in (0, 1):
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    assert not fibonacci.in_cache(10)
    assert fibonacci(10) is 55
    assert fibonacci.in_cache(10) is 55

    #print fibonacci(10)
    print fibonacci(n=10)
    print fibonacci(n=10)


def main():
    _test_class()
    print
    _test_function()

if __name__ == '__main__':
    main()