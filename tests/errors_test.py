from funlib.retry import ErrorCatches
from funlib.retry.errors import ErrorsHandler, handle
from funlib.util import nothing


def _raise(e):
    raise e


def _one():
    return 1


def _errors_mapping_test():
    assert ErrorsHandler((ValueError, BaseException), _raise) == ((ValueError, BaseException), _raise)
    assert ErrorsHandler((ValueError, ), _raise) == (ValueError, _raise)

    assert handle(ValueError, BaseException).doing(_raise) == ((ValueError, BaseException), _raise)
    assert handle(ValueError).doing(_raise) == (ValueError, _raise)
    assert handle(Exception).doing(nothing) == (Exception, nothing)


def _extend_declarations_test():
    declarations = ((ValueError, TypeError), _one), (BaseException, _raise)
    errors = ErrorCatches(*declarations)

    errors[(NotImplementedError, StandardError)] = _one
    errors[Exception] = _raise
    catches = ((ValueError, TypeError), _one), ((NotImplementedError, StandardError), _one), (Exception, _raise), \
              (BaseException, _raise)
    assert errors.catches == catches


def _override_declarations_test():
    errors = ErrorCatches(((ValueError, TypeError), _one), (BaseException, _raise))

    errors2 = errors.override(ErrorsHandler(ValueError, nothing))
    assert errors2.catches == ((ValueError, nothing), (TypeError, _one), (BaseException, _raise))

    errors2 = errors.override(ErrorsHandler(StandardError, nothing))
    assert errors2.catches == (((ValueError, TypeError), _one), (StandardError, nothing), (BaseException, _raise))


def main():
    _errors_mapping_test()
    _extend_declarations_test()
    _override_declarations_test()

if __name__ == '__main__':
    main()