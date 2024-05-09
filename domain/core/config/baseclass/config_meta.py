import os, sys
from core.utils.baseclass import (
    ConfigField,
    ConfigValue,
    is_valid_envvar_name,
    ConfigEnvVarType_Priority
)
from core.config.baseclass.config_enums import ConfigEnvVarType
from core.utils.baseclass.yaml_loader import YAMLLoader
from core.utils.os_sys import get_abs_path
#  _YAML_FILE_VAR is the name of the class attribute that ConfigMeta will
#  look for in each subclass that points to an optional YAML config file.
_YAML_FILE_VAR = "_YAML_PATH"

#os.path.dirname(sys.modules[new_class.__module__].__file__)

class ConfigMeta(type):
    """Base metaclass for Config classes that can be loaded from environment
    and designed to manage subclassed and multiple inheritances."""

    def __new__(mcs, name, bases, attrs, *args, **kwargs):
        new_class = super().__new__(mcs, name, bases, attrs)

        new_class.__init_subclass__ = classmethod(mcs.init_subclass())
        new_class._is_top_parent = bases == ()
        if rel_yaml_file := getattr(new_class, _YAML_FILE_VAR, None):
            abs_yaml_file = get_abs_path(rel_yaml_file, new_class)
            setattr(new_class, _YAML_FILE_VAR, abs_yaml_file)
        new_class.import_values = classmethod(mcs.import_values())
        new_class.generate_config_field = classmethod(mcs.generate_config_field())
        new_class._class_fields = classmethod(mcs.class_fields())
        new_class._class_values = classmethod(mcs.class_values())
        new_class._values = {}
        new_class.import_values()

        local_defined_init_func = new_class.__init__
        new_class.__init__ = mcs.init(new_class, local_defined_init_func)
        return new_class

    @classmethod
    def init(mcs, cls, local_init):
        def _init(self, *args, **kwargs):
            if cls._is_top_parent:
                # Pre_init_code here
                print(f"Running pre-init from {cls.__name__}")
            super(cls, self).__init__(*args, **kwargs)

            local_init(self, *args, **kwargs)
        return _init

    @staticmethod
    def init_subclass():
        def _init_subclass(cls, **kwargs):
            pass
        return _init_subclass

    @staticmethod
    def generate_config_field():
        def _gen_field(cls, name: str, metadata: dict = None, by_value=None):
            metadata = metadata or {}
            metadata['name'] = name
            if by_value:
                metadata['datatype'] = type(by_value)
                metadata['default'] = by_value
            if (metadata.get('default', None) is not None and
                    metadata.get('datatype', None) is None):
                metadata['datatype'] = type(metadata['default'])
            return ConfigField(**metadata)
        return _gen_field

    @staticmethod
    def class_fields():
        def _class_fields(cls) -> list:
            fields = []

            # Get child YAML
            if yaml_file := getattr(cls, _YAML_FILE_VAR, None):
                yaml_data = YAMLLoader(yaml_file).asdict
                for k, v in yaml_data.items():
                    if isinstance(v, (dict, type(None))):
                        fields.append(cls.generate_config_field(k, v))
                    else:
                        fields.append(cls.generate_config_field(k, by_value=v))
            # Get Class
            for attr in [a for a in vars(cls) if a != _YAML_FILE_VAR and is_valid_envvar_name(a)]:
                val = getattr(cls, attr)
                if isinstance(val, ConfigField):
                    fields.append(val)
                elif isinstance(val, dict):
                    if not set(val.keys()).difference(set(ConfigField._fields.keys())):
                        fields.append(cls.generate_config_field(attr, val))
                elif isinstance(val, tuple):
                    metadata = {}
                    try:
                        for i, item in enumerate(val):
                            if i == 0:  # first index is the value
                                metadata['datatype'] = type(item)
                            elif isinstance(item, str):
                                if item.lower() == 'locked':
                                    metadata['locked'] = True
                                elif item.lower() == 'required':
                                    metadata['required'] = True
                                elif item.startswith('metadata={') and item.endswith('}'):
                                    field_meta = {}
                                    for metastr in [s.strip() for s in item.split(',')]:
                                        kw, val = parse_keyword_str(metastr)
                                        field_meta[kw] = val
                                    metadata['metadata'] = field_meta
                                elif set(item).intersection({'=', ':'}):
                                    kw, val = parse_keyword_str(item)
                                    metadata[kw] = val
                        fields.append(cls.generate_config_field(attr, metadata))
                    except:
                        pass
                else:
                    fields.append(cls.generate_config_field(attr, by_value=val))
            return fields
        return _class_fields

    @staticmethod
    def class_values():
        def _class_values(cls, class_fields: list) -> list:
            yaml_data = {}
            if yaml_file := getattr(cls, _YAML_FILE_VAR, None):
                yaml_data = YAMLLoader(yaml_file).asdict
            values = []
            for field in class_fields:
                value = None
                for priority in reversed(ConfigEnvVarType_Priority):
                    new_value = None
                    if (priority == ConfigEnvVarType.OS_ENVIRON and
                            field.name in os.environ):
                        new_value = os.environ.get(field.name)
                        new_value = ConfigValue(field, new_value, priority, cls.__name__)
                    elif (priority == ConfigEnvVarType.CONFIG_CLASS and
                          field.name in vars(cls)):
                        new_value = getattr(cls, field.name)
                        if isinstance(new_value, tuple):
                            new_value = new_value[0]
                        new_value = ConfigValue(field, new_value, priority, cls.__name__)
                    elif (priority == ConfigEnvVarType.CONFIG_YAML and
                          field.name in yaml_data):
                        yaml_value = yaml_data[field.name]
                        if not isinstance(yaml_value, (dict, type(None))):
                            if isinstance(yaml_value, tuple):
                                yaml_value = yaml_value[0]
                            new_value = ConfigValue(field, yaml_value, priority, cls.__name__)
                    else:
                        continue
                    if new_value:
                        value = value.compare(new_value) if value else new_value
                    elif field.default is not None:
                        new_value = ConfigValue(field, field.default, ConfigEnvVarType.CONFIG_CLASS, cls.__name__)
                        value = value.compare(new_value) if value else new_value
                if value:
                    values.append(value)
            return values
        return _class_values

    @staticmethod
    def import_values():
        def _import_values(cls: ConfigMeta):
            existing_values = {}
            for base in cls.__bases__:
                if isinstance(base, ConfigMeta):
                    existing_values.update(base._values)
                else:
                    # TODO: figure out how to import non-ConfigMeta attrs
                    pass

            fields = cls._class_fields()
            new_values = cls._class_values(fields)

            for value in new_values:
                if existing_value := existing_values.get(value.field.name, None):
                    value = existing_value.compare(value)
                existing_values[value.field.name] = value
            cls._values = existing_values

            for attr, config_value in cls._values.items():
                new_attr = config_value.field.alt_name or attr
                setattr(cls, new_attr.lower(), config_value.value)
                if hasattr(cls, attr):
                    delattr(cls, attr)
        return _import_values


def parse_keyword_str(kw_str):
    """ takes str 'keyword=my value' and returns {keyword: 'my_value'}"""
    delimiters = ['=', ':']
    kw, val = None, None
    # Find first instance of any delimiter
    sep = min([i for i in [kw_str.find(d) for d in delimiters] if i >=0] or [-1])
    if 0 >= sep or sep == len(kw_str) - 1:
        # (delimiter not found or is first/last character)
        raise Exception(f'bad format: {kw_str}')
    else:
        kw, val = kw_str[: sep], kw_str[sep+1:]

    quotes = ("'", '"')
    if val[0] in quotes and val[-1] in quotes and val[0] == val[-1]:
        return kw, val[1:-1]
    elif val.lower() == 'true':
        return kw, True
    elif val.lower() == 'false':
        return kw, False
    else:
        try:
            return kw, int(val)
        except ValueError:
            try:
                return kw, float(val)
            except ValueError:
                return kw, val

