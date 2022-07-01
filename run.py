import json
import pathlib

from numpy import uint8 as numpy_uint8, zeros
from pyvirtualcam import Camera, PixelFormat
from requests import get, post
from imageio.v3 import imread


QX100_HOST = '10.0.0.1'
QX100_PORT = 10000
QX100_BASE_URL = f'http://{QX100_HOST}:{QX100_PORT}/sony'
QX100_COMMON_HEADERS = {
    'Content-type': 'text/plain',
    'Accept': '*/*',
    'X-Requested-With': 'com.sony.playmemories.mobile',
}


def get_liveview_url() -> str:
    response = post(
        f'{QX100_BASE_URL}/camera',
        data=json.dumps(
            {
                'method': 'startLiveview',
                'params': [],
                'id': 1,
                'version': '1.0',
            },
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
            buffer += content[:end_index + 2]
            image = imread(buffer)
            frame = zeros((camera.height, camera.width, 3), numpy_uint8)
            frame[:] = 0
            frame[0:camera.height, 0:camera.width] = image
            camera.send(frame)
            camera.sleep_until_next_frame()
        if start_index != -1:
            buffer = content[start_index:]
        else:
            buffer += content


def main():
    liveview_url = get_liveview_url()
    with Camera(640, 480, 15) as camera:
        capture_liveview_images(liveview_url, camera)


if __name__ == '__main__':
    main()
