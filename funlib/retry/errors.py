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
    def __init__(self, *errors):
        assert errors
        self._errors = errors

    def doing(self, handler):
        return ErrorsHandler(self._errors, handler)


class ErrorCatches(object):

    def __init__(self, *errors_handlers):
        self._catches = CatchList()

        for error_classes, handler in errors_handlers:
            self[error_classes] = handler

    def __setitem__(self, error_classes, handler):
        errors_handler = ErrorsHandler(error_classes, handler)
        self.add(errors_handler)

    def add(self, *errors_handlers):
        catches = self._update_catches(errors_handlers)

        self._catches = catches

    def override(self, *errors_handlers):
        declarations = self._update_catches(errors_handlers)

        return self.__class__(*declarations)

    def _update_catches(self, errors_handlers):
        catches = CatchList(self._catches)

        for catch in errors_handlers:
            catches.add(catch)

        return catches

    def get(self, error_class):
        '''If the exception does not match a catch clause than check for parent classes'''
        return self._catches.get_handler(error_class) or self._resolve_from_base_errors(error_class)

    def handler(self, error_class):
        catch = self.get(error_class)
        if catch:
            return catch.handler

    def _resolve_from_base_errors(self, error):
        base_errors_catches = self._catches.base_errors(error)
        if base_errors_catches:
            return self._catches.get_handler(base_errors_catches[0])

    @property
    def catches(self):
        return tuple(self._catches)

    def __str__(self):
        return '\n'.join((str(declaration) for declaration in self._catches))

    def __copy__(self):
        copy = self.__class__(*self._catches)
        return copy

    def copy(self):
        return copy.copy(self)


#Try/catch declarations
class CatchList(object):

    def __init__(self, catches=()):
        self._catches = []
        self._catch_errors = OrderedDict()
        for catch in catches:
            self.add(catch)

    def add(self, catch):
        existing_catches = self._match_existing_catches(catch)
        if existing_catches:
            self._split_existing(catch, existing_catches)
        else:
            self.add_to_bottom(catch)

    def add_to_bottom(self, catch):
        self._catches.append(catch)
        for error_class in catch.errors:
            if not error_class in self._catch_errors:
                self._catch_errors[error_class] = catch

    def _split_existing(self, catch, existing_catches):
        for existing, matching, remaining in _iterate_matching_catches(catch, existing_catches):
            position = self._catches.index(existing)

            if remaining.errors:
                self._catches[position] = remaining
                self._catches = self._catches[:position] + [matching] + self._catches[position:]
            else:
                self._catches[position] = matching

            for error_class in matching.errors:
                self._catch_errors[error_class] = matching

    def _match_existing_catches(self, catch):
        errors_definition = self._get_existing_handlers(catch.errors)

        existing_handlers = itertools.groupby(catch.errors, key=lambda x: errors_definition.get(x))

        existing_catches = []
        for existing, group in existing_handlers:
            if existing:
                existing_catches.append((existing, list(group)))

        return existing_catches

    def _get_existing_handlers(self, errors):
        existing_handlers = OrderedDict()

        for error_class in errors:
            declaration = self._get_error_handler(error_class)

            if declaration:
                existing_handlers[error_class] = declaration

        return existing_handlers

    def get_handler(self, error_class):
        return self._catch_errors.get(error_class)

    def _get_error_handler(self, error_class):
        error_definition = self._catch_errors.get(error_class)

        if not error_definition:
            for base_error in self.base_errors(error_class):
                error_definition = self._catch_errors.get(base_error)
                if error_definition:
                    return error_definition
        return error_definition

    def base_errors(self, error):
        '''Resolve a mapping to an exception in the same order errors are listed'''
        error_mro = (error_class for error_class in _base_errors(error) if error_class in self._catch_errors)
        return sorted(error_mro, key=lambda e: self._catches.index(self._catch_errors[e]))

    def __iter__(self):
        return iter(self._catches)

    def __len__(self):
        return len(self._catches)

    def __contains__(self, catch):
        return catch in self._catches


def _base_errors(error_class):
    return (cls for cls in inspect.getmro(error_class) if issubclass(cls, BaseException))


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