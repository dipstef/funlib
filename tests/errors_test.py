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

    assert errors.handler(ValueError) == _one
    assert errors.handler(TypeError) == _one
    assert errors.handler(BaseException) == _raise
    assert errors.handler(StandardError) == _raise

    errors[(NotImplementedError, StandardError)] = _one
    errors[Exception] = _raise
    catches = ((ValueError, TypeError), _one), ((NotImplementedError, StandardError), _one), (Exception, _raise), \
              (BaseException, _raise)

    assert errors.catches == catches

    assert errors.handler(NotImplementedError) == _one
    assert errors.handler(StandardError) == _one
    assert errors.handler(Exception) == _raise
    #ValueError
    assert errors.handler(UnicodeDecodeError) == _one


def _add_same_declaration_test():
    declarations = ((ValueError, TypeError), _one), (BaseException, _raise)
    errors = ErrorCatches(*declarations)

    errors[(ValueError, Exception)] = _one
    catches = ((ValueError, TypeError), _one), (Exception, _one), (BaseException, _raise)
    assert errors.catches == catches


def _update_declarations_test():
    errors = ErrorCatches(((ValueError, TypeError), _one), (BaseException, _raise))

    assert errors.handler(ValueError) == _one

    errors.add(ErrorsHandler(ValueError, nothing))
    assert errors.catches == ((ValueError, nothing), (TypeError, _one), (BaseException, _raise))

    assert errors.handler(ValueError) == nothing
    assert errors.handler(StandardError) == _raise

    errors.add(ErrorsHandler(StandardError, nothing))
    assert errors.catches == ((ValueError, nothing), (TypeError, _one), (StandardError, nothing), (BaseException, _raise))

    assert errors.handler(StandardError) == nothing


def _override_declarations_test():
    errors = ErrorCatches(((ValueError, TypeError), _one), (BaseException, _raise))

    assert errors.handler(ValueError) == _one

    errors2 = errors.override(ErrorsHandler(ValueError, nothing))
    assert errors2.catches == ((ValueError, nothing), (TypeError, _one), (BaseException, _raise))

    assert errors2.handler(ValueError) == nothing
    assert errors2.handler(StandardError) == _raise

    errors2 = errors.override(ErrorsHandler(StandardError, nothing))
    assert errors2.catches == (((ValueError, TypeError), _one), (StandardError, nothing), (BaseException, _raise))

    assert errors2.handler(StandardError) == nothing


def main():
    _errors_mapping_test()
    _extend_declarations_test()
    _add_same_declaration_test()
    _update_declarations_test()
    _override_declarations_test()

if __name__ == '__main__':
    main()