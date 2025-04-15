# -*- coding: utf-8 -*-

import qrcode
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def generate_qr_code(data, output_file):
    """
    生成二维码图片并保存到指定文件。

    :param data: 二维码中包含的数据
    :param output_file: 保存二维码图片的文件路径
    """
    qr = qrcode.QRCode(
        version=None,  # 控制二维码的大小，1 是最小的
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错率
        box_size=10,  # 每个点的像素大小
        border=4,  # 边框宽度，单位为点
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_file)
    messagebox.showinfo("成功", f"二维码已保存到 {output_file}")

def browse_file():
    """
    打开文件对话框以选择保存路径。
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG 文件", "*.png"), ("所有文件", "*.*")]
    )
    return file_path

def generate_qr_from_gui(event=None):
    """
    从 GUI 获取输入并生成二维码。
    """
    data = entry_data.get()
    if not data:
        messagebox.showwarning("警告", "请输入数据！")
        return

    output_file = browse_file()
    if not output_file:
        # 如果用户未选择路径，则默认保存到程序所在目录
        output_file = os.path.join(os.getcwd(), "default_qr.png")
        messagebox.showinfo("提示", f"未选择路径，二维码将保存为 {output_file}")

    generate_qr_code(data, output_file)

# 创建主窗口
root = tk.Tk()
root.title("二维码生成器")

# 创建输入框和按钮
frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

label_data = tk.Label(frame, text="输入数据：")
label_data.grid(row=0, column=0, sticky="w")

entry_data = tk.Entry(frame, width=40)
entry_data.grid(row=0, column=1, padx=5, pady=5)

button_generate = tk.Button(frame, text="生成二维码", command=generate_qr_from_gui)
button_generate.grid(row=1, column=0, columnspan=2, pady=10)

# 绑定 Enter 键到生成二维码的功能
root.bind('<Return>', generate_qr_from_gui)

# 运行主循环
root.mainloop()