import cv2
import numpy as np
from sklearn.cluster import KMeans
from collections import deque
from math import atan2, degrees
import math
import cvzone
from find_ball import FindBall
import socket
import threading
import matplotlib.pyplot as plt

pts_0 = deque(maxlen=3)
pts_1 = deque(maxlen=3)
Ypoint = deque(maxlen=128)
data = []
pointX = []
pointY = []
last_tennis_pos = None
serverIP = "127.0.0.1"
serverPort = 5055
# 設置網球場尺寸
length = 23.6
width = 10.94
text_x = -3
text_y = 4

def onmouse_pick_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print('\n像素坐標 x = %d, y = %d' % (x, y))

def receive_data():
    while True:
        data, address = sock2.recvfrom(1024)
        print(data)
        message = data.decode('utf-8')
        values = message.split(',')
        pointX.append(values[0])
        pointY.append(values[1])

knn = cv2.createBackgroundSubtractorKNN()
cap1=cv2.VideoCapture("D:/tennis/side2.mp4")
cap2=cv2.VideoCapture("D:/tennis/air2.mp4")

# width = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))    # 取得影像寬度
# height = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 取得影像高度
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('line.avi', fourcc, 20.0, (766,  826))

side1=(574,1076)

scales = 103.2727272727273 #pixel/公尺
side_scales = 0.0072916666666667
Zscales = 0.0104575163398693
Xscales = 0.0093696763202726
air_scales = 0.0261096605744125
air2_scales= 0.0130548302872063

left_find_ball = FindBall()
right_find_ball = FindBall()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5054)

sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddress = (serverIP, serverPort)
sock2.bind(serverAddress)
# fps1 = cap1.get(cv2.CAP_PROP_FPS)
# fps2 = cap2.get(cv2.CAP_PROP_FPS)
# start_frame1 = int(37 * fps1)
# start_frame2 = int(37 * fps2)

