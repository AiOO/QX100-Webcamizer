import enum
import json

from aiohttp import ClientSession

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


async def set_shoot_mode(shoot_mode: ShootMode):
    async with ClientSession() as session:
        async with session.post(
            f'{QX100_BASE_URL}/camera',
            json=dict(
                method='setShootMode',
                params=[shoot_mode.value[0]],
                **QX100_COMMON_DATA,
            ),
            headers=QX100_COMMON_HEADERS,
        ) as response:
            result = await response.json()
            assert result == dict(result=[0], id=1), 'Shoot mode change failed'


async def get_liveview_url() -> str:
    async with ClientSession() as session:
        async with session.post(
            f'{QX100_BASE_URL}/camera',
            json=dict(
                method='startLiveview',
                params=[],
                **QX100_COMMON_DATA,
            ),
            headers=QX100_COMMON_HEADERS,
        ) as response:
            result = await response.json()
            return result['result'][0]
