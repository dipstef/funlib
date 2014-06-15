from collections import OrderedDict, namedtuple
import copy
import inspect


class ErrorClassHandling(object):

    def __init__(self, *errors_handlers):
        self.declarations = tuple(ErrorHandlers(*error_handler_tuple) for error_handler_tuple in errors_handlers)
        self._error_mappings = self._error_tuples_to_dict(errors_handlers)
        self._mro_mappings = dict(self._error_mappings)
        self._lookups = set()

    @staticmethod
    def _error_tuples_to_dict(error_mappings):
        error_handlers = OrderedDict()
        for error_tuple in error_mappings:
            error_classes = error_tuple[0]
            if isinstance(error_classes, type):
                error_classes = (error_classes, )

            for error_class in error_classes:
                assert issubclass(error_class, BaseException)
                error_handlers[error_class] = error_tuple[1]

        return error_handlers

    def get(self, error_class):
        return self._mro_mappings.get(error_class) or self._resolve_mro_mapping(error_class)

    def __setitem__(self, error_classes, mapping):
        self.declarations += (ErrorHandlers(error_classes, mapping), )

        if isinstance(error_classes, type):
            error_classes = (error_classes, )

        for error_class in error_classes:
            self._error_mappings[error_class] = mapping
            self._mro_mappings[error_class] = mapping

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
        return copy

    def copy(self):
        return copy.copy(self)


class ErrorCatches(ErrorClassHandling):

    def __init__(self, *errors_handlers):
        super(ErrorCatches, self).__init__(*errors_handlers)

    def _base_errors(self, error):
        '''Resolve a mapping to an exception in the same order errors are listed'''
        error_mro = super(ErrorCatches, self)._base_errors(error)
        catches = self._error_mappings.keys()
        return sorted(error_mro, key=lambda e: catches.index(e))


class ErrorHandle(namedtuple('ErrorHandle', ['error', 'handler'])):
    def __new__(cls, error, handler):
        assert issubclass(error, BaseException)
        return super(ErrorHandle, cls).__new__(cls, error, handler)


class ErrorHandlers(namedtuple('ErrorHandlers', ['errors', 'handler'])):

    def __new__(cls, errors, handler):
        if isinstance(errors, type):
            errors = (errors, )
        if len(errors) == 1:
            return ErrorHandle(errors[0], handler)
        else:
            assert all((issubclass(error_class, BaseException) for error_class in errors))
            return super(ErrorHandlers, cls).__new__(cls, tuple(errors), handler)


class handle(object):
    def __init__(self, error, *errors):
        self._errors = (error, ) + errors

    def doing(self, handler):
        return ErrorHandlers(self._errors, handler)