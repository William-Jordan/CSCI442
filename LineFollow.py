import cv2 as cv
import numpy as np
import time
from maestro import Controller

thresh1= 0
thresh2= 0

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

stopThresh = 4000

headBang = True
headUp = 6600
headDown = 5400


def onMouse(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDBLCLK:
        print("row " + str(y) + " col " + str(x) + ": " + str(frame_hsv[y][x]))
        
def threshold1(val):
    global thresh1
    thresh1 = val
def threshold2(val):
    global thresh2
    thresh2 = val

cv.namedWindow('thresholds')
cv.namedWindow('video')
cv.namedWindow('thresh')
cv.createTrackbar('thresh1', 'thresholds', 0,255, threshold1)
cv.setTrackbarPos('thresh1', 'thresholds', 210)
cv.createTrackbar('thresh2', 'thresholds', 0,255,threshold2)
cv.setTrackbarPos('thresh2', 'thresholds', 210)
video = cv.VideoCapture(2)
kernel = np.ones((5,5),np.uint8)

lowerBound = 125
upperBound = 275
#time.sleep(5)
while True:
    check, frame = video.read()
    #frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    #gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    blur = cv.blur(frame, (5,5))
    mask = cv.inRange(blur, (thresh1,0,0), (255,255,255))
    mask2 = cv.inRange(blur, (0,0,thresh2), (255,255,255))
    img = mask + mask2
    ret,thresh = cv.threshold(img, 50, 255, cv.THRESH_BINARY)
    frame = cv.resize(frame, (400, 400))
    thresh = cv.resize(thresh, (400,400))
    
    massX, massY = np.where(thresh >=255)
    if len(massX) == 0 or len(massY) == 0:
        continue
    cogX = np.average(massX)
    cogY = np.average(massY)
    #print(cogX)
    #print(cogY)
    #print()
    frame = cv.circle(frame, (int(cogY), int(cogX)), 10, (255,255,0), 2)
    frame = cv.line(frame, (lowerBound,0), (lowerBound,400), (255,0,0),2)
    frame = cv.line(frame, (upperBound,0), (upperBound,400), (255,0,0),2)
    if cogY < lowerBound:
        print('turn left')
        tango.setTarget(MOTORS, stop)
        tango.setTarget(TURN, left)
    elif cogY > upperBound:
        print('turn right')
        tango.setTarget(MOTORS, stop)
        tango.setTarget(TURN, right)
    elif len(massX) < stopThresh and len(massY) < stopThresh:
        print('stop')
        tango.setTarget(TURN, stop)
        tango.setTarget(MOTORS, stop)
        if headBang:
            tango.setTarget(HEADTILT, headUp)
            tango.setTarget(HEADTURN, headUp)
        else:
            tango.setTarget(HEADTILD, headDown)
            tango.setTarget(HEADTURN, headDown)
        headBang = !headBang
        
    else:
        print('straight')
        tango.setTarget(TURN, stop)
        tango.setTarget(MOTORS, forward)
    #cv.imshow('mask', img)
    #print(frame.shape)

    cv.imshow('video', frame)
    cv.imshow('thresh', thresh)


    
    #hist = cv.equalizeHist(frame)
    #ret, binary = cv.threshold(hist, thresh,255, cv.THRESH_BINARY)
    #cv.imshow('gray', gray)
    #cv.imshow('equal', hist)
    #cv.imshow('binary', binary)
    #cv.imshow('video_HSV', frame_hsv)
    #cv.setMouseCallback("video_HSV", onMouse)

    #mask = cv.inRange(frame_hsv, np.array([minH,minS,minV]), np.array([maxH,maxS,maxV]))
    #frame_dilate = cv.dilate(mask, kernel, iterations = 1)
    #frame_erode = cv.erode(frame_dilate, kernel, iterations = 1)
    #cv.imshow('mask', frame_erode)

    
    
    key = cv.waitKey(1)
    if key == 27:
        break
tango.setTarget(TURN, stop)
tango.setTarget(MOTORS, stop)
tango.setTarget(HEADTURN, stop)
tango.setTarget(HEADTILT, stop)
video.release()
cv.destroyAllWindows()
