import argparse
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
import logging
from ruruki.graphs import Graph
from ruruki_eye.server import run
import sys


GRAPH = Graph()
LOADER = DataLoader()
VARIABLE_MANAGER = VariableManager()


GRAPH.add_vertex_constraint("HOST", "name")
GRAPH.add_vertex_constraint("GROUP", "name")
GRAPH.add_vertex_constraint("VAR", "name")


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


def _link_node_to_groups(node, groups, edge_label="HAS-GROUP"):
    """
    Create group node for all the groups provided and link the
    node to the group node.

    :param node: Node that is using the group.
    :type node: :class:`ruruki.interfaces.IVertex`
    :param groups: Iterable of groups that you are creating,
        inspecting and linking to the node.
    :type groups: :class:`ansible.inventroy.group.Group`
    :param edge_label: Edge label to use.
    :type edge_label: :class:`str`
    """
    for group in groups:
        group_node = GRAPH.get_or_create_vertex(
            "GROUP",
            name=group.get_name(),
            priority=group.priority,
            **group.get_vars()
        )
        GRAPH.get_or_create_edge(node, edge_label, group_node)

        # create links between the parent and child groups
        _link_node_to_groups(group_node, group.child_groups, "HAS-CHILD-GROUP")


def scrape_hosts(hosts):
    """
    Scrape interesting information about all the hosts.

    :param hosts: Iterable of host to scrape.
    :type hosts: Iterable of :class:`ansible.inventory.host.Host`
    """
    for host in hosts:
        # get the host vars but remove the group_names becaus that is
        # done at a later stage with _link_node_to_groups.
        vars = host.get_vars()
        del vars["group_names"]
        node = GRAPH.get_or_create_vertex(
            "HOST",
            name=host.get_name(),
            **vars
        )

        _link_node_to_groups(node, host.get_groups())
        print host.get_group_vars()


def scrape(inventory):
    """
    Scrape the inventories and build a graph.

    :param inventory: Inventories that you are scrapping.
    :type inventory: :class:`ansible.inventory.Inventory`
    """
    scrape_hosts(inventory.get_hosts())


def run():
    """
    Entry point.
    """
    logging.basicConfig(level=logging.INFO)
    namespace = parse_arguments()

    if namespace.runserver is True:
        run(namespace.address, namespace.port, False, GRAPH)


if __name__ == "__main__":
    run()
