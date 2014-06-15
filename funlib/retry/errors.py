from collections import OrderedDict, namedtuple
import copy
import inspect


class ErrorClassHandling(object):

    def __init__(self, *errors_handlers):
        self.declarations = ()
        self._error_mappings = OrderedDict()
        self._mro_mappings = OrderedDict()

        for error_classes, handler in errors_handlers:
            self[error_classes] = handler

        self._lookups = set()

    def __setitem__(self, error_classes, handler):
        errors_handler = ErrorsHandler(error_classes, handler)
        self.add(errors_handler)

    def add(self, errors_handler):
        self.declarations += (errors_handler, )
        for error_class in errors_handler.errors:
            self._error_mappings[error_class] = errors_handler.handler
            self._mro_mappings[error_class] = errors_handler.handler

    def get(self, error_class):
        return self._mro_mappings.get(error_class) or self._resolve_mro_mapping(error_class)

    def _resolve_mro_mapping(self, error):
        if not error in self._lookups:
            self._lookups.add(error)
            error_mappings = OrderedDict(((error, self._mro_mappings[error]) for error in self._base_errors(error)))
            return error_mappings.get(error)

    def _base_errors(self, error):
        return (cls for cls in inspect.getmro(error) if issubclass(cls, BaseException) if cls in self._error_mappings)

    @property
    def classes(self):
        return tuple(self._error_mappings.keys())

    def __str__(self):
        return '\n'.join((str(declaration) for declaration in self.declarations))

    def __copy__(self):
        copy = self.__class__()
        copy.declarations = tuple(self.declarations)
        copy._error_mappings = OrderedDict(self._error_mappings)
        copy._mro_mappings = dict(self._mro_mappings)
        copy._lookups = set(self._lookups)
        return copy

    def copy(self):
        return copy.copy(self)


class ErrorHandle(namedtuple('ErrorHandle', ['error', 'handler'])):

    def __new__(cls, error, handler):
        assert issubclass(error, BaseException)
        return super(ErrorHandle, cls).__new__(cls, error, handler)

    @property
    def errors(self):
        return self.error,


class ErrorCatches(ErrorClassHandling):

    def __init__(self, *errors_handlers):
        super(ErrorCatches, self).__init__(*errors_handlers)

    def _base_errors(self, error):
        '''Resolve a mapping to an exception in the same order errors are listed'''
        error_mro = super(ErrorCatches, self)._base_errors(error)
        catches = self._error_mappings.keys()
        return sorted(error_mro, key=lambda e: catches.index(e))


class ErrorsHandler(namedtuple('ErrorHandlers', ['errors', 'handler'])):

    def __new__(cls, errors, handler):
        if isinstance(errors, type):
            errors = (errors, )
        if len(errors) == 1:
            return ErrorHandle(errors[0], handler)
        else:
            assert all((issubclass(error_class, BaseException) for error_class in errors))
            return super(ErrorsHandler, cls).__new__(cls, tuple(errors), handler)


class handle(object):
    def __init__(self, error, *errors):
        self._errors = (error, ) + errors

    def doing(self, handler):
        return ErrorsHandler(self._errors, handler)