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
MARGIN = 25  # 增加边距以适应更大的形状

# ==== 颜色列表 ====
colors = [
    (255, 0, 0),      # 红
    (0, 255, 0),      # 绿
    (0, 0, 255),      # 蓝
    (255, 255, 0),    # 黄
    (0, 255, 255),    # 青
    (255, 0, 255),    # 咸红
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
def is_overlapping(box, margin=MARGIN):
    # 添加边距，使图形之间有一定的空间
    # 对不同形状使用不同的边距，进一步防止重叠
    box_with_margin = (
        box[0] - margin,
        box[1] - margin,
        box[2] + margin,
        box[3] + margin
    )
    for b in placed_boxes:
        # 计算两个框的中心点距离
        box1_center = ((box_with_margin[0] + box_with_margin[2]) / 2, (box_with_margin[1] + box_with_margin[3]) / 2)
        box2_center = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
        
        # 计算中心点距离
        center_distance = math.sqrt((box1_center[0] - box2_center[0])**2 + (box1_center[1] - box2_center[1])**2)
        
        # 计算两个框的对角线长度
        diag1 = math.sqrt((box_with_margin[2] - box_with_margin[0])**2 + (box_with_margin[3] - box_with_margin[1])**2)
        diag2 = math.sqrt((b[2] - b[0])**2 + (b[3] - b[1])**2)
        
        # 如果中心点距离小于对角线长度和的一半，认为可能重叠
        if center_distance < (diag1 + diag2) / 3:
            # 再进行精确的边界框检测
            if not (box_with_margin[2] < b[0] or box_with_margin[0] > b[2] or 
                    box_with_margin[3] < b[1] or box_with_margin[1] > b[3]):
                return True
    return False

def get_non_overlapping_position(w, h, margin=MARGIN):
    max_tries = 300
    for _ in range(max_tries):
        x = random.randint(w + margin, canvas_size[0] - w - margin)
        y = random.randint(h + margin, canvas_size[1] - h - margin)
        box = (x - w, y - h, x + w, y + h)
        if not is_overlapping(box, margin):
            return x, y
    return None

def get_non_overlapping_position_from_points(points, margin=MARGIN):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    box = (min(xs), min(ys), max(xs), max(ys))
    
    # 确保图形在画布内，留有边距
    if (box[0] - margin < 0 or box[1] - margin < 0 or 
        box[2] + margin > canvas_size[0] or box[3] + margin > canvas_size[1]):
        return False
        
    if is_overlapping(box, margin):
        return False
    placed_boxes.append(box)
    return True

def rotate_points(points, center, angle_deg):
    angle_rad = math.radians(angle_deg)
    cx, cy = center
    rotated = []
    for x, y in points:
        dx, dy = x - cx, y - cy
        rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        rotated.append((cx + rx, cy + ry))
    return rotated

# ==== 各种图形绘制函数 ====
def draw_star(draw, center, size, color, angle=0):
    x, y = center
    points = []
    for i in range(10):
        angle_deg = 36 * i - 90
        angle_rad = math.radians(angle_deg)
        r = size if i % 2 == 0 else size * 0.4
        px = x + r * math.cos(angle_rad)
        py = y + r * math.sin(angle_rad)
        points.append((px, py))
    points = rotate_points(points, center, angle)
    if get_non_overlapping_position_from_points(points):
        draw.polygon(points, fill=color)
        return True
    return False

def draw_triangle(draw, center, size, color, direction='up', angle=0):
    x, y = center
    if direction == 'up':
        points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
    else:
        points = [(x, y + size), (x - size, y - size), (x + size, y - size)]
    points = rotate_points(points, center, angle)
    if get_non_overlapping_position_from_points(points):
        draw.polygon(points, fill=color)
        return True
    return False

def draw_diamond(draw, center, size, color):
    x, y = center
    points = [(x, y - size * 1.5), (x - size, y), (x, y + size * 1.5), (x + size, y)]
    if get_non_overlapping_position_from_points(points):
        draw.polygon(points, fill=color)
        return True
    return False

def draw_tilted_diamond_safe(draw, color, w, margin=MARGIN):
    h = int(w * 1.5)
    max_tries = 300
    for _ in range(max_tries):
        x = random.randint(w + margin, canvas_size[0] - w - margin)
        y = random.randint(h + margin, canvas_size[1] - h - margin)
        center = (x, y)
        angle = random.choice([0, 45, 90, 135, 180, 225, 270, 315])

        base_points = [
            (x, y - h),
            (x + w, y),
            (x, y + h),
            (x - w, y)
        ]

        rotated_points = rotate_points(base_points, center, angle)
        if get_non_overlapping_position_from_points(rotated_points, margin):
            draw.polygon(rotated_points, fill=color)
            return True
    return False

# ==== 主函数 ====
def generate_image(image_index):
    global placed_boxes
    placed_boxes = []
    
    # 添加图形计数
    shape_counts = {
        'rect': 0,
        'circle': 0,
        'triangle': 0,
        'star': 0,
        'diamond': 0,
        'diamond_tilted': 0
    }

    img = load_random_background()
    draw = ImageDraw.Draw(img)

    # 确定本图像要生成的形状总数，减少总数以适应更大的形状
    total_shapes = random.randint(8, 12)
    current_shapes = 0
    
    # 确保每种形状至少有一个
    shape_types = ['rect', 'circle', 'triangle', 'star', 'diamond', 'diamond_tilted']
    random.shuffle(shape_types)  # 随机打乱顺序
    
    # 首先尝试生成每种形状至少一个
    for shape_type in shape_types:
        if current_shapes >= total_shapes:
            break
        color = random.choice(colors)
        if generate_shape(draw, shape_type, color, shape_counts):
            current_shapes += 1
    
    # 继续随机生成剩余的形状
    max_total_attempts = 300  # 增加总尝试次数
    total_attempts = 0
    
    while current_shapes < total_shapes and total_attempts < max_total_attempts:
        # 选择各种形状类型
        shape_type = random.choice(shape_types)
        color = random.choice(colors)
        total_attempts += 1
        
        if generate_shape(draw, shape_type, color, shape_counts):
            current_shapes += 1

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(os.path.join(shape_output_dir, f"shapes_{image_index:03d}.png"))
    print(f"图片 {image_index:03d} 生成的图形数量: {shape_counts}，总数: {current_shapes}")

def generate_shape(draw, shape_type, color, shape_counts):
    """生成指定类型的形状，并更新计数"""
    max_attempts = 15  # 增加尝试次数，提高成功率
    
    if shape_type == 'rect':
        for attempt in range(max_attempts):
            # 增大矩形尺寸
            rect_size_w = random.randint(25, 50)
            rect_size_h = random.randint(25, 50)
            cx = random.randint(rect_size_w + 25, canvas_size[0] - rect_size_w - 25)
            cy = random.randint(rect_size_h + 25, canvas_size[1] - rect_size_h - 25)
            
            angle = random.randint(0, 359)
            points = [
                (cx - rect_size_w, cy - rect_size_h),
                (cx + rect_size_w, cy - rect_size_h),
                (cx + rect_size_w, cy + rect_size_h),
                (cx - rect_size_w, cy + rect_size_h)
            ]
            points = rotate_points(points, (cx, cy), angle)
            
            if get_non_overlapping_position_from_points(points):
                draw.polygon(points, fill=color)
                shape_counts['rect'] += 1
                return True
    
    elif shape_type == 'circle':
        for attempt in range(max_attempts):
            # 增大圆形尺寸
            size = random.randint(30, 55)
            cx = random.randint(size + 25, canvas_size[0] - size - 25)
            cy = random.randint(size + 25, canvas_size[1] - size - 25)
            
            box = (cx - size, cy - size, cx + size, cy + size)
            if not is_overlapping(box):
                placed_boxes.append(box)
                draw.ellipse(box, fill=color)
                shape_counts['circle'] += 1
                return True
    
    elif shape_type == 'triangle':
        for attempt in range(max_attempts):
            # 增大三角形尺寸
            size = random.randint(30, 55)
            cx = random.randint(size + 25, canvas_size[0] - size - 25)
            cy = random.randint(size + 25, canvas_size[1] - size - 25)
            
            direction = random.choice(['up', 'down'])
            angle = random.randint(0, 359)
            if draw_triangle(draw, (cx, cy), size, color, direction, angle):
                shape_counts['triangle'] += 1
                return True
    
    elif shape_type == 'star':
        for attempt in range(max_attempts):
            # 增大星形尺寸
            size = random.randint(30, 55)
            cx = random.randint(size + 25, canvas_size[0] - size - 25)
            cy = random.randint(size + 25, canvas_size[1] - size - 25)
            
            angle = random.randint(0, 359)
            if draw_star(draw, (cx, cy), size, color, angle):
                shape_counts['star'] += 1
                return True
    
    elif shape_type == 'diamond':
        for attempt in range(max_attempts):
            # 增大菱形尺寸
            size = random.randint(30, 50)
            height = int(size * 1.5)
            cx = random.randint(size + 25, canvas_size[0] - size - 25)
            cy = random.randint(height + 25, canvas_size[1] - height - 25)
            
            if draw_diamond(draw, (cx, cy), size, color):
                shape_counts['diamond'] += 1
                return True
    
    elif shape_type == 'diamond_tilted':
        for attempt in range(max_attempts):
            # 增大倾斜菱形尺寸
            size = random.randint(30, 50)
            if draw_tilted_diamond_safe(draw, color, size):
                shape_counts['diamond_tilted'] += 1
                return True
    
    return False

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
create_number = 400
for i in range(create_number):
    generate_image(i)
batch_convert_images("res/1", "resbin/1")