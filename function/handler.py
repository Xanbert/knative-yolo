#hander detection request

import cv2 #opencv-python 4.1.1.26 : https://pypi.org/project/opencv-python/
import base64
import sys

sys.path.append('/home/app/function')
from utils.darknet import Yolov3  #another option (not try): https://pypi.org/project/darknetpy/
from utils.mongodbController import mongodbController
from utils.redisController import redisController
from utils import globalconstant as gvar

#import os

#save to redis
'''
videoname = "yolotest.mp4"
with open(videoname,"r+b") as src:
    videoBytes = src.read()
temp.saveVideo(videoname,videoBytes)
'''

#create collection
'''
username = "yolotest.mp4"
colname = db.createuserdb(username,True)
userid = db.insertUserProcess(username)
print("username: {}, userid: {}, collection name: {}".format(username,userid,colname))
'''

#req = "name.mp4"
def handle(username):
    #cwd = os.getcwd()
    # print(cwd)
    # yolo = Yolov3(
    #     "{}/{}".format(cwd,gvar.classesfile),
    #     "{}/{}".format(cwd,gvar.configfile),
    #     "{}/{}".format(cwd,gvar.weightfile),
    # )
    yolo = Yolov3(gvar.classesfile,gvar.configfile,gvar.weightfile)
    temp = redisController(gvar.REDIS_HOST,gvar.REDIS_PORT)
    db = mongodbController(gvar.MONGO_HOST,gvar.MONGO_PORT)
    #colname = db.createuserdb(username,True)
    userid = db.getUserID(username,"submitted") #get submitted userid
    if userid==False:
        print("username: {}, not submit".format(username,userid))
        return False
    if db.updateUserProcess(userid,"pending") == False:
        return userid
    #userid = db.insertUserProcess(username)
    
    #print("username: {}, userid: {}, collection name: {}".format(username,userid,colname))

    #https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames
    #print(cv2.__version__)
    #vidcap = cv2.VideoCapture("yolotest.mp4") #video from: https://www.youtube.com/watch?v=vF1RPI6j7b0
    vidcap = cv2.VideoCapture(temp.getVideoTemppath(username))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    #print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
    success,image = vidcap.read()
    totalframe = 0
    frameno = 0.0
    success = True
    print("Reading Frame...")
    while success:
        if db.getUserProcess(userid)=="removed": #new process replaced
            vidcap.release()
            print("username: {}, userid: {} is removed".format(username,userid))
            break
        #cv2.imwrite("out/frame%d.jpg" % totalframe, image)     # save frame as JPEG file
        success,image = vidcap.read()
        #print ('Read frame{}:{}'.format(frameno,success))
        if success:
            outimage = yolo.detectFrame(image)
            #cv2.imwrite("out/out{}.jpg".format(totalframe), outimage) # save detection as JPEG file
            #https://stackoverflow.com/questions/40928205/python-opencv-image-to-byte-string-for-json-transfer/40930153
            retval, buffer = cv2.imencode('.jpg', outimage) # encode detection as JPEG
            #encode base64
            imageid = db.insertoneBase64(
            username,
            userid,
            frameno,
            "{}_{}.jpg".format(username,totalframe),
            #base64.b64encode(buffer) #type(bytes)
            base64.b64encode(buffer).decode() #type(str)
            )
            #print('image{} id: {}'.format(totalframe,imageid))

            #get frame per second
            #https://stackoverflow.com/questions/22704936/reading-every-nth-frame-from-videocapture-in-opencv
            frameno += fps
            vidcap.set(1, frameno)
            totalframe+=1
        else:
            vidcap.release()
            print("Read Frame total: ",str(totalframe))
            db.updateUserProcess(userid,"done") #"done"
    return userid