#     # 設置影片的當前幀
# cap1.set(cv2.CAP_PROP_POS_FRAMES, start_frame1)
# cap2.set(cv2.CAP_PROP_POS_FRAMES, start_frame2)
def capture_frames():
    while True:
        ret, frame1 = cap1.read()
        ret, frame2 = cap2.read()
        rows,cols = frame2.shape[:2]
        pts_o = np.float32([[549,414],[1266,398],[306,907],[1515,873]])
        pts_d = np.float32([[0,0],[766,0],[0,826],[766,826]])
        # pts_o = np.float32([[411,477],[1527,486],[204,976],[1731,983]])
        # pts_d = np.float32([[0,0],[766,0],[0,826],[766,826]])
        # pts_o = np.float32([[495,171],[1509,155],[249,821],[1761,826]])
        # pts_d = np.float32([[0,0],[766,0],[0,826],[766,826]])
        M = cv2.getPerspectiveTransform(pts_o, pts_d)
        dst = cv2.warpPerspective(frame2, M, (766, 826))
        q = isinstance(left_find_ball(frame1), list)
        if q == False:
            side_center = left_find_ball(frame1)
            air_center = right_find_ball(dst)

        if len(side_center) >= 1:
            side_tennis_x = side_center[0][1]
            side_tennis_y = side_center[0][0]
        if len(air_center) >= 1:
            air_tennis_x = air_center[0][1]
            air_tennis_y = air_center[0][0]
        if len(side_center) >= 1 and len(air_center) >= 1 and side_tennis_x > side1[0]:
                # frame1 = cv2.circle(frame1, side_center[0][::-1], 10, (0,0,225), -1)
                # dst = cv2.circle(dst, air_center[0][::-1], 10, (0,0,225), -1)
                pts_0.append([side_tennis_x,side_tennis_y])
                pts_1.append([air_tennis_x,air_tennis_y])
                Ypoint.append(side_tennis_y)
        elif q == True:
            pts_0.clear()
            pts_1.clear()
            data.clear()
            Ypoint.clear()
        # if len(side_center) >= 1 and len(air_center) >= 1 and side_tennis_x > side1[0] and len(pts_0) < 2 and len(pts_1) < 2:
                # if len(pts_0) > 1 and pts_0[0][0] < pts_0[1][0]:
                #         pts_0.popleft()
                #         pts_1.popleft()
        if len(pts_0) > 2 and len(pts_1) > 2 and pts_0[0][0] > pts_0[1][0] and pts_1[0][1] > pts_1[1][1]:
                side_start_point = pts_0[2]
                side_end_point = pts_0[0]
                air_start_point = pts_1[0]
                air_end_point = pts_1[2]
                speed_start_point = pts_1[0]
                speed_end_point = pts_1[1]
                side_y = side_end_point[1] - side_start_point[1]
                side_x = side_end_point[0] - side_start_point[0]
                # air_y = air_end_point[1] - air_start_point[1]
                # air_x = air_end_point[0] - air_start_point[0]
                air_y = air_start_point[1]-air_end_point[1]
                air_x = air_end_point[0]-air_start_point[0]
                speed_y = air_end_point[1] - air_start_point[1]
                speed_x = air_end_point[0] - air_start_point[0]
                ymin = max(Ypoint)
                startY = ((ymin - side_start_point[1]) ) + 0.05
                startY = startY * side_scales
                if startY < 1.2:
                    startY = 1.3
                startX = ((pts_1[0][1]) * (-Xscales)) -6.2
                if pts_1[0][0] >= 381 :
                    startZ = pts_1[0][0] * (-Zscales) + 4
                elif pts_1[0][0] < 380 :
                    startZ = pts_1[0][0] * Zscales - 4
                air_distance = math.dist(speed_end_point,speed_start_point)
                side_angle = degrees(atan2(side_y, side_x))
                air_angel = degrees(atan2(air_x, air_y))
                # print(air_angel)
                if air_angel < 0:
                    air_angel = air_angel+ ((pts_1[0][0]-383)*air_scales)
                elif air_angel > 0:
                    air_angel =  -air_angel 
                    # + ((pts_1[0][0]-383)*air_scales)
                time_diff = cap1.get(cv2.CAP_PROP_FPS)
                # velocity = move_distance * time_diff
                # speed_meters_per_second = velocity * scales
                velocity = (air_distance/scales)/(1/time_diff)
                # if  velocity > 80 :
                #     velocity = velocity / 2
                # elif velocity > 120:
                #     velocity = velocity / 3
                
                if len(data) < 1 and velocity > 15:
                    cv2.line(dst, (int(pts_1[0][0]),int(pts_1[0][1])), (int(pts_1[1][0]),int(pts_1[1][1])), (0, 0, 255), 5)
                    cv2.line(frame1, (int(pts_0[0][0]),int(pts_0[0][1])), (int(pts_0[1][0]),int(pts_0[1][1])), (0, 0, 255), 5)
                    print('side_角',side_angle)
                    print('air_角',air_angel)
                    print(f"球的速度為 {velocity:.2f} 公尺/秒")
                    print(startX,startY,startZ)
                    data.append([side_angle,air_angel,velocity,startX,startY,startZ])
                    # data = (side_angle,air_angel,velocity,startX,startY,startZ)
                    sock.sendto(str.encode(str(data)), serverAddressPort)
        # out.write(dst)
        cv2.namedWindow('frame1',0)
        cv2.resizeWindow('frame1', 640, 480)
        cv2.imshow('frame1',dst)
        cv2.namedWindow('frame2', 0)
        cv2.resizeWindow('frame2', 640, 480)
        cv2.imshow('frame2',frame1)
        # cv2.setMouseCallback('frame2', onmouse_pick_points)
            # imgStack = cvzone.stackImages([frame1, dst], 2, 0.4)
            # cv2.imshow("Image", imgStack)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.waitKey(0) 
        elif cv2.waitKey(100) & 0xff == ord('q'):
            break
receive_thread = threading.Thread(target=receive_data)
capture_thread = threading.Thread(target=capture_frames)
receive_thread.start()
capture_thread.start()
capture_thread.join()
sock2.close()

# imgStack = cvzone.stackImages([run_0(cap[0]), run_1(cap[1])], 2, 0.4)
# cv2.imshow("Image", imgStack)
# cv2.setMouseCallback('frame' + str(i), onmouse_pick_points)
cap1.release()
cap2.release()
cv2.destroyAllWindows()

# 設置圖形大小
plt.figure(figsize=(15, 20))

# 畫出場地線
plt.plot([0, length, length, 0, 0], [0, 0, width, width, 0], color='green')

# 畫出中央線
plt.plot([length/2, length/2], [0, width], color='black')

#單打線
plt.plot([length,0],[1.37,1.37],color='green')
plt.plot([length,0],[width-1.37,width-1.37],color='green')

#發球線
plt.plot([5.5,5.5],[0,width],color='green')
plt.plot([length-5.5,length-5.5],[0,width],color='green')

#中線
plt.plot([length-5.5,5.5],[width/2,width/2],color='green')

for i,j in zip(pointX,pointY):
    plt.scatter(length/2 + float(i),width/2 - float(j), color='Brown')
    print(length/2 + float(i),width/2 - float(j))
    
# 設置標籤和標題
plt.xlabel('Length (m)')
plt.ylabel('Width (m)')
plt.title('Tennis Court')
plt.gca().invert_xaxis()
# 顯示圖形
plt.show()

