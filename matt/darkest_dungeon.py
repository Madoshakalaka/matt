import os
import subprocess
from collections import Counter
from itertools import chain
from pathlib import Path
from shutil import rmtree
from subprocess import Popen
from threading import Thread
from typing import Iterable, List, Dict
import sys
from matt import AppName
import PySimpleGUI as sg
from pyunpack import Archive

# used in dev
from matt.app_components import AppHandler


def get_monster_folder_names() -> List[str]:
    d = "/home/matt/.steam/steam/steamapps/common/DarkestDungeon/monsters"
    return [p.name for p in Path(d).glob("*") if p.is_dir()]


def find_warrens_1() -> Path:
    workshop_content_dir = Path("/home/matt/.steam/steam/steamapps/workshop/content/")
    for content in workshop_content_dir.glob("*"):
        if content.is_dir():
            if (content / "1885424457").exists():
                return content / "1885424457"


# ['pew_small', 'swine_reaver', 'brigand_sapper', 'spider_webber', 'swinetaur', 'brigand_hunter', 'templar_ranged_mb', 'siren', 'drowned_pirate', 'fishman_shaman', 'crow', 'jellyfish', 'ancestor_nebula', 'fungal_bloat', 'swine_piglet', 'cultist_witch', 'hag', 'cauldron_full', 'pew_medium', 'snail_urchin', 'spider_webber_old', 'maggot', 'skeleton_courtier', 'shambler_tentacle', 'ancestor_perfect', 'ancestor_heart', 'totem_guard', 'cell_battle', 'swine_drummer', 'octotank', 'ghoul', 'errant_flesh_dog', 'shuffler', 'swine_skiver', 'skeleton_common', 'nest', 'ectoplasm', 'formless_weak', 'fishman_crabby', 'ancestor_pod', 'collector_shaman', 'spider_spitter', 'formless_melee', 'brigand_blood', 'fungal_artillery', 'cultist_orgiastic', 'drowned_captain', 'cell_white', 'virago_hateful', 'formless_melee_old', 'ancestor_flawed', 'brigand_fuseman', 'drowned_anchor', 'swine_prince_old', 'ectoplasm_large', 'crone', 'swine_slasher', 'brigand_barrel', 'prophet', 'cultist_harpy', 'brigand_raider', 'corpse_large', 'templar_melee', 'cultist_brawler', 'brigand_cutthroat', 'fishman_harpoon', 'swine_wretch', 'skeleton_defender', 'skeleton_captain', 'templar_melee_mb', 'corpse', 'spider_spitter_old', 'ancestor_small', 'templar_ranged', 'carrion_eater', 'cauldron_empty', 'ancestor_big', 'totem_attack', 'drowned_anchored', 'cultist_warlord', 'errant_flesh_bat', 'skeleton_militia', 'brigand_fusilier', 'formless_guard', 'rabid_dog', 'skeleton_militia_old', 'skeleton_arbalist', 'necromancer', 'bloated_corpse', 'skeleton_spear', 'skeleton_bearer', 'collector_battle', 'madman', 'gargoyle', 'collector', 'swine_piglet_old', 'brigand_cannon', 'skeleton_spear_old', 'virago_shroom', 'unclean_giant', 'collector_protect', 'shambler', 'swine_prince', 'pew_large', 'carrion_eater_big', 'cyst', 'cultist_shrouded', 'formless_ranged']


