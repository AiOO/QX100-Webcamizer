import asyncio
import logging
import sys

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientPayloadError, ServerTimeoutError
from click import Choice, command, option
from imageio.v3 import imread
from numpy import uint8 as numpy_uint8
from numpy import zeros
from pyvirtualcam import Camera, PixelFormat

from qx100 import ShootMode, get_liveview_url, set_shoot_mode

logging.basicConfig(format='[%(levelname)s - %(asctime)s] %(message)s')
logger = logging.getLogger(__name__)


async def capture_liveview_images(liveview_url: str, camera: Camera):
    async with ClientSession(timeout=ClientTimeout(sock_read=5)) as session:
        async with session.get(liveview_url) as response:
            try:
                buffer = b''
                async for content in response.content.iter_chunked(1024):
                    start_index = content.find(b'\xFF\xD8\xFF')
                    end_index = content.find(b'\xFF\xD9')
                    if end_index != -1:
                        buffer += content[: end_index + 2]
                        image = imread(buffer)
                        height, width, _ = image.shape
                        if height == camera.height and width == camera.width:
                            frame = zeros(
                                (camera.height, camera.width, 3), numpy_uint8
                            )
                            frame[0 : camera.height, 0 : camera.width] = image
                            camera.send(frame)
                            camera.sleep_until_next_frame()
                    if start_index != -1:
                        buffer = content[start_index:]
                    else:
                        buffer += content
            except ClientPayloadError:
                camera.close()
                raise


async def main_loop(shoot_mode: ShootMode):
    while True:
        logger.info('Changing shoot mode...')
        is_set_shoot_mode_succeeded = await set_shoot_mode(shoot_mode)
        if not is_set_shoot_mode_succeeded:
            logger.error('Changing shoot mode is failed.')
            continue
        logger.info('Getting liveview url...')
        liveview_url = await get_liveview_url()
        if liveview_url is None:
            logger.error('Getting liveview url is failed.')
            continue
        logger.info('Starting camera...')
        with Camera(*shoot_mode.value[1], 30) as camera:
            logger.info('Camera started.')
            try:
                await capture_liveview_images(liveview_url, camera)
            except (ClientPayloadError, ServerTimeoutError):
                logger.error('Connection closed.')


@command()
@option(
    '--mode',
    type=Choice(['still', 'movie']),
    default='still',
    help='Choose camera shoot mode.',
    show_default='still',
)
@option(
    '--log-level',
    type=Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
    default='INFO',
    help='Choose log level.',
    show_default='INFO',
)
def main(mode: str, log_level: str):
    logger.setLevel(logging.getLevelName(log_level))
    logger.info('Webcamizer started!')
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main_loop(ShootMode[mode]))


if __name__ == '__main__':
    main()
