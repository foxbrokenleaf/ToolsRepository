from tkinter import Tk, Label, Button, filedialog, messagebox, Text, Scrollbar, END
from tkinter.ttk import Progressbar
from PIL import Image, ImageDraw
import random
import os
import math
import struct
import threading

def convert_image_to_rgb565(image: Image.Image):
    """将Pillow图像对象转为RGB565字节列表"""
    image = image.convert('RGB')
    # image = image.transpose(Image.FLIP_TOP_BOTTOM)  # 适配Image2Lcd的扫描方向
    pixels = list(image.getdata())

    rgb565_bytes = bytearray()
    for r, g, b in pixels:
        value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        rgb565_bytes.extend(struct.pack('<H', value))  # 小端写入

    return rgb565_bytes

def scale_and_crop_image(image: Image.Image, target_width: int, target_height: int):
    """将图像缩放并裁剪到指定大小"""
    img_ratio = image.width / image.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        # 图像更宽，按高度缩放
        new_height = target_height
        new_width = int(target_height * img_ratio)
    else:
        # 图像更高或等比，按宽度缩放
        new_width = target_width
        new_height = int(target_width / img_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)

    # 中心裁剪
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return image.crop((left, top, right, bottom))

def batch_convert_images(input_folder, output_folder, cropped_folder, width=800, height=480):
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(cropped_folder, exist_ok=True)
    supported_ext = ('.png', '.jpg', '.jpeg', '.bmp')

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_ext)]
    total_files = len(files)
    progress_bar["maximum"] = total_files

    for index, filename in enumerate(files):
        input_path = os.path.join(input_folder, filename)
        output_name = os.path.splitext(filename)[0] + '.bin'
        cropped_name = os.path.splitext(filename)[0] + '.cropped.png'
        output_path = os.path.join(output_folder, output_name)
        cropped_path = os.path.join(cropped_folder, cropped_name)

        try:
            with Image.open(input_path) as img:
                img_scaled_cropped = scale_and_crop_image(img, width, height)
                img_scaled_cropped.save(cropped_path)  # 保存缩放裁剪后的图片
                data = convert_image_to_rgb565(img_scaled_cropped)
                with open(output_path, 'wb') as f:
                    f.write(data)
                log_message(f"[✅] 已转换: {filename} → {output_name}, 裁剪图像保存为: {cropped_name}")
        except Exception as e:
            log_message(f"[❌] 转换失败: {filename}, 错误: {e}")

        # 更新进度条
        progress_bar["value"] = index + 1
        root.update_idletasks()

    messagebox.showinfo("完成", "🎉 全部转换完成！")

def log_message(message):
    """在日志窗口中显示信息"""
    log_text.insert(END, message + "\n")
    log_text.see(END)

def select_input_folder():
    folder = filedialog.askdirectory(title="选择输入文件夹")
    if folder:
        input_folder_label.config(text=folder)

def select_output_folder():
    folder = filedialog.askdirectory(title="选择输出文件夹")
    if folder:
        output_folder_label.config(text=folder)

def select_cropped_folder():
    folder = filedialog.askdirectory(title="选择裁剪图像输出文件夹")
    if folder:
        cropped_folder_label.config(text=folder)

def start_conversion():
    input_folder = input_folder_label.cget("text")
    output_folder = output_folder_label.cget("text")
    cropped_folder = cropped_folder_label.cget("text")

    if not os.path.isdir(input_folder):
        messagebox.showerror("错误", "请选择有效的输入文件夹！")
        return

    if not os.path.isdir(output_folder):
        messagebox.showerror("错误", "请选择有效的输出文件夹！")
        return

    if not os.path.isdir(cropped_folder):
        messagebox.showerror("错误", "请选择有效的裁剪图像输出文件夹！")
        return

    log_message("开始转换...")

    # 使用线程执行转换操作
    threading.Thread(
        target=batch_convert_images,
        args=(input_folder, output_folder, cropped_folder),
        daemon=True
    ).start()

# 创建主窗口
root = Tk()
root.title("图像转换工具")

# 输入文件夹选择
Label(root, text="输入文件夹:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
input_folder_label = Label(root, text="未选择", width=50, anchor="w")
input_folder_label.grid(row=0, column=1, padx=10, pady=5)
Button(root, text="选择", command=select_input_folder).grid(row=0, column=2, padx=10, pady=5)

# 输出文件夹选择
Label(root, text="输出文件夹:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_folder_label = Label(root, text="未选择", width=50, anchor="w")
output_folder_label.grid(row=1, column=1, padx=10, pady=5)
Button(root, text="选择", command=select_output_folder).grid(row=1, column=2, padx=10, pady=5)

# 裁剪图像输出文件夹选择
Label(root, text="裁剪图像输出文件夹:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
cropped_folder_label = Label(root, text="未选择", width=50, anchor="w")
cropped_folder_label.grid(row=2, column=1, padx=10, pady=5)
Button(root, text="选择", command=select_cropped_folder).grid(row=2, column=2, padx=10, pady=5)

# 日志输出窗口
Label(root, text="日志输出:").grid(row=3, column=0, padx=10, pady=5, sticky="nw")
log_text = Text(root, width=70, height=15, wrap="word")
log_text.grid(row=3, column=1, padx=10, pady=5, columnspan=2)
scrollbar = Scrollbar(root, command=log_text.yview)
scrollbar.grid(row=3, column=3, sticky="ns", pady=5)
log_text.config(yscrollcommand=scrollbar.set)

# 进度条
progress_bar = Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, pady=10)

# 开始转换按钮
Button(root, text="开始转换", command=start_conversion, width=20).grid(row=5, column=0, columnspan=3, pady=20)

# 运行主循环
root.mainloop()

