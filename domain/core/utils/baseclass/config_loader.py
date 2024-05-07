from typing import List
from dataclasses import MISSING
from core.utils.baseclass.yaml_loader import YAMLLoader
from core.utils.enums.config import SystemEnvironment
from string import ascii_uppercase, ascii_lowercase, digits
from operator import attrgetter
import os

ENVIRON_MAP = {
    SystemEnvironment.LOCAL: 'LOCAL',
    SystemEnvironment.TEST: 'TEST',
    SystemEnvironment.STAGING: 'STAGE',
    SystemEnvironment.UAT: 'UAT'
}


class FieldMeta:
    _DEF_REQUIRED_FIELD = False  # Only explicitly declared keys are required
    _STRICT_DATATYPES = True  # Only allow values that are of _VALID_DATATYPES
    _DEF_DATATYPE = str
    __ERR = "FieldMeta - "
    _VALID_DATATYPES_AND_DEFAULTS = [(int, 0), (str, ""), (bool, False)]

    def __init__(
            self,
            name: str,      # Name of Field
            datatype: type = MISSING,  # Datatype of Field
            required: bool = MISSING,  # Field is required
            default: [str, int, bool] = MISSING,  # Default value
            alt_name: str = MISSING,  # Alternate name of Field (How it will be saved in Config() instance)
            valid_datatypes: List[tuple] = MISSING  # Allowable value datatypes
    ):
        valid_datatypes = (
            FieldMeta._VALID_DATATYPES_AND_DEFAULTS
            if valid_datatypes == MISSING else valid_datatypes)
        self.__validate_valid_datatypes(valid_datatypes)
        valid_datatypes = dict(valid_datatypes)
        self.valid_datatypes = valid_datatypes

        datatype = FieldMeta._DEF_DATATYPE if datatype == MISSING else datatype
        if isinstance(datatype, str):
            for dtype in self.valid_datatypes.keys():
                if dtype.__name__.lower() == datatype:
                    datatype = dtype

        required = FieldMeta._DEF_REQUIRED_FIELD if required == MISSING else required
        required = (True if required not in
                    [0, False, "false", "False", "f", "F", "FALSE"] else False)

        self.__validate_name(name)
        self.name = name
        self.alt_name = MISSING
        if alt_name is not MISSING:
            self.__validate_name(alt_name)
            self.alt_name = alt_name

        if FieldMeta._STRICT_DATATYPES and datatype not in valid_datatypes:
            raise TypeError(self.__ERR + f"Unsupported Field datatype '{datatype}' for field '{name}'.")
        self.datatype = datatype
        self.required = required
        if default is not MISSING:
            default = self.validate(default, True)
        if default is not MISSING and not isinstance(default, datatype):
            raise ValueError(
                self.__ERR + f"Field `{name}` is of type `{datatype}` but has an "
                             f"inappropriate default value of `{default}` ({type(default)})")
        self.default = default
    def validate(self, value, force_type=False):
        if value is MISSING:
            return None
        elif isinstance(value, self.datatype):
            return value
        elif force_type:
            try:
                return self.datatype(value)
            except Exception:
                return None
        return None

    @staticmethod
    def __validate_name(name):
        if not isinstance(name, str) or len(str(name)) < 2:
            raise KeyError(
                FieldMeta.__ERR + f"Field name must be a string of at least 2 characters. Got `{name}`")

        if name[0] in digits:
            raise KeyError(
                FieldMeta.__ERR + f"Field name cannot begin with a digit.  Got '{name}'")

        if illegal_char := (
                set(name).difference(set(ascii_lowercase + ascii_uppercase + digits + '_'))):
            raise KeyError(
                FieldMeta.__ERR + f"Field name '{name}' cannot contain illegal "
                                  f"characters: {', '.join(list(illegal_char))}")

    @staticmethod
    def __validate_valid_datatypes(vtypes):
        for vtype, default in vtypes:
            if not isinstance(vtype, type) or not isinstance(default, vtype):
                default = f'"{default}"' if vtype is str else default
                raise TypeError(
                    FieldMeta.__ERR + f"`valid_datatypes` must be a list of (type, default value). "
                                      f"Got (`{vtype}`, {default}).")


