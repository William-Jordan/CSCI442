# Arthur Battaglin and William Jordan
# CSCI 442 - Project 2
# 03/10/23

"""
This is a tracking algorithm that works in conjunction with the RealSense depth camera.
The algorithm will begin by searching for white objects in the frame. If an object
is large enough it will apply a KCF Tracker and continuously record the depth. Results
are displayed in the black window beneath the image/depth pair. In this black
window the red box simulates the robot/cameras location and blue horizontal lines indicate
the depth and width of tracked object. In this sense, the width of the blue line indicates the
size of the tracked item. Further the closer the blue line is to the red box the closer
the item is to the camera in real space. Lastly a window labeled 'white' is displayed which can
be used to fine tune the 'mask' window for the detection algorithm.
"""
import pyrealsense2 as rs
import numpy as np
import cv2
import time
from maestro import Controller


MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

tango = Controller()
body = 6000
headTurn = 6000
headTilt = 6000
motors = 6000
turn = 6000

forward = 5400
backward = 6800
stop = 6000

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

scale = 10000  # determines how much to scale depth camera by

depthMax = 300  # maximum value for depth pixel
depthMin = 0  # minimum value for depth pixel

depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
align_to = rs.stream.color
align = rs.align(align_to)

frames = pipeline.wait_for_frames()
frames = align.process(frames)
color_frame = frames.get_color_frame()
color_image = np.asanyarray(color_frame.get_data())
tracker = cv2.TrackerMIL_create()
time.sleep(1)  # delay to let camera warm up
bbox = cv2.selectROI(color_image, False)
ok = tracker.init(color_image, bbox)
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

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), 0)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        ok, bbox = tracker.update(color_image)

        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(color_image, p1, p2, (255, 0, 0), 2, 1)

        # Find the center of each bounding box
        center = (int(int(bbox[1]) + (int(bbox[3]) / 2)), int(int(bbox[0]) + (int(bbox[2]) / 2)))

        # Get the depth from the center of each bounding box and keep it within bounds
        depthSum = 0
        for j in range(-1, 2, 1):
            for k in range(-1, 2, 1):
                depthSum += depth_image[center[0] + j][center[1] + k] * depth_scale  # Collects depth in meters
        depthMeter = depthSum/9
        if depthMeter > 1.1:
            print('Forward')
            tango.setTarget(MOTORS, forward)
        elif depthMeter < .9:
            tango.setTarget(MOTORS, backward)
            print('Backward')
        else:
            tango.setTarget(MOTORS, stop)
            print('Stop')

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow('RealSense', 300,300)
        cv2.imshow('RealSense', images)

        key = cv2.waitKey(1)
        if key == 27:
            break
finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()
