import cv2
import re
import numpy as np

Debug = False
Color_Number = {"red" : {'number' : 0, 'shape' : []}, "yellow" : {'number' : 0, 'shape' : []}, "cyan-blue" : {'number' : 0, 'shape' : []}, "purple" : {'number' : 0, 'shape' : []}, "blue" : {'number' : 0, 'shape' : []}, "white" : {'number' : 0, 'shape' : []}, "green" : {'number' : 0, 'shape' : []}}  # 颜色数量

def read_pos(pos):
    """读取位置"""
    check_is_file_re = re.compile(r'^[a-zA-Z0-9_]+\.pos$')
    if check_is_file_re.match(pos):
        with open(pos, "r", encoding='utf-8') as f:
            res = []
            pos_lines = f.readlines()
            pos_lines = [line.strip() for line in pos_lines]  # 去除每行末尾的换行符
            for tmp in pos_lines:
                # 假设每行格式为：形状名称 x y w h conf
                parts = tmp.split()
                if len(parts) >= 6:  # 确保有足够的元素
                    name = parts[0]
                    try:
                        x = float(parts[1])
                        y = float(parts[2])
                        w = float(parts[3])
                        h = float(parts[4])
                        conf = float(parts[5])
                        
                        if Debug:
                            print(name)
                            print([x, y, w, h, conf])
                        
                        res.append({
                            'Name': name, 
                            'Value': {
                                'x': x, 
                                'y': y, 
                                'w': w, 
                                'h': h, 
                                'conf': conf
                            }
                        })
                        
                        if Debug:
                            print(res)
                    except ValueError:
                        # 如果转换失败，尝试其他格式
                        try:
                            # 尝试查找形式为 x=123.4, y=123.4 的模式
                            x_match = re.search(r'x=([\d\.]+)', tmp)
                            y_match = re.search(r'y=([\d\.]+)', tmp)
                            w_match = re.search(r'w=([\d\.]+)', tmp)
                            h_match = re.search(r'h=([\d\.]+)', tmp)
                            conf_match = re.search(r'conf=([\d\.]+)', tmp)
                            
                            if all([x_match, y_match, w_match, h_match, conf_match]):
                                x = float(x_match.group(1))
                                y = float(y_match.group(1))
                                w = float(w_match.group(1))
                                h = float(h_match.group(1))
                                conf = float(conf_match.group(1))
                                
                                # 尝试从行中提取形状名称
                                name_match = re.search(r'检测到([a-zA-Z]+):', tmp)
                                if name_match:
                                    name = name_match.group(1)
                                    
                                if Debug:
                                    print(name)
                                    print([x, y, w, h, conf])
                                
                                res.append({
                                    'Name': name, 
                                    'Value': {
                                        'x': x, 
                                        'y': y, 
                                        'w': w, 
                                        'h': h, 
                                        'conf': conf
                                    }
                                })
                                
                                if Debug:
                                    print(res)
                            else:
                                if Debug:
                                    print(f"无法解析行: {tmp}")
                        except Exception as e:
                            if Debug:
                                print(f"解析错误: {e}, 行: {tmp}")
                elif Debug:
                    print(f"行格式不正确: {tmp}")
            
            if res:
                return res
            else:
                print("未能从文件中提取任何有效位置数据")
                return None
    else:
        # 如果不是文件，尝试从字符串直接解析
        # 这部分保持不变...
        tmp = pos
        try:
            # 尝试查找形式为 x=123.4, y=123.4 的模式
            x_match = re.search(r'x=([\d\.]+)', tmp)
            y_match = re.search(r'y=([\d\.]+)', tmp)
            w_match = re.search(r'w=([\d\.]+)', tmp)
            h_match = re.search(r'h=([\d\.]+)', tmp)
            conf_match = re.search(r'conf=([\d\.]+)', tmp)
            
            if all([x_match, y_match, w_match, h_match, conf_match]):
                x = float(x_match.group(1))
                y = float(y_match.group(1))
                w = float(w_match.group(1))
                h = float(h_match.group(1))
                conf = float(conf_match.group(1))
                
                # 尝试从行中提取形状名称
                name_match = re.search(r'检测到([a-zA-Z]+):', tmp)
                if name_match:
                    name = name_match.group(1)
                else:
                    name = "unknown"
                    
                if Debug:
                    print(name)
                    print([x, y, w, h, conf])
                
                return {
                    'Name': name, 
                    'Value': {
                        'x': x, 
                        'y': y, 
                        'w': w, 
                        'h': h, 
                        'conf': conf
                    }
                }
        except Exception as e:
            if Debug:
                print(f"解析错误: {e}, 字符串: {tmp}")
        
        return None

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
#==================================================
# 读取图片并生成掩码
# param image_path: 图片路径
# param hsv_thresholds: HSV阈值列表
# param pos_data: 位置数据列表
# return: None
#===================================================
def read_image(image_path, hsv_thresholds, pos_data):
    """读取图片并生成掩码"""
    check_is_file_re = re.compile(r'^[a-zA-Z0-9_]+\.jpg$')
    if check_is_file_re.match(image_path):
        if Debug:
            print("已找到图片文件")
        image = cv2.imread(image_path)
        if image is None:
            print("无法加载图片，请检查路径！")
            return None
        
        #根据坐标和长宽截取图片
        for pos in pos_data:
            x = int(pos['Value']['x'])
            y = int(pos['Value']['y'])
            w = int(pos['Value']['w'])
            h = int(pos['Value']['h'])
            conf = float(pos['Value']['conf'])
            
            if Debug:
                print(f"截取区域: x={x}, y={y}, w={w}, h={h}")
            
            # 截取图片
            cropped_image = image[y:y+h, x:x+w]
            
            # 转换为 HSV
            hsv_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
            
            masks = []
            for threshold in hsv_thresholds:
                lower_bound = np.array([threshold['LowerHue'], threshold['LowerSaturation'], threshold['LowerValue']])
                upper_bound = np.array([threshold['UpperHue'], threshold['UpperSaturation'], threshold['UpperValue']])
                
                mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
                
                # 计算掩码比例
                ratio = cv2.countNonZero(mask) / (w * h)
                
                masks.append({
                    'color': threshold['color'],
                    'mask': mask,
                    'ratio': ratio
                })
                #获取面积
                area = cv2.countNonZero(mask)
                if Debug and ratio > 0.2:
                    print(f"颜色: {threshold['color']}, 面积: {area}, 比例: {ratio:.2%}")
                #将面积大于0.2的掩码与原图进行与操作并显示
                if ratio > 0.2:
                    result = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)
                    if Debug:
                        cv2.imshow(f"Result - {threshold['color']}", result)
                        cv2.waitKey(0)
                #统计颜色数量
                if ratio > 0.2:
                    Color_Number[threshold['color']]['number'] += 1
                    Color_Number[threshold['color']]['shape'].append(pos['Name'])
                    if Debug:
                        print(f"颜色数量统计: {threshold['color']} - {Color_Number[threshold['color']]['number']}")
        pass

def return_result(th_path, pos_path, image_path):
    hsv_thresholds = read_th(th_path)  # 读取HSV阈值
    pos_data = read_pos(pos_path)  # 读取位置数据
    if pos_data:
        masks = read_image(image_path, hsv_thresholds, pos_data)  # 读取图片并生成掩码
    else:
        print("无法读取位置数据，请检查文件格式。")
    
    print("颜色数量和形状:")
    for color, data in Color_Number.items():
        print(f"{color}: 数量 = {data['number']}, 形状 = {data['shape']}")
    # 关闭所有OpenCV窗口

if __name__ == "__main__":
    res = return_result("HSV.th", "1.pos", "1.jpg")