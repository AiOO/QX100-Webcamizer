from click import Choice, command, option

from pyvirtualcam import Camera
from qx100 import (
    ShootMode,
    capture_liveview_images,
    get_liveview_url,
    set_shoot_mode,
)


@command()
@option(
    '--mode',
    type=Choice(['still', 'movie']),
    default='movie',
    help='Choose camera shoot mode.',
    show_default='movie',
)
def main(mode: str):
    shoot_mode = ShootMode[mode]
    set_shoot_mode(shoot_mode)
    liveview_url = get_liveview_url()
    with Camera(*shoot_mode.value[1], 30) as camera:
        capture_liveview_images(liveview_url, camera)


if __name__ == '__main__':
    main()
