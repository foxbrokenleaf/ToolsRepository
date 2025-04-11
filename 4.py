import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def plot_normal_distributions():
    # 生成 x 值
    x = np.linspace(-5, 5, 1000)

    # 左侧曲线
    left_mean = -2
    left_std = 1
    left_y = norm.pdf(x, left_mean, left_std)
    plt.plot(left_y, x, label='Left', color='blue')

    # 右侧曲线
    right_mean = 2
    right_std = 1
    right_y = norm.pdf(x, right_mean, right_std)
    plt.plot(right_y, x, label='Right', color='red')

    # 上侧曲线
    top_mean = 2
    top_std = 1
    top_y = norm.pdf(x, top_mean, top_std)
    plt.plot(x, top_y, label='Top', color='green')

    # 下侧曲线
    bottom_mean = -2
    bottom_std = 1
    bottom_y = norm.pdf(x, bottom_mean, bottom_std)
    plt.plot(x, bottom_y, label='Bottom', color='orange')

    # 设置坐标轴和图例
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Normal Distribution Curves')
    plt.legend()
    plt.grid(True)

    # 显示图形
    plt.show()


# 调用函数
plot_normal_distributions()
    