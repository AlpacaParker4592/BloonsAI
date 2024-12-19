import random
import pandas as pd
import os.path
import numpy as np

def getThrowList(filepath: str,
                 initialMinAngle: float, initialMaxAngle: float,
                 initialMinThrowSec: float, initialMaxThrowSec: float,
                 isInitial: bool, dartNumber: int, totalIteration: int,
                 currentGenerationNo: int, currentIterationNo: int):
    if isInitial:
        return [(random.uniform(initialMinAngle,initialMaxAngle), random.uniform(initialMinThrowSec,initialMaxThrowSec)) for _ in range(dartNumber)]
    
    database_path = os.path.join(os.getcwd(),"bloons_data.csv")
    monkey_data = pd.read_csv(filepath)
    unallocated_iterations = monkey_data[(monkey_data['generation'] == currentGenerationNo-1) & (monkey_data['poppedBloons'] < 0)]['iteration'].tolist()  # 목표하던 만큼의 풍선을 터뜨리지 못한 시도 리스트
    allocated_iterations = [i+1 for i in range(totalIteration) if not i+1 in unallocated_iterations]  # 목표를 완수한 시도 리스트
    if len(allocated_iterations) == 0:
        return [(random.uniform(initialMinAngle,initialMaxAngle), random.uniform(initialMinThrowSec,initialMaxThrowSec)) for _ in range(dartNumber)]


    refined_data = monkey_data.loc[(monkey_data["iteration"].isin(allocated_iterations)) & (monkey_data['generation'] == currentGenerationNo-1)]
    max_popped_iterations = refined_data[refined_data['totalPoppedBloons'] == max(refined_data['totalPoppedBloons'].tolist())]['iteration'].tolist()
    
    chosen_data = refined_data[(refined_data['iteration'] == random.choice(max_popped_iterations))][['generation','iteration','seq','angle','throwSec']]
    throwData = chosen_data[["angle","throwSec"]].values.tolist()
    if currentIterationNo == 0:
        throwData = [(throwData[i][0], throwData[i][1]) for i in range(len(throwData))]
    else:
        throwData = [(throwData[i][0] * (1 + np.random.normal()/40), throwData[i][1]) for i in range(len(throwData))]
    return throwData