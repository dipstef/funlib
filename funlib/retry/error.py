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
        self._class_resolutions = {}

    def get(self, error_class):
        return self._class_resolutions.get(error_class) or self._map_from_base_classes(error_class)

    def _map_from_base_classes(self, error_class):
        searched = set()

        def get_callback(error_cls):
            if not error_cls in searched:
                error_callback = self._errors.get(error_cls)

                while not error_cls or error_cls != BaseException:
                    searched.add(error_cls)

                    base_errors = [cls for cls in inspect.getmro(error_cls) if issubclass(cls, BaseException)]
                    for base_class in base_errors:
                        if not base_class in searched:
                            error_callback = self._errors.get(base_class)
                            if error_callback:
                                return error_callback
                            searched.add(base_class)

                return error_callback

        value = get_callback(error_class)
        if value:
            self._class_resolutions[error_class] = value
        return value

    @property
    def classes(self):
        return tuple(self._errors.keys())
