import argparse
import json
import sys
import threading
import time
from abc import ABC, abstractmethod
from itertools import chain
from queue import Queue, Empty
from subprocess import Popen
from threading import Thread

from pyautogui import prompt
from gooey import Gooey, GooeyParser
from typing import List, Dict, Callable, Any
from matt import AppID, darkest_dungeon
import PySimpleGUI as sg

from matt.darkest_dungeon import Skin


class StatusReporter:
    def __init__(self):
        self._progress_bar_widget = sg.ProgressBar(1000, orientation="h", size=(20, 20))
        self._text_widget = sg.Text("", size=(30, 1))
        self.frame = sg.Frame("", [[self._progress_bar_widget, self._text_widget]])
        # self._message_queue = Queue()
        # self._write_lock = threading.Lock()

    # def get_message(self):
    #     try:
    #         return self._message_queue.get_nowait()
    #     except Empty:
    #         return None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._progress_bar_widget.update_bar(0)
        self._text_widget.update("")

    def report_message(self, text: str):
        self._text_widget.update(text)

    def report_progress(self, number: float):
        """
        
        :param number: between 0 and 1000
        :return:
        """
        self._progress_bar_widget.update_bar(int(number))

    # def show_popup(self, message):
    #     # sg.popup(message)
    #     self._message_queue.put(message)


class AppLayout:
    def __init__(self, app_name: str, pre_layout: List[list], window: sg.Window = None):
        """

        :param app_name: beautiful display name
        :param pre_layout:
        """
        self.app_name = app_name
        self.window = window
        self.layout = self.attach_app_prefix_and_initiate(pre_layout)

    def attach_app_prefix_and_initiate(self, pre_layout):
        """
        do attach_app_prefix_and_initiate from bottom, in place

        :param pre_layout:
        :return:
        """

        for i, pre_row in enumerate(pre_layout):

            for j, pre_cell in enumerate(pre_row):

                # detect embedded pre_layouts
                all_args = []
                for x in pre_cell:
                    if isinstance(x, list):
                        all_args.extend(x)
                    elif isinstance(x, dict):
                        all_args.extend(x.values())

                for thing in all_args:
                    if (
                        isinstance(thing, list)
                        and len(thing) > 0
                        and isinstance(thing[0], list)
                        and len(thing[0]) > 0
                        and isinstance(thing[0][0], list)
                        and len(thing[0][0]) > 0
                        and issubclass(thing[0][0][0], sg.Element)
                    ):
                        self.attach_app_prefix_and_initiate(thing)
                # print(pre_cell)
                for b in pre_cell:
                    print(b)
                constructor, *stuff = pre_cell
                args = []
                kwargs = {}
                for stonf in stuff:
                    if isinstance(stonf, list):
                        args = stonf
                    elif isinstance(stonf, dict):
                        kwargs = stonf
                    else:
                        raise ValueError

                if "key" in kwargs:
                    kwargs["key"] = "%s: " % self.app_name + kwargs["key"]
                else:
                    if len(args) > 0:
                        kwargs["key"] = "%s: " % self.app_name + args[0]

                pre_row[j] = constructor(*args, **kwargs)

        layout = pre_layout

        return layout

    def find_app_widget(self, app_widget_name: str):
        return self.window.FindElement("%s: " % self.app_name + app_widget_name)


class AppHandler(ABC):
    def __init__(
        self,
        app_name: str,
        status_reporter: StatusReporter,
        app_layout: AppLayout = None,
    ):
        self.app_layout = app_layout
        self.app_name = app_name
        self.status_reporter = status_reporter

    @abstractmethod
    def handle(self, event: str, values: Dict[str, str]):
        ...

    def find_app_widget(self, key: str):
        return self.app_layout.find_app_widget(key)


class App:
    def __init__(
        self, app_name: str, app_layout: AppLayout, handler: AppHandler,
    ):
        """

        :param app_name: beautiful display name
        :param layout:
        """
        self.app_name = app_name
        self.app_layout = app_layout
        self.handler = handler


class DarkestDungeonHandler(AppHandler):
    def show_download_progress(self, p: Popen):
        with self.status_reporter as r:
            i = 1
            while p.poll() is None:
                i += 0.5
                r.report_progress(1000 - 1000 / i)
                r.report_message(text=p.stdout.readline())
                self.find_app_widget("Downloaded Skins").update(
                    values=[
                        p.stem for p in darkest_dungeon.Skin.load_downloaded_skins()
                    ]
                )
            r.report_progress(1000)
        self.find_app_widget("Download Skins").update(disabled=False)

    def handle(self, app_event: str, values: Dict[str, str]):
        # print(event)
        if app_event == "Download Skins":
            p = darkest_dungeon.Skin.download_skins()
            self.find_app_widget(app_event).update(disabled=True)
            Thread(target=self.show_download_progress, args=(p,)).start()


def cmd_entry(argv=sys.argv):
    app_data = {
        AppID.DARKEST_DUNGEON: [
            [
                # type aw to have [sg., [], {}] ready
                [[sg.Button, ["Download Skins"]]],
                [
                    [
                        sg.Frame,
                        {
                            "title": "",
                            "layout": [
                                [[sg.Text, ["Hello"]], [sg.Text, ["Hi"]],],
                                [
                                    [
                                        sg.Listbox,
                                        {
                                            "values": [
                                                p.stem
                                                for p in darkest_dungeon.Skin.load_downloaded_skins()
                                            ],
                                            "size": (30, 6),
                                            "key": "Downloaded Skins",
                                        },
                                    ],
                                    [
                                        sg.Listbox,
                                        {"values": [1, 2, 3], "size": (30, 6)},
                                    ],
                                ],
                            ],
                        },
                    ],
                ],
            ],
            DarkestDungeonHandler,
        ],
    }

    status_reporter = StatusReporter()

    app_name_to_app: Dict[str, App] = {
        app_id.display_name(): App(
            app_id.display_name(),
            AppLayout(app_id.display_name(), app_layout),
            handler_constructor(app_id.display_name(), status_reporter),
        )
        for app_id, (app_layout, handler_constructor) in app_data.items()
    }

    sg.theme("DarkAmber")  # Add a touch of color
    # All the stuff inside your window.
    search_input = sg.InputText(key="-Uh-")

    tab_group_layout = [
        [
            sg.Tab(app_name, app.app_layout.layout, font="Courier 15")
            for app_name, app in app_name_to_app.items()
        ]
    ]

    tab_group = sg.TabGroup(tab_group_layout, enable_events=True, key="-TABGROUP-")

    layout = [
        [sg.Text("Some text on Row 1")],
        [sg.Text("Enter something on Row 2"), search_input],
        [sg.Button("Ok"), sg.Button("Cancel")],
        [tab_group],
        [status_reporter.frame],
    ]

    # Create the Window
    window = sg.Window("Window Title", layout, finalize=True)

    for app in app_name_to_app.values():
        app.app_layout.window = window
        app.handler.app_layout = app.app_layout

    window.bind("<Control_L><f>", "SEARCH")
    window["-Uh-"].bind("<Button-2>", "+LEFT CLICK+")

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        event: str

        # events outside apps first
        if event in (None, "Cancel"):  # if user closes window or clicks cancel
            break
        elif event == "SEARCH":
            search_input.set_focus()
        # app events
        elif event.partition(": ")[0] in app_name_to_app.keys():
            app_name, _, app_event = event.partition(": ")
            app = app_name_to_app.get(app_name)
            app.handler.handle(app_event, values)

    window.close()


if __name__ == "__main__":
    cmd_entry()
