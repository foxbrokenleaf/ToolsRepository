import cv2
import numpy as np
import random
from PIL import Image, ImageDraw
import math
import matplotlib.pyplot as plt
from scipy.stats import norm

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


def generate_star_png(center = (500, 500), size = 100, color = (0, 255, 0), aspect_ratio=1, rotation_angle=0, is_filled=True):
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

def generate_diamond_image(center=(500, 500), size=100, color=(0, 255, 0), aspect_ratio=1, rotation_angle=0, is_filled=True):
    # 根据 aspect_ratio 计算两条对角线的一半长度
    half_diagonal_1 = size / 2
    half_diagonal_2 = half_diagonal_1 * aspect_ratio

    # 计算菱形的四个顶点（未旋转时）
    points = np.array([
        [0, -half_diagonal_1],
        [half_diagonal_2, 0],
        [0, half_diagonal_1],
        [-half_diagonal_2, 0]
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

def generate_transparent_triangle(center = (500, 500), size = 100, color = (0, 255, 0), aspect_ratio=1, rotation_angle=0, is_filled=True):
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

def generate_transparent_rectangle(center = (500, 500), size = 100, color = (0, 255, 0), aspect_ratio=1, rotation_angle=0, is_filled=True):
    t_color = (color[0], color[1], color[2], 255)
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
        cv2.fillPoly(img, [box], t_color)
    else:
        cv2.polylines(img, [box], True, t_color, 2)

    return img

def draw_transparent_circle(center = (500, 500), size = 100, color = (0, 255, 0), aspect_ratio=1, rotation_angle=0, is_filled=True):
    # 确保 size 是可迭代对象，如果是整数，将其转换为元组
    if isinstance(size, int):
        size = (size, size)

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

def overlay_images(image_a_path, image_b_paths, overlap_ratio=0, compactness=1):
    try:
        # 打开图片 A
        image_a = Image.open(image_a_path)
        width_a, height_a = image_a.size

        # 计算图片 B 的总宽度和总高度
        total_width_b = 0
        total_height_b = 0
        max_width_b = 0
        max_height_b = 0
        for image_b_path in image_b_paths:
            image_b = Image.open(image_b_path)
            width_b, height_b = image_b.size
            total_width_b += width_b
            total_height_b += height_b
            max_width_b = max(max_width_b, width_b)
            max_height_b = max(max_height_b, height_b)

        # 考虑重叠部分
        total_overlap_width = (len(image_b_paths) - 1) * int(
            sum([Image.open(path).size[0] for path in image_b_paths]) / len(image_b_paths) * overlap_ratio
        )
        total_overlap_height = (len(image_b_paths) - 1) * int(
            sum([Image.open(path).size[1] for path in image_b_paths]) / len(image_b_paths) * overlap_ratio
        )
        total_width_b -= total_overlap_width
        total_height_b -= total_overlap_height

        # 等比例缩放图片 A 的宽度和高度以适应图片 B 的总宽度和总高度
        ratio_width = total_width_b / width_a if total_width_b > width_a else 1
        ratio_height = total_height_b / height_a if total_height_b > height_a else 1
        ratio = max(ratio_width, ratio_height)
        new_width = int(width_a * ratio)
        new_height = int(height_a * ratio)
        image_a = image_a.resize((new_width, new_height), Image.LANCZOS)

        # 打乱图片 B 的顺序
        random.shuffle(image_b_paths)

        # 生成 4 条正态分布曲线
        draw = ImageDraw.Draw(image_a)
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for i in range(4):
            center_x = image_a.width // 2
            center_y = image_a.height // 2
            std_x = (image_a.width) / (4 * compactness)
            std_y = (image_a.height) / (4 * compactness)
            curve_points = []
            for x in range(image_a.width):
                y = int(np.random.normal(center_y, std_y))
                curve_points.append((x, y))
            draw.line(curve_points, fill=colors[i], width=2)

        positions = []
        # 第一步：使用正态分布生成所有B图像在A中的坐标
        for image_b_path in image_b_paths:
            image_b = Image.open(image_b_path)
            width_b, height_b = image_b.size
            # 若B中的图像过大，则等比例缩放
            if width_b > image_a.width or height_b > image_a.height:
                ratio_b = min(image_a.width / width_b, image_a.height / height_b)
                new_width_b = int(width_b * ratio_b)
                new_height_b = int(height_b * ratio_b)
                image_b = image_b.resize((new_width_b, new_height_b), Image.LANCZOS)
                width_b, height_b = image_b.size

            # 根据紧凑性调整正态分布的标准差
            std_x = (image_a.width - width_b) / (4 * compactness)
            std_y = (image_a.height - height_b) / (4 * compactness)
            center_x = image_a.width // 2
            center_y = image_a.height // 2
            x_offset = int(np.random.normal(center_x, std_x))
            y_offset = int(np.random.normal(center_y, std_y))
            positions.append((x_offset, y_offset))

        # 第二步：根据重叠率计算重叠（若为0则没有重叠）
        if overlap_ratio > 0:
            for i in range(len(positions)):
                x_offset, y_offset = positions[i]
                image_b = Image.open(image_b_paths[i])
                width_b, height_b = image_b.size
                overlap_width = int(width_b * overlap_ratio)
                overlap_height = int(height_b * overlap_ratio)
                # 调整坐标以考虑重叠
                for j in range(i + 1, len(positions)):
                    x_offset_other, y_offset_other = positions[j]
                    image_b_other = Image.open(image_b_paths[j])
                    width_b_other, height_b_other = image_b_other.size
                    if abs(x_offset - x_offset_other) < overlap_width or abs(y_offset - y_offset_other) < overlap_height:
                        # 计算新的坐标以避免重叠
                        # 这里简单地调整坐标，实际情况可能需要更复杂的处理
                        x_offset += overlap_width
                        y_offset += overlap_height
                        positions[i] = (x_offset, y_offset)

        # 第三步：重新根据正态分布将B中距离中心过远的图像重新生成坐标
        for i in range(len(positions)):
            x_offset, y_offset = positions[i]
            center_x = image_a.width // 2
            center_y = image_a.height // 2
            distance = np.sqrt((x_offset - center_x) ** 2 + (y_offset - center_y) ** 2)
            if distance > (image_a.width + image_a.height) / 4:
                image_b = Image.open(image_b_paths[i])
                width_b, height_b = image_b.size
                std_x = (image_a.width - width_b) / (4 * compactness)
                std_y = (image_a.height - height_b) / (4 * compactness)
                x_offset = int(np.random.normal(center_x, std_x))
                y_offset = int(np.random.normal(center_y, std_y))
                positions[i] = (x_offset, y_offset)

        # 粘贴图片 B 到图片 A 上
        for i, (x_offset, y_offset) in enumerate(positions):
            image_b = Image.open(image_b_paths[i])
            width_b, height_b = image_b.size
            # 若B中的图像过大，则等比例缩放
            if width_b > image_a.width or height_b > image_a.height:
                ratio_b = min(image_a.width / width_b, image_a.height / height_b)
                new_width_b = int(width_b * ratio_b)
                new_height_b = int(height_b * ratio_b)
                image_b = image_b.resize((new_width_b, new_height_b), Image.LANCZOS)
            image_a.paste(image_b, (x_offset, y_offset), image_b)

        return image_a

    except FileNotFoundError:
        print("错误: 未找到图片文件!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")
    return None


# # 创建一个透明背景的图像
# image = np.zeros((200, 200, 4), dtype=np.uint8)
# center = (500, 500)
# size = 100
# color = (0, 255, 0)  # 绿色，完全不透明
# aspect_ratio = 2
# rotation_angle = 30
# is_filled = True

# result = draw_transparent_circle()

# # 保存图像
# cv2.imwrite('1.png', result)

# 示例使用
# if __name__ == "__main__":
#     image_a_path = "img/1/1.jpg"
#     image_b_paths = ["1.png", "2.png","1.png", "2.png"]
#     overlap_ratio = 0  # 20% 的重叠率
#     result_image = overlay_images(image_a_path, image_b_paths, overlap_ratio)
#     if result_image:
#         result_image.save("3.jpg")

if __name__ == "__main__":
    image_function_list = [generate_star_png, generate_diamond_image, generate_transparent_triangle, generate_transparent_rectangle, draw_transparent_circle]
    image_color = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (0, 0, 0),
        (255, 255, 255),
    ]
    image = np.zeros((200, 200, 4), dtype=np.uint8)
    center = (500, 500)
    size = 100
    color = (0, 255, 0)  # 绿色，完全不透明
    aspect_ratio = 2
    rotation_angle = 30
    is_filled = True
    counter = 1
    

    for i in range(0, 5):
        overlap_ratio = 0  # 20% 的重叠率
        A = f"img/1/{random.randint(1, 30)}.jpg"
        Bs = []
        for num in range(0, 10):
            image_function = random.choice(image_function_list)
            res = image_function(size = random.randint(200, 220), 
                                color = random.choice(image_color),
                                aspect_ratio = random.choice(np.arange(0.5,1.5, 0.1)),
                                rotation_angle = random.randint(0, 360)
                                )
            # print(counter)
            cv2.imwrite(f"tmp/{counter}.png", res)
            print(f"[{counter}] -> {image_function}")
            Bs.append(f"tmp/{counter}.png")
            counter += 1
        result_image = overlay_images(A, Bs, overlap_ratio, 1)
        if result_image:
            result_image.save(f"res/1/{i}.jpg")
        print(Bs)