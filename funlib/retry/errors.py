from collections import OrderedDict, namedtuple
import copy
import inspect
import itertools


class ErrorClassHandling(object):

    def __init__(self, *errors_handlers):
        self._declarations = []
        self._handlers_declaration = OrderedDict()
        self._error_mappings = OrderedDict()
        self._mro_mappings = OrderedDict()

        for error_classes, handler in errors_handlers:
            self[error_classes] = handler

        self._lookups = set()

    def __setitem__(self, error_classes, handler):
        errors_handler = ErrorsHandler(error_classes, handler)
        self.add(errors_handler)

    def add(self, *errors_handlers):
        for errors_handler in errors_handlers:
            if not errors_handlers in self._declarations:
                self._declarations.append(errors_handler)
                self._add_errors_handler(errors_handler)

    def _add_errors_handler(self, errors_handler):
        for error_class in errors_handler.errors:
            self._error_mappings[error_class] = errors_handler.handler
            self._mro_mappings[error_class] = errors_handler.handler
            self._handlers_declaration[error_class] = errors_handler

    def override(self, *errors_handlers):
        declarations = self._update_declarations(errors_handlers)

        return self.__class__(*declarations)

    def _update_declarations(self, errors_handlers):
        declarations = list(self._declarations)
        for errors_handler in errors_handlers:
            errors_definition = self._get_existing_handlers(errors_handler.errors)

            existing_definitions = itertools.groupby(errors_handler.errors, key=lambda x: errors_definition.get(x))

            for definition, group in existing_definitions:
                if definition:
                    matching = [error for error in errors_handler.errors if definition.matching(error)]
                    remaining = [error for error in definition.errors if not error in matching]

                    position = declarations.index(definition)
                    new_errors_handler = ErrorsHandler(matching, errors_handler.handler)
                    if remaining:
                        declarations[position] = ErrorsHandler(remaining, definition.handler)
                        declarations = declarations[:position] + [new_errors_handler] + declarations[position:]
                    else:
                        declarations[position] = new_errors_handler
                else:
                    declarations.append(errors_handler)

        return declarations

    def _get_existing_handlers(self, errors):
        existing_handlers = OrderedDict()

        for error_class in errors:
            declaration = self._get_error_handler(error_class)

            if declaration:
                existing_handlers[error_class] = declaration

        return existing_handlers

    def _get_error_handler(self, error_class):
        declaration = self._handlers_declaration.get(error_class)
        return declaration

    def get(self, error_class):
        return self._mro_mappings.get(error_class) or self._resolve_mro_mapping(error_class)

    def _resolve_mro_mapping(self, error):
        if not error in self._lookups:
            self._lookups.add(error)
            error_mappings = OrderedDict(((error, self._mro_mappings[error]) for error in self._base_errors(error)))
            return error_mappings.get(error)

    def _base_errors(self, error):
        return (error_class for error_class in _base_errors(error) if error_class in self._error_mappings)

    @property
    def classes(self):
        return tuple(self._error_mappings.keys())

    @property
    def declarations(self):
        return tuple(self._declarations)

    def __str__(self):
        return '\n'.join((str(declaration) for declaration in self._declarations))

    def __copy__(self):
        copy = self.__class__(*self._declarations)
        copy._mro_mappings = dict(self._mro_mappings)
        copy._lookups = set(self._lookups)
        return copy

    def copy(self):
        return copy.copy(self)

    def new_from(self):
        pass


class ErrorCatches(ErrorClassHandling):

    def __init__(self, *errors_handlers):
        super(ErrorCatches, self).__init__(*errors_handlers)

    def _base_errors(self, error):
        '''Resolve a mapping to an exception in the same order errors are listed'''
        error_mro = super(ErrorCatches, self)._base_errors(error)
        catches = self._error_mappings.keys()
        return sorted(error_mro, key=lambda e: catches.index(e))

    def _get_error_handler(self, error_class):
        error_definition = super(ErrorCatches, self)._get_error_handler(error_class)
        if not error_definition:
            for base_error in self._base_errors(error_class):
                error_definition = super(ErrorCatches, self)._get_error_handler(base_error)
                if error_definition:
                    return error_definition
        return error_definition


def _base_errors(error_class):
    return (cls for cls in inspect.getmro(error_class) if issubclass(cls, BaseException))


class ErrorMatching(object):

    def matches(self, error):
        return any(self.matching(error))

    def _matching(self, error):
        return (error for error in _base_errors(error) if error in self.errors)

    def matching(self, error):
        return list(self._matching(error))


class ErrorHandle(namedtuple('ErrorHandle', ['error', 'handler']), ErrorMatching):

    def __new__(cls, error, handler):
        assert issubclass(error, BaseException)
        return super(ErrorHandle, cls).__new__(cls, error, handler)

    @property
    def errors(self):
        return self.error,


class ErrorsHandler(namedtuple('ErrorHandlers', ['errors', 'handler']), ErrorMatching):

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