import os.path
from abc import abstractmethod
from time import sleep
from typing import Any

from PIL import Image
from adbutils._device import AdbDevice

import adb_auto_player.adb as adb
import logging
import adb_auto_player.screen_utils as screen_utils
from adb_auto_player.exceptions import UnsupportedResolutionException, TimeoutException


class Plugin:
    def __init__(self, device: AdbDevice, config: dict[str, Any]) -> None:
        self.device = device
        self.config = config
        self.store: dict[str, Any] = {}

    @abstractmethod
    def get_template_dir_path(self) -> str:
        return ""

    @abstractmethod
    def get_config_choices(self) -> dict[str, Any]:
        return {}

    @abstractmethod
    def get_menu_options(self) -> list[dict[str, Any]]:
        return []

    def check_requirements(self) -> None:
        """
        :raises UnsupportedResolutionException:
        """
        resolution = adb.get_screen_resolution(self.device)
        supported_resolution = self.config.get("plugin", {}).get(
            "supported_resolution", "1080x1920"
        )
        if resolution != supported_resolution:
            raise UnsupportedResolutionException(
                f"This plugin only supports {supported_resolution}"
            )
        return None

    def find_first_template_center(
        self,
        template: str,
        grayscale: bool = False,
        base_image: Image.Image | None = None,
    ) -> tuple[int, int] | None:
        template_path = os.path.join(
            self.get_template_dir_path(),
            template,
        )

        return screen_utils.find_center(
            self.device, template_path, grayscale=grayscale, base_image=base_image
        )

    def find_all_template_centers(
        self, template: str, grayscale: bool = False
    ) -> list[tuple[int, int]] | None:
        template_path = os.path.join(
            self.get_template_dir_path(),
            template,
        )

        return screen_utils.find_all_centers(
            self.device,
            template_path,
            grayscale=grayscale,
        )

    def wait_for_template(
        self,
        template: str,
        grayscale: bool = False,
        delay: int = 1,
        timeout: int = 30,
        timeout_message: str | None = None,
    ) -> tuple[int, int]:
        """
        :raises TimeoutException:
        """
        elapsed_time = 0
        while True:
            result = self.find_first_template_center(
                template,
                grayscale=grayscale,
            )
            if result is not None:
                logging.debug(f"{template} found")
                return result

            sleep(delay)
            elapsed_time += delay
            if elapsed_time >= timeout:
                if timeout_message:
                    raise TimeoutException(f"{timeout_message}")
                else:
                    raise TimeoutException(
                        f"Could not find Template: '{template}' after {timeout} seconds"
                    )

    def wait_until_template_disappears(
        self, template: str, delay: int = 1, timeout: int = 30
    ) -> None:
        """
        :raises TimeoutException:
        """
        elapsed_time = 0
        while True:
            if self.find_first_template_center(template) is None:
                logging.debug(f"{template} no longer visible")
                return None

            sleep(delay)
            elapsed_time += delay
            if elapsed_time >= timeout:
                raise TimeoutException(
                    f"Template: {template} is still visible after {timeout} seconds"
                )

    def wait_for_any_template(
        self, templates: list[str], delay: int = 3, timeout: int = 30
    ) -> tuple[str, int, int]:
        """
        :raises TimeoutException:
        """
        elapsed_time = 0
        while True:
            result = self.find_any_template_center(templates)

            if result is not None:
                return result

            sleep(delay)
            elapsed_time += delay
            if elapsed_time >= timeout:
                raise TimeoutException(
                    f"None of the templates {templates}"
                    f" were found after {timeout} seconds"
                )

    def find_any_template_center(
        self,
        templates: list[str],
        grayscale: bool = False,
    ) -> tuple[str, int, int] | None:
        base_image = screen_utils.get_screenshot(self.device)
        for template in templates:
            result = self.find_first_template_center(
                template,
                grayscale=grayscale,
                base_image=base_image,
            )
            if result is not None:
                x, y = result
                return template, x, y
        return None

    def press_back_button(self) -> None:
        self.device.keyevent(4)
