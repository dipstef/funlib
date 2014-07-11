Funlib
======

Collection of functions and decorators categorized for different problems.

Decorators
==========


.. code-block:: python

    from funlib import decorator

    @decorator
    def add(fun, value=2):
        def add_fun(*args, **kwargs):
            return fun(*args, **kwargs) + value
        return add_fun

can take optional arguments:

.. code-block:: python

    @add
    def seven():
        return 5

    @add(value=3)
    def eight():
        return 5

    >>> assert seven() is 7
    >>> assert eight() is 8

and decorate class methods:

.. code-block:: python

    class Numbers(object):
        @add
        def nine(self):
            return 7
        @add(value=3)
        def ten(self):
            return 7

    numbers = Numbers()
    >>> assert numbers.nine() is 9
    >>> assert numbers.ten() is 10

and work with properties:

.. code-block:: python

    from funlib.decorator import property_decorator

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
    >>> assert numbers.eleven is 11
    >>> assert numbers.twelve is 12

calling class decorators work exactly the same:

.. code-block:: python

    class plus2(Decorator):
        def _decorate(self, fun, args, kwargs):
            return fun(*args, **kwargs) + 2

    class add(Decorator):
        def __init__(self, value=2):
            self._value = value

        def _decorate(self, fun, args, kwargs):
            return fun(*args, **kwargs) + self._value


But can be sub-classed:

.. code-block:: python

    class plus5(add):
        def __init__(self, fun):
            super(add5, self).__init__(fun, value=5)

    @plus5
    def seven():
        return 2

    >>> assert seven() is 7

Memoization
===========
Saves previously computed values

.. code-block:: python

    from funlib.cached import cached

    @cached
    def fibonacci(n):
        if n in (0, 1):
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    >>> assert not fibonacci.in_cache(10)
    >>> assert fibonacci(10) is 55
    >>> assert fibonacci.in_cache(10) is 55


Which can also expire

.. code-block:: python


    @cached(expiration=seconds(1))
    def fibonacci(self, n):
        ....

    >>> fibonacci(10)
    >>> assert fibonacci.in_cache(10) is 55
    >>> time.sleep(1)

    >>> assert not fibonacci.in_cache(10)
    >>> cached_result = fibonacci.memoized(10)
    >>> assert cached_result.is_expired()

As well properties and class methods can also be memoized

.. code-block:: python

    from funlib.cached import cached_property

    class Numbers(object):
        @cached
        def one():
            return 1
        @cached_property
        def two(self):
            return 2

Timeouts
========

.. code-block:: python

    from funlib.signals import timeout

    @timeout(sleep=0.1)
    def foo():
        time.sleep(sleep)
        return 'foo'

    >>> foo()
    'foo'
    >>> foo(sleep=2)
    TimeoutError('Function call timed out')

Retrying
========
Try executing a function a number of times until a value is returned or aborted after a number of attempts.

.. code-block:: python

    from funlib import Lambda
    from funlib.retry import retry, try_times
    from funlib.retry.sleep import sleep

    def _print_attempt(attempt):
        print attempt

    def _fail(times=10):
        attempts = []

        def fail(times):
            attempts.append(len(attempts))
            attempted = len(attempts)

            if attempted <= times:
                raise ValueError(attempted)

            return attempted

        return Lambda(fail, times=times)


    @retry(times=4, on_err=_print_attempt, sleep=sleep(1))
    def test(attempt):
        return attempt()

Fails three times at the forth the result is returned

.. code-block:: python

    >>> test(_fail(times=3))
    test(fail(times=3)) Failed attempt: 1, ValueError
    test(fail(times=3)) Failed attempt: 2, ValueError
    test(fail(times=3)) Failed attempt: 3, ValueError
    4


Can handle different of errors using the ``catches`` module

.. code-block:: python

    from funlib.retry import retry_on_errors, try_times, handle
    from funlib.retry.sleep import sleep, random_sleep, incremental_sleep

    @retry_on_errors(handle(ValueError).doing(try_times(2, on_err=_print_attempt, sleep=sleep(1))),
                     handle(StandardError).doing(try_times(2, on_err=_print_attempt, sleep=incremental_sleep(1))),
                     handle(BaseException).doing(try_times(10, on_err=_print_attempt, sleep=random_sleep(1, to=2))))
    def test(attempt):
        return attempt()

    >>> test(_fail(times=3))
    test(fail(times=3)) Failed attempt: 1, ValueError
    test(fail(times=3)) Failed attempt: 2, ValueError
    ValueError('2')