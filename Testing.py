import cv2 as cv
import numpy as np
import time
from maestro import Controller

MOTORS = 1
TURN = 0
BODY = 2
HEADTILT = 4
HEADTURN = 3

tango = Controller()
body = 6000
headTurn = 6000
headTilt = 6000
motors = 6000
turn = 6000

forward = 5300
backward = 6800
left = 6900
right = 5100
stop = 6000

rotate = True
if rotate:
    tango.setTarget(MOTORS, stop)
    tango.setTarget(TURN, left)
    time.sleep(.1)
    tango.setTarget(TURN, stop)

tango.setTarget(TURN, stop)
tango.setTarget(MOTORS, stop)
tango.setTarget(HEADTURN, stop)
tango.setTarget(HEADTILT, stop)
tango.setTarget(BODY, stop)
video.release()
cv.destroyAllWindows()
