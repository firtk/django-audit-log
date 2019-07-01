import inspect


class FieldRegistry(object):
    _registry = {}
    audit_field_module = 'audit_log.models.fields'

    def __init__(self, fieldcls):
        # Save first audit base class, to allow audit_log field inheritance
        first_audit_base_class = None
        if fieldcls.__module__ != self.audit_field_module:
            for base_class in inspect.getmro(fieldcls):
                if base_class.__module__ == self.audit_field_module:
                    first_audit_base_class = base_class
                    break
        self._fieldcls = first_audit_base_class or fieldcls

    def add_field(self, model, field):
        reg = self.__class__._registry.setdefault(self._fieldcls, {}).setdefault(model, [])
        reg.append(field)

    def get_fields(self, model):
        return self.__class__._registry.setdefault(self._fieldcls, {}).get(model, [])

    def __contains__(self, model):
        return model in self.__class__._registry.setdefault(self._fieldcls, {})

