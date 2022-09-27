import cv2
import argparse
import configparser
from pathlib import Path
import time


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--vid", default="0", help="Video sourse, default 0")
parser.add_argument(
    "-f", "--auto_focus", action="store_true", default=False, help="Turn on auto focus"
)
parser.add_argument(
    "-c",
    "--config",
    default="focus.ini",
    help="Focus config file, default focus.ini",
)
args = parser.parse_args()

try:
    vid = int(args.vid)
except ValueError:
    vid = args.vid

config_path = (Path(__file__).parent / Path(args.config)).resolve().absolute()
print("config file :", config_path)

config = configparser.ConfigParser()

config.read(config_path, encoding="utf-8")

cap = cv2.VideoCapture(vid)
cap.grab()
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

if not args.auto_focus and config.has_section("Focus"):
    auto_focus = (
        config.getint("Focus", "auto_focus")
        if config.has_option("Focus", "auto_focus")
        else 1
    )
    focus = (
        config.getint("Focus", "focus")
        if config.has_option("Focus", "focus")
        else int(cap.get(cv2.CAP_PROP_FOCUS))
    )
else:
    auto_focus = 1
    focus = None
print("config auto_focus = %s" % auto_focus)
print("config focus = %s" % focus)
print("*" * 10)


if not auto_focus:
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

time.sleep(2)
if focus:
    cap.set(cv2.CAP_PROP_FOCUS, focus)

cv2.namedWindow("frame")


def set_auto_focus(x):
    cap.set(cv2.CAP_PROP_AUTOFOCUS, x)


cv2.createTrackbar(
    "0: OFF\r\n 1: ON\r\nauto_focus",
    "frame",
    int(cap.get(cv2.CAP_PROP_AUTOFOCUS)),
    1,
    set_auto_focus,
)


def set_focus(x):
    cap.set(cv2.CAP_PROP_FOCUS, x)


cv2.createTrackbar("focus", "frame", int(cap.get(cv2.CAP_PROP_FOCUS)), 1022, set_focus) # 1023

while cap.isOpened():
    # cap frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break
    focus = int(cap.get(cv2.CAP_PROP_FOCUS))
    cv2.setTrackbarPos("focus", "frame", focus)

    af = int(cap.get(cv2.CAP_PROP_AUTOFOCUS))
    cv2.setTrackbarPos("0: OFF\r\n 1: ON\r\nauto_focus", "frame", af)

    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# When everything done, release the cap
cap.release()
cv2.destroyAllWindows()

if not config.has_section("Focus"):
    config.add_section("Focus")

print("set auto_focus = 0")
config.set("Focus", "auto_focus", "0")

print("set focus = %s" % focus)
config.set("Focus", "focus", str(focus))

config.write(open(config_path, "w"))