import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QColorDialog, QFileDialog, QGraphicsTextItem, QInputDialog, QGraphicsItem, QDockWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QPointF, QLineF, QRectF, QSize, QEvent
from PyQt5.QtGui import QPen, QColor, QPainter, QImage, QTransform, QWheelEvent


class ShapeItem(QGraphicsRectItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for line in self.scene().lines:
                line.updatePosition()
        return super().itemChange(change, value)


class ConnectorLine(QGraphicsLineItem):
    def __init__(self, start_item, end_item, *args):
        super().__init__(*args)
        self.start_item = start_item
        self.end_item = end_item
        self.setPen(QPen(Qt.black, 2))
        self.setFlags(QGraphicsItem.ItemIsSelectable)

    def updatePosition(self):
        self.setLine(QLineF(self.start_item.scenePos() + self.start_item.rect().center(),
                            self.end_item.scenePos() + self.end_item.rect().center()))


class FlowchartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Flowchart Drawer')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.scene = FlowchartScene()
        self.view = FlowchartView(self.scene)

        self.layout.addWidget(self.view)

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        self.select_button = QPushButton("Select/Drag")
        self.select_button.clicked.connect(lambda: self.scene.setMode('select'))
        self.buttons_layout.addWidget(self.select_button)

        self.add_line_button = QPushButton("Draw Line")
        self.add_line_button.clicked.connect(lambda: self.scene.setMode('line'))
        self.buttons_layout.addWidget(self.add_line_button)

        self.add_connector_button = QPushButton("Draw Connector")
        self.add_connector_button.clicked.connect(lambda: self.scene.setMode('connector'))
        self.buttons_layout.addWidget(self.add_connector_button)

        self.add_square_button = QPushButton("Draw Square")
        self.add_square_button.clicked.connect(lambda: self.scene.setMode('square'))
        self.buttons_layout.addWidget(self.add_square_button)

        self.add_rectangle_button = QPushButton("Draw Rectangle")
        self.add_rectangle_button.clicked.connect(lambda: self.scene.setMode('rectangle'))
        self.buttons_layout.addWidget(self.add_rectangle_button)

        self.add_circle_button = QPushButton("Draw Circle")
        self.add_circle_button.clicked.connect(lambda: self.scene.setMode('circle'))
        self.buttons_layout.addWidget(self.add_circle_button)

        self.add_text_button = QPushButton("Add Text")
        self.add_text_button.clicked.connect(lambda: self.scene.setMode('text'))
        self.buttons_layout.addWidget(self.add_text_button)

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

        self.initShapeTemplates()

    def initShapeTemplates(self):
        self.shape_dock = QDockWidget("Shape Templates", self)
        self.shape_list = QListWidget()
        self.shape_list.setViewMode(QListWidget.IconMode)
        self.shape_list.setIconSize(QSize(64, 64))
        self.shape_list.setMovement(QListWidget.Static)
        self.shape_list.setSpacing(10)

        square_item = QListWidgetItem("Square")
        square_item.setData(Qt.UserRole, 'square')
        self.shape_list.addItem(square_item)

        rectangle_item = QListWidgetItem("Rectangle")
        rectangle_item.setData(Qt.UserRole, 'rectangle')
        self.shape_list.addItem(rectangle_item)

        circle_item = QListWidgetItem("Circle")
        circle_item.setData(Qt.UserRole, 'circle')
        self.shape_list.addItem(circle_item)

        self.shape_dock.setWidget(self.shape_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.shape_dock)

        self.shape_list.itemClicked.connect(self.addShape)

    def addShape(self, item):
        shape_type = item.data(Qt.UserRole)
        if shape_type == 'square':
            shape = ShapeItem(0, 0, 100, 100)
        elif shape_type == 'rectangle':
            shape = ShapeItem(0, 0, 150, 100)
        elif shape_type == 'circle':
            shape = QGraphicsEllipseItem(0, 0, 100, 100)
            shape.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)
        else:
            return

        shape.setPen(QPen(Qt.black, 2))
        self.scene.addItem(shape)

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
        self.connector = None
        self.start_item = None
        self.end_item = None
        self.current_mode = None
        self.line_color = Qt.black
        self.lines = []

    def setMode(self, mode):
        self.current_mode = mode

    def setLineColor(self, color):
        self.line_color = color

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.scenePos()
            if self.current_mode == 'select':
                item = self.itemAt(self.start_point, QTransform())
                if item:
                    item.setSelected(True)
            elif self.current_mode == 'line':
                self.line = QGraphicsLineItem(QLineF(self.start_point, self.start_point))
                pen = QPen(self.line_color, 2)
                self.line.setPen(pen)
                self.addItem(self.line)
            elif self.current_mode == 'connector':
                self.start_item = self.itemAt(self.start_point, QTransform())
                if self.start_item:
                    self.connector = QGraphicsLineItem(QLineF(self.start_point, self.start_point))
                    pen = QPen(self.line_color, 2)
                    self.connector.setPen(pen)
                    self.addItem(self.connector)
            elif self.current_mode in ['square', 'rectangle']:
                self.rect = ShapeItem(0, 0, 0, 0)
                pen = QPen(self.line_color, 2)
                self.rect.setPen(pen)
                self.addItem(self.rect)
            elif self.current_mode == 'circle':
                self.ellipse = QGraphicsEllipseItem(0, 0, 0, 0)
                pen = QPen(self.line_color, 2)
                self.ellipse.setPen(pen)
                self.addItem(self.ellipse)
            elif self.current_mode == 'text':
                text, ok = QInputDialog.getText(None, "Input Text", "Enter your text:")
                if ok and text:
                    self.text_item = QGraphicsTextItem(text)
                    self.text_item.setDefaultTextColor(self.line_color)
                    self.text_item.setPos(self.start_point)
                    self.text_item.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
                    self.addItem(self.text_item)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        end_point = event.scenePos()
        if self.current_mode == 'line' and self.line is not None:
            self.line.setLine(QLineF(self.start_point, end_point))
        elif self.current_mode == 'connector' and self.connector is not None:
            self.connector.setLine(QLineF(self.start_point, end_point))
        elif self.current_mode in ['square', 'rectangle'] and self.rect is not None:
            rect = QRectF(self.start_point, end_point).normalized()
            if self.current_mode == 'square':
                side = min(rect.width(), rect.height())
                rect.setWidth(side)
                rect.setHeight(side)
            self.rect.setRect(rect)
        elif self.current_mode == 'circle' and self.ellipse is not None:
            rect = QRectF(self.start_point, end_point).normalized()
            diameter = min(rect.width(), rect.height())
            self.ellipse.setRect(rect.topLeft().x(), rect.topLeft().y(), diameter, diameter)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            end_point = event.scenePos()
            if self.current_mode == 'line' and self.line is not None:
                self.line.setLine(QLineF(self.start_point, end_point))
                self.line = None
            elif self.current_mode == 'connector' and self.connector is not None:
                self.end_item = self.itemAt(end_point, QTransform())
                if self.start_item and self.end_item and self.start_item != self.end_item:
                    connector = ConnectorLine(self.start_item, self.end_item)
                    self.lines.append(connector)
                    self.addItem(connector)
                self.removeItem(self.connector)
                self.connector = None
            elif self.current_mode in ['square', 'rectangle'] and self.rect is not None:
                rect = QRectF(self.start_point, end_point).normalized()
                if self.current_mode == 'square':
                    side = min(rect.width(), rect.height())
                    rect.setWidth(side)
                    rect.setHeight(side)
                self.rect.setRect(rect)
                self.rect = None
            elif self.current_mode == 'circle' and self.ellipse is not None:
                rect = QRectF(self.start_point, end_point).normalized()
                diameter = min(rect.width(), rect.height())
                self.ellipse.setRect(rect.topLeft().x(), rect.topLeft().y(), diameter, diameter)
                self.ellipse = None
        super().mouseReleaseEvent(event)

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
    game = FlowchartApp()
    game.show()
    sys.exit(app.exec_())