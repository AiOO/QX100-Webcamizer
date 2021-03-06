# Sony DSC-QX100 Webcamizer

You can use your DSC-QX100 as webcam.

## Prerequisites

### A WiFi device that is not used for Internet connections

To use the camera as a webcam, you need a WiFi connection with the camera.
Therefore, additional Internet connections are needed.

### Installing and preparing virtual camera application

Pelase read carefully and follow below link:

https://github.com/letmaik/pyvirtualcam#supported-virtual-cameras

## How to install

```console
$ ./install.sh
```

This build script builds `pyvirtualcamera` directly to run in a variety of
environments, especially Apple Silicon. If you want, install the
`pyvirtualcamera` project with `pip` and skip the build process.

## How to run

First of all, turn on your QX-100 and connect with it's WiFi AP.

```console
$ python run.py
```

Then use your virtual camera!

### Option

You can choose shoot mode between `still` and `movie`.

```console
$ python run.py --mode movie
```

According to my experiment, the still mode can achieve an aspect ratio of 4:3,
but the focus shifts unnaturally. And the movie mode can achieve an aspect
ratio cropped 16:9, and the focus shifts naturally. But, various camera
settings are limited.

## FYI

Inspired by:

- https://github.com/letmaik/pyvirtualcam
- https://github.com/Tsar/sony_qx_controller
