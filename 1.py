from PIL import Image
import cv2
import numpy as np
import random
import os
import struct
import math

def draw_star(image, center, size, color, aspect_ratio=1, rotation_angle=0, is_filled=False):
    # 计算五角星的顶点
    angles = np.linspace(0, 2 * np.pi, 10, endpoint=False)
    outer_radius = size
    inner_radius = size * 0.382
    points = []
    for i in range(10):
        if i % 2 == 0:
            r = outer_radius
        else:
            r = inner_radius
        # 考虑长宽比
        x = r * np.cos(angles[i]) * aspect_ratio
        y = r * np.sin(angles[i])
        # 考虑旋转角度
        rotated_x = x * np.cos(np.radians(rotation_angle)) - y * np.sin(np.radians(rotation_angle))
        rotated_y = x * np.sin(np.radians(rotation_angle)) + y * np.cos(np.radians(rotation_angle))
        x = int(center[0] + rotated_x)
        y = int(center[1] - rotated_y)
        points.append([x, y])
    points = np.array(points, np.int32)
    points = points.reshape((-1, 1, 2))
    # 绘制五角星
    if is_filled:
        cv2.fillPoly(image, [points], color)
    else:
        cv2.polylines(image, [points], True, color, 2)
    return image

def draw_triangle(image, center, size, color, aspect_ratio=1, rotation_angle=0, is_filled=False):
    # 计算三角形的顶点
    angles = np.linspace(0, 2 * np.pi, 3, endpoint=False)
    points = []
    for angle in angles:
        # 考虑长宽比
        x = size * np.cos(angle) * aspect_ratio
        y = size * np.sin(angle)
        # 考虑旋转角度
        rotated_x = x * np.cos(np.radians(rotation_angle)) - y * np.sin(np.radians(rotation_angle))
        rotated_y = x * np.sin(np.radians(rotation_angle)) + y * np.cos(np.radians(rotation_angle))
        x = int(center[0] + rotated_x)
        y = int(center[1] - rotated_y)
        points.append([x, y])
    points = np.array(points, np.int32)
    points = points.reshape((-1, 1, 2))
    # 绘制三角形
    if is_filled:
        cv2.fillPoly(image, [points], color)
    else:
        cv2.polylines(image, [points], True, color, 2)
    return image

def draw_rhombus(image, center, size, color, aspect_ratio=1, rotation_angle=0, is_filled=False):
    # 计算菱形的顶点
    angles = np.linspace(0, 2 * np.pi, 4, endpoint=False)
    points = []
    for angle in angles:
        # 考虑长宽比
        x = size * np.cos(angle) * aspect_ratio
        y = size * np.sin(angle)
        # 考虑旋转角度
        rotated_x = x * np.cos(np.radians(rotation_angle)) - y * np.sin(np.radians(rotation_angle))
        rotated_y = x * np.sin(np.radians(rotation_angle)) + y * np.cos(np.radians(rotation_angle))
        x = int(center[0] + rotated_x)
        y = int(center[1] - rotated_y)
        points.append([x, y])
    points = np.array(points, np.int32)
    points = points.reshape((-1, 1, 2))
    # 绘制菱形
    if is_filled:
        cv2.fillPoly(image, [points], color)
    else:
        cv2.polylines(image, [points], True, color, 2)
    return image

def draw_rectangle(image, center, size, color, aspect_ratio=1, rotation_angle=0, is_filled=False):
    # 计算矩形的四个顶点
    half_width = size * aspect_ratio
    half_height = size
    # 定义矩形未旋转时的四个顶点
    vertices = [
        [-half_width, -half_height],
        [half_width, -half_height],
        [half_width, half_height],
        [-half_width, half_height]
    ]
    rotated_vertices = []
    for vertex in vertices:
        x, y = vertex
        # 考虑旋转角度
        rotated_x = x * np.cos(np.radians(rotation_angle)) - y * np.sin(np.radians(rotation_angle))
        rotated_y = x * np.sin(np.radians(rotation_angle)) + y * np.cos(np.radians(rotation_angle))
        x = int(center[0] + rotated_x)
        y = int(center[1] - rotated_y)
        rotated_vertices.append([x, y])
    points = np.array(rotated_vertices, np.int32)
    points = points.reshape((-1, 1, 2))
    # 绘制矩形
    if is_filled:
        cv2.fillPoly(image, [points], color)
    else:
        cv2.polylines(image, [points], True, color, 2)
    return image

def draw_circle(image, center, size, color, is_filled=False):
    radius = size
    thickness = -1 if is_filled else 2
    cv2.circle(image, center, radius, color, thickness)
    return image

