from abc import ABC, abstractmethod
from typing import List, Dict
import re
import PySimpleGUI as sg


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
                        # then thing is pre layout
                        self.attach_app_prefix_and_initiate(thing)
                # print(pre_cell)
                # for b in pre_cell:
                #     print(b)
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
                    if len(args) > 0 and isinstance(args[0], str):
                        kwargs["key"] = "%s: " % self.app_name + args[0]

                pre_row[j] = constructor(*args, **kwargs)

        layout = pre_layout
        return layout

    def find_app_widget(self, app_widget_name: str):
        return self.window.FindElement("%s: " % self.app_name + app_widget_name)


class StatusReporter:
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")

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
        self._text_widget.update(self.ansi_escape.sub("", text))

    def report_progress(self, number: float):
        """

        :param number: between 0 and 1000
        :return:
        """
        self._progress_bar_widget.update_bar(int(number))

    # def show_popup(self, message):
    #     # sg.popup(message)
    #     self._message_queue.put(message)


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

    def get_app_widget_value(self, app_widget_key: str, values: dict):
        return values[self.app_name + ": " + app_widget_key]


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
