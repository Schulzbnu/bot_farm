from navigation.path_executor import PathExecutor
from navigation.waypoints import Waypoint


def test_direction_to_waypoint():
    exec_ = PathExecutor([Waypoint(id="1", x=100, y=100)], tolerance=3)

    direction = exec_.direction_to_waypoint(x=80, y=120)

    assert direction.horizontal == "right"
    assert direction.vertical == "up"


def test_advance_if_reached():
    exec_ = PathExecutor([Waypoint(id="1", x=100, y=100), Waypoint(id="2", x=200, y=200)], tolerance=5)

    advanced = exec_.advance_if_reached(103, 98)

    assert advanced is True
    assert exec_.current_waypoint.id == "2"
