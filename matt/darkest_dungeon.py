import os
import subprocess
from pathlib import Path
from typing import Iterable, List
import sys
from matt import AppID


# used in dev
def get_monster_folder_names() -> List[str]:
    d = "/home/matt/.steam/steam/steamapps/common/DarkestDungeon/monsters"
    return [p.name for p in Path(d).glob("*") if p.is_dir()]


def find_warrens_1() -> Path:
    workshop_content_dir = Path("~/.steam/steam/steamapps/workshop/content/")
    for content in workshop_content_dir.glob("*"):
        if content.is_dir():
            if (content / "1885424457").exists():
                return content / "1885424457"


# ['pew_small', 'swine_reaver', 'brigand_sapper', 'spider_webber', 'swinetaur', 'brigand_hunter', 'templar_ranged_mb', 'siren', 'drowned_pirate', 'fishman_shaman', 'crow', 'jellyfish', 'ancestor_nebula', 'fungal_bloat', 'swine_piglet', 'cultist_witch', 'hag', 'cauldron_full', 'pew_medium', 'snail_urchin', 'spider_webber_old', 'maggot', 'skeleton_courtier', 'shambler_tentacle', 'ancestor_perfect', 'ancestor_heart', 'totem_guard', 'cell_battle', 'swine_drummer', 'octotank', 'ghoul', 'errant_flesh_dog', 'shuffler', 'swine_skiver', 'skeleton_common', 'nest', 'ectoplasm', 'formless_weak', 'fishman_crabby', 'ancestor_pod', 'collector_shaman', 'spider_spitter', 'formless_melee', 'brigand_blood', 'fungal_artillery', 'cultist_orgiastic', 'drowned_captain', 'cell_white', 'virago_hateful', 'formless_melee_old', 'ancestor_flawed', 'brigand_fuseman', 'drowned_anchor', 'swine_prince_old', 'ectoplasm_large', 'crone', 'swine_slasher', 'brigand_barrel', 'prophet', 'cultist_harpy', 'brigand_raider', 'corpse_large', 'templar_melee', 'cultist_brawler', 'brigand_cutthroat', 'fishman_harpoon', 'swine_wretch', 'skeleton_defender', 'skeleton_captain', 'templar_melee_mb', 'corpse', 'spider_spitter_old', 'ancestor_small', 'templar_ranged', 'carrion_eater', 'cauldron_empty', 'ancestor_big', 'totem_attack', 'drowned_anchored', 'cultist_warlord', 'errant_flesh_bat', 'skeleton_militia', 'brigand_fusilier', 'formless_guard', 'rabid_dog', 'skeleton_militia_old', 'skeleton_arbalist', 'necromancer', 'bloated_corpse', 'skeleton_spear', 'skeleton_bearer', 'collector_battle', 'madman', 'gargoyle', 'collector', 'swine_piglet_old', 'brigand_cannon', 'skeleton_spear_old', 'virago_shroom', 'unclean_giant', 'collector_protect', 'shambler', 'swine_prince', 'pew_large', 'carrion_eater_big', 'cyst', 'cultist_shrouded', 'formless_ranged']


class Skin:
    WARRENS_1_DIR = find_warrens_1()

    @staticmethod
    def find_installed_skins():
        pass

    @staticmethod
    def load_downloaded_skins() -> Iterable[Path]:
        return AppID.DARKEST_DUNGEON.get_app_cache_dir().glob("*")

    @staticmethod
    def load_applied_skins():
        pass

    @staticmethod
    def download_skins() -> subprocess.Popen:
        """
        async
        :return: a StringIO for progress
        """
        return subprocess.Popen(
            [
                sys.executable,
                "-m",
                "gitdir",
                "-f",
                "https://github.com/Madoshakalaka/warehouse/tree/master/darkest_dungeon/skins",
            ],
            cwd=Path(os.path.dirname(__file__)) / ".darkest_dungeon",
            stdout=subprocess.PIPE,
            encoding="utf-8",
        )

    def __init__(self, name_stem: str):
        """
        :param name_stem: name under git:warehouse/darkest_dungeon/skins
        """
        self.name_stem = name_stem


if __name__ == "__main__":
    # Skin.download_skins()
    from pyunpack import Archive
    from tempfile import TemporaryDirectory

    big = get_monster_folder_names()
    print(big)

    # with TemporaryDirectory() as temp_dir:
    #     Archive(
    #         "/home/matt/PycharmProjects/matt/matt/.darkest_dungeon/skeleton_militia_pack.zip"
    #     ).extractall(temp_dir)
    #     for b in Path(temp_dir).rglob("*"):
    #         print(b)
