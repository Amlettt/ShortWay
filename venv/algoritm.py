from PyQt5.QtCore import *
import math

def neigbourAlgoritm(points, start, finish):
    point = points.copy()
    neighbor = []
    neighbor.append(start)

    while point:

        dist = math.fabs((QPointF.x(neighbor[-1]) - QPointF.x(point[0])) ** 2 +
                (QPointF.y(neighbor[-1]) - QPointF.y(point[0])) ** 2) ** 0.5
        indexPop = 0

        for index, i in enumerate(point):
            d = math.fabs((QPointF.x(neighbor[-1]) - QPointF.x(i)) ** 2 +
                 (QPointF.y(neighbor[-1]) - QPointF.y(i)) ** 2) ** 0.5
            if dist > d:
                dist = d
                indexPop = index  # ближайшая точка. берем ее индекс чтобы из списка вычеркнуть

        neighbor.append(point[indexPop])
        point.pop(indexPop)

    if finish:
        neighbor.append(finish)

    return neighbor