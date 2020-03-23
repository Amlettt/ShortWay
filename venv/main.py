from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from shortway import Ui_MainWindow

import os

MODES = [
    'start', 'finish', 'point', 'line'
]

CANVAS_DIMENSIONS = 800, 500

class Canvas(QLabel):

    primary_color = QColor(Qt.black)
    active_color = None
    preview_pen = None

    timer_event = None

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
        # mode_group = QButtonGroup(self)
        # mode_group.setExclusive(True)
        #
        # for mode in MODES:
        #     btn = getattr(self, '%sButton' % mode)
        #     btn.pressed.connect(lambda mode=mode: self.canvas.set_mode(mode))
        #     mode_group.addButton(btn)

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
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.canvas.on_timer)
        # self.timer.setInterval(100)
        # self.timer.start()

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
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "PNG image files (*.png); JPEG image files (*jpg); All files (*.*)")

        if path:
            pixmap = QPixmap()
            pixmap.load(path)

            # We need to crop down to the size of our canvas. Get the size of the loaded image.
            iw = pixmap.width()
            ih = pixmap.height()

            # Get the size of the space we're filling.
            cw, ch = CANVAS_DIMENSIONS

            if iw/cw < ih/ch:  # The height is relatively bigger than the width.
                pixmap = pixmap.scaledToWidth(cw)
                hoff = (pixmap.height() - ch) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(0, hoff), QPoint(cw, pixmap.height()-hoff))
                )

            elif iw/cw > ih/ch:  # The height is relatively bigger than the width.
                pixmap = pixmap.scaledToHeight(ch)
                woff = (pixmap.width() - cw) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(woff, 0), QPoint(pixmap.width()-woff, ch))
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
            pixmap.save(path, "PNG" )

    def invert(self):
        img = QImage(self.canvas.pixmap())
        img.invertPixels()
        pixmap = QPixmap()
        pixmap.convertFromImage(img)
        self.canvas.setPixmap(pixmap)

    def flip_horizontal(self):
        pixmap = self.canvas.pixmap()
        self.canvas.setPixmap(pixmap.transformed(QTransform().scale(-1, 1)))

    def flip_vertical(self):
        pixmap = self.canvas.pixmap()
        self.canvas.setPixmap(pixmap.transformed(QTransform().scale(1, -1)))



if __name__ == '__main__':

    app = QApplication([])
    window = MainWindow()
    app.exec_()