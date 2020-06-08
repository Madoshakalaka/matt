import sys

from typing import Dict
from matt import AppName, darkest_dungeon
import PySimpleGUI as sg

from matt.app_components import AppLayout, App, StatusReporter
import importlib


def cmd_entry(argv=sys.argv):
    app_data = {}
    for ai in AppName:
        name_space = importlib.import_module("matt." + ai.camel_snake())
        app_data[ai] = [name_space.ui, getattr(name_space, ai.handler_class_name())]

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
        [sg.Text("Search"), search_input],
        [tab_group],
        [status_reporter.frame],
    ]

    # Create the Window
    window = sg.Window("Anaertailin Skin Manager", layout, finalize=True)

    for app in app_name_to_app.values():
        app.app_layout.window = window
        app.handler.app_layout = app.app_layout

    window.bind("<Control_L><f>", "SEARCH")
    # window["-Uh-"].bind("<Button-2>", "+LEFT CLICK+")

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
        print(values)
    window.close()


if __name__ == "__main__":
    cmd_entry()
