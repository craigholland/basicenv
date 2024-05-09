from core.config.baseclass.config_field import ConfigField
from core.config.baseclass.config_enums import ConfigEnvVarType
from dataclasses import dataclass, InitVar
from typing import Any

ConfigEnvVarType_Priority = [
    # ConfigEnvVarType determines the sequence in which ConfigMeta searches
    # for and defines config variables...with those of lower priority being
    # defined first, but possibly overwritten by those of higher priority.
    # Note: A variable of low priority can be 'locked', thus disabling
    # a higher priority from overwriting it.

    ConfigEnvVarType.CONFIG_INSTANCE,   # Highest Priority
    ConfigEnvVarType.CONFIG_CLASS,
    ConfigEnvVarType.CONFIG_YAML,
    ConfigEnvVarType.OS_ENVIRON         # Lowest Priority
]

_ERR_PFX = "ConfigValue: "


class ConfigValueError:
    """Message Literals used for Errors in ConfigValue."""
    UNCOMMON = (
            _ERR_PFX + "Expected type 'ConfigValue'. Got '{0}' instead.")
    BAD_FIELD = (
            _ERR_PFX + "Config `field` must be of type `ConfigField`. "
                       "Got {0} instead.")
    BAD_SOURCE = (
            _ERR_PFX + "Config `{0}.source` must be of type "
                       "`ConfigEnvVarType`. Got {1} instead.")
    BAD_VALUE = (_ERR_PFX + "Config `{0}.value` must be of type(s) {1}. Got "
                            "{2} instead.")
    REQUIRED_VALUE = (_ERR_PFX + "field '{0}' value is required and no default"
                                 " value was defined.")
    LOCKED = (_ERR_PFX + "Locked. Cannot edit field `{0}`.")


@dataclass
class ConfigValue:
    field: ConfigField
    _value: Any = None
    source: ConfigEnvVarType = ConfigEnvVarType.OS_ENVIRON
    source_name: str = ''
    _raise_exception_on_edit: InitVar[bool] = True

    def __post_init__(self, _raise_exception_on_edit):
        if self.value is None:
            if self.field.default:
                self.value = self.field.default

        self._initialized = True
        self.__validate()

    def __validate(self):
        if not isinstance(self.field, ConfigField):
            raise ValueError(ConfigValueError.BAD_FIELD.format(type(self.field)))
        field_name = self.field.name
        if not isinstance(self.source, ConfigEnvVarType):
            raise ValueError(ConfigValueError.BAD_SOURCE.format(field_name, type(self.source)))
        if not self.field.validate_value(self.value):
            if self.value is None and self.field.required:
                raise ValueError(ConfigValueError.REQUIRED_VALUE.format(field_name))
            raise ValueError(ConfigValueError.BAD_VALUE.format(field_name, self.field.datatype, type(self.value)))

    @property
    def value(self):
        if self._value is not None:
            return self._value
        if self.field.default:
            return self.field.default
        return None

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def _is_initialized(self):
        return getattr(self, '_initialized', False)

    def __setattr__(self, key, value):
        if self._is_initialized and self.is_locked:
            if self._raise_exception_on_edit:
                raise ValueError(ConfigValueError.LOCKED.format(key))
            return
        super().__setattr__(key, value)
        if self._raise_exception_on_edit and self._is_initialized:
            self.__validate()

    @property
    def source_priority(self):
        # Lower Number = Higher Priority
        return ConfigEnvVarType_Priority.index(self.source)

    def __ge__(self, config_value):
        return self > config_value or self == config_value

    def __le__(self, config_value):
        return self < config_value or self == config_value
    
    def __gt__(self, config_value):
        if self.common(config_value):
            return self.source_priority < config_value.source_priority
        raise TypeError(ConfigValueError.UNCOMMON.format(type(config_value)))
            
    def __eq__(self, config_value):
        if self.common(config_value):
            return self.source_priority == config_value.source_priority
        raise TypeError(ConfigValueError.UNCOMMON.format(type(config_value)))
        
    def __lt__(self, config_value):
        if self.common(config_value):
            return self.source_priority > config_value.source_priority
        raise TypeError(ConfigValueError.UNCOMMON.format(type(config_value)))

    @property
    def is_locked(self):
        return self.field.locked

    def common(self, config_value):
        return (
                isinstance(config_value, ConfigValue) and
                config_value.field == self.field)

    def compare(self, config_value):
        """Compare 2 ConfigValues and return the one of higher priority IF
        the existing value is not locked; otherwise, return existing
        value regardless of new value's priority."""

        #  The context of the comparison is that 'self' is the existing value
        if self.common(config_value):
            if self.field.name == 'ENV_URL':
                pass
            if self.is_locked or self > config_value:
                return self

            # if existing value is not locked and has <= priority to new value
            return config_value
        raise TypeError(ConfigValueError.UNCOMMON.format(type(config_value)))

    def copy(self, unlocked=True):
        new_field = self.field
        if unlocked:
            new_field.locked = False
        return ConfigValue(
            new_field,
            self.value,
            self.source
        )
