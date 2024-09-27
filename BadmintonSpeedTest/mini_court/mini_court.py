import cv2
import numpy as np
import sys
sys.path.append('../')
import constants
from utils import (
    convert_meters_to_pixel_distance,
    convert_pixel_distance_to_meters,
    get_foot_position,
    get_closest_keypoint_index,
    get_height_of_bbox,
    measure_xy_distance,
    get_center_of_bbox,
    measure_distance
)

class MiniCourt():
    def __init__(self,frame):
        self.drawing_rectangle_width = 250
        self.drawing_rectangle_height = 500
        self.buffer = 100
        self.padding_court=20

        self.set_canvas_background_box_position(frame)
        self.set_mini_court_position()
        self.set_court_drawing_key_points()
        self.getMapToRealRatio()


    def convert_meters_to_pixels(self, meters):
        return convert_meters_to_pixel_distance(meters,
                                                constants.DOUBLE_LINE_WIDTH,
                                                self.court_drawing_width
                                            )
    ###Now using###
    def set_court_drawing_key_points(self):
        if constants.IS_TENNIS:
            drawing_key_points = [0]*28
            
            # point 0 
            drawing_key_points[0] , drawing_key_points[1] = int(self.court_start_x), int(self.court_start_y)
            # point 1
            drawing_key_points[2] , drawing_key_points[3] = int(self.court_end_x), int(self.court_start_y)
            # point 2
            drawing_key_points[4] = int(self.court_start_x)
            drawing_key_points[5] = self.court_start_y + self.convert_meters_to_pixels(constants.HALF_COURT_LINE_HEIGHT*2)
            # point 3
            drawing_key_points[6] = drawing_key_points[0] + self.court_drawing_width
            drawing_key_points[7] = drawing_key_points[5] 
            # #point 4
            drawing_key_points[8] = drawing_key_points[0] +  self.convert_meters_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
            drawing_key_points[9] = drawing_key_points[1] 
            # #point 5
            drawing_key_points[10] = drawing_key_points[4] + self.convert_meters_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
            drawing_key_points[11] = drawing_key_points[5] 
            # #point 6
            drawing_key_points[12] = drawing_key_points[2] - self.convert_meters_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
            drawing_key_points[13] = drawing_key_points[3] 
            # #point 7
            drawing_key_points[14] = drawing_key_points[6] - self.convert_meters_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
            drawing_key_points[15] = drawing_key_points[7] 
            # #point 8
            drawing_key_points[16] = drawing_key_points[8] 
            drawing_key_points[17] = drawing_key_points[9] + self.convert_meters_to_pixels(constants.NO_MANS_LAND_HEIGHT)
            # # #point 9
            drawing_key_points[18] = drawing_key_points[16] + self.convert_meters_to_pixels(constants.SINGLE_LINE_WIDTH)
            drawing_key_points[19] = drawing_key_points[17] 
            # #point 10
            drawing_key_points[20] = drawing_key_points[10] 
            drawing_key_points[21] = drawing_key_points[11] - self.convert_meters_to_pixels(constants.NO_MANS_LAND_HEIGHT)
            # # #point 11
            drawing_key_points[22] = drawing_key_points[20] +  self.convert_meters_to_pixels(constants.SINGLE_LINE_WIDTH)
            drawing_key_points[23] = drawing_key_points[21] 
            # # #point 12
            drawing_key_points[24] = int((drawing_key_points[16] + drawing_key_points[18])/2)
            drawing_key_points[25] = drawing_key_points[17] 
            # # #point 13
            drawing_key_points[26] = int((drawing_key_points[20] + drawing_key_points[22])/2)
            drawing_key_points[27] = drawing_key_points[21] 
        else:
            drawing_key_points = [0]*40

            # point 0 
            drawing_key_points[0] , drawing_key_points[1] = int(self.court_start_x), int(self.court_start_y)
            # point 1
            drawing_key_points[2] , drawing_key_points[3] = int(self.court_end_x), int(self.court_start_y)
            # point 2
            drawing_key_points[4] = int(self.court_start_x)
            drawing_key_points[5] = self.court_start_y + self.convert_meters_to_pixels(constants.HALF_COURT_LINE_HEIGHT*2)
            # point 3
            drawing_key_points[6] = drawing_key_points[0] + self.court_drawing_width
            drawing_key_points[7] = drawing_key_points[5] 
            # #point 4
            drawing_key_points[8] = drawing_key_points[0] +  self.convert_meters_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
            drawing_key_points[9] = drawing_key_points[1] 
            # #point 5
            drawing_key_points[10] = drawing_key_points[4] + self.convert_meters_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
            drawing_key_points[11] = drawing_key_points[5] 
            # #point 6
            drawing_key_points[12] = drawing_key_points[2] - self.convert_meters_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
            drawing_key_points[13] = drawing_key_points[3] 
            # #point 7
            drawing_key_points[14] = drawing_key_points[6] - self.convert_meters_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
            drawing_key_points[15] = drawing_key_points[7] 
            # #point 8
            drawing_key_points[16] = drawing_key_points[0]
            drawing_key_points[17] = drawing_key_points[9] + self.convert_meters_to_pixels(constants.NO_MANS_LAND_HEIGHT)
            # # #point 9
            drawing_key_points[18] = drawing_key_points[2]
            drawing_key_points[19] = drawing_key_points[17] 
            # #point 10
            drawing_key_points[20] = drawing_key_points[0] 
            drawing_key_points[21] = drawing_key_points[11] - self.convert_meters_to_pixels(constants.NO_MANS_LAND_HEIGHT)
            # # #point 11
            drawing_key_points[22] = drawing_key_points[2]
            drawing_key_points[23] = drawing_key_points[21] 
            # # #point 12
            drawing_key_points[24] = int((drawing_key_points[16] + drawing_key_points[18])/2)
            drawing_key_points[25] = drawing_key_points[17] 
            # # #point 12-1
            drawing_key_points[26] = int((drawing_key_points[0] + drawing_key_points[2])/2)
            drawing_key_points[27] = drawing_key_points[1] 
            # # #point 13
            drawing_key_points[28] = int((drawing_key_points[20] + drawing_key_points[22])/2)
            drawing_key_points[29] = drawing_key_points[21]
            # # #point 13-1
            drawing_key_points[30] = int((drawing_key_points[4] + drawing_key_points[6])/2)
            drawing_key_points[31] = drawing_key_points[5] 

            drawing_key_points[32] = drawing_key_points[4]
            drawing_key_points[33] = drawing_key_points[5] - self.convert_meters_to_pixels(constants.DOUBLE_BOTTOM_DIFFERENCE)

            drawing_key_points[34] = drawing_key_points[6]
            drawing_key_points[35] = drawing_key_points[7] - self.convert_meters_to_pixels(constants.DOUBLE_BOTTOM_DIFFERENCE)

            drawing_key_points[36] = drawing_key_points[0]
            drawing_key_points[37] = drawing_key_points[1] + self.convert_meters_to_pixels(constants.DOUBLE_BOTTOM_DIFFERENCE)

            drawing_key_points[38] = drawing_key_points[2]
            drawing_key_points[39] = drawing_key_points[3] + self.convert_meters_to_pixels(constants.DOUBLE_BOTTOM_DIFFERENCE)

        self.drawing_key_points=drawing_key_points

    def set_mini_court_position(self):
        self.court_start_x = self.start_x + self.padding_court
        self.court_start_y = self.start_y + self.padding_court
        self.court_end_x = self.end_x - self.padding_court
        self.court_end_y = self.end_y - self.padding_court
        self.court_drawing_width = self.court_end_x - self.court_start_x

    def set_canvas_background_box_position(self,frame):
        frame= frame.copy()

        self.end_x = frame.shape[1] - self.buffer
        self.end_y = self.buffer + self.drawing_rectangle_height
        self.start_x = self.end_x - self.drawing_rectangle_width
        self.start_y = self.end_y - self.drawing_rectangle_height

    
    
    ###Now using###
    def courtMap(self,frame, top_left, top_right, bottom_left, bottom_right):

        shapes = np.zeros_like(frame, dtype=np.uint8)
        pts1 = np.float32([[top_left, top_right, bottom_left, bottom_right]])
        pts2 = np.float32([[self.start_x ,self.start_y ], [self.end_x ,self.start_y ], [self.start_x ,self.end_y ], [self.end_x ,self.end_y ]])
        M = cv2.getPerspectiveTransform(pts1,pts2)
        # 在 shapes 上繪製填滿的多邊形，以保留四個點的區域
        cv2.fillPoly(shapes, np.array([[[self.start_x ,self.start_y ], [self.end_x ,self.start_y ], [self.start_x ,self.end_y ], [self.end_x ,self.end_y ]]], dtype=np.int32), (255, 255, 255))

        # 使用遮罩來保留 processedFrame 中四個點的區域，並將其餘部分設置為黑色
        result = cv2.bitwise_and(frame, shapes)

        # result 將只包含 processedFrame 中四個點的區域，其餘部分為黑色
        dst = cv2.warpPerspective(result,M,(result.shape[1],result.shape[0]))
        
        cv2.rectangle(dst, (self.start_x,self.start_y),(self.end_x,self.end_y),(5,5,5),cv2.FILLED)
        # cv2.circle(dst, (100,100),5, (0,97,255),-1)

        # cv2.imshow('processedFrame', dst)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        combined_frame=frame.copy()

        mask = dst.astype(bool)

        combined_frame[mask] = cv2.addWeighted(frame, 0.5, dst, 0.5, 0)[mask]
        
        
        cv2.rectangle(combined_frame, (self.court_start_x,self.court_start_y), (self.court_end_x,self.court_end_y), (255, 255, 255), 2)
        
        if constants.IS_TENNIS:
            cv2.line(combined_frame, (int(self.drawing_key_points[8] ),int(self.drawing_key_points[9])), (int(self.drawing_key_points[10]) ,int(self.drawing_key_points[11])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[12]) ,int(self.drawing_key_points[13])), (int(self.drawing_key_points[14]) ,int(self.drawing_key_points[15])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[16]) ,int(self.drawing_key_points[17])), (int(self.drawing_key_points[18]) ,int(self.drawing_key_points[19])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[20]) ,int(self.drawing_key_points[21])), (int(self.drawing_key_points[22]) ,int(self.drawing_key_points[23])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[24]) ,int(self.drawing_key_points[25])), (int(self.drawing_key_points[26]) ,int(self.drawing_key_points[27])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[0]) ,int((self.drawing_key_points[5]-self.drawing_key_points[1])/2)+int(self.court_start_y)), (int(self.drawing_key_points[2]) ,int((self.drawing_key_points[5]-self.drawing_key_points[1])/2)+int(self.court_start_y)), (255, 255, 255), 2)
        else:
            cv2.line(combined_frame, (int(self.drawing_key_points[8] ),int(self.drawing_key_points[9])), (int(self.drawing_key_points[10]) ,int(self.drawing_key_points[11])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[12]) ,int(self.drawing_key_points[13])), (int(self.drawing_key_points[14]) ,int(self.drawing_key_points[15])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[16]) ,int(self.drawing_key_points[17])), (int(self.drawing_key_points[18]) ,int(self.drawing_key_points[19])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[20]) ,int(self.drawing_key_points[21])), (int(self.drawing_key_points[22]) ,int(self.drawing_key_points[23])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[24]) ,int(self.drawing_key_points[25])), (int(self.drawing_key_points[26]) ,int(self.drawing_key_points[27])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[28]) ,int(self.drawing_key_points[29])), (int(self.drawing_key_points[30]) ,int(self.drawing_key_points[31])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[32]) ,int(self.drawing_key_points[33])), (int(self.drawing_key_points[34]) ,int(self.drawing_key_points[35])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[36]) ,int(self.drawing_key_points[37])), (int(self.drawing_key_points[38]) ,int(self.drawing_key_points[39])), (255, 255, 255), 2)
            cv2.line(combined_frame, (int(self.drawing_key_points[0]) ,int((self.drawing_key_points[5]-self.drawing_key_points[1])/2)+int(self.court_start_y)), (int(self.drawing_key_points[2]) ,int((self.drawing_key_points[5]-self.drawing_key_points[1])/2)+int(self.court_start_y)), (255, 255, 255), 2)

        # pts2 = np.float32([[0 ,0], [720 ,0 ], [0 ,550 ], [720 ,550 ]])
        # M = cv2.getPerspectiveTransform(pts1,pts2)
        # dst = cv2.warpPerspective(frame,M,(750,575))
        return combined_frame, M
    
    ###Now using###
    def showPlayerPoint(self,frame, M, point,player_id):
        map_player=frame.copy()
        if point is None:
            return map_player
        points = np.float32([[point]])
        transformed = cv2.perspectiveTransform(points, M)[0][0]
        if player_id == 1:
            cv2.circle(map_player, (int(transformed[0]), int(transformed[1])), radius=0, color=(160, 255, 183), thickness=15)
        else:
            cv2.circle(map_player, (int(transformed[0]), int(transformed[1])), radius=0, color=(125,62,255), thickness=15)
        return map_player
    
    ###Now using###
    def showBallPoint(self,frame, M, point,bounce=0):
        map_ball=frame.copy()
        if point is None:
            return map_ball
        points = np.float32([[point]])
        transformed = cv2.perspectiveTransform(points, M)[0][0]
        if bounce==1:
            cv2.circle(map_ball, (int(transformed[0]), int(transformed[1])), radius=0, color=(255, 255, 0), thickness=10)
        elif bounce==2:
            cv2.circle(map_ball, (int(transformed[0]), int(transformed[1])), radius=0, color=(0, 0, 255), thickness=10)
        else:
            cv2.circle(map_ball, (int(transformed[0]), int(transformed[1])), radius=0, color=(0, 250, 237), thickness=10)
        self.setBallPosOnMap((int(transformed[0]), int(transformed[1])))
        return map_ball
    
    def setBallPosOnMap(self, ball_pos_on_frame): # left corner is Origin Point (0, 0)
        self.map_ball_x = ball_pos_on_frame[0] - self.start_x
        self.map_ball_y = ball_pos_on_frame[1] - self.start_y

    def getBallPosOnMap(self):
        return (self.map_ball_x, self.map_ball_y)

    def getMapToRealRatio(self):
        self.line_width = self.drawing_rectangle_width - 2 * self.padding_court
        self.line_height = self.drawing_rectangle_height - 2 * self.padding_court
        return (constants.DOUBLE_LINE_WIDTH / self.line_width, # meter per pixel
                (2 * constants.HALF_COURT_LINE_HEIGHT) / self.line_height)