def convert_image_to_rgb565(image: Image.Image):
    """将Pillow图像对象转为RGB565字节列表"""
    image = image.convert('RGB')
    image = image.transpose(Image.FLIP_TOP_BOTTOM)  # 适配Image2Lcd的扫描方向
    pixels = list(image.getdata())

    rgb565_bytes = bytearray()
    for r, g, b in pixels:
        value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        rgb565_bytes.extend(struct.pack('<H', value))  # 小端写入

    return rgb565_bytes

def batch_convert_images(input_folder, output_folder, width=800, height=480):
    os.makedirs(output_folder, exist_ok=True)
    supported_ext = ('.png', '.jpg', '.jpeg', '.bmp')

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(supported_ext):
            input_path = os.path.join(input_folder, filename)
            output_name = os.path.splitext(filename)[0] + '.bin'
            output_path = os.path.join(output_folder, output_name)

            try:
                with Image.open(input_path) as img:
                    img_resized = img.resize((width, height))
                    data = convert_image_to_rgb565(img_resized)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    print(f"[✅] 已转换: {filename} → {output_name}")
            except Exception as e:
                print(f"[❌] 转换失败: {filename}, 错误: {e}")

    print("\n🎉 全部完成！")

# 计算两点之间距离
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# 判断圆形是否重叠
def circle_overlap(circle1, circle2):
    x1, y1, r1 = circle1
    x2, y2, r2 = circle2
    return distance(x1, y1, x2, y2) < r1 + r2


