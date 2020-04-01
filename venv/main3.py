from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from shortway2 import Ui_MainWindow

import os, math

MODES = [
    'start', 'finish', 'point', 'line', 'pen'
]

WINDOW_SIZE = 798, 500

PREVIEW_PEN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.SolidLine)
primary_color = QColor(Qt.red)

class Scene(QGraphicsScene):

    mode = ''
    start = None
    finish = None
    primary_color = QColor(Qt.red)
    value = 10
    image = QGraphicsItemGroup()
    object = QGraphicsItemGroup()
    length_line = 0
    timer_event = None

    def initialize(self):
        self.setSceneRect(QRectF(0, 62, *WINDOW_SIZE))  # координаты сцены относительно окна программы
        felt = QBrush(QColor(Qt.white))  # цвет фонф
        self.setBackgroundBrush(felt)  # установка фона
        self.reset()

    def reset(self):
        self.clear()
        self.start = False
        self.finish = False
        self.mode = ''
        self.value = 10
        self.length_line = 0

    def set_mode(self, mode):
        self.timer_cleanup()

        self.last_pos = None
        self.origin_pos = None
        self.current_pos = None

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
            timer_event(final=True)


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


    def generic_mousePressEvent(self, e):
        self.last_pos = e.scenePos()

    def generic_mouseReleaseEvent(self, e):
        self.last_pos = None

    # Pen events

    def pen_mousePressEvent(self, e):
        self.generic_mousePressEvent(e)

    def pen_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QGraphicsLineItem(self.last_pos.x(), self.last_pos.y(),
                                  e.scenePos().x(),e.scenePos().y())
            p.setPen(QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
            self.addItem(p)
            self.length_line += 1
            self.last_pos = e.scenePos()
            print(self.last_pos)
            # self.update()

    def pen_mouseReleaseEvent(self, e):
        self.generic_mouseReleaseEvent(e)
        print(self.length_line)

    # Line events
    def line_mousePressEvent(self, e):
        self.last_pos = e.scenePos()

    def line_mouseReleaseEvent(self, e):
        if self.last_pos:
            p = QGraphicsLineItem(self.last_pos.x(), self.last_pos.y(),
                                  e.scenePos().x(), e.scenePos().y())
            p.setPen(QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.addItem(p)
            self.update()

    # def line_mousePressEvent(self, e):
    #     self.origin_pos = e.scenePos()
    #     self.current_pos = e.scenePos()
    #     self.timer_event = self.line_timerEvent
    #
    # def line_timerEvent(self, final=False):
    #     # p = QGraphicsLineItem(self.origin_pos.x(), self.origin_pos.y(),
    #     #                       self.last_pos().x(), self.last_pos().y())
    #     # p2 = QGraphicsLineItem(self.origin_pos.x(), self.origin_pos.y(),
    #     #                       self.current_pos().x(), self.current_poss().y())
    #     # p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
    #     # p.setPen(QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
    #     if self.last_pos:
    #         p = QGraphicsLineItem(self.origin_pos.x(), self.origin_pos.y(),
    #                               self.last_pos().x(), self.last_pos().y())
    #         p.setPen(QPen(self.primary_color, self.value / 5, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
    #         self.addItem(p)
    #
    #     if not final:
    #         p2 = QGraphicsLineItem(self.origin_pos.x(), self.origin_pos.y(),
    #                                self.current_pos().x(), self.current_pos().y())
    #         p2.setPen(QPen(self.primary_color, self.value / 5, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
    #         self.addItem(p2)
    #
    #     self.update()
    #     self.last_pos = self.current_pos
    #
    # def line_mouseMoveEvent(self, e):
    #     self.current_pos = e.scenePos()
    #
    # def line_mouseReleaseEvent(self, e):
    #     if self.last_pos:
    #         # Clear up indicator.
    #         self.timer_cleanup()
    #         p = QGraphicsLineItem(self.last_pos.x(), self.last_pos.y(),
    #                               e.scenePos().x(), e.scenePos().y())
    #         p.setPen(QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    #         self.addItem(p)
    #         self.update()
    #     self.reset_mode()

    # Ellipse events

    def point_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            p = QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)  # настройки карандаша
            point = QGraphicsEllipseItem(QRectF(e.scenePos().x()-self.value,
                                                e.scenePos().y()-self.value,
                                                self.value*2, self.value*2))
            point.setPen(p)
            # self.object.addToGroup(point)
            self.addItem(point)

    # Finish events

    def finish_mousePressEvent(self, e):
        p = QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        if not self.finish and e.button() == Qt.LeftButton:
            self.addEllipse(e.scenePos().x()-self.value, e.scenePos().y()-self.value, self.value*2, self.value*2, p)
            self.addEllipse(e.scenePos().x()-(self.value+self.value/3), e.scenePos().y()-(self.value+self.value/3),
                                  (self.value+self.value/3)*2, (self.value+self.value/3)*2, p)
            self.finish = True

    # Start events

    def start_mousePressEvent(self, e):
        if not self.start and e.button() == Qt.LeftButton:
            p = QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
            polygon = QPolygonF()
            polygon.append(QPointF(e.scenePos().x(), e.scenePos().y() - self.value*3 / 3 * math.sqrt(3)))
            polygon.append(QPointF(e.scenePos().x() - self.value*3/2, e.scenePos().y() + self.value*3 / 6 * math.sqrt(3)))
            polygon.append(QPointF(e.scenePos().x() + self.value*3/2, e.scenePos().y() + self.value*3 / 6 * math.sqrt(3)))
            self.addPolygon(polygon, p)
            self.start = True


    def changeSize(self, value):
        print(value)
        self.value = value
        self.scene.update()
        self.graphicsView.update()


class MainWindow(QMainWindow, Ui_MainWindow):

    mode = ''
    start = None
    finish = None
    primary_color = QColor(Qt.red)
    value = 10

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
        self.actionClear.triggered.connect(self.reset)

        # Change size
        self.horizontalSlider.valueChanged.connect(self.changeSize)

        self.show()

    def reset(self):
        self.scene.clear()
        self.scene.start = False
        self.scene.finish = False
        self.scene.mode = ''
        self.scene.value = 10
        self.scene.length_line = 0
        self.horizontalSlider.setValue(10)


    def changeSize(self, value):
        print(value)
        self.scene.value = value
        self.scene.update()
        self.graphicsView.update()

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


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()