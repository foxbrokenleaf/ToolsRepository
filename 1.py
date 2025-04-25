import cv2
import numpy as np

# 读取 1.jpg 图像
image = cv2.imread('2.jpg')

# 打开 1.pos 文件并读取内容
with open('2.pos', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 遍历每一行，提取位置信息并裁剪内容
for i, line in enumerate(lines):
    # 提取位置信息
    if '检测到' in line:
        parts = line.split(':')[1].split(',')
        x = int(float(parts[0].split('=')[1]))
        y = int(float(parts[1].split('=')[1]))
        w = int(float(parts[2].split('=')[1]))
        h = int(float(parts[3].split('=')[1]))

        # 裁剪图像
        cropped = image[y:y+h, x:x+w]

        # 保存裁剪结果
        cv2.imwrite(f'cropped_{i}.jpg', cropped)

print("裁剪完成，结果已保存为 cropped_0.jpg, cropped_1.jpg 等文件。")

# 转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 边缘检测
edges = cv2.Canny(gray, 50, 150)

# 查找轮廓
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 初始化红框计数
red_box_count = 0

# 遍历轮廓
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    # 提取框内的颜色
    roi = image[y:y+h, x:x+w]
    avg_color = cv2.mean(roi)[:3]  # 获取 BGR 平均值

    # 判断是否为红框（红色分量显著高于其他分量）
    if avg_color[2] > 100 and avg_color[2] > avg_color[1] * 1.5 and avg_color[2] > avg_color[0] * 1.5:
        red_box_count += 1
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 绘制红框

# 输出红框数量
print(f"红框的数量: {red_box_count}")

# 显示结果
cv2.imshow('Red Boxes', image)
cv2.waitKey(0)
cv2.destroyAllWindows()