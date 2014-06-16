from collections import OrderedDict, namedtuple
import copy
import inspect
import itertools


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


class CatchClauses(object):

    def __init__(self, *errors_handlers):
        self._catches = []
        self._error_handlers = OrderedDict()

        for error_classes, handler in errors_handlers:
            self._add(ErrorsHandler(error_classes, handler))

        self._lookups = set()

    def _add(self, *errors_handlers):
        for errors_handler in errors_handlers:
            if not errors_handlers in self._catches:
                self._catches.append(errors_handler)
                self._add_errors_handler(errors_handler)

    def _add_errors_handler(self, errors_handler):
        for error_class in errors_handler.errors:
            self._error_handlers[error_class] = errors_handler

    def _get_existing_handlers(self, errors):
        existing_handlers = OrderedDict()

        for error_class in errors:
            declaration = self._get_error_handler(error_class)

            if declaration:
                existing_handlers[error_class] = declaration

        return existing_handlers

    def _get_error_handler(self, error_class):
        declaration = self._error_handlers.get(error_class)
        return declaration

    def get(self, error_class):
        return self._error_handlers.get(error_class) or self._resolve_mro_mapping(error_class)

    def _resolve_mro_mapping(self, error):
        if not error in self._lookups:
            base_handlers = OrderedDict(((error, self._error_handlers[error]) for error in self._base_errors(error)))
            if base_handlers:
                self._error_handlers.update(base_handlers)
                self._lookups.update(base_handlers.keys())
                handler = base_handlers.values()[0]
                self._lookups.add(error)
                self._error_handlers[error] = handler
                return handler

    def _base_errors(self, error):
        '''Resolve a mapping to an exception in the same order errors are listed'''
        error_mro = (error_class for error_class in _base_errors(error) if error_class in self._error_handlers)
        catches = self._error_handlers.keys()
        return sorted(error_mro, key=lambda e: catches.index(e))

    @property
    def catches(self):
        return tuple(self._catches)

    def __str__(self):
        return '\n'.join((str(declaration) for declaration in self._catches))

    def __copy__(self):
        copy = self.__class__(*self._catches)
        copy._error_handlers = dict(self._error_handlers)
        copy._lookups = set(self._lookups)
        return copy

    def copy(self):
        return copy.copy(self)


class ErrorCatches(CatchClauses):

    def __init__(self, *errors_handlers):
        super(ErrorCatches, self).__init__(*errors_handlers)

    def __setitem__(self, error_classes, handler):
        errors_handler = ErrorsHandler(error_classes, handler)
        self._add(errors_handler)

    def _add(self, *errors_handlers):
        declarations = self._update_catches(errors_handlers)
        new_declarations = [handler for handler in declarations if not handler in self._catches]

        self._catches = declarations
        for errors_handler in new_declarations:
            self._add_errors_handler(errors_handler)

    def override(self, *errors_handlers):
        declarations = self._update_catches(errors_handlers)

        return self.__class__(*declarations)

    def _update_catches(self, errors_handlers):
        declarations = list(self._catches)
        for errors_handler in errors_handlers:
            existing_catches = self._match_existing_catches(errors_handler)
            if existing_catches:
                declarations = _split_existing_catches(declarations, errors_handler, existing_catches)
            else:
                declarations.append(errors_handler)

        return declarations

    def _match_existing_catches(self, catch):
        errors_definition = self._get_existing_handlers(catch.errors)

        existing_handlers = itertools.groupby(catch.errors, key=lambda x: errors_definition.get(x))

        existing_catches = []
        for existing, group in existing_handlers:
            if existing:
                existing_catches.append((existing, list(group)))

        return existing_catches

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


def _split_existing_catches(declarations, errors_handler, existing_catches):
    for existing, matching, remaining in _iterate_matching_catches(errors_handler, existing_catches):
        position = declarations.index(existing)

        if remaining.errors:
            declarations[position] = remaining
            declarations = declarations[:position] + [matching] + declarations[position:]
        else:
            declarations[position] = matching

    return declarations


def _iterate_matching_catches(catch, existing_catches):
    for existing, group_errors in existing_catches:
        matching = _catch_errors_move_up(catch, existing, group_errors)

        remaining = [error for error in existing.errors if not error in matching] if matching else []

        if matching:
            yield existing, ErrorsHandler(matching, catch.handler), ErrorsHandler(remaining, existing.handler)


def _catch_errors_move_up(catch, existing, group_errors):
    matching = []
    for error in group_errors:
        matches = existing.matching(error)
        for match in matches:
            if match and (match != error and issubclass(error, match) or existing.handler != catch.handler):
                matching.append(error)
    return matching