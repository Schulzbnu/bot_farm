from navigation.waypoints import load_waypoints


def test_load_waypoints(tmp_path):
    p = tmp_path / "waypoints.json"
    p.write_text(
        '{"waypoints":[{"id":"a","x":10,"y":20},{"id":"b","x":15,"y":25,"action":"use-rope"}]}'
    )

    waypoints = load_waypoints(str(p))

    assert len(waypoints) == 2
    assert waypoints[0].id == "a"
    assert waypoints[1].action == "use-rope"
