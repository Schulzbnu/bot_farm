from bot.navigation.pathfinding import generateFloorWalkpoints


def test_generate_floor_walkpoints_encontra_caminho() -> None:
    current = (100, 100, 7)
    goal = (103, 100, 7)
    blocked = [(101, 100, 7)]

    path = generateFloorWalkpoints(current, goal, blocked, radius=5)

    assert path
    assert path[-1] == goal
    assert (101, 100, 7) not in path


def test_generate_floor_walkpoints_floor_diferente() -> None:
    current = (100, 100, 7)
    goal = (100, 100, 6)

    try:
        generateFloorWalkpoints(current, goal, [])
    except ValueError as exc:
        assert "Mudança de floor" in str(exc)
    else:
        raise AssertionError("Era esperado ValueError para floor diferente")
