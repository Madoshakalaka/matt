import os
from enum import Enum, auto
from pathlib import Path


class AppID(Enum):
    DARKEST_DUNGEON = auto()

    def display_name(self) -> str:
        names = {self.DARKEST_DUNGEON: "Darkest Dungeon"}
        return names[self]

    def camel_snake(self) -> str:
        return self.name.lower()

    def get_app_cache_dir(self) -> Path:
        return Path(os.path.dirname(__file__)) / ("." + self.camel_snake())
