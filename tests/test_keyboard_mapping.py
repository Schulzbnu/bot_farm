from input.keyboard_controller import KeyMapping, KeyboardController


def test_keyboard_mapping_resolution():
    ctrl = KeyboardController(mapping=KeyMapping(up="i", down="k", left="j", right="l"))

    assert ctrl._resolve_key("up") == "i"
    assert ctrl._resolve_key("left") == "j"
