import pyrealsense2 as rs
import numpy as np
import cv2
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
backward = 6700
left = 7000
right = 5000
stop = 6000



t1 = 0
t2 = 0
def t1t(val):
    global t1
    t1 = val
def t2t(val):
    global t2
    t2 = val

def onMouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print("row " + str(y) + " col " + str(x) + ": " + str(color_image[y][x]))
cv2.namedWindow('sliders')
cv2.createTrackbar('t1','sliders',0,255, t1t)
cv2.createTrackbar('t2','sliders',0,255, t2t)
# Used for dilation and erosion in the mask
kernel = np.ones((5,5),np.uint8)

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 360, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

scale = 10000   # determines how much to scale depth camera by
rescan = 250    # how often to research for objects
time.sleep(1)   # delay to let camera warm up
frame = 0       # frame counter
depthMax = 300  # maximum value for depth pixel
depthMin = 0    # minimum value for depth pixel

depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
align_to = rs.stream.color
align = rs.align(align_to)

stage = 0
blueMin = np.array([230,200,50])
blueMax = np.array([255,255,150])

orangeMin = np.array([90, 160, 220])
orangeMax = np.array([175, 255, 255])

whiteMin = np.array([120, 120, 120])
whiteMax = np.array([170, 170, 170])

yellowMin = np.array([15, 15, 150])
yellowMax = np.array([90, 255, 255])

pinkMin = np.array([90, 20, 210])
pinkMax = np.array([190, 110, 255])

greenMin = np.array([40, 160, 85])
greenMax = np.array([140, 250, 145])

thresholdCounts = 16000000
IceColor = 'None'

t90 = 1.5
tick = 0.3

whiteROIThresh = 3825000

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

