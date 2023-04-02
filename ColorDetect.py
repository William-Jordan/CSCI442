import cv2 as cv
import numpy as np

minH = 0
minS = 0
minV = 0
maxH = 360
maxS = 100
maxV = 100

def onMouse(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDBLCLK:
        print("row " + str(y) + " col " + str(x) + ": " + str(frame_hsv[y][x]))
        
def HueMinTrackbar(val):
    global minH
    minH = val
def HueMaxTrackbar(val):
    global maxH
    maxH = val
def SatMinTrackbar(val):
    global minS
    minS = val
def SatMaxTrackbar(val):
    global maxS
    maxS = val
def ValMinTrackbar(val):
    global minV
    minV = val
def ValMaxTrackbar(val):
    global maxV
    maxV = val


video = cv.VideoCapture(2)
cv.namedWindow("video")
cv.namedWindow("video_HSV")
cv.createTrackbar("MinH", "video_HSV", 0, 255, HueMinTrackbar)
cv.createTrackbar("MaxH", "video_HSV", 0, 255, HueMaxTrackbar)
cv.createTrackbar("MinS", "video_HSV", 0, 255, SatMinTrackbar)
cv.createTrackbar("MaxS", "video_HSV", 0, 255, SatMaxTrackbar)
cv.createTrackbar("MinV", "video_HSV", 0, 255, ValMinTrackbar)
cv.createTrackbar("MaxV", "video_HSV", 0, 255, ValMaxTrackbar)

cv.setTrackbarPos("MinH", "video_HSV", 26)
cv.setTrackbarPos("MaxH", "video_HSV", 54)
cv.setTrackbarPos("MinS", "video_HSV", 193)
cv.setTrackbarPos("MaxS", "video_HSV", 255)
cv.setTrackbarPos("MinV", "video_HSV", 5)
cv.setTrackbarPos("MaxV", "video_HSV", 120)

kernel = np.ones((5,5),np.uint8)

while True:
    check, frame = video.read()
    frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    
    cv.imshow('video', frame)
    cv.imshow('video_HSV', frame_hsv)
    cv.setMouseCallback("video_HSV", onMouse)

    mask = cv.inRange(frame_hsv, np.array([minH,minS,minV]), np.array([maxH,maxS,maxV]))
    frame_dilate = cv.dilate(mask, kernel, iterations = 1)
    frame_erode = cv.erode(frame_dilate, kernel, iterations = 1)
    cv.imshow('mask', frame_erode)

    
    
    key = cv.waitKey(1)
    if key == 27:
        break
video.release()
cv.destroyAllWindows()
