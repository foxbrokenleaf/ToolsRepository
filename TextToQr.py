# -*- coding: utf-8 -*-

import qrcode

def generate_qr_code(data, output_file):
    """
    生成二维码图片并保存到指定文件。

    :param data: 二维码中包含的数据
    :param output_file: 保存二维码图片的文件路径
    """
    qr = qrcode.QRCode(
        version=1,  # 控制二维码的大小，1 是最小的
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错率
        box_size=10,  # 每个点的像素大小
        border=4,  # 边框宽度，单位为点
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_file)
    print(f"二维码已保存到 {output_file}")

# 示例用法
if __name__ == "__main__":
    data = "((n*y+r)^4)/100"  # 替换为需要生成二维码的数据
    output_file = "qrcode.png"  # 输出文件名
    generate_qr_code(data, output_file)