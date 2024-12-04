import os
from time import sleep
from typing import Any, NoReturn

from adbutils._device import AdbDevice

import adb_auto_player.logger as logging
from adb_auto_player.plugin import Plugin
from adb_auto_player.plugin_loader import get_plugins_dir


class GOGOMuffin(Plugin):
    def get_template_dir_path(self) -> str:
        return os.path.join(get_plugins_dir(), "GOGOMuffin", "templates")

    def get_menu_options(self) -> list[dict[str, Any]]:
        return [
            {
                "label": "Auto Progress",
                "action": self.auto_progress,
                "kwargs": {},
            },
        ]

    def auto_progress(self) -> NoReturn:
        logging.info("Starting Auto Progress")
        while True:
            template, x, y = self.wait_for_any_template(
                [
                    "next_stage.png",
                    "enter_new_stage.png",
                    "new_stage.png",
                    "boss.png",
                    "waiting.png",
                    "challenging.png",
                    "percent.png",
                ],
                delay=1,
            )
            match template:
                case "next_stage.png":
                    logging.info("Moving to new stage")
                    self.device.click(x, y)
                case "enter_new_stage.png" | "new_stage.png":
                    logging.info("Moving to new stage")
                    self.device.click(1000, 1200)
                case "boss.png":
                    logging.info("Starting boss battle")
                    self.device.click(1000, 1200)
                case "waiting.png", "challenging.png", "percent.png":
                    pass
            sleep(3)


def execute(device: AdbDevice, config: dict[str, Any]) -> NoReturn:
    logging.critical_and_exit("WIP")
