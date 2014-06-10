from funlib.util import call_string
from funlib.lazy import cached_property, lazy


def main():

    class A(object):
        @cached_property(expiration=1)
        def boo(self):
            print 'Expensive calculation'
            return 1

        @lazy
        def post(self):
            print 'Expensive Post'
            return 2

        @lazy
        def foo(self, *args, **kwargs):
            print 'Expensive Foo: ', call_string('foo', *args, **kwargs)
            return 3

    a = A()
    print a.boo
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