class Skin:
    vanilla_monster_names = {
        "pew_small",
        "swine_reaver",
        "brigand_sapper",
        "spider_webber",
        "swinetaur",
        "brigand_hunter",
        "templar_ranged_mb",
        "siren",
        "drowned_pirate",
        "fishman_shaman",
        "crow",
        "jellyfish",
        "ancestor_nebula",
        "fungal_bloat",
        "swine_piglet",
        "cultist_witch",
        "hag",
        "cauldron_full",
        "pew_medium",
        "snail_urchin",
        "spider_webber_old",
        "maggot",
        "skeleton_courtier",
        "shambler_tentacle",
        "ancestor_perfect",
        "ancestor_heart",
        "totem_guard",
        "cell_battle",
        "swine_drummer",
        "octotank",
        "ghoul",
        "errant_flesh_dog",
        "shuffler",
        "swine_skiver",
        "skeleton_common",
        "nest",
        "ectoplasm",
        "formless_weak",
        "fishman_crabby",
        "ancestor_pod",
        "collector_shaman",
        "spider_spitter",
        "formless_melee",
        "brigand_blood",
        "fungal_artillery",
        "cultist_orgiastic",
        "drowned_captain",
        "cell_white",
        "virago_hateful",
        "formless_melee_old",
        "ancestor_flawed",
        "brigand_fuseman",
        "drowned_anchor",
        "swine_prince_old",
        "ectoplasm_large",
        "crone",
        "swine_slasher",
        "brigand_barrel",
        "prophet",
        "cultist_harpy",
        "brigand_raider",
        "corpse_large",
        "templar_melee",
        "cultist_brawler",
        "brigand_cutthroat",
        "fishman_harpoon",
        "swine_wretch",
        "skeleton_defender",
        "skeleton_captain",
        "templar_melee_mb",
        "corpse",
        "spider_spitter_old",
        "ancestor_small",
        "templar_ranged",
        "carrion_eater",
        "cauldron_empty",
        "ancestor_big",
        "totem_attack",
        "drowned_anchored",
        "cultist_warlord",
        "errant_flesh_bat",
        "skeleton_militia",
        "brigand_fusilier",
        "formless_guard",
        "rabid_dog",
        "skeleton_militia_old",
        "skeleton_arbalist",
        "necromancer",
        "bloated_corpse",
        "skeleton_spear",
        "skeleton_bearer",
        "collector_battle",
        "madman",
        "gargoyle",
        "collector",
        "swine_piglet_old",
        "brigand_cannon",
        "skeleton_spear_old",
        "virago_shroom",
        "unclean_giant",
        "collector_protect",
        "shambler",
        "swine_prince",
        "pew_large",
        "carrion_eater_big",
        "cyst",
        "cultist_shrouded",
        "formless_ranged",
    }

    warrens_1_dir = find_warrens_1()

    @classmethod
    def load_installed_skins(cls) -> List["Skin"]:
        return [
            cls(f.parent, installed=True)
            for f in chain(
                (cls.warrens_1_dir / "monsters").rglob(".skin_identifier"),
                (cls.warrens_1_dir / "heroes").rglob(".skin_identifier"),
            )
        ]

    @classmethod
    def load_downloaded_skins(cls) -> Iterable["Skin"]:
        return [
            cls(p, installed=False)
            for p in AppName.DARKEST_DUNGEON.get_app_cache_dir().glob("*")
        ]

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

    def __init__(self, filename: Path, installed: bool = False):
        """
        :param filename: for downloaded skin, it's the zip file path. For installed skin, it's the folder with the monster/hero name
        """
        self.filename = filename
        self.installed = installed
        if not installed:
            self.skin_name = filename.stem
        else:
            self.skin_name = (filename / ".skin_identifier").read_text()

    def __str__(self):
        return self.skin_name

    def install(self):
        modfiles_txt = self.warrens_1_dir / "modfiles.txt"
        if modfiles_txt.exists():
            modfiles_txt.unlink()
        if self.installed:
            print("already installed")
        else:
            Archive(str(self.filename)).extractall(self.warrens_1_dir)

    def uninstall(self):
        modfiles_txt = self.warrens_1_dir / "modfiles.txt"
        if modfiles_txt.exists():
            modfiles_txt.unlink()
        if self.installed:
            rmtree(self.filename)
        else:
            print("Already uninstalled")

        # monster_dirs = [
        #     path
        #     for path in self.filename.rglob("*")
        #     if path.is_dir() and path.stem in self.vanilla_monster_names
        # ]

        # monster_name_to_num = Counter([monster.stem for monster in monster_dirs])
        # for monster_dir in monster_dirs:
        #     monster_name = monster_dir.stem
        #     if monster_name_to_num[monster_name] > 1:
        #         raise NotImplementedError
        #         # x = sg.popup_get_text("which?")
        #         # print(x)
        #     else:
        #         pass


