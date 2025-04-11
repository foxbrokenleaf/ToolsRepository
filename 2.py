from PIL import Image
import cv2
import numpy as np
import random
import os
import struct

def add_png_to_image(src_image, png_path, top_left, scale):
    # 读取 PNG 图像
    png_image = cv2.imread(png_path, cv2.IMREAD_UNCHANGED)

    # 缩放 PNG 图像
    new_width = int(png_image.shape[1] * scale)
    new_height = int(png_image.shape[0] * scale)
    png_image = cv2.resize(png_image, (new_width, new_height))

    # 提取 PNG 图像的透明通道
    alpha_channel = png_image[:, :, 3] / 255.0
    png_image = png_image[:, :, :3]

    # 获取 PNG 图像的尺寸
    h, w = png_image.shape[:2]

    # 计算放置 PNG 图像的位置
    x, y = top_left

    # 确保位置在源图像范围内
    x_end = min(x + w, src_image.shape[1])
    y_end = min(y + h, src_image.shape[0])
    x_start = max(x, 0)
    y_start = max(y, 0)

    # 计算裁剪后的 PNG 图像的位置
    x_png_start = max(0, -x)
    y_png_start = max(0, -y)
    x_png_end = x_png_start + (x_end - x_start)
    y_png_end = y_png_start + (y_end - y_start)

    # 裁剪 PNG 图像和透明通道
    cropped_png = png_image[y_png_start:y_png_end, x_png_start:x_png_end]
    cropped_alpha = alpha_channel[y_png_start:y_png_end, x_png_start:x_png_end]

    # 裁剪源图像的对应区域
    cropped_src = src_image[y_start:y_end, x_start:x_end]

    # 混合图像
    for c in range(0, 3):
        cropped_src[:, :, c] = (cropped_alpha * cropped_png[:, :, c] +
                                (1 - cropped_alpha) * cropped_src[:, :, c]).astype(np.uint8)

    # 将混合后的图像放回源图像
    src_image[y_start:y_end, x_start:x_end] = cropped_src

    return src_image

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

w = 800
h = 480
for i in range(0, 400):
    bck_path = f"img/2/background/{random.randint(1, 17)}.jpg"
    traffic_path = f"img/2/{random.randint(1, 7)}.png"
    pos = (random.randint(50, 650), random.randint(100, 350))
    img = cv2.imread(bck_path)
    traffic = cv2.imread(traffic_path)
    img = cv2.resize(img, (w, h))
    img = add_png_to_image(img, traffic_path, pos, 0.25)
    if i >= 300:
        traffic_path = f"img/2/{random.randint(1, 7)}.png"
        pos = (random.randint(50, 650), random.randint(100, 350))
        traffic = cv2.imread(traffic_path)
        img = add_png_to_image(img, traffic_path, pos, 0.25)    

    img = cv2.flip(img, 0) 
    cv2.imwrite(f"res/2/{i}.jpg", img)

batch_convert_images("res/2", "resbin/2")