try:
    while True:
            
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()

        frames = align.process(frames)

        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        hsv_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2HSV)
        blur = cv2.blur(color_image, (5,5))
        blurHSV = cv2.blur(hsv_image, (5,5))
        if stage == 0:
            maskOrange = cv2.inRange(blur, orangeMin, orangeMax)
            #maskOrange = cv2.resize(maskOrange, (400,400))
            ret, thresh = cv2.threshold(maskOrange, 127,255,0)
            contours = cv2.findContours(thresh,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            theo = 1
            count = 0
            for con in contours[0]:
                (x,y,w,h) = cv2.boundingRect(con)
                if w > 50 and h > 50:
                    #cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
                    roi = thresh[y:y+h, x:x+w]
                    count = np.sum(roi)
                    theo = w*h*255*.40
            if count > theo:
                #print('Flat')
                stage +=1
            else:
                #print('angled')
                tango.setTarget(MOTORS, stop)
                tango.setTarget(TURN, left)
                time.sleep(tick)
                tango.setTarget(TURN, stop)
            cv2.imshow('orange', maskOrange)
            
            
            '''
            orangeROI = maskOrange[150:250, 100:300]
            orangeCount = np.sum(orangeROI)
            if orangeCount > whiteROIThresh:
                stage += 1
                print('Faceing Correct')
            else:
                tango.setTarget(MOTORS, stop)
                tango.setTarget(TURN, left)
                time.sleep(tick)
                tango.setTarget(TURN, stop)
            cv2.imshow('Orange', orangeROI)
            '''
            #rotate until we see a blue line
            #Cross line straight
            #Counting Pixels in center screen only to align
            #if facing direction stage +=1
        elif stage == 1:
            tango.setTarget(MOTORS, forward)
            maskBlue = cv2.inRange(blur, blueMin, blueMax)
            maskBlue = cv2.resize(maskBlue, (400,400))
            blueROI = maskBlue[300:400, 0:400]
            theo = 400*100*255*.2
            count = np.sum(blueROI)
            
            if count > theo:
                tango.setTarget(MOTORS, forward)
                time.sleep(2.8)
                tango.setTarget(MOTORS, stop)
                print('Crossed Blue')
                stage +=1

            #ret, thresh = cv2.threshold(maskOrange, 127,255,0)
            #im2,contours,hie = cv2.findContours(thresh, cv2.RETR_TREE, cv2. CHAIN_APPROX_SIMPLE)
            #cv2.imshow('Contours', im2)
            cv2.imshow('blue', maskBlue)
            
            #edges = cv2.Canny(blur, t1, t2)
            #avoid white notebooks
            #travel to orange line
            #Cross Line Straight
            #if cross line stage +=1
        elif stage == 2:
            #time.sleep(2)
            #Sweep 180 looking for different ice colors
            img_gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(img_gray, 1.3,5)
            
            #for (x,y,w,h) in faces:
            #    cv2.rectangle(color_image,(x,y),(x+w,y+h),(255,0,0),2)
            if len(faces) > 0:
                (x,y,w,h) = faces[0]
                cv2.rectangle(color_image,(x,y),(x+w,y+h),(255,0,0),2)
                tango.setTarget(MOTORS, forward)
                time.sleep(3)
                tango.setTarget(MOTORS, stop)
                time.sleep(2)
                tango.setTarget(HEADTILT, 5000)
                stage += 1
                
            else:
                tango.setTarget(MOTORS, stop)
                tango.setTarget(TURN, right)
                time.sleep(tick)
                tango.setTarget(TURN, stop)
            cv2.imshow('img', color_image)
                
            '''
            maskYellow = cv2.inRange(blur, yellowMin, yellowMax)
            maskPink = cv2.inRange(blur, pinkMin, pinkMax)
            maskGreen = cv2.inRange(blur, greenMin, greenMax)


            yellowCount = np.sum(maskYellow)
            pinkCount = np.sum(maskPink)
            greenCount = np.sum(maskGreen)

            cv2.imshow('yellow', maskYellow)
            cv2.imshow('pink', maskPink)
            cv2.imshow('green', maskGreen)
            
            if yellowCount > thresholdCounts:
                IceColor = 'Yellow'
                print(IceColor)
                stage +=1
            elif pinkCount > thresholdCounts:
                IceColor = 'Pink'
                print(IceColor)
                stage +=1
            elif greenCount > thresholdCounts:
                IceColor = 'Green'
                print(IceColor)
                stage +=1
            else:
                tango.setTarget(MOTORS, stop)
                tango.setTarget(TURN, right)
                time.sleep(tick)
                tango.setTarget(TURN, stop)
            '''
        elif stage == 3:
            maskYellow = cv2.inRange(blur, yellowMin, yellowMax)
            maskPink = cv2.inRange(blur, pinkMin, pinkMax)
            maskGreen = cv2.inRange(blur, greenMin, greenMax)

            yellowCount = np.sum(maskYellow)
            pinkCount = np.sum(maskPink)
            greenCount = np.sum(maskGreen)

            cv2.imshow('yellow', maskYellow)
            cv2.imshow('pink', maskPink)
            cv2.imshow('green', maskGreen)
            
            if yellowCount > thresholdCounts:
                IceColor = 'Yellow'
                print(IceColor)
                tango.setTarget(MOTORS, backward)
                time.sleep(1.5)
                tango.setTarget(MOTORS, stop)
                stage +=1
                cv2.destroyAllWindows()
            elif pinkCount > thresholdCounts:
                IceColor = 'Pink'
                print(IceColor)
                tango.setTarget(MOTORS, backward)
                time.sleep(1.5)
                tango.setTarget(MOTORS, stop)
                stage +=1
                cv2.destroyAllWindows()
            elif greenCount > thresholdCounts:
                IceColor = 'Green'
                print(IceColor)
                tango.setTarget(MOTORS, backward)
                time.sleep(1.5)
                tango.setTarget(MOTORS, stop)
                stage +=1
                cv2.destroyAllWindows()
        elif stage == 4:
            #hprint(IceColor)
            maskBlue = cv2.inRange(blur, blueMin, blueMax)
            #maskBlue = cv2.resize(maskBlue,(400,400))
            #maskBlue = maskBlue[200:400, 0:400]
            #maskOrange = cv2.resize(maskOrange, (400,400))
            ret, thresh = cv2.threshold(maskBlue, 127,255,0)
            contours = cv2.findContours(thresh,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            theo = 1
            count = 0
            for con in contours[0]:
                (x,y,w,h) = cv2.boundingRect(con)
                if w > 30 and h > 30:
                    #cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
                    roi = thresh[y:y+h, x:x+w]
                    count = np.sum(roi)
                    theo = w*h*255*.40
            if count > theo:
                #print('Flat')
                stage +=1
            else:
                #print('angled')
                tango.setTarget(MOTORS, stop)
                tango.setTarget(TURN, right)
                time.sleep(tick)
                tango.setTarget(TURN, stop)
            cv2.imshow('blue', maskBlue)
            '''
            
            if IceColor == 'Yellow':
                mask = cv2.inRange(blur, yellowMin, yellowMax)
            elif IceColor == 'Pink':
                mask = cv2.inRange(blur, pinkMin, pinkMax)
            else:
                mask = cv2.inRange(blur, greenMin, greenMax)

            maskCounts = np.sum(mask)
            while maskCounts < maxCountsThresh:
                #drive forward
                break
            stage += 1
            print(IceColor)
            #aproach
            #if close stage += 1
            '''
        elif stage ==5:
            tango.setTarget(MOTORS, forward)
            maskOrange = cv2.inRange(blur, orangeMin, orangeMax)
            maskOrange = cv2.resize(maskOrange, (400,400))
            orangeROI = maskOrange[300:400, 0:400]
            theo = 400*100*255*.2
            count = np.sum(orangeROI)
            
            if count > theo:
                tango.setTarget(MOTORS, forward)
                time.sleep(1.5)
                tango.setTarget(MOTORS, stop)
                print('Crossed Orange')
                tango.setTarget(TURN, left)
                time.sleep(1)
                tango.setTarget(TURN, stop)
                stage +=1
            #Turn 180
            #Drive Forward to find orange line
            #aproach line center on
            #if facing direction stage +=1
        elif stage ==6:
            cv2.destroyAllWindows()
            #time.sleep(2)
            
            #Sweep 180 looking for different ice colors
            if IceColor == 'Yellow':
                mask = cv2.inRange(blur, yellowMin, yellowMax)
            elif IceColor == 'Pink':
                mask = cv2.inRange(blur, pinkMin, pinkMax)
            else:
                mask = cv2.inRange(blur, greenMin, greenMax)

            mask= cv2.resize(mask, (400,400))


            ROI = mask[0:400, 100:300]
            
            count = np.sum(ROI)

            cv2.imshow('mask', mask)
            
            if count > 500000:
                tango.setTarget(MOTORS, forward)
                time.sleep(10)
                tango.setTarget(MOTORS, stop)
                stage += 1
            else:
                tango.setTarget(MOTORS, stop)
                tango.setTarget(TURN, right)
                time.sleep(tick)
                tango.setTarget(TURN, stop)
            #avoid white notebooks
            #travel to blue line
            #if cross stage +=1
            

        elif stage == 7:
            maskOrange = cv2.inRange(blur, blueMin, blueMax)
            cv2.imshow('orange', maskOrange)
            #print(np.sum(maskOrange))
            #img_gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
            #faces = face_cascade.detectMultiScale(img_gray, 1.3,5)
            #for (x,y,w,h) in faces:
            #    cv2.rectangle(color_image,(x,y),(x+w,y+h),(255,0,0),2)
            
            # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', color_image)
        #cv2.imshow('hsv', hsv_image)
        cv2.setMouseCallback("RealSense", onMouse)
        frame += 1
        key = cv2.waitKey(1)
        if key == 27:
            break
finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()
