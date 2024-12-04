import os
from time import sleep
from typing import Any, NoReturn

from adbutils._device import AdbDevice

import adb_auto_player.logger as logging
from adb_auto_player.plugin import Plugin
from adb_auto_player.plugin_loader import get_plugins_dir


class Example(Plugin):
    def get_template_dir_path(self) -> str:
        return os.path.join(get_plugins_dir(), "<your_dir>", "templates")

    def get_menu_options(self) -> list[dict[str, Any]]:
        return [
            {
                "label": "Test",
                "action": self.test,
                "kwargs": {},
            },
        ]

    def test(self) -> None:
        logging.info("Test")
        return None


def execute(device: AdbDevice, config: dict[str, Any]) -> None | NoReturn:
    game = Example(device, config)

    game.check_requirements()

    sleep(1)

    game.run_cli_menu()

    return None
