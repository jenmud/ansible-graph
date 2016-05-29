"""
Scrape an ansable inventory and build a dependency graph.
"""
from ruruki.graphs import Graph

__all__ = ["GRAPH", "scrape", "scrape_hosts"]

GRAPH = Graph()
GRAPH.add_vertex_constraint("HOST", "name")
GRAPH.add_vertex_constraint("GROUP", "name")


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
        variables = host.get_vars()
        del variables["group_names"]

        node = GRAPH.get_or_create_vertex(
            "HOST",
            name=host.get_name(),
            **variables
        )

        _link_node_to_groups(node, host.get_groups())


def scrape(inventory):
    """
    Scrape the inventories and build a graph.

    :param inventory: Inventories that you are scrapping.
    :type inventory: :class:`ansible.inventory.Inventory`
    """
    scrape_hosts(inventory.get_hosts())
