from funlib.cached import Wraps

wraps = Wraps()


def foo():
    return 1

wraps(foo)

print wraps
print wraps.__name__

print Wraps().__name__