from PyQt5.QtCore import *
import numpy as np
import math, random

populationSize = 1000  # количество создаваемых маршрутов
wrGroupSize = 5  # размер рабочей группы. В массив случайным образом выбираются маршуты популяции.
# первые два маршрута отсортированного массива порождают дочерний маршрут, который заменяет самый плохой в дочерней группе
mutationChance = 3  # процент мутации
maxGenerations = 30000  # максимальное число скрещиваний
numberOfClosePoints = 5  # число городов соседей. для каждого города формируется список городов соседей данного размера
chanceUseClosePoint = 90  # вероятность выбора следующего городамаршрута из списка его городов-соседей для начальной популяции
seed = 0  # для датчика случайных чисел при формировании начальной популяции при выполнении срещиваний и мутаций

class City():
    def __init__(self, point):
        self.point = point  # позиция точки координаты
        self.distance = []  # расстояние от точки до каждой прочей точки, индекс списка конкретный город
        self.closePoint = []  # список ближайших 5 точек, в индексе номер города, не координаты

    def findClosePoint(self, numberOfClosePoints):
        shortestDistance = None 
        shortestPoint = 0
        dCnt = len(self.distance)
        dist = np.array(dCnt)
        dist = self.distance.copy()
        self.closePoint.Clear()
        for i in range(0, numberOfClosePoints):
            shortestDistance =
            for j in range(0, dCnt):
                if dist[j] < shortestDistance:
                    shortestDistance = dist[j]
                    shortestPoint = j
            self.closePoint.append(shortestPoint)
            dist[shortestPoint]

class Cities():
    def __init__(self):
        pass

class Population():
    pass

class Tour():
    pass



def generationAlgoritm(points, start, finish):
    point = points.copy()
    point.insert(0, start)
    if finish:
        point.append(finish)

    distPoint = np.zeros((len(point), len(point)))

    for indx, i in enumerate(point):
        for indx2, j in enumerate(point):
            if indx != indx2:
                distPoint[indx, indx2] = math.fabs((QPointF.x(i) - QPointF.x(j)) ** 2 +
                          (QPointF.y(i) - QPointF.y(j)) ** 2) ** 0.5


    print(distPoint)
    return point


