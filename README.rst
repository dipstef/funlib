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

    >>> assert not fibonacci.result(10)
    >>> assert fibonacci(10) is 55
    >>> assert fibonacci.result(10) is 55


Which can also expire

.. code-block:: python


    @cached(expiration=seconds(1))
    def fibonacci(self, n):
        ....

    >>> fibonacci(10)
    >>> assert fibonacci.result(10) is 55
    >>> time.sleep(1)

    >>> assert not fibonacci.result(10)
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

    from funlib.timeout import timeout

    @timeout(sleep=0.1)
    def foo():
        time.sleep(sleep)
        return 'foo'

    >>> foo()
    'foo'
    >>> foo(sleep=2)
    TimeoutError('Function call timed out')