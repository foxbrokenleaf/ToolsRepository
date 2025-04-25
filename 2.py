import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def update_image():
    """更新图像显示"""
    global hsv, image, canvas_result, photo_result

    # 获取 Trackbar 的值
    lh = lh_scale.get()
    ls = ls_scale.get()
    lv = lv_scale.get()
    uh = uh_scale.get()
    us = us_scale.get()
    uv = uv_scale.get()

    # 定义 HSV 的上下限
    lower_hsv = np.array([lh, ls, lv])
    upper_hsv = np.array([uh, us, uv])

    # 创建掩膜
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

    # 使用掩膜提取结果
    result = cv2.bitwise_and(image, image, mask=mask)

    # 转换为 Tkinter 可显示的格式
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    result_image = Image.fromarray(result_rgb)
    photo_result = ImageTk.PhotoImage(result_image)

    # 更新 Canvas
    canvas_result.create_image(0, 0, anchor=tk.NW, image=photo_result)

def load_image():
    """加载图片"""
    global image, hsv, canvas_original, photo_original

    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if not file_path:
        return

    # 加载图片
    image_loaded = cv2.imread(file_path)
    if image_loaded is None:
        print("无法加载图片，请检查路径！")
        return

    # 调整全局变量以适应加载的图片尺寸
    global image, hsv
    image = image_loaded
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 转换为 Tkinter 可显示的格式
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    original_image = Image.fromarray(image_rgb)
    photo_original = ImageTk.PhotoImage(original_image)

    # 调整 Canvas 尺寸以适应图片
    canvas_original.config(width=image.shape[1], height=image.shape[0])
    canvas_result.config(width=image.shape[1], height=image.shape[0])

    # 更新 Canvas
    canvas_original.create_image(0, 0, anchor=tk.NW, image=photo_original)
    update_image()

# 初始化 Tkinter 窗口
root = tk.Tk()
root.title("HSV 阈值调整")

# 初始化全局变量
image = np.zeros((300, 300, 3), dtype=np.uint8)
hsv = np.zeros_like(image)
photo_original = None
photo_result = None

# 创建控件
frame_controls = tk.Frame(root)
frame_controls.pack(side=tk.LEFT, fill=tk.Y)

# 加载图片按钮
btn_load = tk.Button(frame_controls, text="加载图片", command=load_image)
btn_load.pack(pady=5)

# 创建滑块
lh_scale = tk.Scale(frame_controls, from_=0, to=179, label="Lower Hue", orient=tk.HORIZONTAL, command=lambda x: update_image())
lh_scale.pack(fill=tk.X)
ls_scale = tk.Scale(frame_controls, from_=0, to=255, label="Lower Saturation", orient=tk.HORIZONTAL, command=lambda x: update_image())
ls_scale.pack(fill=tk.X)
lv_scale = tk.Scale(frame_controls, from_=0, to=255, label="Lower Value", orient=tk.HORIZONTAL, command=lambda x: update_image())
lv_scale.pack(fill=tk.X)
uh_scale = tk.Scale(frame_controls, from_=0, to=179, label="Upper Hue", orient=tk.HORIZONTAL, command=lambda x: update_image())
uh_scale.pack(fill=tk.X)
us_scale = tk.Scale(frame_controls, from_=0, to=255, label="Upper Saturation", orient=tk.HORIZONTAL, command=lambda x: update_image())
us_scale.pack(fill=tk.X)
uv_scale = tk.Scale(frame_controls, from_=0, to=255, label="Upper Value", orient=tk.HORIZONTAL, command=lambda x: update_image())
uv_scale.pack(fill=tk.X)

# 创建显示区域
frame_images = tk.Frame(root)
frame_images.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

canvas_original = tk.Canvas(frame_images, width=300, height=300, bg="gray")
canvas_original.pack(side=tk.LEFT, padx=5, pady=5)

canvas_result = tk.Canvas(frame_images, width=300, height=300, bg="gray")
canvas_result.pack(side=tk.RIGHT, padx=5, pady=5)

# 启动主循环
root.mainloop()