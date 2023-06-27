from matplotlib import pyplot as plt
import numpy as np
import time
import math
import random
import sys
import json
import picamera

import cv2

def find_single_point(frame, min_radius, max_radius):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    blur = cv2.medianBlur(gray, 5)

    # ~ pix = cv2.HoughCircles(blur,cv2.HOUGH_GRADIENT, 1.6, minDist=100, param1=100, param2=100)
    for g in np.arange(1, 5, 0.1):
        # find the right gain to find a single circle
        # change min/max radius based on your height
        pix = cv2.HoughCircles(blur,
                               cv2.HOUGH_GRADIENT,
                               g,
                               minDist=100,
                               param1=100,
                               param2=100,
                               minRadius=min_radius,
                               maxRadius=max_radius
                               )
        if pix is None:
            continue
        numCircles = pix[0,:].shape[0]
        if numCircles == 1:
            print(f"I used a gain of {g}")
            break

    if pix is None:
        print(f"I found no circles")
        return None
#     if pix is not None:
#         circlesDraw = np.uint16(np.around(pix))
#         circles = pix[0,:]

#         for i in circlesDraw[0,:]:
#             # draw the outer circle
#             print(f"the radius is: {i[2]}")
#             print(f"the center is: ({i[0]},{i[1]})")
#             cv2.circle(frame,(i[0], i[1]), i[2], (255, 0, 0), 5)
#             plt.imshow(frame)
#             plt.show()

    pix = pix[0,:]
    
    if pix.shape[0] != 1:
        print(f"I found {pix.shape[0]} circles")
        return None

    x,y = pix[0,0:2]
    size = frame.shape
    
    return (x / size[1]) - 0.5, (y / size[0]) - 0.5

    
    
def least_square_mapping(calibration_points):
    """Compute a 2x2 map from displacement vectors in screen space
    to real space. """
    n = len(calibration_points)
    print(f"there are {n} points")
    real_coords, pixel_coords = np.empty((n,2)),np.empty((n,2))
    
    for i, (r,p) in enumerate(calibration_points):
        real_coords[i] = r
        pixel_coords[i] = p
        
    x,y = pixel_coords[:,0],pixel_coords[:,1]
    A = np.vstack([x**2,y**2,x * y, x,y,np.ones(n)]).T
    transform = np.linalg.lstsq(A, real_coords, rcond = None)
    return transform[0], transform[1].mean()

def frame_getter(resolution, camera):

    def ret():
        output = np.empty((resolution[1], resolution[0], 3), dtype=np.uint8)
        camera.capture(output, 'rgb', use_video_port = True)
        mtx, dist = load_coefficients('/home/pi/duckbot/notebooks/calibration/calibration_checkerboard.yml')
        dst = cv2.undistort(output, mtx, dist, None, mtx)
        ## what if you just return ouput? not transpose?
        #return output # didnt seem to work...
        return np.transpose(dst, axes = (1,0,2)) # this was the original
        # what if we flip axis so +/- pixel coords match +/- machine coords?
        #return np.flip(output, axis=0)
    
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

    return ret


def collect_random_points(center, radius, evaluate_location, points = 30):

    for _ in range(points):
        target = 2 * radius * (np.random.rand(2) - 0.5) + center
        pxy = evaluate_location(target)

        if pxy is None:
            print(f"""CV failed at {target[0]}, {target[1]}""")
        else:
            print(f"""Data point: {target[0]},{target[1]} vs. {pxy[0]},{pxy[1]}""") 
            yield target, pxy

def collect_grid_points(transform, evaluate, border = 0.1, n = 5):
    for x in np.linspace(border - 0.5, 1 - border - 0.5, n):
        for y in np.linspace(border - 0.5 , 1 - border -0.5, n):
            v = np.array([x**2, y **2, x * y, x, y, 1.0])
            target = transform.T @ v
            print(target)
            # explicitly avoid collisions with frame/tools
            if (target[0] > 200 or target[0] < 20 or target[1] > 317 or target[1] < 50):
                print('skip')
                break
            pxy = evaluate(target)

            
            if pxy is None:
                print(f"""CV failed at {target[0]}, {target[1]}""")
            else:
                print(f"""Data point: {target[0]},{target[1]} vs. {pxy[0]},{pxy[1]}""") 
                yield target, pxy
            
def decorate_image(img):
    x,y,_ = img.shape
    
    # make some simple cross hairs too
    img[:, y //2,:] = 255, 0, 255
    img[x //2, :,:] = 255, 0, 255
    

def calibrate_camera_machine(m, focus_height, min_radius = 0, max_radius = 500):
    with picamera.PiCamera() as camera:
        camera.resolution = (1200,1200)
        camera.framerate = 24
        time.sleep(2)
        print("...camera connection established")

        frames = frame_getter(camera.resolution, camera)

        print("Moving to focus")
        m.moveTo(z=focus_height)

        radius = 10
        points = 20

        position = m.getPosition()
        print(f"position: {position}")
        xy = (float(position['X']), float(position['Y']))
        print(f"xy is {xy}")

        def evaluate_at_point(p):
            m.moveTo(x=p[0], y=p[1])
            print(f"x is {p[0]}, y is {p[1]}")
            return find_single_point(frames(), min_radius, max_radius)

        print("Begining rough pass")
        results = list(collect_random_points(xy, 5, evaluate_at_point))
        
        if len(results) < 10:
            print("Too many failures")
            exit()

        print(f"results so far: {results}")
        transform, residual = least_square_mapping(results)
        print("current transform")
        print(transform)


        # temporarily remove fine pass
        print("Begining fine pass")
        results += list(collect_grid_points(transform, evaluate_at_point))

        frame = frames()
        transform, residual = least_square_mapping(results)

        linear_part = transform[:-1,:]
        _,sigma,_ = np.linalg.svd(linear_part[-2:,:] @ np.diag([1 / frame.shape[0], 1 / frame.shape[1]]))


        # Write out the calibration data
        #trying without removing last element (transform[:-1,:])
        cal = {'bed_focus' : focus_height,
               'transform' : transform.tolist(),
               'resolution' : camera.resolution,
               'scale': [min(sigma),max(sigma)]}
        with open("camera_cal.json","w") as j:
            json.dump(cal, j)

        print("Calibration file writen to camera_cal.json")
         # Now move the centroid of the dot to the center of the screen,
        # take a snap, and write that out as a human-checkable certificate
        point = transform.T @ np.array([0, 0, 0, 0, 0, 1])
        print('this is where i would move to"')
        print(point)
        # m.move(point)
        # frame = frames()
        # decorate_image(frame)
        # fp = "cal_certificate.png"
        # print("Check image written to " + fp)
        #cv2.imwrite(fp,frame)

        # m.move(xy)


