from core.config.baseclass import ConfigMeta


class BaseConfig(metaclass=ConfigMeta):
    """The base Config Class for all services."""

    """
    Config variables/values can be set at multiple levels:
        -   os.environ['var_name']
        -   as a Class attribute (here or a subclass)
        -   in a referenced YAML file (pointed to by _YAML_FILE)
        -   at the instance-level
        
    The priority to which each of these levels has over the others is
    defined in the list `ConfigEnvVarType_Priority` 
    (found in: core.config.baseclass.config_value.py)
    """

    # `_YAML_PATH` is the file location of desired YAML-file relative to the
    # particular Config() class.
    _YAML_PATH = 'config.yaml'


config = BaseConfig()





