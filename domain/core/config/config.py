from core.utils.baseclass.config_loader import ConfigYAML


class BaseConfig(ConfigYAML):
    """
    This is the base config for all services.  Inherit from it and add
    specific config vars to it.
    """
    _YAML_FILE = 'core/config/config2.yaml'





