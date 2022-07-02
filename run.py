from pyvirtualcam import Camera
from qx100 import capture_liveview_images, get_liveview_url, set_shoot_mode


def main():
    liveview_url = get_liveview_url()
    with Camera(640, 480, 15) as camera:
        capture_liveview_images(liveview_url, camera)


if __name__ == '__main__':
    main()
