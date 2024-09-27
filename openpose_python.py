# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
import math
import numpy as np
import time
from sys import platform
import argparse
import frozen_dir

#----------------------------計算角度函式(餘弦定理)------------------------------
def angle(name,point_number_1,point_number_2,point_number_3,point_number_4):
       
        #----獲取關節點位置-----
        point_1 = int(keypoint[frame_num][0][point_number_1][0]),int(keypoint[frame_num][0][point_number_1][1])
        point_2 = int(keypoint[frame_num][0][point_number_2][0]),int(keypoint[frame_num][0][point_number_2][1])
        point_3 = int(keypoint[frame_num][0][point_number_3][0]),int(keypoint[frame_num][0][point_number_3][1])
        point_4 = int(keypoint[frame_num][0][point_number_4][0]),int(keypoint[frame_num][0][point_number_4][1])

        #----------------------

        #------計算三邊長度-----
        a=math.sqrt((point_2[0]-point_3[0])*(point_2[0]-point_3[0])+(point_2[1]-point_3[1])*(point_2[1] - point_3[1]))
        b=math.sqrt((point_1[0]-point_3[0])*(point_1[0]-point_3[0])+(point_1[1]-point_3[1])*(point_1[1] - point_3[1]))
        c=math.sqrt((point_1[0]-point_2[0])*(point_1[0]-point_2[0])+(point_1[1]-point_2[1])*(point_1[1]-point_2[1]))
        #----------------------
        
        if (-2*a*c)!=0:
            if (b*b-a*a-c*c)/(-2*a*c)<-1 or (b*b-a*a-c*c)/(-2*a*c)>1:
                B=180
                print(name)
                #keepangle.append(B)         
            else:
                B=round(math.degrees(math.acos((b*b-a*a-c*c)/(-2*a*c)))) #取得角度
                if((name == 'R_armpit' and point_2[1]>point_3[1]+20 and point_3[1]!= 0) or (name == 'L_armpit' and point_2[1]>point_3[1]+20 and point_3[1]!= 0) ):
                    #cv2.rectangle(OutputData, (point_4[0]-80, point_4[1]-80), (point_3[0]+80, point_3[1]+80), (0, 255, 0), 2)
                    cv2.line(OutputData,(point_4[0]-80,point_4[1]-80),(point_4[0]+80,point_4[1]-80), (0, 255, 0), 2)
                    cv2.line(OutputData,(point_4[0]-80,point_4[1]-80),(point_3[0]-80,point_3[1]+80), (0, 255, 0), 2)
                    cv2.line(OutputData,(point_3[0]-80,point_3[1]+80),(point_3[0]+80,point_3[1]+80), (0, 255, 0), 2)
                    cv2.line(OutputData,(point_3[0]+80,point_3[1]+80),(point_4[0]+80,point_4[1]-80), (0, 255, 0), 2)
                    uphand = 'put up hand'
                else:
                    uphand= " "
                cv2.putText(OutputData,uphand, (10, 120),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                middle_position = np.array(point_1)-(int((point_1[0] - point_3[0])/2),int((point_1[1] - point_3[1])/2)) #計算部位中間位置(方便顯示)
                cv2.putText(OutputData,name+' : '+str(B),(middle_position[0],middle_position[1]), 1, 1,(255,255,255),1,cv2.LINE_AA)
                #keepangle.append(B)
#----------------------------------------------------------------------------   
                
#----------自定義變數----------
start = time.time() #計算時間
frame_num = 0 #計算FPS
Save_point = {}
keypoint ={} #存放每幀關節點數據
position = {'R_armpit':[1,2,3],'R_elbow': [2,3,4], 'R_knee':[9,10,11],'L_armpit':[1,5,6],'L_elbow':[5,6,7],'L_knee':[12,13,14]}
#需要部位的角度計算 = [[右腋下],[右手肘],[右膝蓋],[左腋下],[左手肘],[左膝蓋]]
#-----------------------------
try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = frozen_dir.app_path()
    print("print: dir_path",dir_path)
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            #sys.path.append(r"D:\Lab\Project\openpose-1.7.0\build\python\openpose\__init__.py")
            sys.path.append(dir_path + '/../../python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
            import pyopenpose as op
            
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    # # Flags
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--image_path", default="../../../examples/media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
    # args = parser.parse_known_args()

    # # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    # params = dict()
    # params["model_folder"] = "../../../models/"
    # #
    # # Add others in path?
    # for i in range(0, len(args[1])):
    #     curr_item = args[1][i]
    #     if i != len(args[1])-1: next_item = args[1][i+1]
    #     else: next_item = "1"
    #     if "--" in curr_item and "--" in next_item:
    #         key = curr_item.replace('-','')
    #         if key not in params:  params[key] = "1"
    #     elif "--" in curr_item and "--" not in next_item:
    #         key = curr_item.replace('-','')
    #         if key not in params: params[key] = next_item

    # # Construct it from system arguments
    # # op.init_argv(args[1])
    # # oppython = op.OpenposePython()

    # # Starting OpenPose
  
            
    # opWrapper = op.WrapperPython(op.ThreadManagerMode.Synchronous)
    # opWrapper.configure(params)

    # opWrapper.execute()
    params = dict()
    params["model_folder"] = "../../../models/"
    params["net_resolution"] = '128x192'
    params["model_pose"] = "BODY_25"
    params["render_pose"] = 1
    #----------引入openpose--------
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()
    datum = op.Datum()
    # cap = cv2.VideoCapture(0)#開啟相機
    cap = cv2.VideoCapture('pose1_test.mp4')
    #----------------------------
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # size = (int(cap.get(cv2.cv2.CAP_PROP_FRAME_WIDTH)),
    #     int(cap.get(cv2.cv2.CAP_PROP_FRAME_HEIGHT)))
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # out = cv2.VideoWriter('video.avi',fourcc, fps,size)
    #----------自定義變數----------
    start = time.time() #計算時間
    frame_num = 0 #計算FPS
    Save_point = {}
    keypoint ={} #存放每幀關節點數據
    position = {'R_armpit':[1,2,3,4],'R_elbow': [2,3,4,5], 'R_knee':[9,10,11,12],'L_armpit':[1,5,6,7],'L_elbow':[5,6,7,8],'L_knee':[12,13,14,15]}
    #需要部位的角度計算 = [[右腋下],[右手肘],[右膝蓋],[左腋下],[左手肘],[左膝蓋]]
    #----------------------------
    #-----------------------------------------進入影像處理----------------------------------------------------
    while (cap.isOpened()):
        ret, frame = cap.read()

        #---------------------如果有獲取影像，即進入運算-----------------------------------
        if ret==True:
            datum.cvInputData = frame    
            #opWrapper.emplaceAndPop([datum]) #原本的但有問題
            opWrapper.emplaceAndPop(op.VectorDatum([datum])) #改成這個程式碼
            OutputData = datum.cvOutputData #加上骨架後影像
            keypoint[frame_num] = datum.poseKeypoints #儲存每幀關節點數據
            #print(datum.poseKeypoints)


            #-----在影像上顯示(部位角度&&關節點座標)----
            if(str(datum.poseKeypoints)!='None'):
                

                #------計算每個部位角度----------
                for i in position:
                    angle(i,position[i][0],position[i][1],position[i][2],position[i][3])
                #------------------------------
                #---------------------------------八塊腹肌----------------------------------------
                # if(keypoint[frame_num][0][8][0] != 0 and keypoint[frame_num][0][1][0] != 0):
                #     waist = int(keypoint[frame_num][0][8][0]),int(keypoint[frame_num][0][8][1])
                #     neck = int(keypoint[frame_num][0][1][0]),int(keypoint[frame_num][0][1][1])
                #     len = int((neck[1] - waist[1])/8)
                #     for i in range(0,4):
                #         cv2.rectangle(OutputData, (waist[0]+len-i*2, waist[1]+len-40+i*len), (waist[0], waist[1]-40+i*len), (0, 255, 0), 2)
                #         cv2.rectangle(OutputData, (waist[0], waist[1]+len-40+i*len), (waist[0]-len+i*2, waist[1]-40+i*len), (0, 255, 0), 2)
                # ----------關節座標-------------
                    
                for i in datum.poseKeypoints[0]:
                    x = i[0]
                    y = i[1]
                    point = '({x},{y}){score}'.format(x=int(x),y=int(y),score = int(i[2]*100))
                    # if x>0:
                    #     cv2.putText(OutputData,point,(x,y), 1, 1,(0,0,255),1,cv2.LINE_AA)
                #------------------------------
                    
                
                #----------------------------------------
            
            #----------------計算時間和FPS------------
            frame_num += 1 #每新增一幀+1
            optime = round(time.time()-start, 2) #計算時間
            cv2.putText(OutputData,'FPS : {0:.2f}'.format(round(frame_num/optime,2)), (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(OutputData,'Time : '+str(optime), (10, 60),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(OutputData,'Frame :'+str(frame_num), (10, 90),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            #----------------------------------------
            #cv2.putText(OutputData,'Student', (round(OutputData.shape[0])+70, round(OutputData.shape[1]/4+50)),cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
            cv2.imshow("Openpose Python - Press q to Exit",OutputData)
            #--------------------------------------------------------------------------------
            print(frame_num)
            print(datum.poseKeypoints)
            print('-----------------')
            
                

        #------------------------------------按鍵反饋-----------------------------------------
        keypress = cv2.waitKey(1)
        #----------------按z暫停-------------------
        if keypress & 0xFF == ord('z'):
            print('暫停(按任意鍵繼續)')
            print(datum.poseKeypoints)
            cv2.putText(OutputData,'STOP', (round(OutputData.shape[0]/2)+70, round(OutputData.shape[1]/4+50)),cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 10)
            cv2.putText(OutputData,'(You can press any key to continue)', (round(OutputData.shape[0]/3+85), round(OutputData.shape[1]/4)+100),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),5)
            cv2.imshow("Openpose Python - Press q to Exit",OutputData)

            cv2.waitKey(0)  
            print('繼續')
        #------------------------------------------    
        
        #-----------按q鍵退出迴圈(攝影機)------------
        if keypress & 0xFF == ord('q'):
            break
        #------------------------------------------
        #-------------------------------------------------------------------------------------

except Exception as e:
    print(e)
    sys.exit(-1)
