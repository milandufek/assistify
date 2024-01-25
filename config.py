import json
import os
from dataclasses import dataclass, field


class ConfigLoader:

    def __init__(self) -> None:
        self.global_conf_path = 'config.json'
        self.user_conf_path = 'config.user.json'

    def get_config(self) -> dict:
        global_conf = self.load_json(self.global_conf_path)
        user_conf = {}

        if os.path.isfile(self.user_conf_path):
            user_conf = self.load_json(self.user_conf_path)

        return self.merge_configs(global_conf, user_conf)

    def load_json(self, conf_path: str) -> dict:
        with open(conf_path) as f:
            config = json.loads(f.read())

        return config

    def merge_configs(self, first: dict, second: dict) -> dict:
        merged = {}

        for key, val in first.items():
            if isinstance(val, dict):
                merged[key] = self.merge_configs(val, second.get(key, {}))
            else:
                merged[key] = second.get(key, val)

        for key, val in second.items():
            if key not in first:
                merged[key] = val

        return merged


@dataclass
class Config:
    models: dict
    templates: dict
    archive: bool = True
    archive_path: str = 'archive'
    copy_to_clipboard: bool = True
    currency_exchange_rate: float = 1.0
    currency: str = 'USD'
    resizable_window: bool = False
    theme: str = 'dark'


@dataclass
class UI:
    button_generate: str
    button_load_article: str
    copied: str
    error_load_article: str
    error_no_input: str
    error_no_url: str
    error: str
    message_input: str
    message_url: str
    ready: str
    request_completed: str
    separator: str
    title: str
    waiting: str
    button_width: int = 16
    dropdown_width: int = 14
    paddings: dict = field(default_factory=lambda: {'padx': 2, 'pady': 2})
