from bot.navigation.radar import getCoordinateFromPixel, getPixelFromCoordinate


def test_pixel_coordinate_round_trip() -> None:
    pixel = (512, 1024)
    coord = getCoordinateFromPixel(pixel, 7)

    assert coord == (32256, 32000, 7)
    assert getPixelFromCoordinate(coord) == pixel
