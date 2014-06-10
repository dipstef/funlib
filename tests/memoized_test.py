from funlib.decorators.memoized import memoized


def _test_class():

    class A(object):
        @memoized
        def fibonacci(self, n):
            print 'Computing', n
            if n in (0, 1):
                return n
            return self.fibonacci(n - 1) + self.fibonacci(n - 2)

    a = A()
    a.fibonacci(10)
    a.fibonacci(10)


def _test_function():

    @memoized
    def fibonacci(n):
        print 'Computing', n
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