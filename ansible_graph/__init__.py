"""
Setup the environment by parsing the command line options and staring
a ruruki http server.
"""
import argparse
import logging
from ansible.inventory import Inventory
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook import Playbook
from ruruki_eye.server import run
from ansible_graph.scrape import GRAPH
from ansible_graph.scrape import scrape_inventroy, scrape_playbook
import os


__all__ = ["create_playbook", "create_inventory", "parse_arguments"]


LOADER = DataLoader()
VARIABLE_MANAGER = VariableManager()


def setup_loader(path):
    """
    Setup the ansible loader with the base dir path.

    :param path: Ansible base directory path.
    :type path: :class:`str`
    """
    logging.info("Updated ansible loader basedir to %r", path)
    LOADER.set_basedir(path)


def create_inventory(inventory_path):
    """
    Load the given inventory and return the ansible inventory.

    :param inventory_path: Path to the inventory file.
    :type inventory_path: :class:`str`
    :returns: The loaded ansible inventory.
    :rtype: :class:`ansible.inventory.Inventory`
    """
    try:
        inventory = Inventory(
            loader=LOADER,
            variable_manager=VARIABLE_MANAGER,
            host_list=inventory_path,
        )

        scrape_inventroy(inventory)
        return inventory
    except Exception as error:  # pylint: disable=broad-except
        logging.exception(
            "Unexpected error scrapping inventory %r: %r",
            inventory_path, error
        )

        raise argparse.ArgumentTypeError(error)


def create_playbook(playbook_path):
    """
    Load the given playbook and return the ansible playbook.

    :param playbook_path: Path to the playbook file.
    :type playbook_path: :class:`str`
    :returns: The loaded ansible playbook.
    :rtype: :class:`ansible.playbook.Playbook`
    """
    try:
        playbook = Playbook.load(
            playbook_path,
            loader=LOADER,
            variable_manager=VARIABLE_MANAGER,
        )

        scrape_playbook(playbook)
        return playbook
    except Exception as error:  # pylint: disable=broad-except
        logging.exception(
            "Unexpected error scrapping playbook %r: %r",
            playbook_path, error
        )

        raise argparse.ArgumentTypeError(error)


def parse_arguments():
    """
    Parse the command line arguments.

    :returns: All the command line arguments.
    :rtype: :class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="Ansible inventory grapher."
    )

    parser.add_argument(
        "-b",
        "--base-dir",
        default=os.getcwd(),
        type=setup_loader,
        help="Ansible base directory path (default: %(default)s)",
    )

    parser.add_argument(
        "--runserver",
        action="store_true",
        help="Start a ruruki http server.",
    )

    parser.add_argument(
        "--address",
        default="0.0.0.0",
        help="Address to start the web server on. (default: %(default)s)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help=(
            "Port number that the web server will accept connections on. "
            "(default: %(default)d)"
        ),
    )

    parser.add_argument(
        "-i",
        "--inventories",
        nargs="*",
        type=create_inventory,
        required=False,
        help=(
            "One of more inventories to load and scrape."
        ),
    )

    parser.add_argument(
        "-p",
        "--playbooks",
        nargs="*",
        type=create_playbook,
        required=False,
        help=(
            "One of more playbooks to load and scrape."
        ),
    )

    return parser.parse_args()


def main():
    """
    Entry point.
    """
    logging.basicConfig(level=logging.INFO)
    namespace = parse_arguments()

    if namespace.runserver is True:
        run(namespace.address, namespace.port, False, GRAPH)
