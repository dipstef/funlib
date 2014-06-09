from collections import OrderedDict
import inspect


class ErrorClasses(object):

    def __init__(self, *errors):
        error_handlers = OrderedDict()

        for error_tuple in errors:
            error_classes = error_tuple[0]
            if isinstance(error_classes, type):
                error_classes = (error_classes, )

            mapping_value = error_tuple[1] if len(error_tuple) >1 else None
            for error_class in error_classes:
                assert issubclass(error_class, BaseException)
                error_handlers[error_class] = mapping_value

        self._errors = error_handlers
        self._mappings = {}

    def get(self, error_class):
        return self._mappings.get(error_class) or self._mapping_from_error_mro(error_class)

    def _mapping_from_error_mro(self, error_class):
        '''Resolve a mapping to an exception in the same order errors are listed'''

        error_mappings = self._get_mro_mappings(error_class)
        for error_class in self._errors.keys():
            mapping = error_mappings.get(error_class)
            if mapping:
                return mapping

    def _get_mro_mappings(self, error_class):
        searched = set()

        mappings = OrderedDict()

        if not error_class in searched:
            mapping = self._errors.get(error_class)
            searched.add(error_class)

            if mapping:
                mappings[error_class] = mapping

            base_errors = [cls for cls in inspect.getmro(error_class) if issubclass(cls, BaseException)]
            for base_class in base_errors:
                if not base_class in searched:
                    mapping = self._errors.get(base_class)
                    if mapping:
                        mappings[base_class] = mapping
                    searched.add(base_class)

        return mappings

    @property
    def classes(self):
        return tuple(self._errors.keys())
