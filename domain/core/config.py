import os


class BaseConfig:
    """
    This is the base config for all services.  Inherit from it and add
    specific config vars to it.
    """

    def __init__(self):
        self._str_cache = dict()
        self._int_cache = dict()

        self.uhg_debug = self.get_int("UHG_DEBUG", 0)
        self.env_url = self.get_str("ENV_URL", "")
        self.app_url = self.get_str("APP_URL", "")
        self.deployment_locale = self.get_str(
            "DEPLOYMENT_LOCALE", "US/Pacific"
        )

    def get_int(self, name: str, default: int, required=False):
        if val := self._int_cache.get(name):
            return val

        val = os.getenv(name, "")
        if required is True and val == "":
            raise Exception(f"Config.get_int() '{name}' is required")
        if val != "" and val.isdigit():
            val = int(val)
        else:
            val = default
        self._int_cache[name] = val
        return val

    def get_bool(self, name: str, default: bool):
        val = self.get_int(name, 0)
        if val == 1:
            return True
        elif val == 0:
            return False
        return default

    def get_str(self, name: str, default: str, required=False):
        val = self._str_cache.get(name)
        if val is None:
            val = os.getenv(name, default)
            if required is True and not val:
                raise Exception(f"Config.get_str() '{name}' is required")
            self._str_cache[name] = val
        return val
