from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from shortway import Ui_MainWindow

import os, math

MODES = [
    'start', 'finish', 'point', 'line'
]

CANVAS_DIMENSIONS = 800, 500

PREVIEW_PEN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.SolidLine)


class Canvas(QLabel):
    primary_color = QColor(Qt.red)
    active_color = None
    preview_pen = None

    timer_event = None
    start = None
    finish = None

    mode = 'rectangle'

    # Store configuration settings, including pen width, fonts etc.
    config = {
        # Drawing options.
        'size': 1,  # толщина линии
        'fill': True,
        # # Font options.
        # 'font': QFont('Times'),
        # 'fontsize': 12,
        # 'bold': False,
        # 'italic': False,
        # 'underline': False,
    }

    def initialize(self):
        self.background_color = QColor(Qt.white)
        # self.eraser_color = QColor(self.secondary_color) if self.secondary_color else QColor(Qt.white)
        # self.eraser_color.setAlpha(100)
        self.reset()

    def reset(self):
        # Create the pixmap for display.
        self.setPixmap(QPixmap(*CANVAS_DIMENSIONS))

        # Clear the canvas.
        self.pixmap().fill(self.background_color)
        # обновить прорисовку для старта и финиша
        self.start = False
        self.finish = False

    def set_config(self, key, value):
        self.config[key] = value

    def set_mode(self, mode):
        # Clean up active timer animations.
        self.timer_cleanup()
        # Reset mode-specific vars (all)
        self.active_shape_fn = None
        self.active_shape_args = ()

        self.origin_pos = None

        self.current_pos = None
        self.last_pos = None

        self.history_pos = None
        self.last_history = []

        self.current_text = ""
        self.last_text = ""

        self.last_config = {}

        self.dash_offset = 0
        self.locked = False
        # Apply the mode
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

    # Generic events (shared by brush-like tools)

    def generic_mousePressEvent(self, e):
        self.last_pos = e.pos()

        if e.button() == Qt.LeftButton:
            self.active_color = self.primary_color
        # else:
        #     self.active_color = self.secondary_color

    def generic_mouseReleaseEvent(self, e):
        self.last_pos = None

    # Generic shape events: Rectangle, Ellipse, Rounded-rect

    def generic_shape_mousePressEvent(self, e):
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.timer_event = self.generic_shape_timerEvent

    def generic_shape_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        pen.setDashOffset(self.dash_offset)
        p.setPen(pen)
        if self.last_pos:
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, self.last_pos), *self.active_shape_args)

        if not final:
            self.dash_offset -= 1
            pen.setDashOffset(self.dash_offset)
            p.setPen(pen)
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, self.current_pos), *self.active_shape_args)

        self.update()
        self.last_pos = self.current_pos

    def generic_shape_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def generic_shape_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Clear up indicator.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))

            # if self.config['fill']:
            #     p.setBrush(QBrush(self.secondary_color))
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, e.pos()), *self.active_shape_args)
            self.update()

        self.reset_mode()

    # Ellipse events

    def point_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
            p.drawEllipse(e.pos(), 10, 10)
            self.update()
            self.reset_mode()

    # Finish events

    def finish_mousePressEvent(self, e):
        p = QPainter(self.pixmap())
        p.setPen(QPen(self.primary_color, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        if not self.finish:
            p.drawEllipse(e.pos(), 10, 10)
            p.drawEllipse(e.pos(), 13, 13)
            self.finish = True
            self.update()
            self.reset_mode()
        else:
            pass

    # Start events

    def start_mousePressEvent(self, e):
        if not self.start:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
            polygon = QPolygonF()
            polygon.append(QPointF(e.x(), e.y() - 30 / 3 * math.sqrt(3)))
            polygon.append(QPointF(e.x() - 15, e.y() + 30 / 6 * math.sqrt(3)))
            polygon.append(QPointF(e.x() + 15, e.y() + 30 / 6 * math.sqrt(3)))
            p.drawPolygon(polygon)
            # p.drawPolygon([QPointF(e.x(), e.y() + 10/3*math.sqrt(3)),
            #                QPointF(e.x()-5, e.y() - 5/3*math.sqrt(3)),
            #                QPointF(e.x()+5, e.y()-5/3*math.sqrt(3))])
            self.start = True
            self.update()
            self.reset_mode()


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Replace canvas placeholder from QtDesigner.
        self.canvas = Canvas()
        self.canvas.initialize()
        # We need to enable mouse tracking to follow the mouse without the button pressed.
        self.canvas.setMouseTracking(True)
        # Enable focus to capture key inputs.
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.verticalLayout.addWidget(self.canvas)

        # Setup the mode buttons
        mode_group = QButtonGroup(self)
        mode_group.setExclusive(True)

        for mode in MODES:
            btn = getattr(self, '%sButton' % mode)
            btn.pressed.connect(lambda mode=mode: self.canvas.set_mode(mode))
            mode_group.addButton(btn)

        # Setup the color selection buttons.
        # self.primaryButton.pressed.connect(lambda: self.choose_color(self.set_primary_color))
        # self.secondaryButton.pressed.connect(lambda: self.choose_color(self.set_secondary_color))

        # Initialize button colours.
        # for n, hex in enumerate(COLORS, 1):
        #     btn = getattr(self, 'colorButton_%d' % n)
        #     btn.setStyleSheet('QPushButton { background-color: %s; }' % hex)
        #     btn.hex = hex  # For use in the event below
        #
        #     def patch_mousePressEvent(self_, e):
        #         if e.button() == Qt.LeftButton:
        #             self.set_primary_color(self_.hex)
        #
        #         elif e.button() == Qt.RightButton:
        #             self.set_secondary_color(self_.hex)
        #
        #     btn.mousePressEvent = types.MethodType(patch_mousePressEvent, btn)

        # Initialize animation timer.
        self.timer = QTimer()
        self.timer.timeout.connect(self.canvas.on_timer)
        self.timer.setInterval(100)
        self.timer.start()

        # Setup to agree with Canvas.
        # self.set_primary_color('#000000')
        # self.set_secondary_color('#ffffff')

        # Signals for canvas-initiated color changes (dropper).
        # self.canvas.primary_color_updated.connect(self.set_primary_color)
        # self.canvas.secondary_color_updated.connect(self.set_secondary_color)

        # Menu options
        self.actionNew.triggered.connect(self.open_file)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionClear.triggered.connect(self.canvas.reset)

        self.show()

    def open_file(self):
        """
        Open image file for editing, scaling the smaller dimension and cropping the remainder.
        :return:
        """
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                              "PNG image files (*.png); JPEG image files (*jpg); All files (*.*)")

        if path:
            pixmap = QPixmap()
            pixmap.load(path)

            # We need to crop down to the size of our canvas. Get the size of the loaded image.
            iw = pixmap.width()
            ih = pixmap.height()

            # Get the size of the space we're filling.
            cw, ch = CANVAS_DIMENSIONS

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

            self.canvas.setPixmap(pixmap)

    def save_file(self):
        """
        Save active canvas to image file.
        :return:
        """
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "PNG Image file (*.png)")

        if path:
            pixmap = self.canvas.pixmap()
            pixmap.save(path, "PNG")


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()