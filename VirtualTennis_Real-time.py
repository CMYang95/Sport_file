import LoadWebcam

import cv2
import math
import numpy as np
from sklearn.cluster import KMeans
from imutils import perspective
from imutils import contours
from collections import deque
import socket

VIEW_NAMES = ["Side-View", "Overhead-View"]

cap1 = LoadWebcam.LoadWebcam(0, VIEW_NAMES[1])
cap2 = LoadWebcam.LoadWebcam(2, VIEW_NAMES[0])

# Unity IP and port
unitySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
unityAddressPort = ("127.0.0.1", 65522)

# 1080p maybe can't capture target
(CAP_W, CAP_H) = cap1.get_origin_shape() # 720p (1280x720), from openCV initialation
INIT_SCREEN_W, INIT_SCREEN_H = 720, 405
screenW, screenH = [INIT_SCREEN_W, INIT_SCREEN_W], [INIT_SCREEN_H, INIT_SCREEN_H]

COURT_W, COURT_H = 3.32, 3 # detection area, unit: meter
TENNIS_COURT_W, TENNIS_COURT_H = 10.97, 9.91 # detection area scale to tennis court, unit: meter
TRANSFORM_W, TRANSFORM_H = 664, 600 # for perspective transform
# real-world detection area is 3.32 meters x 3 meters, half-court area = 3.32 meter x 3.6 meter
# real-world tennis half-court area = 10.97 meters x 11.89 meters

IS_PERSPECTIVE_TRANSFORM_USED = True # TO-DO: perspective transform maybe have bug
DEBUG_MODE = True # show key frame and information
LABELING_POINT_MODE = False # get court line point or get hsv color
SHOW_OVERHEAD_CAM_ORIGIN = False if LABELING_POINT_MODE == True else (False) # modify the value int ()
# overhead
pX1, pY1 = 308, 69 # left-top corner
pX2, pY2 = 1012, 73 # right-top corner
pX3, pY3 = 89, 654 # left-bottom corner
pX4, pY4 = 1209, 667 # right-bottom corner
# side
pX1s, pY1s = 315, 640 # left-top corner
pX2s, pY2s = 496, 487 # right-top corner
pX3s, pY3s = 994, 628 # left-bottom corner
pX4s, pY4s = 798, 478 # right-bottom corner

# perspective transform angle offset
OVERHEAD_CAM_GAMMA = 45 # real measurement, it's approximate value
OVERHEAD_CAM_F = 26 / 1000 # unit: mini-meter to meter 
SIDE_CAM_F = 25 / 1000 # unit: mini-meter to meter

# scales
COURT_W_SCALE, COURT_H_SCALE = TENNIS_COURT_W / COURT_W, TENNIS_COURT_H / COURT_H
METERS_PER_PIXEL_X_FOR_SIDE = COURT_H / ((math.dist((pX1s, pY1s), (pX3s, pY3s)) 
                                      + math.dist((pX2s, pY2s), (pX4s, pY4s))) / 2)
# 1.7 is person's height (assume), 400 is person's pixel length (approximately)
METERS_PER_PIXEL_Y = 1.7 / 280 
if IS_PERSPECTIVE_TRANSFORM_USED:
    METERS_PER_PIXEL_X_FOR_OVERHEAD = COURT_H / TRANSFORM_H
    METERS_PER_PIXEL_Z = COURT_W / TRANSFORM_W
else:
    METERS_PER_PIXEL_X_FOR_OVERHEAD = COURT_H / math.dist((pX1 * math.cos(math.radians(OVERHEAD_CAM_GAMMA)), 
                                                           pY1 * math.cos(math.radians(OVERHEAD_CAM_GAMMA))), 
                                                          (pX3 * math.cos(math.radians(OVERHEAD_CAM_GAMMA)), 
                                                           pY3 * math.cos(math.radians(OVERHEAD_CAM_GAMMA))))
    METERS_PER_PIXEL_Z = COURT_W / math.dist((pX3 * math.cos(math.radians(OVERHEAD_CAM_GAMMA)), 
                                              pY3 * math.cos(math.radians(OVERHEAD_CAM_GAMMA))), 
                                             (pX4 * math.cos(math.radians(OVERHEAD_CAM_GAMMA)), 
                                              pY4 * math.cos(math.radians(OVERHEAD_CAM_GAMMA))))
