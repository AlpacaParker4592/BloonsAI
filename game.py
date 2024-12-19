import screenshot
import algorithm
from pyautogui import moveTo, dragTo, click, mouseDown, mouseUp
import os.path

import time
import random
import math

import pandas as pd
from pandas import DataFrame
from ultralytics import YOLO

remaining_darts = 0
isMonkeyExist = False
bloons = 0

model_path = './model/best.onnx'
model = YOLO(model_path, task="detect")
# https://docs.ultralytics.com/ko/modes/predict/#working-with-results
classes = model.names  # dict type ({0: 'bloon', 1: 'bomb_bloon', ...})

print(classes)
print("")

class MultiplePlayerError(Exception):
    #def __str__(self):
    #    return "There are more than 1 players."
    pass
class NoPlayerFoundError(Exception):
    #def __str__(self):
    #    return "There is no player."
    pass

class objInfo:
    def __init__(self, name, xyxy, xywh, conf):
        self.name = name
        self.xyxy = xyxy
        self.xywh = xywh
        self.conf = float(conf)
    def __str__(self):
        str1 = "objName: {0}, conf: {1}".format(self.name,self.conf)
        str2 = "position (xyxy): {0}".format(self.xyxy)
        str3 = "posision (xywh): {0}".format(self.xywh)
        return '{0}\n{1}\n{2}\n'.format(str1,str2,str3)


def getObjDB() -> objInfo:
    objDB = {i:[] for i in range(len(classes))}
    scrImg, positionDict = screenshot.getScreenShot("Ruffle - bloons.swf")
    if scrImg is None:
        raise("NoScreenIMGError")
    result = model.predict(source=scrImg)[0]  # save plotted images

    for box in result.boxes:
        clsNo = int(box.cls)
        clsName = classes[clsNo]
        if box.conf >= 0.6:
            objDB[clsNo].append(objInfo(name=clsName, xyxy=box.xyxy, xywh=box.xywh, conf=box.conf))

    if len(objDB[11]) == 1:  # Monkey
        for obj in objDB[11]:
            print(obj)
    elif len(objDB[11]) >= 2:
        raise(MultiplePlayerError)
    else:
        raise(NoPlayerFoundError)

    print("The number of objection in screen:")
    for i in range(len(classes)):
        if len(objDB[i]) >= 1:
            print("  {0}: {1}".format(classes[i],len(objDB[i])))

    #result.show()  # display to screen
    return objDB, positionDict


num_remaining_darts = 999
num_remaining_bloons = 999
WAITING_TIME = 3

def throw(monkeyDB, screenshotPosision, angle, throwSec):
    throwPositionX = screenshotPosision['left'] + monkeyDB[0].xywh[0][0] + 80 * math.cos(angle) + 5
    throwPositionY = screenshotPosision['top'] + monkeyDB[0].xywh[0][1] - 80 * math.sin(angle) - 8
    print("angle: {0} degree, throwSec: {1} second".format(math.degrees(angle),throwSec))

    #click(button="left")
    #time.sleep(0.6)
    moveTo(throwPositionX,throwPositionY)
    mouseDown()
    time.sleep(throwSec)
    mouseUp()
    time.sleep(WAITING_TIME)


database = DataFrame({"generation":[],"iteration":[],"seq":[],"angle":[],"throwSec":[],"poppedBloons":[],"totalPoppedBloons":[]})
database["generation"] = database["generation"].astype(int)
database["iteration"] = database["iteration"].astype(int)
database["seq"] = database["seq"].astype(int)
database["poppedBloons"] = database["poppedBloons"].astype(int)
database["totalPoppedBloons"] = database["totalPoppedBloons"].astype(int)


database_path = os.path.join(os.getcwd(),"bloons_data.csv")

allocation = 32  # allocation bloons for level 1
number_of_darts = 5  # allocation bloons for level 1

number_of_iteration = 10
number_of_generation = 10

for generation in range(number_of_generation):
    print("Generation: {0}".format(generation+1))
    if generation >= 1:
        moveTo(scrPosition['left']+651-240,scrPosition['top']+712-247)
        time.sleep(0.5)
        click()  # press reset level button
        time.sleep(1)

    
    for iteration in range(number_of_iteration):
        print(" Iteration: {0}".format(iteration+1))
        total_popped_bloons = 0

        # 던지기 리스트 제작
        nth_generation = generation+1
        if generation == 0:
            throwList = algorithm.getThrowList(filepath=database_path, initialMinAngle=math.radians(0), initialMaxAngle=math.radians(90),
                                               initialMinThrowSec=0.2, initialMaxThrowSec=0.8, isInitial=True,
                                               dartNumber=number_of_darts, totalIteration=number_of_iteration,
                                               currentGenerationNo=nth_generation, currentIterationNo=iteration)
        else:
            throwList = algorithm.getThrowList(filepath=database_path, initialMinAngle=math.radians(0), initialMaxAngle=math.radians(90),
                                               initialMinThrowSec=0.2, initialMaxThrowSec=0.8, isInitial=False,
                                               dartNumber=number_of_darts, totalIteration=number_of_iteration,
                                               currentGenerationNo=nth_generation, currentIterationNo=iteration)
        for seq in range(number_of_darts):
            if num_remaining_darts == 0 or num_remaining_bloons == 0:
                break
            objDB,scrPosition = getObjDB()
            monkey = objDB[11]
            remaining_darts_bef = len(objDB[15])  # remaining dart index
            remaining_bloons_bef = len(objDB[0]) + len(objDB[1]) +\
                                    len(objDB[3]) + len(objDB[8]) +\
                                    len(objDB[12]) + len(objDB[13]) +\
                                    len(objDB[14]) + len(objDB[18]) + len(objDB[19])
            angle, throwSec = throwList[seq][0],throwList[seq][1]
            throw(monkey, scrPosition, angle, throwSec)

            try:
                objDB2,_ = getObjDB()
            except NoPlayerFoundError:  # 게임 클리어 등으로 플레이어가 보이지 않을 때
                popped_bloons = 0
                database2 = DataFrame({"generation":[generation+1],"iteration":[iteration+1],"seq":[seq+1],"angle":[angle],
                                       "throwSec":[throwSec],"poppedBloons":[popped_bloons],"totalPoppedBloons":[total_popped_bloons]})
                database = pd.concat([database,database2],ignore_index = True)
                database.to_csv(database_path,index=False)
                print(" Iteration: {0} cleared".format(iteration+1))
                moveTo(scrPosition['left']+621-240,scrPosition['top']+574-247)  # press reset level button
                time.sleep(0.5)
                click()
                time.sleep(1)
                break
            else:
                remaining_bloons_aft = len(objDB2[0]) + len(objDB2[1]) +\
                                        len(objDB2[3]) + len(objDB2[8]) +\
                                        len(objDB2[12]) + len(objDB2[13]) +\
                                        len(objDB2[14]) + len(objDB2[18]) + len(objDB2[19])
                popped_bloons = remaining_bloons_bef - remaining_bloons_aft
                if popped_bloons >= 0:
                    total_popped_bloons += popped_bloons
                database2 = DataFrame({"generation":[generation+1],"iteration":[iteration+1],"seq":[seq+1],"angle":[angle],
                                       "throwSec":[throwSec],"poppedBloons":[popped_bloons],"totalPoppedBloons":[total_popped_bloons]})
                database = pd.concat([database,database2],ignore_index = True)
                database.to_csv(database_path,index=False)
        print(" Iteration: {0} cleared".format(iteration+1))
        
    

