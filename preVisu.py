from readdata import parsefile
import argparse
from itertools import product  
import json
from readinfo import readinfo
class Draw:
    def __init__(self,filename,interval_time,numofcamera,posofcameras,nameofcameras):
        self.list = parsefile(filename)
        #[time0,time2,...]
        self.statelist = []
        #interval time
        self.interval_time = interval_time
        #pos
        self.posofcameras = posofcameras
        self.numofcamera = numofcamera
        self.nameofcameras = nameofcameras

    def getMaxFrameNo(self):
        maxframe = 0
        for person in self.list:
            eventCounter = 0
            for eachEvent in person:
               if eachEvent[0] != 'p':
                   startframe = eachEvent[2]
                   if startframe > maxframe:
                       maxframe = startframe
                   endframe = eachEvent[3]
                   if endframe > maxframe:
                       maxframe = endframe
        return maxframe               

    def getCameraJoinList(self):
        #得到所有可能的镜头组合[((1, 2), ([1, 1], [2, 2])), ((1, 3), ([1, 1], [3, 3])), ((1, 4), ([1, 1], [4, 4])), ((1, 5), ([....list里的一个元素是两个元组，第一个是(fromCam,toCam),第二个是([fromCamX,fromCamY],[toCamX,toCamY])
        cameraList = [n for n in range(1,self.numofcamera + 1)]
        cameraJoinList = []
        #print(cameraList)
        #这个product就是迪卡尔积啊（嘿嘿
        for fromCam,toCam in product(cameraList,cameraList):
            if fromCam != toCam:  #去掉自己到自己的组合
                cameraJoinList.append(((fromCam,toCam),(self.posofcameras[fromCam - 1],self.posofcameras[toCam - 1])))
        return cameraJoinList           
     
    def getFrameTraceMap(self,frame):
        cameraJoinList = self.getCameraJoinList() 
        #print(cameraJoinList)
        #print(frame)
        traceFound = False
        traceMap = []
        for person in self.list:
            eventCounter = 0
            isInTheArea = False # 这一帧下这个人在这个店内吗，不在则没有出现在任何camera中  
            currentCam = '' # 这一帧下这个人在哪
            toCam = '' #在这个人的轨迹中，这一帧的镜头的下一个镜头是哪一个（将要去哪？）
            for eachEvent in person:
                if eachEvent[0] != 'p':
                    eventCounter = eventCounter + 1
                    cam = eachEvent[0] 
                    startFrame = eachEvent[2]
                    endFrame = eachEvent[3]
                    if frame > startFrame and frame < endFrame:
                        isInTheArea = True
                        currentCam = cam
                        if eventCounter != len(person) - 1:
                            toCam = person[eventCounter + 1][0]
                            print(toCam)
                        break  
            traceMap.append((isInTheArea,currentCam,toCam))
       # print(traceMap)  
        return traceMap
    
    def getWholeTraceBook(self,maxFrame):
        tracebook = []
        for frame in range(0,maxFrame):
            tracebook.append(self.getFrameTraceMap(frame))
        print(tracebook)
        return tracebook
    def parse_frame_list(self,frame):

        #output:the STATE of this frame
        #{'camera':str,'pos':[],'frame':int,'numofpeople':int}
        #total state{'c1':camera_state,'c2':camera_state,...}
        total_state = {}  
        for i in range(self.numofcamera):
            camera_state = {'camera':"",'pos':[],'frame' : frame,'numofpeople' : 0}
            #camera_state['camera'] = 'c'+str(i)
            camera_state['camera'] = self.nameofcameras[i-1]
            camera_state['pos'] = self.posofcameras[i]
            #total_state['c'+str(i)] = camera_state
            total_state[self.nameofcameras[i-1]] =  camera_state
        for i in range(self.numofcamera):
            print(total_state[self.nameofcameras[i-1]])
        print('-------------------------------------')
        for person_state in self.list:
            #['p1', ['c1', 's1', 15, 55], ['c2', 's1', 80, 2000], ['c5', 's1', 2300, 2400], ['c4', 's1', 2600, 3800], ['c6', 's1', 3200, 3500]]
            for cameraNo in range(1,len(person_state)):
                person_camera_state = person_state[cameraNo]
                start = person_camera_state[2]
                finish = person_camera_state[3]
                if start < frame and finish > frame:
                    total_state[person_camera_state[0]]['numofpeople'] += 1
                    break
        for i in range(self.numofcamera):
            print(total_state[self.nameofcameras[i-1]])
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--mode',default = 'all')
    parser.add_argument('--frame',help = 'if the mode is all,you will export the whole trace of all people .if the mode is beforeframe ,you will export the whole trace of all people before the this frame to a json;if the mode is one,you just export the position of all person under one frame ',type = int,default = 30)
    parser.add_argument('--infoJson',help = 'the json file where store the camera number,the position of these cameras',default = "info.json")
    args = parser.parse_args()
    frame = args.frame
    mode = args.mode 
    infoJson = args.infoJson    
    info = readinfo(infoJson)
    cameraInfo = info['camera']
    interval_time = info['interval_time']
    numofcamera = len(cameraInfo)
    posofcameras =  [[camera['x'],camera['y']] for camera in cameraInfo]
    nameofcameras = [camera['name'] for camera in cameraInfo]    
    d = Draw('swdata.txt',interval_time,numofcamera,posofcameras,nameofcameras)
    #d.parse_frame_list(frame)
    print("-----------------------")
    #d.getWholeTraceBook(4000)
    #print("-----------------------------------------")
    #print(d.getFrameTraceMap(frame))  
    if mode == 'beforeframe':
        with open("beforeframe.json","w") as f:
            json.dump(d.getWholeTraceBook(frame),f)
            print("写入第"+str(frame)+"帧前的所有轨迹信息到json文件完毕")
    elif mode == 'one':
        with open('one.json','w') as f:
            json.dump(d.getFrameTraceMap(frame),f)
           # print("写入第"+str(frame)+"帧信息入json文件完毕"）
    elif mode == 'all':
        maxframe = d.getMaxFrameNo()
        with open("all.json",'w') as f:
            json.dump(d.getWholeTraceBook(maxframe),f)
            print('写入所有轨迹信息到json文件中完毕')