class DarkestDungeonHandler(AppHandler):
    def show_download_progress(self, p: Popen):
        with self.status_reporter as r:
            i = 1
            while p.poll() is None:
                i += 0.5
                r.report_progress(1000 - 1000 / i)
                r.report_message(text=p.stdout.readline())
                self.find_app_widget("Downloaded Skins").update(
                    values=Skin.load_downloaded_skins()
                )
            r.report_progress(1000)
        self.find_app_widget("Download Skins").update(disabled=False)

    def update_installed_skins(self):
        self.find_app_widget("Installed Skins").update(Skin.load_installed_skins())

    def handle(self, app_event: str, values: Dict[str, str]):
        # print(event)
        if app_event == "Download Skins":
            p = Skin.download_skins()
            self.find_app_widget(app_event).update(disabled=True)
            Thread(target=self.show_download_progress, args=(p,)).start()
        elif app_event == "Install Skin":
            selected_skins = self.get_app_widget_value("Downloaded Skins", values)
            for skin in selected_skins:
                skin.install()

            self.update_installed_skins()

            # print("the player wants to install " + str(selected_skins[0]))
        elif app_event == "Uninstall Skin":
            selected_skins = self.get_app_widget_value("Installed Skins", values)
            for skin in selected_skins:
                skin.uninstall()

            self.update_installed_skins()


downloaded_col = [
    sg.Col,
    [
        [
            [[sg.Text, ["Downloaded Skins"], {"key": "Downloaded Skins Text"}]],
            [
                [
                    sg.Listbox,
                    {
                        "values": Skin.load_downloaded_skins(),
                        "size": (30, 6),
                        "key": "Downloaded Skins",
                    },
                ]
            ],
        ],
    ],
]

skin_control_col = [
    sg.Col,
    [[[[sg.Button, ["Install Skin"]]], [[sg.Button, ["Uninstall Skin"]]]],],
    {"element_justification": "center"},
]

installed_col = [
    sg.Col,
    [
        [
            [[sg.Text, ["Installed Skins"], {"key": "Installed Skin Text"}]],
            [
                [
                    sg.Listbox,
                    {
                        "values": Skin.load_installed_skins(),
                        "size": (30, 6),
                        "key": "Installed Skins",
                    },
                ]
            ],
        ],
    ],
]

# type aw (app widget) to have [sg., [], {}] ready

ui = [
    [[sg.Button, ["Download Skins"]]],
    [
        [
            sg.Frame,
            {
                "title": "",
                "layout": [[downloaded_col, skin_control_col, installed_col,]],
            },
        ],
    ],
]

if __name__ == "__main__":
    # Skin.download_skins()

    from tempfile import TemporaryDirectory

    # big = get_monster_folder_names()
    # print(big)

    # bb = (Skin.warrens_1_dir / "monsters").glob("*")
    # for x in bb:
    #     print(x.stem)

    Archive(
        "/home/matt/PycharmProjects/matt/matt/.darkest_dungeon/skeleton_militia.zip"
    ).extractall("/home/matt/.steam/steam/steamapps/workshop/content/262060/1885424457")

    # with TemporaryDirectory() as temp_dir:
    #     Archive(
    #         "/home/matt/PycharmProjects/matt/matt/.darkest_dungeon/skeleton_militia_pack.zip"
    #     ).extractall(temp_dir)
    #     for b in Path(temp_dir).rglob("*"):
    #         print(b)
