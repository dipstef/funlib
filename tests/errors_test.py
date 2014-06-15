from funlib.retry import ErrorCatches
from funlib.retry.errors import ErrorHandlers, handle


def _raise(e):
    raise e


def _one():
    return 1


def _nothing():
    pass


def _errors_mapping_test():
    assert ErrorHandlers((ValueError, BaseException), _raise) == ((ValueError, BaseException), _raise)
    assert ErrorHandlers((ValueError, ), _raise) == (ValueError, _raise)

    assert handle(ValueError, BaseException).doing(_raise) == ((ValueError, BaseException), _raise)
    assert handle(ValueError).doing(_raise) == (ValueError, _raise)
    assert handle(Exception).doing(_nothing) == (Exception, _nothing)


def main():
    declarations = ((ValueError, TypeError), _one), (BaseException, _raise)
    errors = ErrorCatches(*declarations)
    assert errors.declarations == declarations

    errors2 = errors.copy()

    errors2[(NotImplementedError, StandardError)] = _one
    errors2[Exception] = _raise

    new_declarations = declarations + (((NotImplementedError, StandardError), _one),) + ((Exception, _raise), )
    assert errors2.declarations == new_declarations


if __name__ == '__main__':
    main()