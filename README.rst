Funlib
======

Collection of function classes and decorators

Examples
========

Decorators:

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

    assert 7 == seven()
    assert 8 == eight()

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
    assert numbers.nine() == 9
    assert numbers.ten() == 10

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
    assert numbers.eleven == 11
    assert numbers.twelve == 12

calling class decorators work exactly the same:

.. code-block:: python

    @decorator
    class add(object):
        def __init__(self, value=2):
            self._value = value
    
        def __call__(self, fun):
            def add_fun(*args, **kwargs):
                return fun(*args, **kwargs) + self._value
    
            return add_fun
            
            
But can be sub-classed:

.. code-block:: python


    class plus5(add):
        def __init__(self):
            super(add5, self).__init__(value=5)

    @plus5
    def seven():
        return 2
    
