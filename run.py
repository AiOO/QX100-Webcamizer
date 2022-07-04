from click import Choice, command, option
from imageio.v3 import imread
from numpy import uint8 as numpy_uint8
from numpy import zeros
from pyvirtualcam import Camera, PixelFormat
from requests import get

from qx100 import ShootMode, get_liveview_url, set_shoot_mode


def capture_liveview_images(liveview_url: str, camera: Camera) -> bytes:
    response = get(liveview_url, stream=True)
    buffer = b''
    for content in response.iter_content(1024):
        content: bytes
        start_index = content.find(b'\xFF\xD8\xFF')
        end_index = content.find(b'\xFF\xD9')
        if end_index != -1:
            buffer += content[: end_index + 2]
            image = imread(buffer)
            height, width, _ = image.shape
            if height == camera.height and width == camera.width:
                frame = zeros((camera.height, camera.width, 3), numpy_uint8)
                frame[0 : camera.height, 0 : camera.width] = image
                camera.send(frame)
                camera.sleep_until_next_frame()
        if start_index != -1:
            buffer = content[start_index:]
        else:
            buffer += content


@command()
@option(
    '--mode',
    type=Choice(['still', 'movie']),
    default='still',
    help='Choose camera shoot mode.',
    show_default='still',
)
def main(mode: str):
    shoot_mode = ShootMode[mode]
    set_shoot_mode(shoot_mode)
    liveview_url = get_liveview_url()
    with Camera(*shoot_mode.value[1], 30) as camera:
        capture_liveview_images(liveview_url, camera)


if __name__ == '__main__':
    main()
