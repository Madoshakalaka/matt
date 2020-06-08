import os
from enum import Enum, auto
from pathlib import Path


class AppName(Enum):
    DARKEST_DUNGEON = auto()

    def display_name(self) -> str:
        words = []
        for cap_word in self.name.split("_"):
            words.append(cap_word.lower().capitalize())
        return " ".join(words)

    def camel_snake(self) -> str:
        return self.name.lower()

    def handler_class_name(self) -> str:
        return self.display_name().replace(" ", "") + "Handler"

    def get_app_cache_dir(self) -> Path:
        return Path(os.path.dirname(__file__)) / ("." + self.camel_snake())
