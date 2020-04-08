from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from shortway2 import Ui_MainWindow
import algoritm

import os, math

MODES = [
    'start', 'finish', 'point', 'line', 'pen', 'zone'
]

WINDOW_SIZE = 798, 500

PREVIEW_PEN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.SolidLine)
primary_color = QColor(Qt.red)
scale = [1, 1, 1, 2.75, 1, 1, 1, 1, 1]


class Scene(QGraphicsScene):

    image = QGraphicsItemGroup()
    objectPoint = []
    objectStart = []
    objectFinish = []
    objectPen = []
    objectLine = []
    objectZone = []
    fillZone = []  # Сборщик всех точек зоны для ее заливки
    points = []  # координаты точек КП
    pathPoints = []  # координаты точек КП отсортированные по алгоритму
    objectPath = []  # линии пути по алгоритму

    def initialize(self):
        self.setSceneRect(QRectF(0, 62, *WINDOW_SIZE))  # координаты сцены относительно окна программы
        felt = QBrush(QColor(Qt.white))  # цвет фонф
        self.setBackgroundBrush(felt)  # установка фона
        self.reset()

    def reset(self):
        self.clear()  # очистиить все изображения
        self.startPoint = None
        self.finishPoint = None  # финишная позиция координаты
        self.points.clear()
        self.pathPoints.clear()
        self.mode = ''
        self.value = 10  # масштабирование карты начинается от 10 до 30
        self.scale = 1  # коэфициент масштаба для расчета длины
        self.length_line = 0  # длина пути линии
        self.length_pen = 0  # длина пути карандаша
        self.timer_event = None  # запуск обработчика таймера
        self.fill = []  # сборщик всех закрашенных зон

    def set_mode(self, mode):
        self.timer_cleanup()

        self.last_pos = None
        self.origin_pos = None
        self.current_pos = None
        self.history_pos = None
        self.line = None
        self.fillZone.clear()  # очищаем точки предыдущей зоны для рисовки следующей

        self.pen = QPen(QColor(Qt.red), self.value / 5, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin)
        self.penZone = QPen(QColor(Qt.black), self.value / 5, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin)

        self.mode = mode

    def reset_mode(self):
        self.set_mode(self.mode)

    def on_timer(self):
        if self.timer_event:
            self.timer_event()

    def timer_cleanup(self):
        if self.timer_event:
            # Stop the timer, then trigger cleanup.
            timer_event = self.timer_event
            self.timer_event = None

    def mousePressEvent(self, e):
        fn = getattr(self, "%s_mousePressEvent" % self.mode, None)
        if fn:
            return fn(e)

    def mouseMoveEvent(self, e):
        fn = getattr(self, "%s_mouseMoveEvent" % self.mode, None)
        if fn:
            return fn(e)

    def mouseReleaseEvent(self, e):
        fn = getattr(self, "%s_mouseReleaseEvent" % self.mode, None)
        if fn:
            return fn(e)

    def mouseDoubleClickEvent(self, e):
        fn = getattr(self, "%s_mouseDoubleClickEvent" % self.mode, None)
        if fn:
            return fn(e)

    # Pen events

    def pen_mousePressEvent(self, e):
        self.last_pos = e.scenePos()

    def pen_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QGraphicsLineItem(self.last_pos.x(), self.last_pos.y(),
                                  e.scenePos().x(),e.scenePos().y())
            p.setPen(self.pen)
            self.objectPen.append(p)
            self.addItem(p)
            self.length_pen += 1*self.scale
            self.last_pos = e.scenePos()
            self.update()

    def pen_mouseReleaseEvent(self, e):
        self.last_pos = None
        print(self.length_pen)

        # Line events

    def line_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.history_pos:
                p = QGraphicsLineItem(self.history_pos[-1].x(), self.history_pos[-1].y(),
                                          self.last_pos.x(), self.last_pos.y())
                p.setPen(self.pen)
                self.objectLine.append(p)
                self.addItem(self.objectLine[-1])
                self.length_line += int((math.fabs(
                    math.sqrt((float(self.last_pos.x()) - float(self.history_pos[-1].x())) ** 2 +
                              (float(self.last_pos.y()) - float(self.history_pos[-1].y())) ** 2)))*self.scale)


                self.history_pos.append(self.last_pos)

            else:
                self.history_pos = [e.scenePos()]
                self.current_pos = e.scenePos()
                self.timer_event = self.line_timerEvent

        elif e.button() == Qt.RightButton and self.history_pos:
            # Clean up, we're not drawing
            self.timer_cleanup()
            self.reset_mode()
            self.update()

    def line_timerEvent(self):
        if self.last_pos:
            p = QGraphicsLineItem(self.history_pos[-1].x(), self.history_pos[-1].y(),
                                      self.last_pos.x(), self.last_pos.y())
            p.setPen(self.pen)
            if self.line:
                self.removeItem(self.line)
            self.line = p
            self.addItem(p)

        self.update()
        self.last_pos = self.current_pos

    def line_mouseMoveEvent(self, e):
        self.current_pos = e.scenePos()

    def line_mouseReleaseEvent(self, e):
        if self.origin_pos:
            self.current_pos = e.scenePos()

    def line_mouseDoubleClickEvent(self, e):
        self.timer_cleanup()

        if self.line:
            self.removeItem(self.line)

        self.update()
        self.reset_mode()
        print(self.length_line)

    # Zone events

    def zone_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.history_pos:
                coordinates = QPointF(self.history_pos[-1].x(), self.history_pos[-1].y())
                self.fillZone.append(coordinates)
                p = QGraphicsLineItem(self.history_pos[-1].x(), self.history_pos[-1].y(),
                                      self.last_pos.x(), self.last_pos.y())
                p.setPen(self.penZone)
                self.objectZone.append(p)
                self.addItem(self.objectZone[-1])
                self.history_pos.append(self.last_pos)

            else:

                self.origin_pos = e.scenePos()
                self.history_pos = [e.scenePos()]
                self.current_pos = e.scenePos()
                self.timer_event = self.zone_timerEvent

        elif e.button() == Qt.RightButton and self.history_pos:
            # Clean up, we're not drawing
            self.timer_cleanup()
            self.reset_mode()
        self.update()

    def zone_timerEvent(self):
        if self.last_pos:
            p = QGraphicsLineItem(self.history_pos[-1].x(), self.history_pos[-1].y(),
                                  self.last_pos.x(), self.last_pos.y())
            p.setPen(self.penZone)
            if self.line:
                self.removeItem(self.line)
            self.line = p
            self.addItem(p)

        self.update()
        self.last_pos = self.current_pos

    def zone_mouseMoveEvent(self, e):
        self.current_pos = e.scenePos()

    def zone_mouseReleaseEvent(self, e):
        if self.origin_pos:
            self.current_pos = e.scenePos()

    def zone_mouseDoubleClickEvent(self, e):
        self.timer_cleanup()
        coordinates = QPointF(self.history_pos[-1].x(), self.history_pos[-1].y())
        self.fillZone.append(coordinates)
        p = QGraphicsLineItem(self.history_pos[-1].x(), self.history_pos[-1].y(),
                              self.origin_pos.x(), self.origin_pos.y())
        p.setPen(self.penZone)
        if self.line:
            self.removeItem(self.line)
        self.objectZone.append(p)
        self.addItem(p)

        polygon = QPolygonF()
        for i in self.fillZone:
            polygon.append(i)
        fill = QGraphicsPolygonItem()
        fill.setBrush(QColor(Qt.darkBlue))
        fill.setPolygon(polygon)
        self.fill.append(fill)
        self.addItem(fill)

        self.update()
        self.reset_mode()

    # Ellipse events

    def point_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            point = QGraphicsEllipseItem(QRectF(e.scenePos().x()-self.value,
                                                e.scenePos().y()-self.value,
                                                self.value*2, self.value*2))
            point.setPen(self.pen)  # настройки карандаша
            self.objectPoint.append(point)  # сохраняем все круги для удаления последующего
            self.addItem(point)
            self.points.append(e.scenePos())  # сохраняем все центра кругов для нахождения оптимального пути
            self.update()

    # Finish events

    def finish_mousePressEvent(self, e):
        if not self.finishPoint and e.button() == Qt.LeftButton:
            finish_circle = QGraphicsEllipseItem(QRectF(e.scenePos().x()-self.value, e.scenePos().y()-self.value, self.value*2, self.value*2))
            finish_circle.setPen(self.pen)
            self.objectFinish.append(finish_circle)
            self.addItem(finish_circle)
            finish_circle2 = QGraphicsEllipseItem(QRectF(e.scenePos().x()-(self.value+self.value/3), e.scenePos().y()-(self.value+self.value/3),
                                  (self.value+self.value/3)*2, (self.value+self.value/3)*2))
            finish_circle2.setPen(self.pen)
            self.objectFinish.append(finish_circle2)
            self.addItem(finish_circle2)
            self.finishPoint = e.scenePos()
            self.update()

    # Start events

    def start_mousePressEvent(self, e):
        if not self.startPoint and e.button() == Qt.LeftButton:
            polygon = QPolygonF()
            polygon.append(QPointF(e.scenePos().x(), e.scenePos().y() - self.value * 3 / 3 * math.sqrt(3)))
            polygon.append(QPointF(e.scenePos().x() - self.value * 3 / 2, e.scenePos().y() + self.value * 3 / 6 * math.sqrt(3)))
            polygon.append(QPointF(e.scenePos().x() + self.value * 3 / 2, e.scenePos().y() + self.value * 3 / 6 * math.sqrt(3)))
            start = QGraphicsPolygonItem()
            start.setPen(self.pen)
            start.setPolygon(polygon)

            self.objectStart.append(start)
            self.addItem(start)
            self.startPoint = e.scenePos()
            self.update()

    def changeSize(self, value):
        self.value = value
        self.scene.update()
        self.graphicsView.update()

    def pathLine(self):
        for i in range(len(self.pathPoints)-1):
            p = QGraphicsLineItem(QPointF.x(self.pathPoints[i]), QPointF.y(self.pathPoints[i]),
                                  QPointF.x(self.pathPoints[i+1]), QPointF.y(self.pathPoints[i+1]))
            p.setPen(self.pen)
            self.objectPath.append(p)
            self.addItem(p)
        self.update()

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.scene = Scene()
        self.scene.initialize()
        self.graphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # Задаем выравнивание сцены относительно верхнего левого угла
        self.graphicsView.setScene(self.scene)  # инициализация сцены
        # self.graphicsView.mapFromScene(0,62)
        # self.graphicsView.translate(0,62)

        # self.object.setFlag(QGraphicsItem.ItemIsMovable)

        # Setup the mode buttons
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)

        for mode in MODES:
            btn = getattr(self, '%sButton' % mode)
            btn.pressed.connect(lambda mode=mode: self.scene.set_mode(mode))
            self.mode_group.addButton(btn)

        # Initialize animation timer.
        self.timer = QTimer()
        self.timer.timeout.connect(self.scene.on_timer)
        self.timer.setInterval(100)
        self.timer.start()

        # Menu options
        self.actionNew.triggered.connect(self.new_file)
        self.actionOpen.triggered.connect(self.new_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionClearAll.triggered.connect(self.reset)
        self.actionClearStart.triggered.connect(lambda: self.clear('Start'))
        self.actionClearFinish.triggered.connect(lambda: self.clear('Finish'))
        self.actionClearPoint.triggered.connect(lambda: self.clear('Point'))
        self.actionClearLine.triggered.connect(lambda: self.clear('Line'))
        self.actionClearPen.triggered.connect(lambda: self.clear('Pen'))
        self.actionClearZone.triggered.connect(lambda: self.clear('Zone'))
        self.actionAbout.triggered.connect(self.helpWindow)
        self.actionShortWay.triggered.connect(self.shortWay)
        self.actionOptimalWay.triggered.connect(self.shortWayOpt)

        # Change size
        self.horizontalSlider.valueChanged.connect(self.changeSize)

        # Change scale
        self.comboBox.currentIndexChanged.connect(self.changeScale)

        self.show()

    def reset(self):
        self.scene.reset()
        self.horizontalSlider.setValue(10)

    def clear(self, mode):
        fn = getattr(self.scene, 'object%s' % mode)
        for i in fn:
            self.scene.removeItem(i)
        fn.clear()
        if mode == 'Start':
            self.scene.startPoint = None
        if mode == 'Finish':
            self.scene.finishPoint = None
        if mode == 'Point':
            self.scene.points.clear()
        if mode == 'Line':
            self.scene.length_line = 0
        if mode == 'Pen':
            self.scene.length_pen = 0
        if mode == 'Zone':
            self.scene.fillZone.clear()
            for i in self.scene.fill:
                self.scene.removeItem(i)
        if mode == 'Path':
            self.scene.pathPoints.clear()
        self.scene.mode = ''

    def changeSize(self, value):
        print(value)
        self.scene.value = value
        self.scene.update()
        self.graphicsView.update()

    def changeScale(self, index):
        print(index)
        self.scene.scale = scale[index]  # выбираем кооэфициент умножения от масштаба для расчета длины пути

    def new_file(self):
        """
        Open image file for editing, scaling the smaller dimension and cropping the remainder.
        :return:
        """
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                              "PNG image files (*.png); JPEG image files (*jpg); All files (*.*)")

        if path:
            self.reset()
            newImage = QGraphicsPixmapItem()
            pixmap = QPixmap()
            pixmap.load(path)

            # We need to crop down to the size of our canvas. Get the size of the loaded image.
            iw = pixmap.width()
            ih = pixmap.height()

            # Get the size of the space we're filling.
            cw, ch = WINDOW_SIZE

            if iw / cw < ih / ch:  # The height is relatively bigger than the width.
                pixmap = pixmap.scaledToWidth(cw)
                # hoff = (pixmap.height() - ch) // 2
                # pixmap = pixmap.copy(
                #     QRect(QPoint(0, hoff), QPoint(cw, pixmap.height() - hoff))
                # )

            elif iw / cw > ih / ch:  # The height is relatively bigger than the width.
                pixmap = pixmap.scaledToHeight(ch)
                # woff = (pixmap.width() - cw) // 2
                # pixmap = pixmap.copy(
                #     QRect(QPoint(woff, 0), QPoint(pixmap.width() - woff, ch))
                # )
            newImage.setOffset(0,62)
            newImage.setPixmap(pixmap)
            # newImage.setFlag(QGraphicsItem.ItemIsMovable, True)  # позволяет двигать изображение
            self.scene.image.addToGroup(newImage)
            self.scene.addItem(newImage)

    def save_file(self):
        """
        Save active canvas to image file.
        :return:
        """
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "PNG Image file (*.png)")

        if path:
            # Get region of scene to capture from somewhere.
            rect_f = self.scene.sceneRect()

            # Create a QImage to render to and fix up a QPainter for it.
            img = QImage(QSize(2873, 2016), QImage.Format_RGB888)
            p = QPainter(img)
            self.scene.render(p, target=QRectF(img.rect()), source=rect_f)
            p.end()  # конец рисовки я так понимаю
            img.save(path, "PNG")

    def helpWindow(self):
        QMessageBox.about(window, "Help", "Программа для нахождения оптимального "
                                    "маршрута на картах для спортивного ориентирования")
    def shortWay(self):
        # print(len(self.scene.points), QPointF.x(self.scene.points[0]))
        print(self.scene.points)
        if self.scene.pathPoints:  # надо проверять наличие линий, но лишнюю строчку не хочется
            # вводить, проверяю наличие точек пути, был ли раньше построен путь или нет.
            # без проверки рисовки. т.к. они зависимы
            self.clear('Path')
        self.scene.pathPoints = algoritm.neigbourAlgoritm(self.scene.points, self.scene.startPoint, self.scene.finishPoint)
        self.scene.pathLine()
        print(self.scene.points)

    def shortWayOpt(self):
        pass

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()