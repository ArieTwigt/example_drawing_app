import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView, 
                             QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QColorDialog, QFileDialog, QGraphicsTextItem, QInputDialog, QGraphicsItem)
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt5.QtGui import QPen, QColor, QPainter, QImage, QWheelEvent, QTransform, QPolygonF, QPainterPath



class FlowchartApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 1200, 800)  # Increase window size
        self.setWindowTitle('Flowchart Drawer')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        self.scene = FlowchartScene()
        self.view = FlowchartView(self.scene)
        self.layout.addWidget(self.view)

        self.buttons_layout = QVBoxLayout()  # Change to QVBoxLayout to arrange buttons vertically
        self.layout.addLayout(self.buttons_layout)

        self.add_line_button = QPushButton("Draw Line")
        self.add_line_button.clicked.connect(lambda: self.scene.setMode('line'))
        self.buttons_layout.addWidget(self.add_line_button)

        self.add_arrow_button = QPushButton("Draw Arrow")
        self.add_arrow_button.clicked.connect(lambda: self.scene.setMode('arrow'))
        self.buttons_layout.addWidget(self.add_arrow_button)

        self.add_square_button = QPushButton("Draw Square")
        self.add_square_button.clicked.connect(lambda: self.scene.setMode('square'))
        self.buttons_layout.addWidget(self.add_square_button)

        self.add_rectangle_button = QPushButton("Draw Rectangle")
        self.add_rectangle_button.clicked.connect(lambda: self.scene.setMode('rectangle'))
        self.buttons_layout.addWidget(self.add_rectangle_button)

        self.add_diamond_button = QPushButton("Draw Diamond")
        self.add_diamond_button.clicked.connect(lambda: self.scene.setMode('diamond'))
        self.buttons_layout.addWidget(self.add_diamond_button)

        self.add_circle_button = QPushButton("Draw Circle")
        self.add_circle_button.clicked.connect(lambda: self.scene.setMode('circle'))
        self.buttons_layout.addWidget(self.add_circle_button)

        self.add_text_button = QPushButton("Add Text")
        self.add_text_button.clicked.connect(lambda: self.scene.setMode('text'))
        self.buttons_layout.addWidget(self.add_text_button)

        self.add_text_box_button = QPushButton("Add Text Box")
        self.add_text_box_button.clicked.connect(lambda: self.scene.setMode('textbox'))
        self.buttons_layout.addWidget(self.add_text_box_button)

        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.selectColor)
        self.buttons_layout.addWidget(self.color_button)

        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoomIn)
        self.buttons_layout.addWidget(self.zoom_in_button)

        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoomOut)
        self.buttons_layout.addWidget(self.zoom_out_button)

        self.export_button = QPushButton("Export as PNG")
        self.export_button.clicked.connect(self.exportAsPNG)
        self.buttons_layout.addWidget(self.export_button)

        self.toggle_mode_button = QPushButton("Toggle Select/Draw Mode")
        self.toggle_mode_button.clicked.connect(self.toggleSelectMode)
        self.buttons_layout.addWidget(self.toggle_mode_button)

    def selectColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.scene.setLineColor(color)

    def zoomIn(self):
        self.view.scale(1.2, 1.2)

    def zoomOut(self):
        self.view.scale(0.8, 0.8)

    def exportAsPNG(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            self.scene.exportAsPNG(file_path)

    def toggleSelectMode(self):
        self.scene.toggleSelectMode()

class FlowchartView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.grid_size = 20

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        right = int(rect.right())
        bottom = int(rect.bottom())

        lines = []
        for x in range(left, right, self.grid_size):
            lines.append(QLineF(x, top, x, bottom))
        for y in range(top, bottom, self.grid_size):
            lines.append(QLineF(left, y, right, y))

        painter.setPen(QPen(Qt.lightGray))
        painter.drawLines(lines)

class FlowchartScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.line = None
        self.rect = None
        self.ellipse = None
        self.diamond = None
        self.arrow = None
        self.text_item = None
        self.text_box = None
        self.start_point = None
        self.current_mode = None
        self.line_color = Qt.black
        self.red_dot = None
        self.select_mode = False
        self.selected_item = None
        self.selected_item_start_pos = None
        self.mouse_start_pos = None

    def setMode(self, mode):
        self.current_mode = mode
        self.select_mode = False  # Disable select mode when a drawing mode is selected

    def setLineColor(self, color):
        self.line_color = color

    def toggleSelectMode(self):
        self.select_mode = not self.select_mode

    def mousePressEvent(self, event):
        if self.select_mode:
            item = self.itemAt(event.scenePos(), QTransform())
            if item and event.button() == Qt.LeftButton:
                self.selected_item = item
                self.selected_item_start_pos = self.selected_item.pos()
                self.mouse_start_pos = event.scenePos()
            else:
                super().mousePressEvent(event)
            return

        if event.button() == Qt.LeftButton:
            self.start_point = event.scenePos()
            self.start_point = self.getClosestPoint(self.start_point)
            if self.current_mode == 'line':
                self.line = QGraphicsLineItem(QLineF(self.start_point, self.start_point))
                pen = QPen(self.line_color, 2)
                self.line.setPen(pen)
                self.addItem(self.line)
            elif self.current_mode == 'arrow':
                self.arrow = QGraphicsLineItem(QLineF(self.start_point, self.start_point))
                pen = QPen(self.line_color, 2)
                self.arrow.setPen(pen)
                self.addItem(self.arrow)
            elif self.current_mode in ['square', 'rectangle']:
                self.rect = QGraphicsRectItem(QRectF(self.start_point, self.start_point))
                pen = QPen(self.line_color, 2)
                self.rect.setPen(pen)
                self.addItem(self.rect)
            elif self.current_mode == 'diamond':
                self.diamond = QGraphicsPolygonItem(self.createDiamondPolygon(QRectF(self.start_point, self.start_point)))
                pen = QPen(self.line_color, 2)
                self.diamond.setPen(pen)
                self.addItem(self.diamond)
            elif self.current_mode == 'circle':
                self.ellipse = QGraphicsEllipseItem(QRectF(self.start_point, self.start_point))
                pen = QPen(self.line_color, 2)
                self.ellipse.setPen(pen)
                self.addItem(self.ellipse)
            elif self.current_mode == 'textbox':
                self.text_box = QGraphicsRectItem(QRectF(self.start_point, self.start_point))
                pen = QPen(self.line_color, 2)
                self.text_box.setPen(pen)
                self.addItem(self.text_box)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.select_mode and self.selected_item:
            delta = event.scenePos() - self.mouse_start_pos
            self.selected_item.setPos(self.selected_item_start_pos + delta)
            return

        end_point = event.scenePos()
        closest_point = self.getClosestPoint(end_point)
        if closest_point != end_point:
            if self.red_dot is None:
                self.red_dot = self.addEllipse(closest_point.x() - 3, closest_point.y() - 3, 6, 6, QPen(Qt.red), Qt.red)
            else:
                self.red_dot.setRect(closest_point.x() - 3, closest_point.y() - 3, 6, 6)
        else:
            if self.red_dot is not None:
                self.removeItem(self.red_dot)
                self.red_dot = None

        if self.current_mode == 'line' and self.line is not None:
            self.line.setLine(QLineF(self.start_point, closest_point))
        elif self.current_mode == 'arrow' and self.arrow is not None:
            self.arrow.setLine(QLineF(self.start_point, closest_point))
            self.addArrowHead(self.arrow)
        elif self.current_mode in ['square', 'rectangle'] and self.rect is not None:
            rect = QRectF(self.start_point, end_point).normalized()
            if self.current_mode == 'square':
                side = min(rect.width(), rect.height())
                rect.setWidth(side)
                rect.setHeight(side)
            self.rect.setRect(rect)
        elif self.current_mode == 'diamond' and self.diamond is not None:
            rect = QRectF(self.start_point, end_point).normalized()
            diamond_polygon = self.createDiamondPolygon(rect)
            self.diamond.setPolygon(diamond_polygon)
        elif self.current_mode == 'circle' and self.ellipse is not None:
            rect = QRectF(self.start_point, end_point).normalized()
            diameter = min(rect.width(), rect.height())
            self.ellipse.setRect(rect.topLeft().x(), rect.topLeft().y(), diameter, diameter)
        elif self.current_mode == 'textbox' and self.text_box is not None:
            rect = QRectF(self.start_point, end_point).normalized()
            self.text_box.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.select_mode and self.selected_item:
            self.selected_item = None
            return

        if event.button() == Qt.LeftButton:
            end_point = event.scenePos()
            closest_point = self.getClosestPoint(end_point)
            if self.current_mode == 'line' and self.line is not None:
                self.line.setLine(QLineF(self.start_point, closest_point))
                self.line = None
            elif self.current_mode == 'arrow' and self.arrow is not None:
                self.arrow.setLine(QLineF(self.start_point, closest_point))
                self.addArrowHead(self.arrow)
                self.arrow = None
            elif self.current_mode in ['square', 'rectangle'] and self.rect is not None:
                rect = QRectF(self.start_point, end_point).normalized()
                if self.current_mode == 'square':
                    side = min(rect.width(), rect.height())
                    rect.setWidth(side)
                    rect.setHeight(side)
                self.rect.setRect(rect)
                self.rect = None
            elif self.current_mode == 'diamond' and self.diamond is not None:
                rect = QRectF(self.start_point, end_point).normalized()
                diamond_polygon = self.createDiamondPolygon(rect)
                self.diamond.setPolygon(diamond_polygon)
                self.diamond = None
            elif self.current_mode == 'circle' and self.ellipse is not None:
                rect = QRectF(self.start_point, end_point).normalized()
                diameter = min(rect.width(), rect.height())
                self.ellipse.setRect(rect.topLeft().x(), rect.topLeft().y(), diameter, diameter)
                self.ellipse = None
            elif self.current_mode == 'textbox' and self.text_box is not None:
                rect = QRectF(self.start_point, end_point).normalized()
                self.text_box.setRect(rect)
                text, ok = QInputDialog.getText(None, "Input Text", "Enter your text:")
                if ok and text:
                    text_item = QGraphicsTextItem(text, self.text_box)
                    text_item.setDefaultTextColor(self.line_color)
                    text_item.setPos(rect.topLeft())
                    text_item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                self.text_box = None

            if self.red_dot is not None:
                self.removeItem(self.red_dot)
                self.red_dot = None

        super().mouseReleaseEvent(event)

    def createDiamondPolygon(self, rect):
        diamond = QPolygonF([
            QPointF(rect.center().x(), rect.top()),
            QPointF(rect.right(), rect.center().y()),
            QPointF(rect.center().x(), rect.bottom()),
            QPointF(rect.left(), rect.center().y())
        ])
        return diamond

    def getClosestPoint(self, point, threshold=10):
        min_distance = float('inf')
        closest_point = point
        for item in self.items():
            if isinstance(item, QGraphicsLineItem):
                line = item.line()
                for pt in [line.p1(), line.p2()]:
                    distance = (point - pt).manhattanLength()
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = pt
        if min_distance < threshold:
            return closest_point
        return point

    def addArrowHead(self, line):
        line_end = line.line().p2()
        line_start = line.line().p1()
        angle = line.line().angle()

        arrow_head = QPolygonF()

        arrow_size = 10
        p1 = QPointF(line_end.x() + arrow_size * QPointF(1, 0).x(), line_end.y() + arrow_size * QPointF(1, 0).y())
        p2 = QPointF(line_end.x() - arrow_size * QPointF(1, 0).x(), line_end.y() - arrow_size * QPointF(1, 0).y())

        path = QPainterPath(line_end)
        path.lineTo(p1)
        path.moveTo(line_end)
        path.lineTo(p2)

        arrow = self.addPath(path, QPen(self.line_color, 2))

    def exportAsPNG(self, file_path):
        rect = self.sceneRect()
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
        image.fill(Qt.white)
        painter = QPainter(image)
        self.render(painter)
        painter.end()
        image.save(file_path)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.views()[0].scale(1.2, 1.2)
            else:
                self.views()[0].scale(0.8, 0.8)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FlowchartApp()
    ex.show()
    sys.exit(app.exec_())
