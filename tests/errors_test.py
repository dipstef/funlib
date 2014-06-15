from funlib.retry import ErrorCatches
from funlib.retry.errors import ErrorsHandler, handle, ErrorClassHandling


def _raise(e):
    raise e


def _one():
    return 1


def _nothing():
    pass


def _errors_mapping_test():
    assert ErrorsHandler((ValueError, BaseException), _raise) == ((ValueError, BaseException), _raise)
    assert ErrorsHandler((ValueError, ), _raise) == (ValueError, _raise)

    assert handle(ValueError, BaseException).doing(_raise) == ((ValueError, BaseException), _raise)
    assert handle(ValueError).doing(_raise) == (ValueError, _raise)
    assert handle(Exception).doing(_nothing) == (Exception, _nothing)


def _extend_declarations_test():
    declarations = ((ValueError, TypeError), _one), (BaseException, _raise)
    errors = ErrorCatches(*declarations)

    assert errors.declarations == declarations
    errors2 = errors.copy()
    errors2[(NotImplementedError, StandardError)] = _one
    errors2[Exception] = _raise
    new_declarations = declarations + (((NotImplementedError, StandardError), _one),) + ((Exception, _raise), )
    assert errors2.declarations == new_declarations


def _override_declarations_test():
    errors = ErrorClassHandling(((ValueError, TypeError), _one), (BaseException, _raise))

    errors2 = errors.override(ErrorsHandler(ValueError, _nothing))
    assert errors2.declarations == ((ValueError, _nothing), (TypeError, _one), (BaseException, _raise))

    errors2 = errors.override(ErrorsHandler(StandardError, _nothing))
    assert errors2.declarations == (((ValueError, TypeError), _one), (BaseException, _raise), (StandardError, _nothing))


def _override_declarations2_test():
    errors = ErrorCatches(((ValueError, TypeError), _one), (BaseException, _raise))

    errors2 = errors.override(ErrorsHandler(ValueError, _nothing))
    assert errors2.declarations == ((ValueError, _nothing), (TypeError, _one), (BaseException, _raise))

    errors2 = errors.override(ErrorsHandler(StandardError, _nothing))
    assert errors2.declarations == (((ValueError, TypeError), _one), (StandardError, _nothing), (BaseException, _raise))


def main():
    _errors_mapping_test()
    _extend_declarations_test()
    _override_declarations_test()
    _override_declarations2_test()

if __name__ == '__main__':
    main()