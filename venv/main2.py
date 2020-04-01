from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from shortway2 import Ui_MainWindow

import os, math

MODES = [
    'start', 'finish', 'point', 'line'
]

WINDOW_SIZE = 790, 500

PREVIEW_PEN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.SolidLine)
primary_color = QColor(Qt.red)

# class SceneView(QGraphicsView):
#
#     # sceneView = QGraphicsScene()
#     # self.setScene(sceneView)
#     primary_color = QColor(Qt.red)
#     active_color = None
#     preview_pen = None
#
#     timer_event = None
#     start = None
#     finish = None
#
#     mode = 'rectangle'
#
#     # Store configuration settings, including pen width, fonts etc.
#     config = {
#         # Drawing options.
#         'size': 1,  # толщина линии
#         'fill': True,
#     }
#
#     def initialize(self):
#         self.background_color = QColor(Qt.white)
#         self.reset()
#
#     def reset(self):
#         # # Create the pixmap for display.
#         # self.setPixmap(QPixmap(*CANVAS_DIMENSIONS))
#         #
#         # # Clear the canvas.
#         # self.pixmap().fill(self.background_color)
#         self.clear()
#         self.setBackgroundBrush(QBrush(QColor(237, 237, 237)))
#         # self.drawBackground(QPainter.QBrush(QColor(255,170,255), Qt.SolidPattern))
#         # обновить прорисовку для старта и финиша
#         self.start = False
#         self.finish = False
#
#     def set_config(self, key, value):
#         self.config[key] = value
#
#     def set_mode(self, mode):
#         self.origin_pos = None
#
#         self.current_pos = None
#         self.last_pos = None
#
#         self.history_pos = None
#         self.last_history = []
#
#         self.current_text = ""
#         self.last_text = ""
#
#         self.last_config = {}
#
#         self.dash_offset = 0
#         self.locked = False
#         # Apply the mode
#         self.mode = mode
#
#     def reset_mode(self):
#         self.set_mode(self.mode)
#
#
#

class MainWindow(QMainWindow, Ui_MainWindow):

    mode = ''
    start = None
    finish = None
    primary_color = QColor(Qt.red)
    value = 10

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 62, *WINDOW_SIZE))  # координаты сцены относительно окна программы
        felt = QBrush(QColor(Qt.white))  # цвет фонф
        self.scene.setBackgroundBrush(felt)  # установка фона
        self.graphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # Задаем выравнивание сцены относительно верхнего левого угла
        self.graphicsView.setScene(self.scene)  # инициализация сцены
        # self.graphicsView.translate(0,62)

        self.image = QGraphicsItemGroup()
        self.object = QGraphicsItemGroup()
        # self.object.setFlag(QGraphicsItem.ItemIsMovable)

        # Setup the mode buttons
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)

        for mode in MODES:
            btn = getattr(self, '%sButton' % mode)
            btn.pressed.connect(lambda mode=mode: self.set_mode(mode))
            self.mode_group.addButton(btn)


        # Menu options
        self.actionNew.triggered.connect(self.new_file)
        self.actionOpen.triggered.connect(self.new_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionClear.triggered.connect(self.reset)

        # Scale
        # self.comboBox.

        # Change size
        self.horizontalSlider.valueChanged.connect(self.changeSize)

        self.show()

    def reset(self):
        self.scene.clear()
        self.start = False
        self.finish = False
        self.mode = ''
        self.value = 10
        self.horizontalSlider.setValue(10)

    def set_mode(self, mode):
        # Apply the mode
        self.mode = mode

    def reset_mode(self):
        self.set_mode(self.mode)

    # Mouse events.

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

    # Ellipse events

    def point_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            p = QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)  # настройки карандаша
            point = QGraphicsEllipseItem(QRectF(e.x()-self.value, e.y()-self.value, self.value*2, self.value*2))
            point.setPen(p)
            self.object.addToGroup(point)
            self.scene.addItem(point)
            # print(self.scene.items())

    # Finish events

    def finish_mousePressEvent(self, e):
        p = QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        if not self.finish:
            self.scene.addEllipse(e.x()-self.value, e.y()-self.value, self.value*2, self.value*2, p)
            self.scene.addEllipse(e.x()-(self.value+self.value/3), e.y()-(self.value+self.value/3),
                                  (self.value+self.value/3)*2, (self.value+self.value/3)*2, p)
            self.finish = True

    # Start events

    def start_mousePressEvent(self, e):
        if not self.start:
            p = QPen(self.primary_color, self.value/5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
            polygon = QPolygonF()
            polygon.append(QPointF(e.x(), e.y() - self.value*3 / 3 * math.sqrt(3)))
            polygon.append(QPointF(e.x() - self.value*3/2, e.y() + self.value*3 / 6 * math.sqrt(3)))
            polygon.append(QPointF(e.x() + self.value*3/2, e.y() + self.value*3 / 6 * math.sqrt(3)))
            self.scene.addPolygon(polygon, p)
            self.start = True

    def changeSize(self, value):
        print(value)
        self.value = value  
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
                hoff = (pixmap.height() - ch) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(0, hoff), QPoint(cw, pixmap.height() - hoff))
                )

            elif iw / cw > ih / ch:  # The height is relatively bigger than the width.
                pixmap = pixmap.scaledToHeight(ch)
                woff = (pixmap.width() - cw) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(woff, 0), QPoint(pixmap.width() - woff, ch))
                )

            newImage.setPixmap(pixmap)
            # newImage.setFlag(QGraphicsItem.ItemIsMovable, True)  # позволяет двигать изображение
            self.image.addToGroup(newImage)
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