from tkinter import *
from math import sin, cos, pi, log
import random

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2
IMAGE_ENLARGE = 11
COLOR = '#ff7171'


def heart_func(t, shrink_ratio: float = IMAGE_ENLARGE):
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

    x *= shrink_ratio
    y *= shrink_ratio

    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    ratiox = -beta * log(random.random())
    ratioy = -beta * log(random.random())
    dx = ratiox * (x - CANVAS_CENTER_X)
    dy = ratioy * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def shrink(x, y, ratio):
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    """
    自定义曲线函数，调整跳动周期
    :param p: 参数
    :return: 正弦
    """
    return 2 * (2 * sin(4 * p)) / (2 * pi)


class Heart:
    def __init__(self):
        self._points = set()
        self._extra_points = set()
        self._inside = set()
        self.all_points = {}
        self.build(2000)

    def build(self, number):
        # Heart
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_func(t)
            self._points.add((int(x), int(y)))

        # Heart immediate inside
        for xx, yy in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(xx, yy, 0.05)
                self._extra_points.add((x, y))

        # Inside
        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._inside.add((int(x), int(y)))

    def calc_position(self, x, y, ratio):
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520)
        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy

    def calc(self, frame):
        calc_position = self.calc_position
        ratio = 10 * curve(frame / 10 * pi)  # 圆滑的周期的缩放比例
        halo_radius = int(4 + 6 * (1 + curve(frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(frame / 10 * pi) ** 2))
        all_points = []

        heart_halo_point = set()  # 光环的点坐标集合
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)  # 随机不到的地方造成爱心有缺口
            x, y = heart_func(t, shrink_ratio=11.6)  # 魔法参数
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                # 处理新的点
                heart_halo_point.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                size = random.choice((1, 2, 2))
                all_points.append((x, y, size))

        # outline
        for x, y in self._points:
            x, y = calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        # inner
        for x, y in self._extra_points:
            x, y = calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._inside:
            x, y = calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[frame] = all_points

    def render(self, canvas, frame):
        for x, y, size in self.all_points[frame % 20]:
            canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=COLOR)


def draw(root: Tk, canvas: Canvas, heart: Heart, frame=0):
    canvas.delete('all')
    heart.render(canvas, frame)
    root.after(160, draw, root, canvas, heart, frame + 1)


if __name__ == '__main__':
    root = Tk()
    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart()
    for frame in range(20):
        heart.calc(frame)
    draw(root, canvas, heart)
    root.mainloop()
