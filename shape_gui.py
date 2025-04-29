import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import sys
from shape import generate_image, batch_convert_images
import os

class ShapeGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图形生成器")
        
        # 设置窗口大小和位置
        window_width = 500
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 目录设置框架
        dir_frame = ttk.LabelFrame(main_frame, text="目录设置", padding="5")
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        
        # 图片输出目录
        ttk.Label(dir_frame, text="图片输出目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.img_dir_var = tk.StringVar(value="res\\1")
        img_dir_entry = ttk.Entry(dir_frame, textvariable=self.img_dir_var, width=30)
        img_dir_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5,5))
        ttk.Button(dir_frame, text="浏览", command=lambda: self.browse_directory(self.img_dir_var)).grid(row=0, column=2, padx=5)
        
        # bin文件输出目录
        ttk.Label(dir_frame, text="bin文件输出目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.bin_dir_var = tk.StringVar(value="resbin\\3")
        bin_dir_entry = ttk.Entry(dir_frame, textvariable=self.bin_dir_var, width=30)
        bin_dir_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5,5))
        ttk.Button(dir_frame, text="浏览", command=lambda: self.browse_directory(self.bin_dir_var)).grid(row=1, column=2, padx=5)
        
        # 数量选择
        ttk.Label(main_frame, text="生成数量:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.number_var = tk.StringVar(value="10")
        number_entry = ttk.Entry(main_frame, textvariable=self.number_var, width=10)
        number_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 形状选择标题
        ttk.Label(main_frame, text="选择要生成的形状:", font=("", 10, "bold")).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(15,5))
        
        # 形状选择框架
        shapes_frame = ttk.Frame(main_frame)
        shapes_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 形状选择复选框
        self.shape_vars = {}
        shapes = {
            'rect': '矩形',
            'circle': '圆形',
            'triangle': '三角形',
            'star': '星形',
            'diamond': '菱形',
            'diamond_tilted': '倾斜菱形',
            'trapezoid1': '等腰梯形(大顶)',
            'trapezoid2': '等腰梯形(小顶)',
            'trapezoid3': '直角梯形'
        }
        
        for i, (shape_key, shape_name) in enumerate(shapes.items()):
            self.shape_vars[shape_key] = tk.BooleanVar(value=True)
            ttk.Checkbutton(shapes_frame, text=shape_name, 
                          variable=self.shape_vars[shape_key]).grid(row=i//2, 
                                                                  column=i%2, 
                                                                  sticky=tk.W, 
                                                                  padx=5, pady=2)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # 全选按钮
        ttk.Button(button_frame, text="全选", command=self.select_all).grid(row=0, column=0, padx=5)
        
        # 取消全选按钮
        ttk.Button(button_frame, text="取消全选", command=self.deselect_all).grid(row=0, column=1, padx=5)
        
        # 生成按钮
        ttk.Button(main_frame, text="开始生成", command=self.generate).grid(row=5, column=0, columnspan=2, pady=10)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 进度标签
        self.progress_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=6, column=0, columnspan=2)

    def browse_directory(self, var):
        directory = filedialog.askdirectory()
        if directory:
            # 转换为Windows路径格式
            directory = directory.replace('/', '\\')
            var.set(directory)
            # 确保目录存在
            os.makedirs(directory, exist_ok=True)

    def select_all(self):
        for var in self.shape_vars.values():
            var.set(True)

    def deselect_all(self):
        for var in self.shape_vars.values():
            var.set(False)

    def update_status(self, message, is_progress=False):
        self.status_var.set(message)
        if is_progress:
            self.progress_var.set(message)
        self.root.update()

    def generate(self):
        try:
            # 获取并验证目录
            img_dir = self.img_dir_var.get()
            bin_dir = self.bin_dir_var.get()
            os.makedirs(img_dir, exist_ok=True)
            os.makedirs(bin_dir, exist_ok=True)
            
            # 更新shape.py中的输出目录
            import shape
            shape.shape_output_dir = img_dir
            
            num = int(self.number_var.get())
            if num <= 0:
                messagebox.showerror("错误", "生成数量必须大于0")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
            
        # 获取选中的形状
        selected_shapes = [shape for shape, var in self.shape_vars.items() if var.get()]
        
        if not selected_shapes:
            messagebox.showerror("错误", "请至少选择一种形状")
            return
            
        # 更新原始代码中的shape_types
        import shape
        shape.shape_types = selected_shapes
        
        # 开始生成
        self.update_status("正在生成图片...", True)
        
        try:
            for i in range(num):
                generate_image(i)
                self.update_status(f"正在生成图片... {i+1}/{num}", True)
            
            # 转换为bin文件
            self.update_status("正在转换为bin文件...", True)
            batch_convert_images(img_dir, bin_dir)
            
            self.update_status("生成完成！")
            self.progress_var.set("")  # 清空进度信息
            messagebox.showinfo("完成", f"成功生成{num}个图形文件！")
        except Exception as e:
            self.update_status(f"错误：{str(e)}")
            messagebox.showerror("错误", f"生成过程中出现错误：{str(e)}")

def main():
    root = tk.Tk()
    app = ShapeGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 