import cv2
import numpy as np

import backend
import config

allow_control: bool = False
pixels_per_cm: float = 1.0
object_found: bool = False

import asyncio

async def think(frame):
    global object_found

    available = await asyncio.to_thread(get_object_available, frame)

    if available is not None and not object_found:
        result = await asyncio.to_thread(get_object, frame)
        object_found = True

        container = config.find(
            result["ai"][0],
            config.get_default_model(),
            result["color"][0],
            result["color"][1],
            result["color"][2],
            result["size"][0],
            result["size"][1]
        )

        await backend.Socket.send({
            "type": "parameter",
            "containerId": container if result["ai"] is not None else None,
            "aiType": result["ai"][0] if result["ai"] is not None else None,
            "aiName": config.get_default_model() if result["ai"] is not None else None,
            "r": int(result["color"][0]),
            "g": int(result["color"][1]),
            "b": int(result["color"][2]),
            "w": int(result["size"][0]),
            "h": int(result["size"][1]),
            "containerName": container["name"] if container is not None else None
        })

    elif available is None and object_found:
        object_found = False

def get_object(frame):
    xmin, xmax, ymin, ymax, mask = get_object_available(frame)
    object_size = get_object_size(xmax, xmin, ymin, ymax)
    object_color = get_object_color(frame, mask)
    object_type = get_object_type(frame[ymin:ymax, xmin:xmax])

    return {
        "size": object_size,
        "color": object_color,
        "ai": object_type
    }

def get_object_available(frame):
    h, w = frame.shape[:2]

    mask = get_object_mask(frame)

    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return None

    xmin, xmax = xs.min(), xs.max()
    ymin, ymax = ys.min(), ys.max()

    if xmin == 0 or ymin == 0 or xmax >= w - 1 or ymax >= h - 1:
        return None

    return xmin, xmax, ymin, ymax, mask

def get_object_type(frame):
    if config.get_default_model() is None:
        return None
    return "TODO_RETURN_TYPE"

def get_object_color(frame, mask):
    object_pixels = frame[mask > 0]
    b, g, r = object_pixels.mean(axis=0)
    return r, g, b

def get_object_size(xmax, xmin, ymin, ymax):
    width_px = xmax - xmin
    height_px = ymax - ymin

    width_cm = width_px / pixels_per_cm
    height_cm = height_px / pixels_per_cm

    return width_cm, height_cm

def get_object_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 | mask2

    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    return mask