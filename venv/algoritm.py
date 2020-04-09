from PyQt5.QtCore import *
import math

def neigbourAlgoritm(points, start, finish):
    point = points.copy()
    neighbor = []
    neighbor.append(start)
    dist = 0  #  длина пути

    while point:
        # берем как отправную длину, длина от последний точки до первого элемента в списке точек
        d = math.fabs((QPointF.x(neighbor[-1]) - QPointF.x(point[0])) ** 2 +
                (QPointF.y(neighbor[-1]) - QPointF.y(point[0])) ** 2) ** 0.5
        indexPop = 0  # индекс элемента который будет ближайший, чтобы его потом вычеркнуть из списка

        for index, i in enumerate(point):
            # считаем все длины от записанной точки пути до точек списка и сравниваем с отправной длиной
            d1 = math.fabs((QPointF.x(neighbor[-1]) - QPointF.x(i)) ** 2 +
                 (QPointF.y(neighbor[-1]) - QPointF.y(i)) ** 2) ** 0.5
            if d > d1: #  если новый варинат пути короче то делаем его отправным
                d = d1
                indexPop = index  # ближайшая точка. берем ее индекс чтобы из списка вычеркнуть
        dist += d  # считаем длину
        neighbor.append(point[indexPop])
        point.pop(indexPop)

    if finish:
        neighbor.append(finish)

    return neighbor, dist