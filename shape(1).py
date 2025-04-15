from PIL import Image, ImageDraw
import random
import os
import math
import struct

# ==== 参数 ====
canvas_size = (800, 480)
shape_output_dir = "res\\1"
backgrounds_dir = "img\\1"
os.makedirs(shape_output_dir, exist_ok=True)

# ==== 颜色列表 ====
colors = [
    (255, 0, 0),      # 红
    (0, 255, 0),      # 绿
    (0, 0, 255),      # 蓝
    (255, 255, 0),    # 黄
    (0, 255, 255),    # 青
    (255, 0, 255),    # 品红
    (255, 255, 255)   # 白
]

placed_boxes = []

# ==== 背景加载 ====
def load_random_background():
    if not os.path.exists(backgrounds_dir):
        return Image.new("RGB", canvas_size, (30, 30, 30))
    bg_files = [f for f in os.listdir(backgrounds_dir) if f.endswith(('.png', '.jpg'))]
    if not bg_files:
        return Image.new("RGB", canvas_size, (30, 30, 30))
    bg_path = os.path.join(backgrounds_dir, random.choice(bg_files))
    bg = Image.open(bg_path).convert("RGB")
    return bg.resize(canvas_size)

# ==== 重叠检测 ====
def is_overlapping(box):
    for b in placed_boxes:
        if not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]):
            return True
    return False

def get_non_overlapping_position(w, h):
    max_tries = 300
    for _ in range(max_tries):
        x = random.randint(w, canvas_size[0] - w)
        y = random.randint(h, canvas_size[1] - h)
        box = (x - w, y - h, x + w, y + h)
        if not is_overlapping(box):
            placed_boxes.append(box)
            return x, y
    return None

def get_non_overlapping_position_from_points(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    box = (min(xs), min(ys), max(xs), max(ys))
    if box[0] < 0 or box[1] < 0 or box[2] > canvas_size[0] or box[3] > canvas_size[1]:
        return False
    if is_overlapping(box):
        return False
    placed_boxes.append(box)
    return True

# ==== 各种图形绘制函数 ====
def draw_star(draw, center, size, color):
    x, y = center
    points = []
    for i in range(10):
        angle_deg = 36 * i - 90
        angle_rad = math.radians(angle_deg)
        r = size if i % 2 == 0 else size * 0.4
        px = x + r * math.cos(angle_rad)
        py = y + r * math.sin(angle_rad)
        points.append((px, py))
    draw.polygon(points, fill=color)

def draw_triangle(draw, center, size, color, direction='up'):
    x, y = center
    if direction == 'up':
        points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
    else:
        points = [(x, y + size), (x - size, y - size), (x + size, y - size)]
    if get_non_overlapping_position_from_points(points):
        draw.polygon(points, fill=color)

def draw_diamond(draw, center, size, color):
    x, y = center
    points = [(x, y - size), (x - size, y), (x, y + size), (x + size, y)]
    if get_non_overlapping_position_from_points(points):
        draw.polygon(points, fill=color)

def draw_tilted_diamond_safe(draw, color, w, h):
    max_tries = 300
    for _ in range(max_tries):
        x = random.randint(w, canvas_size[0] - w)
        y = random.randint(h * 2, canvas_size[1] - h * 2)
        center = (x, y)
        angle = random.choice([0, 45, 90, 135, 180, 225, 270, 315])

        height = h * 2
        base_points = [
            (x, y - height),
            (x + w, y),
            (x, y + height),
            (x - w, y)
        ]

        angle_rad = math.radians(angle)
        rotated_points = []
        for px, py in base_points:
            dx = px - x
            dy = py - y
            rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
            rotated_points.append((x + rx, y + ry))

        if get_non_overlapping_position_from_points(rotated_points):
            draw.polygon(rotated_points, fill=color)
            return

# ==== 主函数 ====
def generate_image(image_index):
    global placed_boxes
    placed_boxes = []

    img = load_random_background()
    draw = ImageDraw.Draw(img)

    shape_count = random.randint(10, 20)

    for _ in range(shape_count):
        shape_type = random.choice(['rect', 'circle', 'triangle', 'star', 'diamond', 'diamond_tilted'])
        color = random.choice(colors)

        if shape_type == 'rect':
            w = random.randint(20, 80)
            h = random.randint(20, 80)
            pos = get_non_overlapping_position(w, h)
            if pos:
                x, y = pos
                draw.rectangle([x - w, y - h, x + w, y + h], fill=color)

        elif shape_type == 'circle':
            size = random.randint(20, 60)
            pos = get_non_overlapping_position(size, size)
            if pos:
                x, y = pos
                draw.ellipse([x - size, y - size, x + size, y + size], fill=color)

        elif shape_type == 'triangle':
            size = random.randint(20, 60)
            x = random.randint(size, canvas_size[0] - size)
            y = random.randint(size, canvas_size[1] - size)
            direction = random.choice(['up', 'down'])
            draw_triangle(draw, (x, y), size, color, direction)

        elif shape_type == 'star':
            size = random.randint(20, 60)
            x = random.randint(size, canvas_size[0] - size)
            y = random.randint(size, canvas_size[1] - size)
            points = []
            for i in range(10):
                angle_deg = 36 * i - 90
                angle_rad = math.radians(angle_deg)
                r = size if i % 2 == 0 else size * 0.4
                px = x + r * math.cos(angle_rad)
                py = y + r * math.sin(angle_rad)
                points.append((px, py))
            if get_non_overlapping_position_from_points(points):
                draw.polygon(points, fill=color)

        elif shape_type == 'diamond':
            size = random.randint(20, 60)
            x = random.randint(size, canvas_size[0] - size)
            y = random.randint(size, canvas_size[1] - size)
            draw_diamond(draw, (x, y), size, color)

        elif shape_type == 'diamond_tilted':
            w = random.randint(20, 40)
            h = random.randint(20, 40)
            draw_tilted_diamond_safe(draw, color, w, h)

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(os.path.join(shape_output_dir, f"shapes_{image_index:03d}.png"))


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

# ==== 批量生成 ====
for i in range(100):
    generate_image(i)
batch_convert_images("res/1", "resbin/1")