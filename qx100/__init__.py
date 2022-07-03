import enum
import json

from imageio.v3 import imread
from numpy import uint8 as numpy_uint8
from numpy import zeros
from requests import get, post

from pyvirtualcam import Camera, PixelFormat

QX100_HOST = '10.0.0.1'
QX100_PORT = 10000
QX100_BASE_URL = f'http://{QX100_HOST}:{QX100_PORT}/sony'
QX100_COMMON_HEADERS = {
    'Content-type': 'text/plain',
    'Accept': '*/*',
    'X-Requested-With': 'com.sony.playmemories.mobile',
}
QX100_COMMON_DATA = {
    'id': 1,
    'version': '1.0',
}


class ShootMode(enum.Enum):
    still = ('still', (640, 480))
    movie = ('movie', (640, 360))


def set_shoot_mode(shoot_mode: ShootMode):
    response = post(
        f'{QX100_BASE_URL}/camera',
        data=json.dumps(
            dict(
                method='setShootMode',
                params=[shoot_mode.value[0]],
                **QX100_COMMON_DATA,
            ),
        ),
        headers=QX100_COMMON_HEADERS,
    )
    assert response.json() == dict(
        result=[0], id=1
    ), 'Shoot mode change failed'


def get_liveview_url() -> str:
    response = post(
        f'{QX100_BASE_URL}/camera',
        data=json.dumps(
            dict(
                method='startLiveview',
                params=[],
                **QX100_COMMON_DATA,
            ),
        ),
        headers=QX100_COMMON_HEADERS,
    )
    return response.json()['result'][0]


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
