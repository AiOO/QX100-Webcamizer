import asyncio

from aiohttp import ClientSession, ClientTimeout
from click import Choice, command, option
from imageio.v3 import imread
from numpy import uint8 as numpy_uint8
from numpy import zeros
from pyvirtualcam import Camera, PixelFormat

from qx100 import ShootMode, get_liveview_url, set_shoot_mode


async def capture_liveview_images(liveview_url: str, camera: Camera):
    async with ClientSession(timeout=ClientTimeout()) as session:
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
            except GeneratorExit:
                camera.close()


async def main_loop(shoot_mode: ShootMode):
    await set_shoot_mode(shoot_mode)
    liveview_url = await get_liveview_url()
    with Camera(*shoot_mode.value[1], 30) as camera:
        await capture_liveview_images(liveview_url, camera)


@command()
@option(
    '--mode',
    type=Choice(['still', 'movie']),
    default='still',
    help='Choose camera shoot mode.',
    show_default='still',
)
def main(mode: str):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main_loop(ShootMode[mode]))


if __name__ == '__main__':
    main()
