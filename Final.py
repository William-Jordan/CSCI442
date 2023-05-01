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
backward = 6800
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
blueMin = np.array([230,200,0])
blueMax = np.array([255,255,255])

orangeMin = np.array([35, 115, 230])
orangeMax = np.array([210, 255, 255])

whiteMin = np.array([120, 120, 120])
whiteMax = np.array([170, 170, 170])

yellowMin = np.array([15, 120, 120])
yellowMax = np.array([75, 180, 180])

pinkMin = np.array([55, 10, 175])
pinkMax = np.array([190, 95, 255])

greenMin = np.array([40, 180, 85])
greenMax = np.array([120, 220, 145])

thresholdCounts = 100000
IceColor = 'None'

t90 = 1.5
tick = 0.3

whiteROIThresh = 3825000
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
            maskOrange = cv2.resize(maskOrange, (400,400))
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
            
            #rotate until we see a blue line
            #Cross line straight
            #Counting Pixels in center screen only to align
            #if facing direction stage +=1
        elif stage == 1:
            maskOrange = cv2.inRange(blur, orangeMin, orangeMax)
            cv2.imshow('orange', maskOrange)
            
            #edges = cv2.Canny(blur, t1, t2)
            #avoid white notebooks
            #travel to orange line
            #Cross Line Straight
            #if cross line stage +=1
        elif stage == 2:
            #Sweep 180 looking for different ice colors
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
                stage +=1
            elif pinkCount > thresholdCounts:
                IceColor = 'Pink'
                stage +=1
            elif greenCount > thresholdCounts:
                IceColor = 'Green'
                stage +=1
            else:
                #rotate
                pass

        elif stage == 3:
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
        elif stage ==4:
            #Turn 180
            #Drive Forward to find orange line
            #aproach line center on
            #if facing direction stage +=1
            pass
        elif stage ==5:
            #avoid white notebooks
            #travel to blue line
            #if cross stage +=1
            pass

        elif stage == 6:
            #Sweep 180 with ice color map
            #aproach
            #bump into box
            pass
            
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