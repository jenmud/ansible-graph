"""
Scrape an ansable inventory and build a dependency graph.
"""
from ruruki.graphs import Graph

__all__ = ["GRAPH", "scrape_inventroy", "scrape_hosts", "scrape_playbook"]

GRAPH = Graph()
GRAPH.add_vertex_constraint("HOST", "name")
GRAPH.add_vertex_constraint("GROUP", "name")
GRAPH.add_vertex_constraint("PLAY", "name")
GRAPH.add_vertex_constraint("TASK", "name")


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
        if group.get_name() == "all":
            continue

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


def scrape_inventroy(inventory):
    """
    Scrape the inventory and build a graph.

    :param inventory: Inventory that you are scrapping.
    :type inventory: :class:`ansible.inventory.Inventory`
    """
    scrape_hosts(inventory.get_hosts())


def scrape_tasks(tasks):
    """
    Scrape interesting information about all the tasks.

    :param hosts: Iterable of tasks to scrape.
    :type hosts: Iterable of :class:`ansible.play.task.Task`
    """
    for task in tasks:
        for task in task:
            variables = task.get_vars()

            node = GRAPH.get_or_create_vertex(
                "TASK",
                name=task.get_name(),
                **variables
            )
            yield node
            #_link_node_to_groups(node, host.get_groups())


def scrape_playbook(playbook):
    """
    Scrape the playbook and build a graph.

    :param inventory: Playbook that you are scrapping.
    :type inventory: :class:`ansible.playbook.Playbook`
    """
    for play in playbook.get_plays():
        variables = play.get_vars()
        node = GRAPH.get_or_create_vertex(
            "PLAY",
            name=play.get_name(),
            **variables
        )

        for task in scrape_tasks(play.get_tasks()):
            GRAPH.get_or_create_edge(node, "HAS-TASK", task)
