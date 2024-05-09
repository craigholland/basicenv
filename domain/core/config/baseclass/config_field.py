from typing import List, Any, _GenericAlias # noqa
from dataclasses import dataclass, field, fields, InitVar
from string import ascii_uppercase, ascii_lowercase, digits


#  {type: default value} of datatypes allowed in Config files
_VALID_DATATYPES = {
    int: 0,
    str: '',
    bool: False
}
# Variable names must be strings and only consist of
# uppercase chars, digits, and underscore
VALID_VARNAME_CHARS = set(ascii_uppercase + digits + '_')
ERR_PFX = "Environment Variable Config - "


def is_valid_envvar_name(val):
    return all([
        isinstance(val, str),
        list(set(val).difference(VALID_VARNAME_CHARS)) == [],
        len(val) > 2,
        val[0] not in digits
        ])


class ConfigFieldError:
    """Message Literals used for Errors in ConfigField."""
    TYPE_MISMATCH = (
            ERR_PFX + "Field `{0}` must be of type `{1}`.  Got '{2}' "
                      "({3}) instead.")
    TYPE_MISMATCH_SET = (
            ERR_PFX + "Field '{0}' has a metadata field '{1}' that only "
                      "accepts values of type '{2}. Got {3} ({4}) instead."
    )
    BAD_DEFAULT = (
            ERR_PFX + "Field `{0}` is of type `{1}` but has an "
                      "inappropriate default value of `{2}` ({3})")
    NAME_LENGTH = (
            ERR_PFX + " `{0}` field must be at least 2 characters in "
                      "length. Got '{1}'.")
    NAME_STARTSWITH = (
            ERR_PFX + "Field `{0}` cannot being with a digit - Got '{1}'."
    )
    NAME_ILLEGALCHAR = (
        ERR_PFX + "Field `{0}` cannot contain illegal characters: {1}. Got '{2}'."
    )
    INVALID_KEY = (
            ERR_PFX + "ConfigField has no metadata field '{1}'."
    )


@dataclass
class ConfigField:
    name: str
    # datatype can be any singular type of the established VALID_DATATYPES,
    # OR, it can be a list of any number of them.  The default is <str>
    datatype: [type, List[type]] = str
    alt_name: str = ''
    required: bool = False
    default: Any = None
    locked: bool = False
    metadata: dict = field(default_factory=dict)
    _raise_exception_on_edit: InitVar[bool] = True

    def __post_init__(self, _raise_exception_on_edit):

        self.__validate()
        pass

    def __validate(self):
        self.__validate_name()
        if self.alt_name:
            self.__validate_name(self.alt_name, 'alt_name')
        for field in ['datatype', 'required', 'locked', 'metadata']:
            val = getattr(self, field)
            if field == 'datatype' and not isinstance(val, type):
                if val := self.__validate_datatype(self.datatype):
                    self.datatype = val
            if not self.__isinstance_by_attr(field, val):
                raise TypeError(
                    ConfigFieldError.TYPE_MISMATCH.format(
                        field, self._fields[field].type, val, type(val)))

        if dvalue := self.default:
            if not self.validate_value(dvalue):
                raise ValueError(
                    ConfigFieldError.BAD_DEFAULT.format(
                        self.name, self.datatype, dvalue, type(dvalue)))

    @classmethod
    def __isinstance_by_type(cls, value: Any, datatype: [type, List[type]]):
        if datatype is Any:
            return True
        elif isinstance(datatype, list):
            valid = False
            if single_types := [x for x in datatype if isinstance(x, type)]:
                valid = valid or isinstance(value, tuple(single_types))
                if valid:
                    return valid
            if list_of_types := [x for x in datatype if isinstance(x, _GenericAlias)]:
                for genAlias in list_of_types:
                    typeset = [t for t in genAlias.__args__ if isinstance(t, type)]
                    if isinstance(value, list):
                        valid = valid or all([isinstance(v, tuple(typeset)) for v in value])
                        if valid:
                            break
            return valid
        elif isinstance(datatype, type):
            return isinstance(value, datatype)

    @classmethod
    def __isinstance_by_attr(cls, attr, value):
        if field_meta := cls._fields.get(attr, None):
            ftype = field_meta.type
            if ftype == Any:
                return True
            elif isinstance(ftype, (type, list)):
                return cls.__isinstance_by_type(value, ftype)
        else:
            raise KeyError(
                ConfigFieldError.INVALID_KEY.format(attr)
            )

    def validate_value(self, value):
        return self.__isinstance_by_type(value, self.datatype)

    def cast_value(self, value, as_type=None):
        as_type = as_type or self.datatype
        if isinstance(as_type, type):
            try:
                return as_type(value)
            except Exception:
                return None
        elif isinstance(as_type, (list, tuple)):
            for dtype in as_type:
                if casted_value := self.cast_value(value, dtype):
                    return casted_value
            return None
        return None

    @classmethod
    def __validate_datatype(cls, value: [str, type, list]):
        """Return <type> if value is either in VALID_DATATYPES or
        the string name of one of those types. Else, return None"""

        if isinstance(value, str):
            for datatype in _VALID_DATATYPES.keys():
                if value.lower() == datatype.__name__:
                    return datatype
        elif isinstance(value, type) and value in _VALID_DATATYPES:
            return value
        elif isinstance(value, list):
            return (not any([isinstance(dtype, (list, tuple)) for dtype in value])
                    and all([cls.__validate_datatype(dtype) for dtype in value]))
        return None

    def __validate_name(self, name=None, field='name'):
        name = name or self.name
        ftype = self._fields[field].type
        if not self.__isinstance_by_attr(field, name):
            raise TypeError(ConfigFieldError.TYPE_MISMATCH %
                            (field, ftype, name, type(name)))
        
        if len(name) < 2:
            raise ValueError(ConfigFieldError.NAME_LENGTH.format(field, name))
        
        if name[0] in digits:
            raise ValueError(ConfigFieldError.NAME_STARTSWITH.format(field, name))

        if illegal_char := set(name).difference(VALID_VARNAME_CHARS):
            raise KeyError(
                ConfigFieldError.NAME_ILLEGALCHAR %
                (field, ', '.join(list(illegal_char)), name)
            )

    @classmethod
    @property
    def _fields(cls) -> dict:
        return dict([(f.name, f) for f in fields(cls)])

    @property
    def is_valid(self):
        try:
            self.__validate()
            return True
        except Exception:
            return False

    def __setattr__(self, key, value):
        if key == 'datatype' and isinstance(value, str):
            # This allows datatype to accept type names as a string
            if val := self.__validate_datatype(value):
                value = val
        valid_value = self.__isinstance_by_attr(key, value) or key.startswith('_')
        if valid_value:
            super().__setattr__(key, value)
        elif getattr(self, '_raise_exception_on_edit', False):
            raise ValueError(
                ConfigFieldError.TYPE_MISMATCH_SET.format(
                    self.name, key, self.datatype, value, type(value))
            )

    def __eq__(self, val):
        if not isinstance(val, ConfigField):
            return False

        return self.name.lower() == val.name.lower()







