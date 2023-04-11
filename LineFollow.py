import cv2 as cv
import numpy as np
import time

thresh1= 0
thresh2= 0

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

lowerBound = 220
upperBound = 420
#time.sleep(5)
while True:
    check, frame = video.read()
    #frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    #gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    mask = cv.inRange(frame, (thresh1,0,0), (255,255,255))
    mask2 = cv.inRange(frame, (0,0,thresh2), (255,255,255))
    img = mask + mask2
    ret,thresh = cv.threshold(img, 50, 255, cv.THRESH_BINARY)
    
    
    massX, massY = np.where(thresh >=255)
    if len(massX) == 0 or len(massY) == 0:
        continue
    cogX = np.average(massX)
    cogY = np.average(massY)
    #print(cogX)
    #print(cogY)
    #print()
    frame = cv.circle(frame, (int(cogY), int(cogX)), 10, (255,255,0), 2)
    frame = cv.line(frame, (lowerBound,0), (lowerBound,480), (255,0,0),2)
    frame = cv.line(frame, (upperBound,0), (upperBound,480), (255,0,0),2)
    if cogY < lowerBound:
        print('turn left')
    elif cogY > upperBound:
        print('turn right')
    elif len(massX) < 9000 and len(massY) < 9000:
        print('stop')
    else:
        print('straight')
    #cv.imshow('mask', img)
    #print(frame.shape)
    frame = cv.resize(frame, (240, 360))
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
video.release()
cv.destroyAllWindows()
