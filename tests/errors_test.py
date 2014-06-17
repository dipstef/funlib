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


def _move_up_catch_test():
    catches = ErrorCatches(handle(UnicodeDecodeError, UnicodeEncodeError).doing(_one))

    errors = catches.copy()
    errors.add(ErrorsHandler(ValueError, _raise))

    assert errors.catches == (((UnicodeDecodeError, UnicodeEncodeError), _one), (ValueError, _raise))

    errors = catches.copy()

    errors.top(handle(ValueError).doing(_raise))

    assert errors.catches == ((ValueError, _raise), ((UnicodeDecodeError, UnicodeEncodeError), _one))

    errors = catches.copy()
    errors.top(handle(UnicodeDecodeError).doing(_raise))

    assert errors.catches == ((UnicodeDecodeError, _raise), (UnicodeEncodeError, _one))


def _remove_catches_test():
    catches = ErrorCatches(handle(UnicodeDecodeError, UnicodeEncodeError).doing(_one))
    catches.append(handle(UnicodeDecodeError).doing(_raise))

    errors = catches.copy()

    assert errors.handler(UnicodeDecodeError) == _one

    assert errors.remove_error(UnicodeDecodeError) == (handle(UnicodeDecodeError).doing(_one),
                                                       handle(UnicodeDecodeError).doing(_raise))
    assert errors.get(UnicodeEncodeError) == handle(UnicodeEncodeError).doing(_one)

    errors = catches.copy()
    errors.remove_catch(handle(UnicodeDecodeError, UnicodeEncodeError).doing(_one))
    assert errors.handler(UnicodeDecodeError) == _raise

    errors = catches.copy()
    errors.remove_catch(handle(UnicodeDecodeError).doing(_one))
    assert errors.handler(UnicodeEncodeError) == _one
    assert errors.handler(UnicodeDecodeError) == _raise


def main():
    _errors_mapping_test()
    _extend_declarations_test()
    _add_same_declaration_test()
    _update_declarations_test()
    _override_declarations_test()
    _move_up_catch_test()
    _remove_catches_test()

if __name__ == '__main__':
    main()