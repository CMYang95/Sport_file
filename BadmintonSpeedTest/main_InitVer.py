import constants
from trackers import ball_predict
from court_line_detector import CourtLineDetector
from mini_court import MiniCourt
import cv2
from collections import deque 
import time
import math
import numpy as np

################################################################

IS_LABEL_MODE = False
IS_USING_AI_COURT_LINE_DETECTOR = True
# Because sometimes will fail when using CNN model

model_root = "D:/Lab/Project/# Taiwan-i-Sport/BadmintonSpeedTest/models/"
ball_model_path = model_root + "/model_best.pt"
court_model_path = model_root + "/keypoints_model.pth"

SPEED_SHOW_TIME = 5

################################################################

pX1, pY1 = 855, 400 # left-top corner
pX2, pY2 = 1046, 402 # right-top corner
pX3, pY3 = 674, 836 # left-bottom corner
pX4, pY4 = 1245, 824 # right-bottom corner

def OnMouseClick_PickPoints(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        colorsB  = param[y, x, 0]
        colorsG  = param[y, x, 1]
        colorsR  = param[y, x, 2]
        colorBGR = np.uint8([[[colorsB, colorsG, colorsR]]])
        print("HSV: ", cv2.cvtColor(colorBGR, cv2.COLOR_BGR2HSV))
        print("Position x = %d, y = %d" % (x, y))

def get_point_dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def get_ball_points(ball_detector, frames_list):
    ballpoints = ball_detector.predict(frames_list, 3)
    ballpoints = ball_detector.smooth(ballpoints)
    return ballpoints

def get_court_lines(court_line_detector, frames):
    if IS_USING_AI_COURT_LINE_DETECTOR: court_keypoints = court_line_detector.predict(frames)
    else: court_keypoints = [pX1, pY1, pX2, pY2, pX3, pY3, pX4, pY4]
    return court_keypoints

def main():
    cap = cv2.VideoCapture("D:/Lab/Project/tennis_analysis-main/input_videos/input_video.mp4")
    #cap = cv2.VideoCapture(0)
    #print(cap.get(cv2.CAP_PROP_FPS))
    
    cv2.namedWindow("test", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("test", 1280, 720)

    court_line_detector = CourtLineDetector(court_model_path)
    ball_detector = ball_predict.Ball_Detector(ball_model_path)

    QUE_L = 3
    frames = deque(maxlen=QUE_L)
    times = deque(maxlen=QUE_L)
    balls_pos = deque(maxlen=QUE_L)

    has_shown = False
    show_speed = 0

    handler, timer = False, 0

    while cap.isOpened():
        ret, frame = cap.read()
        if ret is False: break

        court_keypoints = get_court_lines(court_line_detector, frame)

        cv2.fillPoly(frame, 
                      [np.int32([(court_keypoints[0], court_keypoints[1]-25),
                       (court_keypoints[4], court_keypoints[5]),
                       (0, court_keypoints[5]),
                       (0, court_keypoints[1]-25)])], 
                       (0, 0, 0))
            
        cv2.fillPoly(frame, 
                      [np.int32([(court_keypoints[2], court_keypoints[3]-25),
                       (court_keypoints[6], court_keypoints[7]),
                       (frame.shape[1], court_keypoints[7]),
                       (frame.shape[1], court_keypoints[3]-25)])], 
                       (0, 0, 0))

        frames.append(frame)
        if len(times) > 0: t = times[0]
        else: t = time.time()
        times.append(time.time())

        if len(frames) == QUE_L:
            frames_list = list(frames)
            ballpoints = get_ball_points(ball_detector, frames_list)

            # MiniCourt
            mini_court = MiniCourt(frames_list[0])

            ############################### Draw output ################################

            ###  Draw Ballpoints ###
            output_video_frames = ball_detector.draw_ballpoints(frames, ballpoints)
            # print(len(ballpoints_frames))

            if not IS_LABEL_MODE:
                ### Draw court Keypoints ###
                keypoints_frames = []
                for frame in output_video_frames:
                    if IS_USING_AI_COURT_LINE_DETECTOR:
                        keypoints = court_line_detector.predict(frame)
                        keypoints_frames.append(keypoints)
                    else:
                        keypoints_frames.append(court_keypoints)
                output_video_frames = court_line_detector.draw_keypoints_on_video(output_video_frames, keypoints_frames)
                
                ### Draw Mini Court ###
                processedFrame, M = mini_court.courtMap(output_video_frames[0], 
                                                        (court_keypoints[0]-25,court_keypoints[1]-25), 
                                                        (court_keypoints[2],court_keypoints[3]-25), 
                                                        (court_keypoints[4],court_keypoints[5]), 
                                                        (court_keypoints[6],court_keypoints[7]))
                # map.append(processedFrame)
                
                map_ball = mini_court.showBallPoint(processedFrame.copy(), M, ballpoints[0])

                #print(ballpoints)
                if (ballpoints[0][0] > 0 and ballpoints[0][0] <= frames_list[0].shape[1]
                    and ballpoints[0][1] > 0 and ballpoints[0][1] <= frames_list[0].shape[0]):
                    ball_pos = mini_court.getBallPosOnMap()
                    #print(ball_pos)
                    ball_real_pos = (ball_pos[0] * mini_court.getMapToRealRatio()[0],
                                     ball_pos[1] * mini_court.getMapToRealRatio()[1])
                    balls_pos.append(ball_real_pos)

                    delta = 1 / cap.get(cv2.CAP_PROP_FPS)
                    #delta = times[0] - t
                    #print(delta)

                    if len(balls_pos) >= 2:
                        distance = round(get_point_dist(balls_pos[0], balls_pos[1]) * 100) / 100
                        speed = distance / delta # m/s
                        speed = round(speed / 1000 * 3600 * 100) / 100 # km/h

                        if (balls_pos[1][1] < balls_pos[0][1] or distance < 0.3
                            or speed == 0 or speed >= 300
                            or balls_pos[0][1] / mini_court.getMapToRealRatio()[1] > 300): 
                            can_show = False; has_shown = False
                        elif not has_shown: 
                            can_show = True

                        if can_show:
                            timer = 0
                            handler = True
                            show_speed = speed
                            print("Distance: ", distance, " meter, speed = ", speed, "km/h")
                            has_shown = True; can_show = False
                
                if handler:
                    cv2.putText(map_ball, 
                                "Velocity: {} km/h".format(show_speed),
                                (25,100),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 15) # border
                    cv2.putText(map_ball, 
                                "Velocity: {} km/h".format(show_speed),
                                (25,100),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 4)
                    timer += delta
                    #print(timer)
                    if timer >= SPEED_SHOW_TIME: handler = False 

                cv2.imshow("test", map_ball)

                if cv2.waitKey(1) & 0xFF == ord('z'): handler = False 

            else:
                cv2.imshow("test", output_video_frames[0])
                cv2.setMouseCallback("test", OnMouseClick_PickPoints, output_video_frames[0])
                

        if cv2.waitKey(1) & 0xFF == ord('q'): break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()