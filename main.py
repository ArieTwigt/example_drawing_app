import tkinter as tk
from tkinter import colorchooser
import math

class FlowchartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flowchart Drawing App")

        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Bind the mouse wheel for zooming

        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)

        self.shapes_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Shapes", menu=self.shapes_menu)
        self.shapes_menu.add_command(label="Rectangle", command=self.select_rectangle)
        self.shapes_menu.add_command(label="Line", command=self.select_line)
        self.shapes_menu.add_command(label="Arrow", command=self.select_arrow)
        self.shapes_menu.add_command(label="Ellipse", command=self.select_ellipse)
        self.shapes_menu.add_command(label="Diamond", command=self.select_diamond)

        self.color_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Color", menu=self.color_menu)
        self.color_menu.add_command(label="Select Line Color", command=self.choose_line_color)

        self.current_shape = None
        self.start_x = None
        self.start_y = None
        self.current_item = None
        self.line_color = 'black'  # Default line color
        self.snap_threshold = 10  # Distance threshold for snapping
        self.snap_indicator = None

        self.scale_factor = 1.0  # Scale factor for zooming

    def select_rectangle(self):
        self.current_shape = 'rectangle'

    def select_line(self):
        self.current_shape = 'line'

    def select_arrow(self):
        self.current_shape = 'arrow'

    def select_ellipse(self):
        self.current_shape = 'ellipse'

    def select_diamond(self):
        self.current_shape = 'diamond'

    def choose_line_color(self):
        color_code = colorchooser.askcolor(title="Choose line color")
        if color_code:
            self.line_color = color_code[1]

    def on_canvas_click(self, event):
        self.start_x, self.start_y = self.snap_to_nearest_line(event.x / self.scale_factor, event.y / self.scale_factor)
        if self.current_shape == 'rectangle':
            self.current_item = self.canvas.create_rectangle(self.start_x, self.start_y, event.x / self.scale_factor, event.y / self.scale_factor, outline='black', fill='lightblue')
        elif self.current_shape in ('line', 'arrow'):
            self.current_item = self.canvas.create_line(self.start_x, self.start_y, event.x / self.scale_factor, event.y / self.scale_factor, fill=self.line_color, arrow=tk.LAST if self.current_shape == 'arrow' else tk.NONE)
        elif self.current_shape == 'ellipse':
            self.current_item = self.canvas.create_oval(self.start_x, self.start_y, event.x / self.scale_factor, event.y / self.scale_factor, outline='black', fill='lightblue')
        elif self.current_shape == 'diamond':
            self.current_item = self.canvas.create_polygon(self.start_x, self.start_y, event.x / self.scale_factor, self.start_y, (self.start_x + event.x / self.scale_factor) // 2, (self.start_y + event.y / self.scale_factor) // 2, self.start_x, event.y / self.scale_factor, outline='black', fill='lightblue')

    def on_mouse_drag(self, event):
        if self.current_shape in ('line', 'arrow') and self.current_item:
            end_x, end_y = self.snap_to_nearest_line(event.x / self.scale_factor, event.y / self.scale_factor)
            self.canvas.coords(self.current_item, self.start_x, self.start_y, end_x, end_y)
            self.update_snap_indicator(end_x, end_y)
        elif self.current_shape == 'rectangle' and self.current_item:
            self.canvas.coords(self.current_item, self.start_x, self.start_y, event.x / self.scale_factor, event.y / self.scale_factor)
        elif self.current_shape == 'ellipse' and self.current_item:
            self.canvas.coords(self.current_item, self.start_x, self.start_y, event.x / self.scale_factor, event.y / self.scale_factor)
        elif self.current_shape == 'diamond' and self.current_item:
            self.canvas.coords(self.current_item, self.start_x, self.start_y, event.x / self.scale_factor, self.start_y, (self.start_x + event.x / self.scale_factor) // 2, (self.start_y + event.y / self.scale_factor) // 2, self.start_x, event.y / self.scale_factor)

    def on_mouse_release(self, event):
        if self.current_shape in ('line', 'arrow') and self.current_item:
            end_x, end_y = self.snap_to_nearest_line(event.x / self.scale_factor, event.y / self.scale_factor)
            self.canvas.coords(self.current_item, self.start_x, self.start_y, end_x, end_y)
            self.remove_snap_indicator()
            self.current_item = None
        elif self.current_shape == 'rectangle' and self.current_item:
            self.canvas.coords(self.current_item, self.start_x, self.start_y, event.x / self.scale_factor, event.y / self.scale_factor)
            self.current_item = None
        elif self.current_shape == 'ellipse' and self.current_item:
            self.canvas.coords(self.current_item, self.start_x, self.start_y, event.x / self.scale_factor, event.y / self.scale_factor)
            self.current_item = None
        elif self.current_shape == 'diamond' and self.current_item:
            self.canvas.coords(self.current_item, self.start_x, self.start_y, event.x / self.scale_factor, self.start_y, (self.start_x + event.x / self.scale_factor) // 2, (self.start_y + event.y / self.scale_factor) // 2, self.start_x, event.y / self.scale_factor)
            self.current_item = None

    def create_rectangle(self, x, y):
        width = 100
        height = 50
        self.canvas.create_rectangle(x, y, x + width, y + height, outline='black', fill='lightblue')

    def snap_to_nearest_line(self, x, y):
        closest_point = (x, y)
        min_distance = self.snap_threshold / self.scale_factor

        for item in self.canvas.find_all():
            if self.canvas.type(item) == 'line':
                coords = self.canvas.coords(item)
                points = [(coords[0], coords[1]), (coords[2], coords[3])]
                for point in points:
                    distance = math.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = point

        return closest_point

    def update_snap_indicator(self, x, y):
        if self.snap_indicator:
            self.canvas.coords(self.snap_indicator, x-5, y-5, x+5, y+5)
        else:
            self.snap_indicator = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='red')

    def remove_snap_indicator(self):
        if self.snap_indicator:
            self.canvas.delete(self.snap_indicator)
            self.snap_indicator = None

    def on_mouse_wheel(self, event):
        # Zoom in
        if event.delta > 0:
            self.scale_factor *= 1.1
        # Zoom out
        else:
            self.scale_factor /= 1.1

        # Rescale all objects on the canvas
        self.canvas.scale("all", event.x, event.y, self.scale_factor, self.scale_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowchartApp(root)
    root.mainloop()
