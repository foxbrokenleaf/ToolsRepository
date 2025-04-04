from PIL import Image
from tkinter import filedialog
import numpy as np
import cv2

def RGB_Change(RGB):
    if (RGB[0] >= 150 and RGB[0] <= 255) and (RGB[1] >= 10 and RGB[1] <= 80) and (RGB[2] >= 50 and RGB[2] <= 150):
        return (255, 0, 0)    
    if (RGB[0] >= 0 and RGB[0] <= 175) and (RGB[1] >= 182 and RGB[1] <= 255) and (RGB[2] >= 0 and RGB[2] <= 163):
        return (0, 255, 0)
    if (RGB[0] >= 0 and RGB[0] <= 14) and (RGB[1] >= 32 and RGB[1] <= 68) and (RGB[2] >= 0 and RGB[2] <= 255):
        return (0, 0, 255)
    if (RGB[0] >= 114 and RGB[0] <= 187) and (RGB[1] >= 198 and RGB[1] <= 246) and (RGB[2] >= 196 and RGB[2] <= 255):
        return (0, 255, 255)
    if (RGB[0] >= 137 and RGB[0] <= 220) and (RGB[1] >= 37 and RGB[1] <= 101) and (RGB[2] >= 205 and RGB[2] <= 255):
        return (255, 0, 255)
    if (RGB[0] >= 186 and RGB[0] <= 233) and (RGB[1] >= 191 and RGB[1] <= 255) and (RGB[2] >= 0 and RGB[2] <= 100):
        return (255, 255, 0)
    if (RGB[0] >= 200 and RGB[0] <= 255) and (RGB[1] >= 200 and RGB[1] <= 255) and (RGB[2] >= 200 and RGB[2] <= 255):
        return (255, 255, 255)
    if (RGB[0] >= 0 and RGB[0] <= 70) and (RGB[1] >= 0 and RGB[1] <= 70) and (RGB[2] >= 0 and RGB[2] <= 80):
        return (0, 0, 0)
    return RGB

f_path = filedialog.askopenfilename()
img = Image.open(f_path)

for x in range(img.width):
    for y in range(img.height):
        img.putpixel((x, y), RGB_Change(img.getpixel((x, y)))) 

img_np = np.array(img, dtype=np.uint8)
mat = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
dst = cv2.GaussianBlur(mat, (11, 11), 0)
dst = cv2.Canny(dst, 100, 110)
# mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)

cv2.imshow("img", mat=dst)
cv2.waitKey()