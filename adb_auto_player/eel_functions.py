import inspect
import logging
import multiprocessing.queues
import sys
from logging.handlers import QueueHandler
from multiprocessing import Process
from typing import Any, NoReturn

import eel
from adbutils._device import AdbDevice

import adb_auto_player.adb as adb
import adb_auto_player.plugin_loader as plugin_loader
from adb_auto_player import logging_setup
from adb_auto_player.exceptions import AdbException
from adb_auto_player.plugin import Plugin

main_config = plugin_loader.get_main_config()
plugins = plugin_loader.load_plugin_configs()
global_device: AdbDevice | None = None
global_plugin: dict[str, Any] | None = None
menu_options: list[dict[str, Any]] | None = None
action_process: Process | None = None


def init() -> None:
    """This is only so functions here can be exposed."""
    return None


def get_device() -> AdbDevice | None:
    global global_device
    if global_device is None:
        try:
            global_device = adb.get_device(main_config)
        except Exception as e:
            logging.error(f"{e}")
            return None
    return global_device


def get_plugin() -> dict[str, Any] | None:
    global global_plugin, menu_options

    device = get_device()
    if device is None:
        return None

    try:
        app = adb.get_currently_running_app(device)
    except AdbException:
        return None
    if global_plugin is not None:
        if app not in global_plugin.get("packages", {}):
            global_plugin = None
            menu_options = None

    if global_plugin is None:
        if app is None:
            return None
        global_plugin = plugin_loader.get_plugin_for_app(
            plugins,
            app,
        )
    return global_plugin


def get_game_object() -> Plugin | None:
    device = get_device()
    if device is None:
        return None
    plugin = get_plugin()
    if plugin is None:
        return None
    try:
        module = plugin_loader.load_plugin_module(str(plugin.get("dir")))
    except Exception as e:
        logging.error(f"{e}")
    classes = [cls for name, cls in inspect.getmembers(module, inspect.isclass)]
    game = None
    for cls in classes:
        if issubclass(cls, Plugin) and cls is not Plugin:
            config = plugin_loader.load_config(str(plugin.get("dir")))
            if config is not None:
                game = cls(device, config)

    if game is not None:
        try:
            game.check_requirements()
            return game
        except Exception as e:
            logging.error(f"{e}")
    return None


@eel.expose
def get_running_supported_game() -> str | None:
    plugin = get_plugin()
    if plugin is None:
        return None
    return plugin.get("name")


@eel.expose
def get_editable_config() -> dict[str, Any] | None:
    game = get_game_object()
    if game is None:
        return None
    return {"config": game.config, "choices": game.get_config_choices()}


@eel.expose
def save_config(new_config: dict[str, Any]) -> None:
    global global_plugin
    plugin = global_plugin
    if plugin is None:
        logging.error("Error saving config keep the game running when changing config.")
        return None
    if str(plugin.get("name")) != str(new_config.get("plugin", {}).get("name")):
        logging.error("Error saving config keep the game running when changing config.")
        return None
    plugin_loader.save_config_for_plugin(new_config, str(plugin.get("dir")))
    logging.info("Config saved.")
    global_plugin = get_plugin()
    return None


@eel.expose
def get_menu() -> list[str] | None:
    global menu_options
    game = get_game_object()
    if game is None:
        return None
    menu_options = game.get_menu_options()
    return [option.get("label", "") for option in menu_options]


@eel.expose
def execute(i: int) -> None:
    global action_process
    if global_plugin is None or menu_options is None:
        logging.warning("No plugin loaded")
        return None

    if i < 0 or i >= len(menu_options):
        logging.warning("Invalid Menu Item")
        return None

    option = menu_options[i]
    action = option.get("action")
    kwargs = option.get("kwargs")

    if callable(action) and isinstance(kwargs, dict):
        action_process = Process(
            target=run_action_in_process,
            args=(
                action.__name__,
                kwargs,
                logging_setup.get_log_queue(),
                logging.getLogger().getEffectiveLevel(),
            ),
        )
        action_process.daemon = True
        action_process.start()
    else:
        logging.warning("Something went wrong executing the task")
    return None


def run_action_in_process(
    action: str,
    kwargs: dict[str, Any],
    log_queue: multiprocessing.Queue,  # type: ignore
    log_level: int,
) -> None:
    try:
        child_logger = logging.getLogger()
        child_logger.addHandler(QueueHandler(log_queue))
        child_logger.setLevel(log_level)
        game = get_game_object()
        if hasattr(game, action):
            action_func = getattr(game, action)
            if callable(action_func):
                action_func(**kwargs)
    except Exception as e:
        logging.error(f"{e}")


@eel.expose
def action_is_running() -> bool:
    global action_process
    if action_process is None:
        return False
    return action_process.is_alive()


@eel.expose
def stop_action() -> None:
    global action_process
    if action_process is not None and action_process.is_alive():
        logging.warning("Stopping")
        action_process.terminate()
    return None


@eel.expose
def shutdown() -> NoReturn:
    sys.exit(0)


@eel.expose
def reload_config() -> None:
    global main_config, global_device
    main_config = plugin_loader.get_main_config()
    global_device = None