# calculate the angle offset of left line and right line
# using 3 lines' slope to get
SLOPE_L = (pY1 - pY3) / (pX1 - pX3)
SLOPE_R = (pY2 - pY4) / (pX2 - pX4)
SLOPE_B = (pY3 - pY4) / (pX3 - pX4)
ANGLE_OFFSET_Z_L = (90 + math.degrees(
    math.atan((SLOPE_L - SLOPE_B) / (1 + SLOPE_L * SLOPE_B))
    )) / (math.dist((pX3, pY3), (pX4, pY4)))
ANGLE_OFFSET_Z_R = (90 - math.degrees(
    math.atan((SLOPE_R - SLOPE_B) / (1 + SLOPE_R * SLOPE_B))
    )) / (math.dist((pX3, pY3), (pX4, pY4)))
EXAMINE_LINE_POINT_X = pX1s + int(math.dist((pX1s, 0), (pX2s, 0)) * .4) # for side-view

'''fourcc = cv2.VideoWriter_fourcc(*'XVID')
sideOut = cv2.VideoWriter('E:/Project/Capstone Project/Tennins Simulator/Project/New folder/side.mp4', fourcc, 20.0, (INIT_SCREEN_W,  INIT_SCREEN_H))
overheadOut = cv2.VideoWriter('E:/Project/Capstone Project/Tennins Simulator/Project/New folder/overhead.mp4', fourcc, 20.0, (TRANSFORM_W,  TRANSFORM_H))
'''
def OnMouseClick_PickPoints(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        colorsB  = param[y, x, 0]
        colorsG  = param[y, x, 1]
        colorsR  = param[y, x, 2]
        colorBGR = np.uint8([[[colorsB, colorsG, colorsR]]])
        print("HSV: ", cv2.cvtColor(colorBGR, cv2.COLOR_BGR2HSV))
        print("Position x = %d, y = %d" % (x, y))

def GetMidPoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def FilterHSV(img, viewName):
    # convert BGR to HSV
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # the range of tennis' color
    #lower_color = (30,120,130)
    #upper_color = (60,255,255)

    if viewName == VIEW_NAMES[1]: # overhead view
        lower_color = (30, 60, 180)
        upper_color = (85, 255, 255)  
    else: # side view
        lower_color = (30, 70, 150)
        upper_color = (80, 255, 255) 

    # find color
    mask_img = cv2.inRange(hsv_img, lower_color, upper_color)
    return mask_img

def GetMask(hsv_mask, fg_mask):
    mask1 = hsv_mask == 255
    mask2 = fg_mask == 255
    out = np.zeros(hsv_mask.shape)
    out[mask1 & mask2] = 255
    out = np.array(out, np.uint8)
    return out

kernel = np.ones((2, 2), np.uint8)

def DilateImg(img):
    return cv2.dilate(img, None, iterations=2)

def ErodeImg(img):
    return cv2.erode(img, None, iterations=2)

def k_means(img):
    point = np.array(np.where(img == 255))
    point = point.T
    if len(point) != 0:
        kmeans = KMeans(n_clusters=4)
        kmeans.fit(point)
        return kmeans.cluster_centers_
    else:
        return None

def Run(cap, viewName, k):
    global screenW, screenH, isCalculating
    global sideYpoints
    
    startT = cv2.getTickCount() # get processing start time
    frame = next(cap)

    if viewName == VIEW_NAMES[1]: # Overhead view
        #overheadOut.write(frame)

        # perspective transform
        if IS_PERSPECTIVE_TRANSFORM_USED:
            pts_o = np.float32([[pX1, pY1], [pX2, pY2], [pX3, pY3], [pX4, pY4]])
            pts_d = np.float32([[0, 0], [TRANSFORM_W, 0], [0, TRANSFORM_H], [TRANSFORM_W, TRANSFORM_H]])
            M = cv2.getPerspectiveTransform(pts_o, pts_d)
            dst = cv2.warpPerspective(frame, M, (TRANSFORM_W, TRANSFORM_H))

        if SHOW_OVERHEAD_CAM_ORIGIN: # draw court line
            cv2.line(frame, (pX2, pY2), (pX4, pY4), (255, 0, 255), 5)
            cv2.line(frame, (pX1, pY1), (pX3, pY3), (255, 0, 255), 5)
            cv2.line(frame, (pX3, pY3), (pX4, pY4), (255, 0, 255), 5)
            cv2.line(frame, (pX1, pY1), (pX2, pY2), (255, 0, 255), 5)
            UpdateWindows(f"{viewName} Origin", frame)

        if not LABELING_POINT_MODE: 
            if IS_PERSPECTIVE_TRANSFORM_USED:
                frame = dst
                screenW[1], screenH[1] = TRANSFORM_W, TRANSFORM_H 
            pass
        else:
            if IS_PERSPECTIVE_TRANSFORM_USED:
                cv2.namedWindow(f"{viewName} Transform", 0)
                cv2.resizeWindow(f"{viewName} Transform", TRANSFORM_W, TRANSFORM_H)
                cv2.imshow(f"{viewName} Transform", dst)
                cv2.setMouseCallback(f"{viewName} Transform", OnMouseClick_PickPoints, dst)
        sW, sH = screenW[1], screenH[1]

    else: # Side view
        #sideOut.write(frame)

        if not LABELING_POINT_MODE: # draw court line
            cv2.line(frame, (pX2s, pY2s), (pX4s, pY4s), (255, 0, 255), 5)
            cv2.line(frame, (pX1s, pY1s), (pX3s, pY3s), (255, 0, 255), 5)
            cv2.line(frame, (pX3s, pY3s), (pX4s, pY4s), (255, 0, 255), 5)
            cv2.line(frame, (pX1s, pY1s), (pX2s, pY2s), (255, 0, 255), 5)

        sW, sH = screenW[0], screenH[0]
    
    # pre-processing
    # background substraction
    fgmask1 = k.apply(frame)
    fgmask1 = cv2.medianBlur(fgmask1, 5)
    fgmask = ErodeImg(fgmask1)

    # hsv filter, then AND
    # find the tennis ball
    hsv_mask = FilterHSV(frame, viewName)
    mask = cv2.bitwise_and(fgmask, hsv_mask)
    ret, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    mask_dilate = DilateImg(DilateImg(DilateImg(mask)))

    # draw the contours of the tennis balls
    cnt, _ = cv2.findContours(mask_dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnt) > 0:
        tmp = frame.copy()
        (cnt, _) = contours.sort_contours(cnt)
        for (i, c) in enumerate(cnt):
            box = cv2.minAreaRect(c)
            box = cv2.boxPoints(box)
            box = box.astype("int")
            box = perspective.order_points(box)
            cv2.drawContours(frame, [box.astype(int)], 0, (0, 255, 0), 2)
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = GetMidPoint(tl, tr)
            (tlblX, tlblY) = GetMidPoint(tl, bl)
            (blbrX, blbrY) = GetMidPoint(bl, br)
            (trbrX, trbrY) = GetMidPoint(tr, br)
            cv2.line(frame, (int(tltrX), int(tltrY)),
                    (int(blbrX), int(blbrY)), (255, 0, 0), 2)
            cv2.line(frame, (int(tlblX), int(tlblY)),
                    (int(trbrX), int(trbrY)), (255, 0, 0), 2)

            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
        endTs = cv2.getTickCount() / cv2.getTickFrequency()
        if viewName == VIEW_NAMES[1]: # Overhead view
            if DEBUG_MODE: overheadPointsAndTimestamps.append([center, endTs, frame])
            else: overheadPointsAndTimestamps.append([center, endTs])
        else: # Side view
            if DEBUG_MODE: sidePointsAndTimestamps.append([center, endTs, frame])
            else: sidePointsAndTimestamps.append([center, endTs])

            sideYpoints.append(center[1])

            if center[0] <= EXAMINE_LINE_POINT_X: 
                # clear deque: when the ball was passed examineLine 
                sidePointsAndTimestamps.clear()
                overheadPointsAndTimestamps.clear()
                sideYpoints.clear()
                isCalculating = False
                frame = tmp
    else: 
        # clear deque: when the ball was vanished
        sidePointsAndTimestamps.clear()
        overheadPointsAndTimestamps.clear()
        sideYpoints.clear()
        isCalculating = False

    '''tickCount = cv2.getTickCount() - startT # get processing end time, then get secs
    fps = 1 // (tickCount / cv2.getTickFrequency())
    cv2.putText(frame, "FPS: " + str(fps), (50, 50)
                , cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)'''
    
    if viewName == VIEW_NAMES[0] and not LABELING_POINT_MODE and DEBUG_MODE:
        cv2.line(frame, (EXAMINE_LINE_POINT_X, 0)
                 , (EXAMINE_LINE_POINT_X, CAP_H), (0, 255, 255), 5) # examineLine
    UpdateWindows(viewName, frame, sW, sH)

    if LABELING_POINT_MODE:
        cv2.setMouseCallback(viewName, OnMouseClick_PickPoints, frame)

isCalculating = False
id = 0
def calculatePhysics():
    global isCalculating, id, screenW, screenH
    global sideYpoints

    #print("side:", sidePointsAndTimestamps)
    #print("overhead:", overheadPointsAndTimestamps)

    if len(sidePointsAndTimestamps) > 1 and len(overheadPointsAndTimestamps) > 1: # has three balls frame
        sidePoints, overheadPoints = [], []
        sideTimestamps, overheadTimestamps = [], []
        if DEBUG_MODE: sideFrames, overheadFrames = [], []
        for i in range(len(sidePointsAndTimestamps)):
            sidePoints.append(sidePointsAndTimestamps[i][0])
            overheadPoints.append(overheadPointsAndTimestamps[i][0])
            sideTimestamps.append(sidePointsAndTimestamps[i][1])
            overheadTimestamps.append(overheadPointsAndTimestamps[i][1])
            if DEBUG_MODE:
                sideFrames.append(sidePointsAndTimestamps[i][2])
                overheadFrames.append(overheadPointsAndTimestamps[i][2])

        # using 3 frame maybe have bug
        if ((sidePoints[0][0] > sidePoints[1][0])
            #and sidePoints[1][0] > sidePoints[2][0])  # side: X0 > X1 > X2 (when closeing right, X is better)
            and (overheadPoints[0][1] > overheadPoints[1][1])):
            #and overheadPoints[1][1] > overheadPoints[2][1])): # overhead: Y0 > Y1 > Y2 (when closeing bottom, Y is better)
            
            if not isCalculating:
                isCalculating = True
                
                # remain image coordinates
                sideStartPointCV = sidePoints[0]
                sideEndPointCV = sidePoints[1]
                overheadStartPointCV = overheadPoints[0]
                overheadEndPointCV = overheadPoints[1]

                # normalization x-y coordinates in images
                sideStartPoint = [-(sidePoints[0][0] - CAP_W), -(sidePoints[0][1] - CAP_H)]
                sideEndPoint = [-(sidePoints[1][0] - CAP_W), -(sidePoints[1][1] - CAP_H)]
                overheadStartPoint = [overheadPoints[0][0] * math.cos(math.radians(OVERHEAD_CAM_GAMMA)),
                                       -(overheadPoints[0][1] - screenH[1])]
                overheadEndPoint = [overheadPoints[1][0] * math.cos(math.radians(OVERHEAD_CAM_GAMMA)),
                                     -(overheadPoints[1][1] - screenH[1])]

                # perspective transform maybe have bug
                overheadO = [0, 0]
                if not IS_PERSPECTIVE_TRANSFORM_USED:
                    overheadO = [pX3 * math.cos(math.radians(OVERHEAD_CAM_GAMMA)),
                                -(pY3 - screenH[1])]

                # find start point (X-Y-Z) for 3D
                oY = -(max(sideYpoints) - CAP_H) # landing point as origin point for 3D
                startY = (sideStartPoint[1] - oY) * METERS_PER_PIXEL_Y * (0.302)
                startX = (overheadStartPoint[1] - overheadO[1]) * METERS_PER_PIXEL_X_FOR_OVERHEAD #* COURT_W_SCALE
                startZ = (overheadStartPoint[0] - overheadO[0]) * METERS_PER_PIXEL_Z #* COURT_H_SCALE
                #print(startX, startY, startZ)

                if startY == 0:
                    startY = 0.302 # sometime can't get Y

                # get angle
                sideX_dist = sideEndPoint[0] - sideStartPoint[0]
                sideY_dist = sideEndPoint[1] - sideStartPoint[1]
                overheadX_dist = overheadEndPoint[0] - overheadStartPoint[0]
                overheadY_dist = overheadEndPoint[1] - overheadStartPoint[1]
                sideAngle = math.degrees(math.atan2(sideY_dist, sideX_dist))
                overheadAngle = math.degrees(math.atan2(overheadX_dist, overheadY_dist))
                # angle offset
                if overheadAngle > 0:
                    overheadAngle += (ANGLE_OFFSET_Z_R 
                                      * ((overheadEndPointCV[0] - overheadStartPointCV[0])
                                          + ((math.dist((pX3, pY3), (pX4, pY4))) - overheadEndPointCV[0]))) #- OVERHEAD_CAM_GAMMA
                    #if overheadAngle >= 180: overheadAngle -= 180
                elif overheadAngle < 0:
                    overheadAngle -= (ANGLE_OFFSET_Z_L 
                                      * ((overheadStartPointCV[0] - overheadEndPointCV[0])
                                         + (overheadEndPointCV[0]))) #+ OVERHEAD_CAM_GAMMA
                    #if overheadAngle <= -180: overheadAngle += 180

                

                #print("side:", sideAngle)
                #print("overhead:", overheadAngle)

                # get initial velocity
                sideProjDist = math.dist(sideEndPoint, sideStartPoint) * METERS_PER_PIXEL_X_FOR_SIDE
                sideProjDist_X = sideProjDist * math.cos(math.radians(sideAngle))
                overheadProjDist = math.dist(overheadEndPoint, overheadStartPoint) * METERS_PER_PIXEL_X_FOR_OVERHEAD
                sideDist = sideProjDist_X / math.cos(math.radians(overheadAngle))
                overheadDist = overheadProjDist / math.cos(math.radians(sideAngle))
                dist = (sideDist + overheadDist) / 2
                sideTimeDiff = sideTimestamps[1] - sideTimestamps[0]
                overheadTimeDiff = overheadTimestamps[1] - overheadTimestamps[0]
                timeDiff = (sideTimeDiff + overheadTimeDiff) / 2
                v = dist / timeDiff
                '''print(f"SideDist: {round(sideDist, 2)}", 
                      f"OverheadDist: {round(overheadDist, 2)}",
                      f"Dist: {round(dist, 2)}",
                      f"SideTimeDiff: {round(sideTimeDiff, 2)}",
                      f"OverheadTimeDiff: {round(overheadTimeDiff, 2)}")'''

                '''sideVelocities, overheadVelocities = [], []
                for i in range(1):
                    sideDist = math.dist(sideEndPoint, sideStartPoint) * METERS_PER_PIXEL_X_FOR_SIDE * COURT_H_SCALE
                    overheadDist = math.dist(overheadEndPoint, overheadStartPoint) * METERS_PER_PIXEL_X_FOR_OVERHEAD * COURT_H_SCALE
                    sideTimeDiff = sideTimestamps[1] - sideTimestamps[0]
                    overheadTimeDiff = overheadTimestamps[1] - overheadTimestamps[0]
                    sideV = sideDist / sideTimeDiff
                    overheadV = overheadDist / overheadTimeDiff
                    sideVelocities.append(sideDist / sideTimeDiff)
                    overheadVelocities.append(overheadDist / overheadTimeDiff)
                # use 2 velocity's average as inital velocity
                sideV = sum(sideVelocities) / 2
                overheadV = sum(overheadVelocities) / 2
                #print("init velocity:", v, "m/s =", sideDist, "/", timeDiff)'''

                # draw line and information to check
                if DEBUG_MODE:
                    tmp1, tmp2 = sideFrames[1], overheadFrames[1]
                    cv2.line(tmp1, sideStartPointCV, sideEndPointCV, (0, 0, 255), 5)
                    cv2.line(tmp2, overheadStartPointCV, overheadEndPointCV, (0, 0, 255), 5)
                    tmp1 = cv2.addWeighted(sideFrames[0], 0.35, tmp1, 0.65, 0)
                    tmp2 = cv2.addWeighted(overheadFrames[0], 0.35, tmp2, 0.65, 0)
                    cv2.putText(tmp1, f"X-Y Angle: {round(sideAngle, 5)} degree"
                                , (50, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                    cv2.putText(tmp1, f"Velocity: {round(v, 5)} m/s"
                                , (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                    cv2.putText(tmp1, f"({round(startX, 2)}, {round(startY, 2)}, {round(startZ, 2)})"
                                , (sideStartPointCV[0] if sideStartPointCV[0] + 300 < CAP_W else sideStartPointCV[0] - 300
                                   , sideStartPointCV[1] + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 255, 255), 2)
                    if IS_PERSPECTIVE_TRANSFORM_USED:
                        cv2.putText(tmp2, f"X-Z Angle: {round(overheadAngle, 5)} degree"
                                    , (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        cv2.putText(tmp2, f"Velocity: {round(v, 5)} m/s"
                                    , (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        cv2.putText(tmp2,  f"({round(startX, 2)}, {round(startY, 2)}, {round(startZ, 2)})"
                                    , (((overheadStartPointCV[0] - 110 if overheadStartPointCV[0] - 125 > 0 else overheadStartPointCV[0])
                                        if overheadStartPointCV[0] + 125 < TRANSFORM_W else overheadStartPointCV[0] - 225)
                                    , (overheadStartPointCV[1] + 25 if overheadStartPointCV[1] + 40 < TRANSFORM_H else overheadStartPointCV[1] - 20))
                                    , cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 255, 255), 2)
                    else:
                        cv2.putText(tmp2, f"X-Z Angle: {round(overheadAngle, 5)} degree"
                                , (50, 75), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                        cv2.putText(tmp2, f"Velocity: {round(v, 5)} m/s"
                                    , (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                        cv2.putText(tmp2,  f"({round(startX, 2)}, {round(startY, 2)}, {round(startZ, 2)})"
                                    , ((overheadStartPointCV[0] if overheadStartPointCV[0] + 300 < CAP_W else overheadStartPointCV[0] - 300)
                                    , (overheadStartPointCV[1] + 25 if overheadStartPointCV[1] + 40 < CAP_H else overheadStartPointCV[1] - 20))
                                    , cv2.FONT_HERSHEY_SIMPLEX, 2, (128, 255, 255), 3)
                    UpdateWindows(f"{VIEW_NAMES[0]} Line", tmp1, int(screenW[0] / 1.5), int(screenH[0] / 1.5))
                    UpdateWindows(f"{VIEW_NAMES[1]} Line", tmp2, int(screenW[1] / 1.5), int(screenH[1] / 1.5))
                    cv2.imwrite(f"E:/Project/Capstone Project/Tennins Simulator/Project/New folder/Frame/{id}_{VIEW_NAMES[0]}.jpg", tmp1)
                    cv2.imwrite(f"E:/Project/Capstone Project/Tennins Simulator/Project/New folder/Frame/{id}_{VIEW_NAMES[1]}.jpg", tmp2)
                    id += 1

                #v = (overheadV if overheadV > sideV else sideV)
                return [sideAngle, overheadAngle, v, startX, startY, startZ]
        
    return []

def UpdateWindows(viewName, f, w=INIT_SCREEN_W, h=INIT_SCREEN_H):
    cv2.namedWindow(viewName, 0)
    cv2.resizeWindow(viewName, w, h)
    cv2.imshow(viewName, f)

if __name__ == "__main__":
    knn1 = cv2.createBackgroundSubtractorKNN()
    knn2 = cv2.createBackgroundSubtractorKNN()

    cap1.start()
    cap2.start()

    sidePointsAndTimestamps = deque(maxlen=2)
    overheadPointsAndTimestamps = deque(maxlen=2)
    sideYpoints = deque(maxlen=128) # for tracking Y point to find origin point

    while(True):
        try:
            Run(cap1, VIEW_NAMES[0], knn1)
            Run(cap2, VIEW_NAMES[1], knn2)

            if not LABELING_POINT_MODE:
                params = calculatePhysics()
                if len(params) > 0:
                    print(params)
                    unitySocket.sendto(str.encode(str(params)), unityAddressPort)
                    # clear deque: when the ball was vanished
                    sidePointsAndTimestamps.clear()
                    overheadPointsAndTimestamps.clear()
                    sideYpoints.clear()

            keycode = cv2.waitKey(1)
            if keycode == ord("q"): break
            if keycode == ord("a"): # testing
                unitySocket.sendto(str.encode(str([9, -13.59, 12, 1.36, 0.3, 2.51])), unityAddressPort)
        except Exception as error:
            print("An exception occurred:", error)
            break

    cap1.stop()
    cap2.stop()
    #sideOut.release()
    #overheadOut.release()
    cv2.destroyAllWindows()

# 造成誤差的因素（不考慮硬體因素）：
# 1. 俯視角並非完全俯視而是有角度，需想辦法轉換
# （除透視變換外，還須搭配其他轉換方法）
# 且透視變換的角度，越靠近邊線拉扯越嚴重。
# 2. 兩相機之三維重構的座標，沒有標準化(?)。
# 可掌握之硬體因素：
# 1. 兩台相機不同步。