import hashlib
import importlib.util
import json
import os
import sys
import tomllib
import toml
import types
from typing import Any, cast

import logging

PLUGIN_LIST_FILE = "plugin_list.json"
PLUGIN_CONFIG_FILE = "config.toml"
MAIN_CONFIG_FILE = "main_config.toml"


def get_plugins_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "plugins")
    return "plugins"


def get_plugin_list_file_location() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return "."


def get_main_config() -> dict[str, Any]:
    if getattr(sys, "frozen", False):
        config_file = os.path.join(os.path.dirname(sys.executable), MAIN_CONFIG_FILE)
    else:
        config_file = os.path.join(MAIN_CONFIG_FILE)
    with open(config_file, "rb") as f:
        return tomllib.load(f)


def scan_plugins() -> list[dict[str, Any]]:
    plugins = []

    for plugin_dir_name in os.listdir(get_plugins_dir()):
        config = load_config(plugin_dir_name)

        if config:
            plugin_config = config.get("plugin", {})
            packages = plugin_config.get("packages")
            name = plugin_config.get("name")
            plugin = {
                "packages": packages,
                "name": name,
                "dir": plugin_dir_name,
            }
            plugins.append(plugin)

    return plugins


def generate_plugin_list_hash() -> str:
    hash_md5 = hashlib.md5()

    plugins_dir = get_plugins_dir()

    for plugin_name in os.listdir(plugins_dir):
        plugin_dir = os.path.join(plugins_dir, plugin_name)
        config_file = os.path.join(plugin_dir, PLUGIN_CONFIG_FILE)

        if os.path.isdir(plugin_dir) and os.path.isfile(config_file):
            hash_md5.update(plugin_name.encode("utf-8"))
            hash_md5.update(str(os.path.getmtime(config_file)).encode("utf-8"))

    return hash_md5.hexdigest()


def load_plugin_configs() -> list[dict[str, Any]]:
    if os.path.exists(PLUGIN_LIST_FILE):
        with open(PLUGIN_LIST_FILE, "r") as f:
            cached_plugins = json.load(f)

        if cached_plugins.get("hash") == generate_plugin_list_hash():
            return cast(list[dict[str, Any]], cached_plugins["plugins"])

    plugins = scan_plugins()
    create_plugin_list_file(plugins)

    return plugins


def create_plugin_list_file(plugins: list[dict[str, Any]]) -> None:
    plugin_data = {"hash": generate_plugin_list_hash(), "plugins": plugins}

    with open(get_plugin_list_file_location() + "/" + PLUGIN_LIST_FILE, "w") as f:
        json.dump(plugin_data, f, indent=4)


def load_config(plugin_dir: str) -> dict[str, Any] | None:
    config_file = os.path.join(get_plugins_dir(), plugin_dir, PLUGIN_CONFIG_FILE)
    if not os.path.exists(config_file):
        return None
    with open(config_file, "rb") as f:
        return tomllib.load(f)


def save_config_for_plugin(config: dict[str, Any], plugin_dir: str) -> None:
    config_file = os.path.join(get_plugins_dir(), plugin_dir, PLUGIN_CONFIG_FILE)
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, "w") as f:
        toml.dump(config, f)


def load_plugin_module(plugin_name: str) -> types.ModuleType:
    """
    :raises ValueError: When module spec could not be loaded
    """
    plugin_main_path = os.path.join(get_plugins_dir(), plugin_name, "run.py")
    logging.debug(f"Loading plugin module: {plugin_main_path}")

    spec = importlib.util.spec_from_file_location(plugin_name, plugin_main_path)
    if spec is None:
        raise ValueError("Failed to load module spec")

    module = importlib.util.module_from_spec(spec)

    sys.modules[plugin_name] = module

    loader = spec.loader
    if loader is None:
        raise ValueError("Failed to load spec loader")

    loader.exec_module(module)

    return module


def get_plugin_for_app(
    plugins: list[dict[str, Any]], app: str
) -> dict[str, Any] | None:
    for plugin in plugins:
        if app in plugin.get("packages", {}):
            return plugin
    return None
