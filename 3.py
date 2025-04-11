import cv2
import numpy as np
import random
from PIL import Image, ImageDraw
import math

    # # 创建一个透明背景的图像
    # image = np.zeros((500, 500, 4), dtype=np.uint8)
    # center = (250, 250)
    # size = 200
    # color = (0, 255, 0, 255)  # 绿色，完全不透明
    # aspect_ratio = 0.8
    # rotation_angle = 30
    # is_filled = True

    # result = draw_diamond(image, center, size, color, aspect_ratio, rotation_angle, is_filled)

    # # 保存图像
    # cv2.imwrite('diamond.png', result)


def generate_star_png(center, size, color, aspect_ratio=1, rotation_angle=0, is_filled=False):
    # 计算五角星的顶点
    def calculate_star_points(center, size, aspect_ratio, rotation_angle):
        points = []
        num_points = 5
        outer_radius = size
        inner_radius = size * 0.382  # 五角星的内半径比例
        angle_step = 2 * math.pi / num_points
        rotation = math.radians(rotation_angle)

        for i in range(num_points * 2):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = i * angle_step / 2 + rotation
            x = center[0] + radius * math.cos(angle) * aspect_ratio
            y = center[1] + radius * math.sin(angle)
            points.append((int(x), int(y)))
        return np.array(points, np.int32)

    # 计算合适的画布大小
    canvas_size = int(size * 2 * max(aspect_ratio, 1))
    canvas = np.zeros((canvas_size, canvas_size, 4), dtype=np.uint8)

    # 调整中心位置以适应画布
    adjusted_center = (canvas_size // 2, canvas_size // 2)

    # 计算五角星的顶点
    star_points = calculate_star_points(adjusted_center, size, aspect_ratio, rotation_angle)

    # 绘制五角星
    if is_filled:
        cv2.fillPoly(canvas, [star_points], color + (255,))
    else:
        cv2.polylines(canvas, [star_points], True, color + (255,), 2)

    # 保存图片
    # cv2.imwrite('star.png', canvas)
    return canvas

def generate_diamond_image(center, size, color, aspect_ratio=1, rotation_angle=0, is_filled=False):
    # 计算菱形的四个顶点（未旋转时）
    half_size_x = int(size * aspect_ratio / 2)
    half_size_y = size / 2
    points = np.array([
        [half_size_x, -half_size_y],
        [half_size_x, half_size_y],
        [-half_size_x, half_size_y],
        [-half_size_x, -half_size_y]
    ], dtype=np.int32)

    # 旋转菱形
    rotation_matrix = cv2.getRotationMatrix2D((0, 0), rotation_angle, 1)
    rotated_points = cv2.transform(np.array([points]), rotation_matrix)[0]

    # 移动菱形到指定的中心位置
    rotated_points[:, 0] += center[0]
    rotated_points[:, 1] += center[1]

    # 计算旋转并移动后菱形的边界
    x_min = np.min(rotated_points[:, 0])
    x_max = np.max(rotated_points[:, 0])
    y_min = np.min(rotated_points[:, 1])
    y_max = np.max(rotated_points[:, 1])

    # 计算图像尺寸，确保能完整容纳菱形
    width = int(x_max - x_min)
    height = int(y_max - y_min)

    # 创建一个带有透明通道的空白图像
    image = np.zeros((height, width, 4), dtype=np.uint8)

    # 调整顶点坐标，使菱形位于图像内合适位置（相对于图像左上角为原点）
    adjusted_points = rotated_points.copy()
    adjusted_points[:, 0] -= x_min
    adjusted_points[:, 1] -= y_min

    # 绘制菱形
    if is_filled:
        cv2.fillPoly(image, [adjusted_points.astype(np.int32)], color + (255,))
    else:
        cv2.polylines(image, [adjusted_points.astype(np.int32)], True, color + (255,), 2)

    return image

def generate_transparent_triangle(center, size, color, aspect_ratio=1, rotation_angle=0, is_filled=False):
    # 计算三角形的顶点
    half_size = size // 2
    points = np.array([
        [center[0], center[1] - half_size],
        [center[0] - int(half_size * aspect_ratio), center[1] + half_size],
        [center[0] + int(half_size * aspect_ratio), center[1] + half_size]
    ], dtype=np.int32)

    # 旋转三角形
    rotation_matrix = cv2.getRotationMatrix2D(tuple(center), rotation_angle, 1)
    points = cv2.transform(np.array([points]), rotation_matrix)[0]

    # 计算包含三角形的最小矩形边界
    min_x = np.min(points[:, 0])
    max_x = np.max(points[:, 0])
    min_y = np.min(points[:, 1])
    max_y = np.max(points[:, 1])
    width = max_x - min_x + 1
    height = max_y - min_y + 1

    # 调整坐标，使三角形位于图像起始坐标 (0, 0) 处
    adjusted_points = points - np.array([min_x, min_y])

    # 创建图像
    image_size = (height, width, 4)
    image = np.zeros(image_size, dtype=np.uint8)

    # 绘制三角形
    if is_filled:
        cv2.fillPoly(image, [adjusted_points], color)
    else:
        cv2.polylines(image, [adjusted_points], isClosed=True, color=color, thickness=1)

    # 提取透明通道
    alpha_channel = np.any(image[:, :, :3] != [0, 0, 0], axis=-1).astype(np.uint8) * 255
    image[:, :, 3] = alpha_channel

    return image

def generate_transparent_rectangle(center, size, color, aspect_ratio=1, rotation_angle=0, is_filled=False):
    # 计算矩形的宽度和高度
    width = size
    height = int(size * aspect_ratio)

    # 计算矩形顶点
    rect = ((center[0], center[1]), (width, height), rotation_angle)
    box = cv2.boxPoints(rect)
    box = np.int32(box)

    # 找到包含矩形的最小外接矩形，以此确定图像大小
    x, y, w, h = cv2.boundingRect(box)
    img_width = w
    img_height = h

    # 创建一个透明背景的图像，大小为最小外接矩形大小
    img = np.zeros((img_height, img_width, 4), dtype=np.uint8)
    img[:, :, 3] = 0  # 初始化alpha通道为透明

    # 调整矩形顶点坐标，使其相对于新图像坐标系统
    box[:, 0] -= x
    box[:, 1] -= y

    # 绘制矩形
    if is_filled:
        cv2.fillPoly(img, [box], color)
    else:
        cv2.polylines(img, [box], True, color, 2)

    return img

def draw_transparent_circle(center, size, color, is_filled=False):
    # 计算图像的大小，确保足够容纳圆形
    diameter = max(size) * 2
    img_size = (diameter, diameter, 4)
    # 创建一个全透明的图像
    img = np.zeros(img_size, dtype=np.uint8)
    center = (diameter // 2, diameter // 2)
    # 转换颜色格式，添加透明度通道
    bgr_color = color[:3]
    alpha = color[3] if len(color) == 4 else 255
    if is_filled:
        # 绘制填充圆形
        cv2.circle(img, center, size[0], (*bgr_color, alpha), -1)
    else:
        # 绘制非填充圆形
        cv2.circle(img, center, size[0], (*bgr_color, alpha), 2)

    return img

# 创建一个透明背景的图像
image = np.zeros((1000, 1000, 4), dtype=np.uint8)
center = (500, 500)
size = 200
color = (0, 255, 0, 255)  # 绿色，完全不透明
aspect_ratio = 2
rotation_angle = 30
is_filled = True

result = generate_transparent_rectangle(center, size, color, aspect_ratio, rotation_angle, is_filled)

# 保存图像
cv2.imwrite('diamond.png', result)