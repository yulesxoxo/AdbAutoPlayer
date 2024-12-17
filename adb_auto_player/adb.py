from typing import Any

from adbutils import AdbClient, AdbDeviceInfo
from adbutils._device import AdbDevice

import logging
from adb_auto_player.exceptions import AdbException


def get_device(main_config: dict[str, Any]) -> AdbDevice:
    """
    :raises AdbException: Device not found
    """
    device_id = main_config.get("device", {}).get("id", "127.0.0.1:5555")
    adb_config = main_config.get("adb", {})
    client = AdbClient(
        host=adb_config.get("host", "127.0.0.1"),
        port=adb_config.get("port", 5037),
    )
    devices = client.list()
    if len(devices) == 0:
        logging.warning("No devices found")
    else:
        devices_str = "Devices:"
        for device_info in devices:
            devices_str += f"\n{device_info.serial}"
        logging.info(devices_str)

    device = client.device(f"{device_id}")

    if device is None:
        raise AdbException(f"{device_id} not found")

    device.get_state()
    logging.info(f"Successfully connected to device {device_id}")
    return device


def get_devices(main_config: dict[str, Any]) -> list[AdbDeviceInfo]:
    adb_config = main_config.get("adb", {})
    client = AdbClient(
        host=adb_config.get("host", "127.0.0.1"),
        port=adb_config.get("port", 5037),
    )
    return client.list()


def get_currently_running_app(device: AdbDevice) -> str:
    """
    :raises AdbException: Unable to determine currently running app
    """
    app = str(
        device.shell(
            "dumpsys activity activities | grep mResumedActivity | "
            'cut -d "{" -f2 | cut -d \' \' -f3 | cut -d "/" -f1'
        )
    ).strip()
    # Not sure why this happens
    # encountered when running on Apple M1 Max using MuMu Player
    if not app:
        app = str(
            device.shell(
                "dumpsys activity activities | grep ResumedActivity | "
                'cut -d "{" -f2 | cut -d \' \' -f3 | cut -d "/" -f1'
            )
        ).strip()
        if "\n" in app:
            app = app.split("\n")[0]
    if app:
        logging.debug(f"Currently running app: {app}")
        return str(app)
    raise AdbException("Unable to determine the currently running app")


def get_screen_resolution(device: AdbDevice) -> str:
    """
    :raises AdbException: Unable to determine screen resolution
    """
    result = str(device.shell("wm size"))
    if result:
        resolution_str = result.split("Physical size: ")[-1].strip()
        logging.debug(f"Device screen resolution: {resolution_str}")
        return str(resolution_str)
    logging.debug(result)
    raise AdbException("Unable to determine screen resolution")
