from dated.date_time import seconds
import time
from funlib.util import call_string
from funlib.cached import cached_property, cached


def main():

    class A(object):
        @cached_property(expiration=seconds(1))
        def boo(self):
            print 'Calculating Boo'
            return 1

        @cached
        def post(self):
            print 'Posting'
            return 2

        @cached
        def foo(self, *args, **kwargs):
            print 'Fooing: ', call_string('foo', *args, **kwargs)
            return 3

    a = A()
    print a.boo
    print a.boo
    time.sleep(1)
    print a.boo

    print a.post()
    print a.post()

    print a.foo(1, 2)
    print a.foo(1, 2)
    print a.foo(3, 4)

    a = A()
    print a.foo(1, 2)


if __name__ == '__main__':
    main()