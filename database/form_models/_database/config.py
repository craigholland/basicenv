from core.config import BaseConfig


class Config(BaseConfig):
    _YAML_PATH = "db_config.yaml"

    @classmethod
    @property
    def database_url(cls):
        url_parts = [
            'db_database', 'db_password', 'db_protocol', 'db_uri',
            'db_uri_port', 'db_user']
        url_dct = {}
        valid = True
        for part in url_parts:
            if val := getattr(cls, part, None):
                url_dct[part] = str(val)
            else:
                valid = False
                break
        if valid:
            return (
                f"{url_dct['db_protocol']}://{url_dct['db_user']}:{url_dct['db_password']}"
                f"@{url_dct['db_uri']}:{url_dct['db_uri_port']}/{url_dct['db_database']}"
            )
        return None


config = Config()
