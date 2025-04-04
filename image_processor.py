import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import cv2

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("图像处理工具")
        self.root.geometry("1200x800")
        
        # 初始化变量
        self.image = None
        self.original_image = None
        self.photo = None
        self.mouse_pos = None
        self.drawing = False
        self.circle_center = None
        self.circle_radius = 0
        
        # 添加图像显示相关的变量
        self.image_scale = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        # 创建主框架
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧图像显示区域
        self.canvas = tk.Canvas(main_frame, width=800, height=600, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 右侧控制面板
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # 信息显示框
        info_frame = ttk.LabelFrame(right_panel, text="信息")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.thumbnail_label = ttk.Label(info_frame)
        self.thumbnail_label.pack(pady=5)
        
        self.rgb_label = ttk.Label(info_frame, text="RGB: (0, 0, 0)")
        self.rgb_label.pack(pady=5)
        
        # 阈值设置框
        threshold_frame = ttk.LabelFrame(right_panel, text="阈值")
        threshold_frame.pack(fill=tk.X, pady=5)
        
        # RGB范围设置
        rgb_frame = ttk.Frame(threshold_frame)
        rgb_frame.pack(fill=tk.X, pady=5)
        
        # 创建标签和输入框
        # R通道设置
        r_frame = ttk.Frame(rgb_frame)
        r_frame.pack(fill=tk.X, pady=2)
        ttk.Label(r_frame, text="R通道:").pack(side=tk.LEFT, padx=5)
        ttk.Label(r_frame, text="最小值:").pack(side=tk.LEFT, padx=2)
        self.r_min = ttk.Spinbox(r_frame, from_=0, to=255, width=5)
        self.r_min.pack(side=tk.LEFT, padx=2)
        ttk.Label(r_frame, text="最大值:").pack(side=tk.LEFT, padx=2)
        self.r_max = ttk.Spinbox(r_frame, from_=0, to=255, width=5)
        self.r_max.pack(side=tk.LEFT, padx=2)
        
        # G通道设置
        g_frame = ttk.Frame(rgb_frame)
        g_frame.pack(fill=tk.X, pady=2)
        ttk.Label(g_frame, text="G通道:").pack(side=tk.LEFT, padx=5)
        ttk.Label(g_frame, text="最小值:").pack(side=tk.LEFT, padx=2)
        self.g_min = ttk.Spinbox(g_frame, from_=0, to=255, width=5)
        self.g_min.pack(side=tk.LEFT, padx=2)
        ttk.Label(g_frame, text="最大值:").pack(side=tk.LEFT, padx=2)
        self.g_max = ttk.Spinbox(g_frame, from_=0, to=255, width=5)
        self.g_max.pack(side=tk.LEFT, padx=2)
        
        # B通道设置
        b_frame = ttk.Frame(rgb_frame)
        b_frame.pack(fill=tk.X, pady=2)
        ttk.Label(b_frame, text="B通道:").pack(side=tk.LEFT, padx=5)
        ttk.Label(b_frame, text="最小值:").pack(side=tk.LEFT, padx=2)
        self.b_min = ttk.Spinbox(b_frame, from_=0, to=255, width=5)
        self.b_min.pack(side=tk.LEFT, padx=2)
        ttk.Label(b_frame, text="最大值:").pack(side=tk.LEFT, padx=2)
        self.b_max = ttk.Spinbox(b_frame, from_=0, to=255, width=5)
        self.b_max.pack(side=tk.LEFT, padx=2)
        
        # 设置初始值
        for spinbox in [self.r_min, self.r_max, self.g_min, self.g_max, self.b_min, self.b_max]:
            spinbox.set(0)
        
        # 目标RGB值设置
        target_frame = ttk.Frame(threshold_frame)
        target_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(target_frame, text="目标颜色:").pack(side=tk.LEFT, padx=5)
        ttk.Label(target_frame, text="R:").pack(side=tk.LEFT, padx=2)
        self.target_r = ttk.Spinbox(target_frame, from_=0, to=255, width=5)
        self.target_r.pack(side=tk.LEFT, padx=2)
        ttk.Label(target_frame, text="G:").pack(side=tk.LEFT, padx=2)
        self.target_g = ttk.Spinbox(target_frame, from_=0, to=255, width=5)
        self.target_g.pack(side=tk.LEFT, padx=2)
        ttk.Label(target_frame, text="B:").pack(side=tk.LEFT, padx=2)
        self.target_b = ttk.Spinbox(target_frame, from_=0, to=255, width=5)
        self.target_b.pack(side=tk.LEFT, padx=2)
        
        # 设置初始值
        for spinbox in [self.target_r, self.target_g, self.target_b]:
            spinbox.set(0)
        
        # 应用阈值按钮
        apply_button = ttk.Button(threshold_frame, text="应用阈值", command=self.apply_threshold)
        apply_button.pack(pady=5)
        
        # 预览图像标签
        self.preview_label = ttk.Label(threshold_frame)
        self.preview_label.pack(pady=5)
        
        # 重设按钮
        reset_button = ttk.Button(right_panel, text="重设图像", command=self.reset_image)
        reset_button.pack(pady=5)
        
        # 打开图像按钮
        open_button = ttk.Button(right_panel, text="打开图像", command=self.open_image)
        open_button.pack(pady=5)
        
        # 绑定鼠标事件
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<Button-1>", self.mouse_press)
        self.canvas.bind("<B1-Motion>", self.mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release)
    
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.bmp")]
        )
        if file_path:
            self.image = Image.open(file_path)
            image_np = np.array(self.image, dtype=np.uint8)
            mat = cv2.cvtColor(image_np, cv2.COLOR_RGB2LAB)
            image_np = np.array(mat, dtype=np.uint8)
            self.image = Image.fromarray(image_np)
            self.original_image = self.image.copy()
            self.update_image()
    
    def update_image(self):
        if self.image:
            # 调整图像大小以适应画布
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            image_ratio = self.image.width / self.image.height
            canvas_ratio = canvas_width / canvas_height
            
            if image_ratio > canvas_ratio:
                new_width = canvas_width
                new_height = int(canvas_width / image_ratio)
            else:
                new_height = canvas_height
                new_width = int(canvas_height * image_ratio)
            
            # 计算缩放比例和偏移量
            self.image_scale = new_width / self.image.width
            self.image_offset_x = (canvas_width - new_width) // 2
            self.image_offset_y = (canvas_height - new_height) // 2
            
            resized_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo)
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """将画布坐标转换为图像坐标"""
        if not self.image:
            return None, None
        
        # 减去偏移量并除以缩放比例
        image_x = int((canvas_x - self.image_offset_x) / self.image_scale)
        image_y = int((canvas_y - self.image_offset_y) / self.image_scale)
        
        # 检查坐标是否在图像范围内
        if (0 <= image_x < self.image.width and 
            0 <= image_y < self.image.height):
            return image_x, image_y
        return None, None
    
    def mouse_move(self, event):
        if self.image:
            self.mouse_pos = (event.x, event.y)
            self.update_thumbnail()
            self.update_rgb_info()
            self.draw_crosshair()
    
    def mouse_press(self, event):
        if self.image:
            self.drawing = True
            self.circle_center = (event.x, event.y)
            self.circle_radius = 0
    
    def mouse_drag(self, event):
        if self.drawing and self.image:
            self.circle_radius = int(((event.x - self.circle_center[0]) ** 2 +
                                    (event.y - self.circle_center[1]) ** 2) ** 0.5)
            self.draw_circle()
    
    def mouse_release(self, event):
        self.drawing = False
        self.circle_center = None
        self.circle_radius = 0
    
    def update_thumbnail(self):
        if self.image and self.mouse_pos:
            canvas_x, canvas_y = self.mouse_pos
            image_x, image_y = self.canvas_to_image_coords(canvas_x, canvas_y)
            
            if image_x is not None and image_y is not None:
                size = 50
                left = max(0, image_x - size//2)
                top = max(0, image_y - size//2)
                right = min(self.image.width, image_x + size//2)
                bottom = min(self.image.height, image_y + size//2)
                
                thumbnail = self.image.crop((left, top, right, bottom))
                thumbnail = thumbnail.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(thumbnail)
                self.thumbnail_label.configure(image=photo)
                self.thumbnail_label.image = photo
    
    def update_rgb_info(self):
        if self.image and self.mouse_pos:
            canvas_x, canvas_y = self.mouse_pos
            image_x, image_y = self.canvas_to_image_coords(canvas_x, canvas_y)
            
            if image_x is not None and image_y is not None:
                rgb = self.image.getpixel((image_x, image_y))
                self.rgb_label.configure(text=f"RGB: {rgb}")
    
    def draw_crosshair(self):
        if self.mouse_pos:
            x, y = self.mouse_pos
            self.canvas.delete("crosshair")
            self.canvas.create_line(x-10, y, x+10, y, fill="red", tags="crosshair")
            self.canvas.create_line(x, y-10, x, y+10, fill="red", tags="crosshair")
    
    def draw_circle(self):
        if self.circle_center and self.circle_radius > 0:
            canvas_x, canvas_y = self.circle_center
            image_x, image_y = self.canvas_to_image_coords(canvas_x, canvas_y)
            
            if image_x is not None and image_y is not None:
                # 计算圆形内的最大和最小RGB值
                min_rgb = [255, 255, 255]
                max_rgb = [0, 0, 0]
                
                # 将半径转换为图像坐标
                image_radius = int(self.circle_radius / self.image_scale)
                
                for i in range(max(0, image_x - image_radius),
                             min(self.image.width, image_x + image_radius)):
                    for j in range(max(0, image_y - image_radius),
                                 min(self.image.height, image_y + image_radius)):
                        if ((i - image_x) ** 2 + (j - image_y) ** 2) <= image_radius ** 2:
                            rgb = self.image.getpixel((i, j))
                            min_rgb = [min(min_rgb[0], rgb[0]),
                                     min(min_rgb[1], rgb[1]),
                                     min(min_rgb[2], rgb[2])]
                            max_rgb = [max(max_rgb[0], rgb[0]),
                                     max(max_rgb[1], rgb[1]),
                                     max(max_rgb[2], rgb[2])]
                
                # 在画布上绘制圆形
                self.canvas.delete("circle")
                self.canvas.create_oval(canvas_x-self.circle_radius, canvas_y-self.circle_radius,
                                      canvas_x+self.circle_radius, canvas_y+self.circle_radius,
                                      outline="blue", width=2, tags="circle")
                
                self.canvas.delete("rgb_text")
                self.canvas.create_text(canvas_x + self.circle_radius + 10, canvas_y,
                                      text=f"Min RGB: {min_rgb}\nMax RGB: {max_rgb}",
                                      fill="black", tags="rgb_text")
    
    def apply_threshold(self):
        if self.image:
            # 将图像转换为numpy数组
            image_array = np.array(self.image)
            
            # 创建掩码
            r_mask = (image_array[:,:,0] >= int(self.r_min.get())) & (image_array[:,:,0] <= int(self.r_max.get()))
            g_mask = (image_array[:,:,1] >= int(self.g_min.get())) & (image_array[:,:,1] <= int(self.g_max.get()))
            b_mask = (image_array[:,:,2] >= int(self.b_min.get())) & (image_array[:,:,2] <= int(self.b_max.get()))
            mask = r_mask & g_mask & b_mask
            
            # 应用新的RGB值
            image_array[mask, 0] = int(self.target_r.get())  # R
            image_array[mask, 1] = int(self.target_g.get())  # G
            image_array[mask, 2] = int(self.target_b.get())  # B
            
            # 更新图像
            self.image = Image.fromarray(image_array)
            self.update_image()
            
            # 显示预览图像
            preview_size = (100, 100)
            preview_image = self.image.resize(preview_size, Image.Resampling.LANCZOS)
            preview_photo = ImageTk.PhotoImage(preview_image)
            self.preview_label.configure(image=preview_photo)
            self.preview_label.image = preview_photo
    
    def reset_image(self):
        if self.original_image:
            self.image = self.original_image.copy()
            self.update_image()
            # 清除预览图像
            self.preview_label.configure(image='')
            self.preview_label.image = None

if __name__ == '__main__':
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop() 