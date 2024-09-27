import sys
import cv2
import os
import math
import numpy as np
import time
from sys import platform
import argparse
import frozen_dir
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import Image,ImageTk,ImageSequence, ImageFont, ImageDraw
import threading
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

plt.rcParams["font.sans-serif"] = ["Taipei Sans TC Beta"]

# OpenPose path settings
openpose_path = f"D:/Lab/Project/openpose-1.7.0/build/python/openpose/Release"
openpose_model_path = f"D:/Lab/Project/openpose-1.7.0/models/"

def cv2putText(img, text, pos, text_color, text_size, border=0):
    if isinstance(img, np.ndarray):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)
    font_style = ImageFont.truetype("font/msjhbd.ttc", text_size, encoding="utf-8")
    draw.text(pos, text, font=font_style, fill=text_color, stroke_width=border, stroke_fill=(0, 0, 0))
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def angle(name,point_number_1,point_number_2,point_number_3):
    #----紀錄關節點座標-----
    # pos_loc = {'R_elbow' :30,'L_elbow':60,'L_armpit':50,'L_knee':90}
    global local_y
    
    #----獲取關節點位置-----
    point_1 = int(keypoint[frame_num][0][point_number_1][0]),int(keypoint[frame_num][0][point_number_1][1])
    point_2 = int(keypoint[frame_num][0][point_number_2][0]),int(keypoint[frame_num][0][point_number_2][1])
    point_3 = int(keypoint[frame_num][0][point_number_3][0]),int(keypoint[frame_num][0][point_number_3][1])

    #------計算三邊長度-----
    a=math.sqrt((point_2[0]-point_3[0])*(point_2[0]-point_3[0])+(point_2[1]-point_3[1])*(point_2[1] - point_3[1]))
    b=math.sqrt((point_1[0]-point_3[0])*(point_1[0]-point_3[0])+(point_1[1]-point_3[1])*(point_1[1] - point_3[1]))
    c=math.sqrt((point_1[0]-point_2[0])*(point_1[0]-point_2[0])+(point_1[1]-point_2[1])*(point_1[1]-point_2[1]))

    if (-2*a*c)!=0:
        if (b*b-a*a-c*c)/(-2*a*c)<-1 or (b*b-a*a-c*c)/(-2*a*c)>1:
            B=180
            print(name)
            #keepangle.append(B)         
        else:
            B=round(math.degrees(math.acos((b*b-a*a-c*c)/(-2*a*c)))) #取得角度
            ang.set(B)
    return B

def draw_angle(point_number, ang):
    global OutputData
    point = (float(keypoint[frame_num][0][point_number][0]),
             float(keypoint[frame_num][0][point_number][1]))
    OutputData = cv2putText(OutputData, str(ang), point, (255, 255, 255), 30, 1)
    #print(ang)
#----------------------------------------------------------------------------   

def act1(pos,point1,point2,ang1,ang2):
    global act_check,standerd,usangtemp1,userangle,usangtimes,usangtemp2
    global is_show_l, is_show_r
    curr = {}
    try: 
        curr[0] = angle(point1,pos[point1][0],pos[point1][1],pos[point1][2])
        if is_show_r: draw_angle(pos[point1][1], curr[0])
        curr[1] = angle(point2,pos[point2][0],pos[point2][1],pos[point2][2])
        if is_show_l: draw_angle(pos[point2][1], curr[1])
        
        if ang1 < ang2:
            if usangtemp1 > curr[0] or usangtemp1 == 0:
                usangtemp1 = curr[0]
            if usangtemp2 > curr[1] or usangtemp2 == 0:
                usangtemp2 = curr[1]
            if curr[0] <= ang2 and curr[1] <= ang2 and act_check == 0:
                standerd = 1
                judge.set("再低一點!")
            if curr[0] <= ang1 and curr[1] <= ang1:
                act_check = 1
                standerd = 0
                judge.set("Good!回到原本動作")
            if standerd and curr[0] >= ang2 and curr[1] >= ang2:
                userangle[point1].append(usangtemp1)
                userangle[point2].append(usangtemp2)
                usangtimes = usangtimes + 1
                usangtemp1 = 0
                usangtemp2 = 0
                standerd = 0
            if act_check and curr[0] >= ang2 and curr[1] >= ang2:
                act_check = 0
                userangle[point1].append(usangtemp1)
                userangle[point2].append(usangtemp2)
                usangtimes = usangtimes + 1
                usangtemp1 = 0
                usangtemp2 = 0
                return True
            return False
        else:
            if usangtemp1 < curr[0] or usangtemp1 == 0:
                usangtemp1 = curr[0]
            if usangtemp2 < curr[1] or usangtemp2 == 0:
                usangtemp2 = curr[1]
            if curr[0] >= ang2 and curr[1] >= ang2 and act_check == 0:
                standerd = 1
                judge.set("再高一點!")
            if curr[0] >= ang1 and curr[1] >= ang1:
                act_check = 1
                standerd = 0
                judge.set("Good!回到原本動作")
            if standerd and curr[0] <= ang2 and curr[1] <= ang2:
                userangle[point1].append(usangtemp1)
                userangle[point2].append(usangtemp2)
                usangtimes = usangtimes + 1
                usangtemp1 = 0
                usangtemp2 = 0
                standerd = 0
            if act_check and curr[0] <= ang2 and curr[1] <= ang2:
                act_check = 0
                userangle[point1].append(usangtemp1)
                userangle[point2].append(usangtemp2)
                usangtimes = usangtimes + 1
                usangtemp1 = 0
                usangtemp2 = 0
                return True
            return False
    except Exception as e:
        print(e)
