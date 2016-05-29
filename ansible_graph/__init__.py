import argparse
from ansible_graph.scrape import scrape
from ansible_graph.scrape import GRAPH
from ansible.parsing.dataloader import DataLoader
from ansible.inventory import Inventory
from ansible.vars import VariableManager
import logging
from ruruki_eye.server import run


__all__ = ["GRAPH", "scrape", "scrape_hosts"]

LOADER = DataLoader()
VARIABLE_MANAGER = VariableManager()


def create_inventory(inventory_path):
    """
    Load the given inventory and return the ansible inventory.

    :param inventory_path: Path to the inventory file.
    :type inventory_path: :class:`str`
    :returns: The loaded ansible inventory.
    :rtype: :class:`ansible.inventory.Inventory`
    """
    inventory = Inventory(
        loader=LOADER,
        variable_manager=VARIABLE_MANAGER,
        host_list=inventory_path,
    )

    try:
        scrape(inventory)
    except Exception as error:
        logging.exception(
            "Unexpected error scrapping inventroy {}: {}".format(
                inventory_path, error
            )
        )

    return inventory


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
        required=True,
        help=(
            "One of more inventories to load and scrape."
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