# 判断矩形是否重叠（用中心坐标、宽高计算边界判断）
def rectangle_overlap(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    left1 = x1 - w1 / 2
    right1 = x1 + w1 / 2
    top1 = y1 - h1 / 2
    bottom1 = y1 + h1 / 2

    left2 = x2 - w2 / 2
    right2 = x2 + w2 / 2
    top2 = y2 - h2 / 2
    bottom2 = y2 + h2 / 2

    return not (right1 < left2 or left1 > right2 or bottom1 < top2 or top1 > bottom2)


# 五角星顶点计算（简化，以中心坐标和外接圆半径计算顶点坐标）
def pentagram_vertices(x, y, r):
    vertices = []
    for i in range(5):
        angle = (i * 2 * math.pi / 5 + math.pi / 2)
        x1 = x + r * math.cos(angle)
        y1 = y + r * math.sin(angle)
        vertices.append((x1, y1))
    for i in range(5):
        angle = ((2 * i + 1) * 2 * math.pi / 10 + math.pi / 2)
        x1 = x + r * math.cos(angle)
        y1 = y + r * math.sin(angle)
        vertices.append((x1, y1))
    return vertices


# 判断五角星是否重叠（简化判断，判断中心点距离和大致范围）
def pentagram_overlap(pentagram1, pentagram2):
    x1, y1, r1 = pentagram1
    x2, y2, r2 = pentagram2
    dist = distance(x1, y1, x2, y2)
    return dist < r1 + r2


# 判断三角形是否重叠（用中心坐标、外接圆半径等简化判断 ）
def triangle_overlap(triangle1, triangle2):
    x1, y1, r1 = triangle1
    x2, y2, r2 = triangle2
    dist = distance(x1, y1, x2, y2)
    return dist < r1 + r2


# 判断菱形是否重叠
def rhombus_overlap(rhombus1, rhombus2):
    x1, y1, w1, h1 = rhombus1
    x2, y2, w2, h2 = rhombus2
    left1 = x1 - w1 / 2
    right1 = x1 + w1 / 2
    top1 = y1 - h1 / 2
    bottom1 = y1 + h1 / 2

    left2 = x2 - w2 / 2
    right2 = x2 + w2 / 2
    top2 = y2 - h2 / 2
    bottom2 = y2 + h2 / 2

    return not (right1 < left2 or left1 > right2 or bottom1 < top2 or top1 > bottom2)


def generate_non_overlapping_images(num_images, w, h, size_min, size_max, overlap_prob=0.2, point=0, offset=0):
    existing_images = []
    result = []

    def is_overlapping(new_pos, new_size, shape):
        # 假设new_size是宽高元组
        if shape == "circle":
            # 取宽高最小值的一半作为半径
            r1 = min(new_size[0], new_size[1]) / 2
            new_obj = (new_pos[0], new_pos[1], r1)
        elif shape == "triangle":
            r1 = min(new_size[0], new_size[1]) / 2
            new_obj = (new_pos[0], new_pos[1], r1)
        else:
            new_obj = (new_pos[0], new_pos[1], new_size[0], new_size[1])
        for pos, size, shp in existing_images:
            if shp == "circle":
                r2 = min(size[0], size[1]) / 2
                old_obj = (pos[0], pos[1], r2)
            elif shp == "triangle":
                r2 = min(size[0], size[1]) / 2
                old_obj = (pos[0], pos[1], r2)
            else:
                old_obj = (pos[0], pos[1], size[0], size[1])
            if shp == "circle":
                if circle_overlap(new_obj, old_obj):
                    return True
            elif shp == "rectangle":
                if rectangle_overlap(new_obj, old_obj):
                    return True
            elif shp == "pentagram":
                if pentagram_overlap(new_obj, old_obj):
                    return True
            elif shp == "triangle":
                if triangle_overlap(new_obj, old_obj):
                    return True
            elif shp == "rhombus":
                if rhombus_overlap(new_obj, old_obj):
                    return True
        return False

    shape_list = ["circle", "rectangle", "pentagram", "triangle", "rhombus"]
    for _ in range(num_images):
        if random.random() < 0  # 计算两点之间距离
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# 判断圆形是否重叠
def circle_overlap(circle1, circle2):
    x1, y1, r1 = circle1
    x2, y2, r2 = circle2
    return distance(x1, y1, x2, y2) < r1 + r2


# 判断矩形是否重叠（用中心坐标、宽高计算边界判断）
def rectangle_overlap(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    left1 = x1 - w1 / 2
    right1 = x1 + w1 / 2
    top1 = y1 - h1 / 2
    bottom1 = y1 + h1 / 2

    left2 = x2 - w2 / 2
    right2 = x2 + w2 / 2
    top2 = y2 - h2 / 2
    bottom2 = y2 + h2 / 2

    return not (right1 < left2 or left1 > right2 or bottom1 < top2 or top1 > bottom2)


# 五角星顶点计算（简化，以中心坐标和外接圆半径计算顶点坐标）
def pentagram_vertices(x, y, r):
    vertices = []
    for i in range(5):
        angle = (i * 2 * math.pi / 5 + math.pi / 2)
        x1 = x + r * math.cos(angle)
        y1 = y + r * math.sin(angle)
        vertices.append((x1, y1))
    for i in range(5):
        angle = ((2 * i + 1) * 2 * math.pi / 10 + math.pi / 2)
        x1 = x + r * math.cos(angle)
        y1 = y + r * math.sin(angle)
        vertices.append((x1, y1))
    return vertices


# 判断五角星是否重叠（简化判断，判断中心点距离和大致范围）
def pentagram_overlap(pentagram1, pentagram2):
    x1, y1, r1 = pentagram1
    x2, y2, r2 = pentagram2
    dist = distance(x1, y1, x2, y2)
    return dist < r1 + r2


# 判断三角形是否重叠（用中心坐标、外接圆半径等简化判断 ）
def triangle_overlap(triangle1, triangle2):
    x1, y1, r1 = triangle1
    x2, y2, r2 = triangle2
    dist = distance(x1, y1, x2, y2)
    return dist < r1 + r2


# 判断菱形是否重叠
def rhombus_overlap(rhombus1, rhombus2):
    x1, y1, w1, h1 = rhombus1
    x2, y2, w2, h2 = rhombus2
    left1 = x1 - w1 / 2
    right1 = x1 + w1 / 2
    top1 = y1 - h1 / 2
    bottom1 = y1 + h1 / 2

    left2 = x2 - w2 / 2
    right2 = x2 + w2 / 2
    top2 = y2 - h2 / 2
    bottom2 = y2 + h2 / 2

    return not (right1 < left2 or left1 > right2 or bottom1 < top2 or top1 > bottom2)


def generate_non_overlapping_images(num_images, w, h, size_min, size_max, overlap_prob=0.2, point=0, offset=0):
    existing_images = []
    result = []

    def is_overlapping(new_pos, new_size, shape):
        new_obj = (new_pos[0], new_pos[1], new_size[0], new_size[1])
        for pos, size, shp in existing_images:
            old_obj = (pos[0], pos[1], size[0], size[1])
            if shp == "circle":
                circle_new_obj = (new_pos[0], new_pos[1], min(new_size[0], new_size[1]) / 2)
                circle_old_obj = (pos[0], pos[1], min(size[0], size[1]) / 2)
                if circle_overlap(circle_new_obj, circle_old_obj):
                    return True
            elif shp == "rectangle":
                if rectangle_overlap(new_obj, old_obj):
                    return True
            elif shp == "pentagram":
                pentagram_new_obj = (new_pos[0], new_pos[1], min(new_size[0], new_size[1]) / 2)
                pentagram_old_obj = (pos[0], pos[1], min(size[0], size[1]) / 2)
                if pentagram_overlap(pentagram_new_obj, pentagram_old_obj):
                    return True
            elif shp == "triangle":
                triangle_new_obj = (new_pos[0], new_pos[1], min(new_size[0], new_size[1]) / 2)
                triangle_old_obj = (pos[0], pos[1], min(size[0], size[1]) / 2)
                if triangle_overlap(triangle_new_obj, triangle_old_obj):
                    return True
            elif shp == "rhombus":
                if rhombus_overlap(new_obj, old_obj):
                    return True
        return False

    shape_list = ["circle", "rectangle", "pentagram", "triangle", "rhombus"]
    for _ in range(num_images):
        if random.random() < overlap_prob:
            # 允许重叠，直接生成随机位置、大小和形状
            random_pos = (random.randint(point, w), random.randint(point, h))
            random_width = random.randint(size_min, size_max)
            random_height = random.randint(size_min, size_max)
            random_size = (random_width, random_height)
            random_shape = random.choice(shape_list)
        else:
            # 避免重叠，不断尝试直到找到不重叠的位置和形状
            max_attempts = 100
            attempts = 0
            while attempts < max_attempts:
                random_pos = (random.randint(point, w), random.randint(point, h))
                random_width = random.randint(size_min, size_max)
                random_height = random.randint(size_min, size_max)
                random_size = (random_width, random_height)
                random_shape = random.choice(shape_list)
                if not is_overlapping(random_pos, random_size, random_shape):
                    break
                attempts += 1
            if attempts == max_attempts:
                # 如果尝试次数达到上限，仍未找到合适位置，继续使用当前生成的位置和大小
                pass

        existing_images.append((random_pos, random_size, random_shape))
        result.append((random_pos, random_size, random_shape))

    return result

other_color_num = 0
all_color_nnum = 0

def create_img(img, num, w, h):
    point = 50
    size_min = 30
    size_max = 50  
    global other_color_num
    global all_color_nnum
    random_pos_list = []
    images = generate_non_overlapping_images(num, w, h, size_min, size_max, 0.001, point, 20)
    for pos, size, tmp in images:
        print(f"Position: {pos}, Size: {size}, shape: {tmp}")    
    for pos, size, shape in images:
        all_color_nnum += 1
        rand = random.randint(1,5)
        rand_color = random.randint(1,8)
        aspect_ratio = random.choice(np.arange(start=0.5, stop=1.5, step=0.1))
        rotation_angle = random.randint(0, 360)
        # random_pos = (random.randint(point, w), random.randint(point, h))
        # random_size = random.randint(size_min,size_max)
        random_pos = pos
        random_size = size
        random_pos_list.append([random_pos, random_size])
        color = 0
        if rand_color == 1:
            color = (255, 0, 0)
        if rand_color == 2:
            color = (0, 255, 0)
        if rand_color == 3:
            color = (0, 0, 255)
        if rand_color == 4:
            color = (255, 255, 0)
        if rand_color == 5:
            color = (255, 0, 255)
        if rand_color == 6:
            color = (0, 255, 255)
        if rand_color == 7:
            color = (0, 0, 0)
        if rand_color == 8:
            color = (255, 255, 255)
        if rand_color == 9:
            other_color_num += 1
            rand_Color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            color = rand_Color
            print(f"[{other_color_num}/{all_color_nnum}]干扰色已生成:", rand_Color)

        if shape == "pentagram":
            img = draw_star(np.array(img, np.uint8), random_pos, random_size, color, 1, rotation_angle, True)
        if shape == "triangle":
            img = draw_triangle(np.array(img, np.uint8), random_pos, random_size, color, aspect_ratio, rotation_angle, True)
        if shape == "rhombus":
            img = draw_rhombus(np.array(img, np.uint8), random_pos, random_size, color, aspect_ratio, rotation_angle, True)
        if shape == "rectangle":
            img = draw_rectangle(np.array(img, np.uint8), random_pos, random_size, color, aspect_ratio, rotation_angle, True)
        if shape == "circle":
            img = draw_circle(np.array(img, np.uint8), (int(random.randint(point, w)), int(random.randint(point, h))), random_size, color, True)
        # print(f"[{all_color_nnum}] - [{rand}] - [{rand_color}] - [{aspect_ratio}] - [{rotation_angle}]")
    img = cv2.flip(img, 0)
    print(random_pos_list)
    return img

w = 800
h = 480




for i in range(0, 5):
    img = cv2.imread(f"img/1/{random.randint(1, 30)}.jpg")
    img = cv2.resize(img, (w, h))
    img = create_img(img, 10, w, h)
    cv2.imwrite(f"res/1/{i}.jpg", img)      

batch_convert_images("res", "resbin")