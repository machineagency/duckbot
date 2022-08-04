#!/usr/bin/env python
# coding: utf-8

import cv2
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import numpy as np
import picamera #Note that this can only be installed on raspbery pi. 
import time


def getCameraIndices():
    """Returns valid camera indices for use with OpenCV"""
    index = 0
    arr = []
    i = 4
    while i > 0:
        try:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                arr.append(index)
                cap.release()
        except:
            print('exception')
        index += 1
        i -= 1
    return arr

def getFrame(resolution = [1200, 1200]):
    with picamera.PiCamera() as camera:
        camera.resolution = (1200, 1200)
        camera.framerate = 24
        time.sleep(2)
        # print("... camera connection established")
        output = np.empty((resolution[1], resolution[0], 3), dtype=np.uint8)
        camera.capture(output, 'rgb', use_video_port = True)
        tpose = np.transpose(output, axes = (1,0,2))
        #N.B. opencv doesn't like opening files in different directories :/
        mtx, dist = load_coefficients('/home/pi/duckbot/notebooks/utils/calibration_checkerboard.yml') 
        undistorted = cv2.undistort(tpose, mtx, dist, None, mtx)
        return undistorted

    
def load_coefficients(path):
    '''Loads camera matrix and distortion coefficients.'''
    # FILE_STORAGE_READ
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)

    # note we also have to specify the type to retrieve other wise we only get a
    # FileNode object back instead of a matrix
    camera_matrix = cv_file.getNode('K').mat()
    dist_matrix = cv_file.getNode('D').mat()

    cv_file.release()
    return [camera_matrix, dist_matrix]

def getFrameCamera(idx=0):
    """Return a frame from the specified camera"""
    videoCaptureObject = cv2.VideoCapture(idx)
    for f in range(5): # on mac we have to read several frames
                       # don't have to on the pi
        ret,frame = videoCaptureObject.read()
    videoCaptureObject.release()
    cv2.destroyAllWindows()
    
    if ret:
        return frame
    else:
        return "couldn't get frame!"

# def saveFrame(idx=0, path="./test.png"):
#     """Return a frame from the specified camera and save it to file"""
#     videoCaptureObject = cv2.VideoCapture(idx)
#     for f in range(5): # on mac we have to read several frames
#                        # don't have to on the pi
#         ret,frame = videoCaptureObject.read()
#         cv2.imwrite(path,frame)
#     videoCaptureObject.release()
#     cv2.destroyAllWindows()
    
#     if ret:
#         return frame
#     else:
#         return "couldn't get frame!"
def showFrame(frame, grid=False, save=False):
    plt.imshow(frame)
    plt.title('frame capture')
    if grid:
        plt.grid() # add a grid
        h, w, z = frame.shape
        plt.plot([w/2], [h/2], marker='o') # put a marker in the center of the image
    if save:
        plt.savefig('fig.png');
    plt.show()

    
def saveFrame(frame, path):
    cv2.imwrite(path, frame)
    
def selectPoint(frame):
    plt.imshow(frame)
    plt.title('frame capture')
    pts = plt.ginput(1)[0] #number of clicks
    print(pts)
    plt.close()
    
    return pts

def getWells(frame, gain = 1.2, minR = 70, maxR = 100):
    """ specific radii range to get well plate circles """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    wellData = []
    circles = cv2.HoughCircles(blur,
                               cv2.HOUGH_GRADIENT,
                               gain,
                               minDist=100,
                               param1=100,
                               param2=100,
                               minRadius=minR,
                               maxRadius=maxR
                               )
    if circles is not None:
        circlesDraw = np.uint16(np.around(circles))
        circles = circles[0,:]

        for i in circlesDraw[0,:]:
            # draw the outer circle
            print(f"the radius is: {i[2]}")
            print(f"the center is: ({i[0]},{i[1]})")
            wellData.append([i[0], i[1], i[2]])
            cv2.circle(frame,(i[0], i[1]), i[2], (255, 0, 0), 5)

        print(f"I found {len(circlesDraw[0])} wells")
        return frame, wellData
    else:
        print("no circles!")
        return None, None

def getSingleWell(frame, gain = 1, minR = 70, maxR = 100):
    """ specific radii range to get well plate circles """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    wellData = []
    
    for g in np.arange(gain, 10, 0.1):
        # find the right gain to find a single circle
        circles = cv2.HoughCircles(blur,
                                   cv2.HOUGH_GRADIENT,
                                   g,
                                   minDist=100,
                                   param1=100,
                                   param2=100,
                                   minRadius=minR,
                                   maxRadius=maxR
                                   )
        if circles is None:
            continue
        numCircles = circles[0,:].shape[0]
        if numCircles == 1:
            print(f"I used a gain of {g}")
            break
            
    if circles is not None:
        circlesDraw = np.uint16(np.around(circles))
        circles = circles[0,:]

        for i in circlesDraw[0,:]:
            # draw the outer circle
            print(f"the radius is: {i[2]}")
            print(f"the center is: ({i[0]},{i[1]})")
            wellData.append([i[0], i[1], i[2]])
            cv2.circle(frame,(i[0], i[1]), i[2], (255, 0, 0), 5)

        print(f"I found {len(circlesDraw[0])} wells")
        return frame, wellData
    else:
        print("no circles!")
        return None, None
    
def getWellPlate(frame, gain = 1, minR = 70, maxR = 100):
    """ specific radii range to get all 24 well plate circles """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    wellData = []
    
    for g in np.arange(gain, 10, 0.1):
        # find the right gain to find a single circle
        circles = cv2.HoughCircles(blur,
                                   cv2.HOUGH_GRADIENT,
                                   g,
                                   minDist=100,
                                   param1=100,
                                   param2=100,
                                   minRadius=minR,
                                   maxRadius=maxR
                                   )
        if circles is None:
            continue
        numCircles = circles[0,:].shape[0]
        if numCircles == 24:
            print(f"I used a gain of {g}")
            break
            
    if circles is not None:
        circlesDraw = np.uint16(np.around(circles))
        circles = circles[0,:]

        for i in circlesDraw[0,:]:
            # draw the outer circle
            print(f"the radius is: {i[2]}")
            print(f"the center is: ({i[0]},{i[1]})")
            wellData.append([i[0], i[1], i[2]])
            cv2.circle(frame,(i[0], i[1]), i[2], (255, 0, 0), 5)

        print(f"I found {len(circlesDraw[0])} wells")
        return frame, wellData
    else:
        print("no circles!")
        return None, None

def getCircles(frame, gain=1.2):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, gain, minDist=100)
    if circles is not None:
        circlesDraw = np.uint16(np.around(circles))
        circles = circles[0,:]

        for i in circlesDraw[0,:]:
            # draw the outer circle
            print(i[2])
            cv2.circle(frame,(i[0], i[1]), i[2], (255, 0, 0), 10)
            # draw the center of the circle
            cv2.circle(frame, (i[0], i[1]), 2, (0, 255, 0), 5)

        print(f"I found {len(circlesDraw[0])} circles")
        return frame
    else:
        print("no circles!")
        return None