class ConfigYAML:

    _FORCE_TYPE = True          # Tries to cast into appropriate type (eg. "1" -> 1 if datatype=int)
    # if envvar isn't found in os.environ with supplied name, automatically retry with name.upper()
    _RETRY_UPPER = True
    __ERR = "Config - "             # Error message prefix
    _ENVVAR_NAME = "ENVIRONMENT"    # env var that states which environment
    _DEF_ENVIRON = "LOCAL"          # Default Environment

    # os.environ variables have suffixes based on environment
    # (eg - DATABASE_URL_UAT, DATABASE_URL_TEST)
    _ENV_BASED_NAME_SUFFIX = True
    _YAML_FILE = 'core/config/config.yaml'
    def __init__(self):

        self._data = {}
        self._data = YAMLLoader(self._YAML_FILE)._asdict
        self.__fields = []

        self._environment = self._set_environment()
        for k, v in self._data.items():
            v = v or {}
            self.__fields.append(self._format_config_data(k, v))
        self.import_data()

    @property
    def environment(self):
        return self._environment

    def _set_environment(self):
        env = os.environ.get(self._ENVVAR_NAME, self._DEF_ENVIRON)
        if env in SystemEnvironment.names():
            return SystemEnvironment[env]
        return self._DEF_ENVIRON

    def import_data(self):
        for field in sorted(self.__fields, key=attrgetter('name')):
            envvar_key = self._envvar_key(field)
            envvar_value = self._envvar_value(envvar_key, field)

            if envvar_value is not MISSING:
                attr = field.name
                if field.alt_name is not MISSING:
                    attr = field.alt_name
                attr = attr.lower()

                setattr(self, attr, envvar_value)

    def _envvar_key(self, field: FieldMeta):
        name = field.name
        if self._ENV_BASED_NAME_SUFFIX:
            if sfx := ENVIRON_MAP.get(self.environment, None):
                name += f"_{sfx}"
        return name

    def _envvar_value(self, key, field: FieldMeta):
        val = os.environ.get(key, MISSING)
        if val is MISSING and self._RETRY_UPPER:
            val = os.environ.get(key.upper(), MISSING)
        if val is MISSING and field.default is not MISSING:
            val = field.default

        if key.upper() == self._ENVVAR_NAME.upper():
            # `ENVIRONMENT` must be set at the session-level - do not let YAML override this
            val = MISSING

        elif val is MISSING:
            if field.required:
                raise ValueError(
                    self.__ERR + f"Environment Variable `{field.name}` is "
                                 f"required but not defined and no default "
                                 f"value for this field has been provided.")
            else:
                val = field.valid_datatypes[field.datatype]

        elif val is not MISSING:
            if field.validate(val, self._FORCE_TYPE) is None:
                raise ValueError(
                    self.__ERR + f"Environment Variable `{key}` is "
                                 f"expecting a datatype of `{field.datatype}`; "
                                 f"got `{val}` ('{type(val)}') instead."
                )
            val = field.validate(val, self._FORCE_TYPE)

        return val

    @staticmethod
    def _format_config_data(key, data):
        return FieldMeta(
            name=key,
            default=data.get('default', MISSING),
            required=data.get('required', MISSING),
            datatype=data.get('datatype', MISSING)
        )


    def __init_subclass__(cls, **kwargs):
        cls._YAML_FILE = [cls._YAML_FILE]
        parent = cls
        while parent.__base__:
            parent = parent.__base__
            if issubclass(parent, ConfigYAML):
                if isinstance(parent._YAML_FILE, list):
                    cls._YAML_FILE += parent._YAML_FILE
                else:
                    cls._YAML_FILE.append(parent._YAML_FILE)
        cls._YAML_FILE = list(set(cls._YAML_FILE))



    
    