'''
Corner Selector Window of the image.py software 

This program:
- Is a part of the image.py software and can not be run alone
- Lets the user manually select the corners of the where the sample
  and the reference shape is.
- Can only work when a reference shape exists (for example, a black square placed 
  under the sample) that has a bigger surface area and good contrast.
- Must be in the same folder as image.py and corner_selector.ui

Purpose:
- Enables the user to find the location and angle drift of the plant based meat sample
  after manually choosing it's and the reference shape's corners.

2026-03
'''

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QLabel, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2

# Load image that is being analyzed
def cv2_to_qpixmap(cv_img):
    height, width = cv_img.shape
    bytes_per_line = width
    q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
    return QPixmap.fromImage(q_img)

# Enable the user to select the corners of the sample area and the reference shape
class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self._pixmap_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self._pixmap_item)
        self.setScene(self._scene)

        self._zoom = 0
        self.selected_points = []
        self.markers = []

        self._panning = False
        self._pan_start = None
        self.setDragMode(QGraphicsView.NoDrag)

        self.mode = "sample"

    def set_mode(self, mode):
        self.mode = mode

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            x, y = int(scene_pos.x()), int(scene_pos.y())
            self.selected_points.append((x, y))

            if self.mode == "sample":
                color = Qt.blue
                text = "Sample Corner"
            else:
                color = Qt.magenta
                text = "Reference Corner"

            # Draw ellipse where a mouseclick happened
            ellipse_item = self._scene.addEllipse(-2, -2, 4, 4,
                                                  pen=QtGui.QPen(color),
                                                  brush=QtGui.QBrush(color))
            ellipse_item.setPos(x, y)
            ellipse_item.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)

            text_item = self._scene.addText(text)
            text_item.setDefaultTextColor(color)
            text_item.setPos(x + 5, y - 5)
            text_item.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)

            self.markers.append((ellipse_item, text_item))

        elif event.button() == Qt.RightButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            super().mousePressEvent(event)
    
    # Enable clicking with a mouse and storing the data of the location
    # where a click was made
    def mouseMoveEvent(self, event):
        if self._panning:
            delta = self._pan_start - event.pos()
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)

    def undo_last_selection(self):
        if self.markers:
            ellipse_item, text_item = self.markers.pop()
            self._scene.removeItem(ellipse_item)
            self._scene.removeItem(text_item)
            self.selected_points.pop()
            
    # Enable zooming in and out with a mouse wheel
    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        old_pos = self.mapToScene(event.pos())

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self._zoom += 1
        else:
            zoom_factor = zoom_out_factor
            self._zoom -= 1

        if self._zoom < -10:
            self._zoom = -10
            return

        self.scale(zoom_factor, zoom_factor)

        new_pos = self.mapToScene(event.pos())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

class CornerSelectorWindow(QtWidgets.QDialog):
    def __init__(self, thresh, parent=None):
        super().__init__(parent)
        uic.loadUi("corner_selector.ui", self)

        self.switch_mode_button = self.findChild(QPushButton, "pushButton")
        self.corner_redo_button = self.findChild(QPushButton, "pushButton_2")

        pixmap = cv2_to_qpixmap(thresh)
        self.view = ZoomableGraphicsView(pixmap, self)

        layout = QtWidgets.QVBoxLayout(self.graphicsContainer)
        layout.addWidget(self.view)

        self.corner_redo_button.clicked.connect(self.view.undo_last_selection)
        self.switch_mode_button.clicked.connect(self.switch_mode)
    
    # Switch between sample and reference marker corner selection modes
    def switch_mode(self):
        if self.view.mode == "sample":
            self.view.set_mode("reference")
        else:
            self.view.set_mode("sample")



        
