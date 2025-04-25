import cv2
import re

Debug = True

def read_pos(pos):
    """读取位置"""
    check_is_file_re = re.compile(r'^[a-zA-Z0-9_]+\.pos$')
    if check_is_file_re.match(pos):
        with open(pos, "r", encoding='utf-8') as f:
            res = []
            pos = f.readlines()
            pos = [line.strip() for line in pos]  # 去除每行末尾的换行符
            i = 0
            for tmp in pos:
                #检测到circle: x=966.9, y=131.8, w=84.2, h=83.2, conf=0.93
                restr = re.compile(r'[a-z]+:')
                name = restr.findall(tmp)[0][:-1]
                if Debug:
                    print(name)
                restr = re.compile(r'[\d]+\.[\d]+')
                value = restr.findall(tmp)
                for t_value in value:
                    value[value.index(t_value)] = float(t_value)
                if Debug:
                    print(value)
                res.append({'Name': name, 'Value': {'x': value[0], 'y': value[1], 'w': value[2], 'h': value[3], 'conf': value[4]}})
                i += 1
                if Debug:
                    print(res)
    else:
        tmp = pos
        #检测到circle: x=966.9, y=131.8, w=84.2, h=83.2, conf=0.93
        restr = re.compile(r'[a-z]+:')
        name = restr.findall(tmp)[0][:-1]
        if Debug:
            print(name)
        restr = re.compile(r'[\d]+\.[\d]+')
        value = restr.findall(tmp)
        for t_value in value:
            value[value.index(t_value)] = float(t_value)
        if Debug:
            print(value)
        pos = {'Name': name, 'Value': {'x': value[0], 'y': value[1], 'w': value[2], 'h': value[3], 'conf': value[4]}}
        if Debug:
            print(pos)
    return pos

def read_th(th_path):
    """读取阈值"""
    check_is_file_re = re.compile(r'^HSV\.th$')
    if check_is_file_re.match(th_path):
        if Debug:
            print("已找到阈值文件")
        with open(th_path, "r", encoding='utf-8') as f:
            HSV = []
            th = f.readlines()[1:]  # 跳过第一行
            th = [line.strip() for line in th]  # 去除每行末尾的换行符
            if Debug:
                print(th)
            for tmp in th:
                ttmp = tmp.split(',')   
                HSV.append({'color': ttmp[0], 'LowerHue': int(ttmp[1]), 'LowerSaturation': int(ttmp[2]), 'LowerValue': int(ttmp[3]), 'UpperHue': int(ttmp[4]), 'UpperSaturation': int(ttmp[5]), 'UpperValue': int(ttmp[6])})
            if Debug:
                print(HSV)
            return HSV

def read_image(image_path, hsv_thresholds):
    """读取图片并根据HSV阈值生成掩码"""
    check_is_file_re = re.compile(r'^[a-zA-Z0-9_]+\.jpg$')
    if check_is_file_re.match(image_path):
        if Debug:
            print("已找到图片文件")
        image = cv2.imread(image_path)
        if image is None:
            print("无法读取图片，请检查路径或文件是否损坏")
            return None
        
        # 转换为HSV色彩空间
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        if Debug:
            print("已转换为HSV色彩空间")
        
        masks = []
        for threshold in hsv_thresholds:
            lower_bound = (threshold['LowerHue'], threshold['LowerSaturation'], threshold['LowerValue'])
            upper_bound = (threshold['UpperHue'], threshold['UpperSaturation'], threshold['UpperValue'])
            
            # 生成掩码
            mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
            masks.append({'color': threshold['color'], 'mask': mask})
            if Debug:
                print(f"生成了颜色 {threshold['color']} 的掩码")
        
        return masks
    else:
        print("文件格式不正确，请检查文件名")
        return None

if __name__ == "__main__":
    hsv_thresholds = read_th("HSV.th")  # 读取HSV阈值
    masks = read_image("1.jpg", hsv_thresholds)  # 读取图片并生成掩码
    if masks:
        for mask in masks:
            print(f"颜色 {mask['color']} 的掩码已生成")

