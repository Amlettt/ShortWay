"""Имитационный отжиг. Алгоритм"""

from PyQt5.QtCore import *
import math, random
import numpy as np

m = 100000  # кол-во итераций
t_start = 10000  # начальная температура
t_end = 0.01  # конечная температура

# s = math.inf  # расстояние начальное = бесконечность

# def createRoute(points, startPoint):
#     route = random.sample(points, len(points))
#     route.insert(0, startPoint)
#     if finish:
#         point.append(finish)
#     else:
#         route.append(startPoint)
#     return route

# def random_points(route):
#     route.pop([0])
#     route.pop()
#     return random.sample(route,k=2)
def distance(points):
    distPoint = np.zeros((len(points), len(points)))

    for indx, i in enumerate(points):
        for indx2, j in enumerate(points):
            if indx != indx2:
                distPoint[indx, indx2] = math.fabs((QPointF.x(i) - QPointF.x(j)) ** 2 +
                                                   (QPointF.y(i) - QPointF.y(j)) ** 2) ** 0.5
    return  distPoint

def simulatedAnnealing(distPoint, route, points):
    s = math.inf
    T = t_start

    randone  = [random.random() for i in range(m)]  # список сгененрированных чисел от 1 до 100 для всех итераций
    # for i in range(len(route)-1):
    #     s += distPoint[route[i], route[i+1]]
    for i in range(1, m):  # время от кол-ва итераций

        sP = 0  # сбрасываем потенциальное расстояние
        routeP = route.copy()  # потенциальный маршрут
        transp = random.sample(range(1,len(route)-1), k=2) # два случайных индекса городов
        routeP[transp[0]], routeP[transp[1]] = routeP[transp[1]], routeP[transp[0]]

        for j in range(len(routeP)-1):
            sP += distPoint[routeP[j], routeP[j+1]]
        if s > sP:
            s = sP
            route = routeP
        else:
            p = math.exp(-(sP-s)/T)
            if p >= randone[i]:
                s = sP
                route = routeP
        if i % 10 ==0:
            T = t_start / i
        if T < t_end:
            print(i)
            break
    pointOptimum = []
    for i in route:
        pointOptimum.append(points[i])

    return pointOptimum, s

def sa(point, start, finish):
    points = point.copy()
    # route = createRoute(points, start, finish)
    # генерируем случайный список индексов городов без первого и последнего
    route = random.sample(range(1,len(points)+1), k=(len(points)) )

    # добавляем старт и финиш если он есть к списку городов и к списку индексов городов
    points.insert(0, start)
    route.insert(0, 0)
    if finish:
        points.append(finish)
        route.append(len(points)-1)
    else:
        points.append(start)
        route.append(0)

    # создаем матрицу расстояний
    distPoint = distance(points)

    # print(distPoint)
    return simulatedAnnealing(distPoint, route, points)

# def sa2(k):
#     points = k.copy()
#     route = [i for i in range(len(points)-1)]
#     if points[0] == points[-1]:
#         route.append(0)
#     else:
#         route.append(len(points)-1)
#
#     distPoint = distance(points)
#     return simulatedAnnealing(distPoint, route, points)