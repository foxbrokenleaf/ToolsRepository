from PIL import Image
import cv2
import numpy as np
import random
import os
import struct
import math

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

batch_convert_images("res/1", "resbin/1")