# ----------------------------------------------------
# def video_loop():
#     try:
#         _,pic = cap.read()
#         frame = pic.copy()
#         datum.cvInputData = frame
#         opWrapper.emplaceAndPop(op.VectorDatum([datum]))
#         OutputData = datum.cvOutputData #加上骨架後影像
#         cv2image = cv2.cvtColor(OutputData,cv2.COLOR_BGR2RGBA)
#         img = Image.fromarray(cv2image)
#         imgtk = ImageTk.PhotoImage(image=img)
#         videolabel.imgtk = imgtk
#         videolabel.config(image=imgtk)
#         root.after(1,video_loop)
#     except AttributeError as e:
#         cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
#         print(0)
# ------------------------------------------------------
def counttimes():
    global timebool, OutputData
    while (cap.isOpened() and timebool):
        ret, frame = cap.read()
        if not ret: break

        datum.cvInputData = frame    
        #opWrapper.emplaceAndPop([datum]) #原本的但有問題
        opWrapper.emplaceAndPop(op.VectorDatum([datum])) #改成這個程式碼
        OutputData = datum.cvOutputData #加上骨架後影像
        keypoint[frame_num] = datum.poseKeypoints #儲存每幀關節點數據
        global local_y,efftimes,userangle,act_checkR,act_checkL,usangtimes,act
        if(str(datum.poseKeypoints)!='None'):
            # -------------------------------------------------------
            if len(pose[act]) >= 5:
                if act1(position,pose[act][1],pose[act][2],pose[act][3],pose[act][4]):
                    efftimes = efftimes+1
                    # print(userangle)
                    judge.set("完美!完成一下")
            else :
                if(act1(position,pose[act][1],pose[act][2],pose[act][3],pose[act][4])):
                    act_checkR = 1
                if(act1(position,pose[act][5],pose[act][6],pose[act][7],pose[act][8])):
                    act_checkL = 1
                if act_checkR and act_checkL:
                    act_checkR = 0
                    act_checkL = 0
                    efftimes = efftimes+1
                    # print(userangle)
                    judge.set("完美!完成一下")


            # --------------------------------------------------------
        ts.set(efftimes)
        tots.set(usangtimes)

        cv2.namedWindow("Openpose Python - Press q to Exit", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Openpose Python - Press q to Exit", 1280, 720)
        cv2.imshow("Openpose Python - Press q to Exit",OutputData)
        #------------------------------------按鍵反饋-----------------------------------------
        keypress = cv2.waitKey(1)
        #----------------按z暫停-------------------
        if keypress & 0xFF == ord('z'):
            print('暫停(按任意鍵繼續)')
            print(datum.poseKeypoints)
            cv2.putText(OutputData,'STOP', (round(OutputData.shape[0]/2)-35, round(OutputData.shape[1]/4+50)),cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 7)
            cv2.putText(OutputData,'(You can press any key to continue)', (round(OutputData.shape[0]/3-130), round(OutputData.shape[1]/4)+100),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            cv2.imshow("Openpose Python - Press q to Exit",OutputData)

            cv2.waitKey(0)  
            print('繼續')
        #------------------------------------------    
        
        #-----------按q鍵退出迴圈(攝影機)------------
        if keypress & 0xFF == ord('q'):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            btn_end_act()
            break
    
    cap.release()
    cv2.destroyAllWindows()
    timebool = False
            #------------------------------------------
            #-------------------------------------------------------------------------------------
def recordtimes():
    global timebool 
    while(timebool):
        optime.set(round(time.time()-start, 2)) #計算時間

def show(*e):
    global act,cap,efftimes
    act = actlist[opact.get()][0]
    efftimes = 0
    # cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
    # cap = cv2.VideoCapture('pose3.gif')
    


def btn_start_act():
    global cap,start,timebool,th2_recordtime
    timebool = True
    start = time.time()
    # cap = cv2.VideoCapture('pose'+str(act+1)+'.gif')
    # cap = cv2.VideoCapture(0)#開啟相機
    # cap = cv2.VideoCapture('C:\openpose-master\\build\examples\\tutorial_api_python\pose1.gif')
    th1_counttime = threading.Thread(target=counttimes)
    th1_counttime.start()
    th2_recordtime = threading.Thread(target=recordtimes)
    th2_recordtime.start()

    global btn_selectfile, btn_opencam
    btn_selectfile["state"] = "disable"
    btn_opencam["state"] = "disable"
 
def btn_end_act():
    global cap,timebool
    timebool = False

    global userangle,act,th2_recordtime,usangtimes
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    # y = np.array(list(userangle.values()))
    key = list(userangle)
    plt.ylim(0,pose[act][3]*2)
    plt.xlim(0.7 if usangtimes!=0 and usangtimes!=1 else 0, 
             usangtimes+0.3 if usangtimes!=0 and usangtimes!=1 else 2)
    x = np.arange(0.7 if usangtimes!=0 and usangtimes!=1 else 0,
                  usangtimes+2.3 if usangtimes!=0 else 3)
    # plt.axhline(y=pose[act][3]-2, c="#f90", ls="-", lw=15)
    plt.fill_between(x,pose[act][3]-30,pose[act][3],color="#BBB",alpha=0.7)
    # plt.axhline(y=ave, c="g", ls="--", lw=3,label='average')
    for i in key:
        if(i!='1'):
            x = np.arange(1,len(userangle[i])+1)
            plt.plot(x,np.array(list(userangle[i])) ,label=keypoint_names_zh[i],marker='o')
    plt.xlabel("次數(下)")
    plt.ylabel("關節角度(度)")
    plt.legend()
    plt.show()

    global videoframe, panelframe
    videoframe.pack()
    panelframe.pack_forget()
    reset_args()
    global btn_selectfile, btn_opencam
    btn_selectfile["state"] = "normal"
    btn_opencam["state"] = "normal"

def btn_select_act(a):
    global act,videoframe,panelframe,userangle
    videoframe.pack_forget()
    panelframe.pack()
    act = a-1
    userangle[pose[act][1]] = []
    userangle[pose[act][2]] = []
    if(act == 6):
        userangle[pose[act][5]] = []
        userangle[pose[act][6]] = []

    root.title(list(actlist.keys())[act])

def select_file():
    global cap
    file_path = filedialog.askopenfilename()
    if len(file_path) > 0:
        cap.release()
        cap.open(file_path)
        btn_start_act()

def open_camera():
    global cap
    cap.release()
    cap.open(2) #開啟相機
    btn_start_act()

def animate_gif(frame=0):
    flen = 1
    try:
        if dyimg == 1:
            imgbtn1.configure(image=frames1[frame])
            flen=len(frames1)
        elif dyimg == 2:
            imgbtn2.configure(image=frames2[frame])
            flen=len(frames2)
        elif dyimg == 3:
            imgbtn3.configure(image=frames3[frame])
            flen=len(frames3)
        elif dyimg == 4:
            imgbtn4.configure(image=frames4[frame])
            flen=len(frames4)
        elif dyimg == 5:
            imgbtn5.configure(image=frames5[frame])
            flen=len(frames5)
        elif dyimg == 6:
            imgbtn6.configure(image=frames6[frame])
            flen=len(frames6)
        elif dyimg == 7:
            imgbtn7.configure(image=frames7[frame])
            flen=len(frames7)
        elif dyimg == 8:
            imgbtn8.configure(image=frames8[frame])
            flen=len(frames8)
        elif dyimg == 9:
            imgbtn9.configure(image=frames9[frame])
            flen=len(frames9)
        elif dyimg == 10:
            imgbtn10.configure(image=frames10[frame])
            flen=len(frames10)
    
        root.after(50,animate_gif,(frame+1)%flen)
    except IndexError as e:
        root.after(50,animate_gif,(frame+1)%flen)

def even_enter(event,n):
    global dyimg
    dyimg = n

def even_leave(event):
    global dyimg
    dyimg = 0

def reset_args():
    global start, frame_num, Save_point, keypoint
    start = time.time() #計算時間
    frame_num = 0 #計算FPS
    global efftimes #該動作的次數
    efftimes = 0
    Save_point = {}
    keypoint ={} #存放每幀關節點數據

    global act_check, act_checkR
    act_check = 0
    global standerd
    standerd = 0
    act_checkR = 0
    global local_y
    global act
    global cap
    global userangle, usangtemp1, usangtemp2, usangtimes, dyimg
    userangle = {"1":[1]}
    usangtemp1 = 0
    usangtemp2 = 0
    usangtimes = 0
    dyimg = 0

    global optime, ts, ang, opact, judge, tots
    optime.set("")
    ts.set("0")
    tots.set("0")
    judge.set("")
    root.title("ten_pose")

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = frozen_dir.app_path()
    print(dir_path)
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(openpose_path)
            #os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../../x64/Release;' +  dir_path + '/../../bin;'
            import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e
    
    cap = cv2.VideoCapture()

    #----------------------------------------------
    params = dict()
    params["model_folder"] = openpose_model_path
    params["net_resolution"] = '480x320'
    #params["net_resolution"] = '128x192'
    params["model_pose"] = "BODY_25"
    params["render_pose"] = 1

    #----------引入openpose--------
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()
    datum = op.Datum()

    #----------自定義變數----------
    keypoint_names_zh = {'R_armpit': "右腋下(R_armpit)",
                         'R_elbow':  "右手肘(R_elbow)", 
                         'R_knee':   "右膝(R_knee)",
                         'L_armpit': "左腋下(L_armpit)",
                         'L_elbow':  "左手肘(L_elbow)",
                         'L_knee':   "左膝(L_knee)",
                         'neck':     "脖子(neck)",
                         'R_waist':  "右腰(R_waist)",
                         'L_waist':  "左腰(L_waist)",
                         "R_thigh":  "右臀(R_thigh)",
                         "L_thigh":  "左臀(L_thigh)"}

    position = {'R_armpit': [1,2,3],
                'R_elbow':  [2,3,4], 
                'R_knee':   [9,10,11],
                'L_armpit': [1,5,6],
                'L_elbow':  [5,6,7],
                'L_knee':   [12,13,14],
                'neck':     [0,1,8],
                'R_waist':  [1,8,9],
                'L_waist':  [1,8,12],
                "R_thigh":  [1,9,10],
                "L_thigh":  [1,12,13]}
    
    pose = [['pose1', 'R_elbow', 'L_elbow', 90, 130],
            ['pose2', 'R_knee', 'L_knee', 120, 170],
            ['pose3', 'R_armpit', 'L_armpit', 170, 110],
            ['pose4', 'R_knee', 'L_knee', 80, 65],
            ['pose5', 'neck', 'neck', 80, 110],
            ['pose6', 'R_thigh', 'L_thigh', 150, 100],
            ['pose7', 'L_armpit', 'R_knee', 160, 100
                    , 'R_armpit', 'L_knee', 100, 160],
            ['pose8', 'R_knee', 'L_knee', 65, 170],
            ['pose9', 'R_knee', 'L_knee', 110, 160],
            ['pose10', 'R_waist', 'R_waist', 80, 100]]
    # act_check = [0,0]
    #需要部位的角度計算 = [[右腋下],[右手肘],[右膝蓋],[左腋下],[左手肘],[左膝蓋]]
    #----------------------------
    actlist = {'靠牆伏地挺身': [0],
               '靠牆深蹲': [1],
               '側肩平舉': [2],
               '橋式': [3],
               '捲腹': [4],
               '仰臥腳尖點地': [5],
               '跪姿撐地': [6],
               '深蹲': [7],
               '平板支撐': [8],
               '勇士捲腹': [9]}
    # act = input("1：靠牆伏地挺身 2：靠牆深蹲 3：側肩平舉 4：橋式 5：捲腹 6：仰臥腳尖點地 7：跪姿撐地 8：深蹲 9：平板支撐 10：勇士捲腹 ：")
    # act = 1
    # act = int(act)-1
    act = 0
    root = tk.Tk()
    optime = tk.StringVar()
    ts = tk.StringVar()
    ang = tk.StringVar()
    opact = tk.StringVar()
    judge = tk.StringVar()
    tots = tk.StringVar()
    reset_args()
    opact.set('靠牆伏地挺身')
    videoframe = tk.Frame(root,bg = "black")
    panelframe = tk.Frame(root,bg="white",width=50)
    #--------------------------------------------------------------------------------------
    tlab = tk.Label(panelframe,text="時間：",font=(20))
    tlab.grid(column=0,row=0,pady=10)
    timelabel = tk.Label(panelframe,textvariable=optime,font=(20),width=10,justify='left')
    timelabel.grid(column=1,row=0,padx=2,pady=10)
     #--------------------------------------------------------------------------------------
    totslab = tk.Label(panelframe,text="總次數：",font=(20))
    totslab.grid(column=0,row=1,pady=10)
    totimeslabel = tk.Label(panelframe,textvariable=tots,font=(20),width=10,justify='left')
    totimeslabel.grid(column=1,row=1,padx=2,pady=10)
    #--------------------------------------------------------------------------------------
    tslab = tk.Label(panelframe,text="標準次數：",font=(20))
    tslab.grid(column=0,row=2,pady=10)
    timeslabel = tk.Label(panelframe,textvariable=ts,font=(20),width=10,justify='left')
    timeslabel.grid(column=1,row=2,padx=2,pady=10)
    #--------------------------------------------------------------------------------------
    # btn_start = tk.Button(panelframe,text= '開始',command=btn_start_act,height=2,width=6)
    # btn_start.grid(column=0,row =3,pady=20)
    btn_selectfile = tk.Button(panelframe,text= '選擇檔案',command=select_file,height=2,width=6)
    btn_selectfile.grid(column=0,row =3,pady=10,padx=5)
    btn_opencam = tk.Button(panelframe,text= '開啟相機',command=open_camera,height=2,width=6)
    btn_opencam.grid(column=1,row =3,pady=10,padx=5)
    btn_end = tk.Button(panelframe,text='結束',command=btn_end_act,height=2,width=6)
    btn_end.grid(column=2,row=3,padx=5,pady=10)

    #--------------------------------------------------------------------------------------

    def show_side(show_r, show_l):
        global is_show_r, is_show_l
        is_show_r = show_r
        is_show_l = show_l
    btn_show_r = tk.Button(panelframe,text='僅顯示右邊數值',command=lambda:show_side(True, False),height=2,width=15)
    btn_show_r.grid(column=4,row=0)
    btn_show_l = tk.Button(panelframe,text='僅顯示左邊數值',command=lambda:show_side(False, True),height=2,width=15)
    btn_show_l.grid(column=5,row=0)
    btn_show_both = tk.Button(panelframe,text='顯示所有數值',command=lambda:show_side(True, True),height=2,width=15)
    btn_show_both.grid(column=4,row=1)
    btn_show_cancel = tk.Button(panelframe,text='關閉顯示數值',command=lambda:show_side(False, False),height=2,width=15)
    btn_show_cancel.grid(column=5,row=1)

    #--------------------------------------------------------------------------------------
    tslab = tk.Label(panelframe,text="監測：",font=(20))
    tslab.grid(column=0,row=5,pady=10)
    judgelabel = tk.Label(panelframe,textvariable=judge,font=(20),width=30,justify='left',height=5)
    judgelabel.grid(column=1,row=5,padx=2,pady=20)
    #--------------------------------------------------------------------------------------
    img1 = Image.open(dir_path + f"/pose1.gif")
    frames1 = []
    for frame in ImageSequence.Iterator(img1):
        frames1.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn1 = tk.Button(videoframe,image=frames1[0],command=lambda:btn_select_act(1))
    imgbtn1.bind("<Enter>",lambda event: even_enter(event,1),add = '+')
    imgbtn1.bind("<Leave>",even_leave,add='+')
    imgbtn1.grid(column=1,row=1,padx=2,pady=20)
    
    img2 = Image.open(dir_path + f"/pose2.gif")
    frames2 = []
    for frame in ImageSequence.Iterator(img2):
        frames2.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn2 = tk.Button(videoframe,image=frames2[0],command=lambda:btn_select_act(2))
    imgbtn2.bind("<Enter>",lambda event: even_enter(event,2),add = '+')
    imgbtn2.bind("<Leave>",even_leave,add='+')
    imgbtn2.grid(column=2,row=1,padx=2,pady=20)

    img3 = Image.open(dir_path + f"/pose3.gif")
    frames3 = []
    for frame in ImageSequence.Iterator(img3):
        frames3.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn3 = tk.Button(videoframe,image=frames3[0],command=lambda:btn_select_act(3))
    imgbtn3.bind("<Enter>",lambda event: even_enter(event,3))
    imgbtn3.bind("<Leave>",even_leave,add='+')
    imgbtn3.grid(column=3,row=1,padx=2,pady=20)

    img4 = Image.open(dir_path + f"/pose4.gif")
    frames4 = []
    for frame in ImageSequence.Iterator(img4):
        frames4.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn4 = tk.Button(videoframe,image=frames4[0],command=lambda:btn_select_act(4))
    imgbtn4.bind("<Enter>",lambda event: even_enter(event,4))
    imgbtn4.bind("<Leave>",even_leave,add='+')
    imgbtn4.grid(column=4,row=1,padx=4,pady=20)

    img5 = Image.open(dir_path + f"/pose5.gif")
    frames5 = []
    for frame in ImageSequence.Iterator(img5):
        frames5.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn5 = tk.Button(videoframe,image=frames5[0],command=lambda:btn_select_act(5))
    imgbtn5.bind("<Enter>",lambda event: even_enter(event,5))
    imgbtn5.bind("<Leave>",even_leave,add='+')
    imgbtn5.grid(column=5,row=1,padx=2,pady=20)

    img6 = Image.open(dir_path + f"/pose6.gif")
    frames6 = []
    for frame in ImageSequence.Iterator(img6):
        frames6.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn6 = tk.Button(videoframe,image=frames6[0],command=lambda:btn_select_act(6))
    imgbtn6.bind("<Enter>",lambda event: even_enter(event,6))
    imgbtn6.bind("<Leave>",even_leave,add='+')
    imgbtn6.grid(column=1,row=2,padx=2,pady=20)

    img7 = Image.open(dir_path + f"/pose7.gif")
    frames7 = []
    for frame in ImageSequence.Iterator(img7):
        frames7.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn7 = tk.Button(videoframe,image=frames7[0],command=lambda:btn_select_act(7))
    imgbtn7.bind("<Enter>",lambda event: even_enter(event,7))
    imgbtn7.bind("<Leave>",even_leave,add='+')
    imgbtn7.grid(column=2,row=2,padx=2,pady=20)

    img8 = Image.open(dir_path + f"/pose8.gif")
    frames8 = []
    for frame in ImageSequence.Iterator(img8):
        frames8.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn8 = tk.Button(videoframe,image=frames8[0],command=lambda:btn_select_act(8))
    imgbtn8.bind("<Enter>",lambda event: even_enter(event,8))
    imgbtn8.bind("<Leave>",even_leave,add='+')
    imgbtn8.grid(column=3,row=2,padx=2,pady=20)

    img9 = Image.open(dir_path + f"/pose9.gif")
    frames9 = []
    for frame in ImageSequence.Iterator(img9):
        frames9.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn9 = tk.Button(videoframe,image=frames9[0],command=lambda:btn_select_act(9))
    imgbtn9.bind("<Enter>",lambda event: even_enter(event,9))
    imgbtn9.bind("<Leave>",even_leave,add='+')
    imgbtn9.grid(column=4,row=2,padx=2,pady=20)

    img10 = Image.open(dir_path + f"/pose10.gif")
    frames10 = []
    for frame in ImageSequence.Iterator(img10):
        frames10.append(ImageTk.PhotoImage(frame.resize((300,300))))
    imgbtn10 = tk.Button(videoframe,image=frames10[0],command=lambda:btn_select_act(10))
    imgbtn10.bind("<Enter>",lambda event: even_enter(event,10))
    imgbtn10.bind("<Leave>",even_leave,add='+')
    imgbtn10.grid(column=5,row=2,padx=2,pady=20)
    #--------------------------------------------------------------------------------------
    # panelframe.pack(fill='y',side='left')
    animate_gif()
    videoframe.pack()
    root.mainloop()
    cv2.destroyAllWindows()
#------------------------------------------

#-------------------------------------------------------------------------------------
            
except Exception as e:
    print(e)
    sys.exit(-1)