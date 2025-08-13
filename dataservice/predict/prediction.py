# -- encoding:utf-8 --
"""
Create by ibf on 2018/7/3
说明：
- 自动根据文件后缀选择 read_csv / read_excel
- 统一用原始字符串 + pathlib.Path 避免 Windows 路径转义问题
- 加强错误处理并打印可读提示
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import PolynomialFeatures  # 若需要可启用

import matplotlib as mpl
import matplotlib.pyplot as plt  # 若不画图可不使用，但保留与原脚本一致

import torch

torch.serialization.add_safe_globals([PolynomialFeatures])
# ===================== 全局配置 =====================
warnings.filterwarnings(action='ignore', category=ConvergenceWarning)
warnings.filterwarnings(action='ignore', category=RuntimeWarning)
# 设置中文显示字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
# 设置正常显示符号
mpl.rcParams["axes.unicode_minus"] = False


# ===================== 路径配置（请按需修改） =====================
DATA_PATH = Path(r"D:\workfile\bjdp\daping\code\predict\data1\grcs20251.csv")
POLY_PATH = Path(r"D:\workfile\bjdp\daping\code\predict\model\shujcl.pth")
FEAT_IDX_PATH = Path(r"D:\workfile\bjdp\daping\code\predict\model\algo-gr3.txt")
MODEL_PATH = Path(r"D:\workfile\bjdp\daping\code\predict\model\algo-gr3.pth")


# ===================== 工具函数 =====================
def load_tabular(file_path: Path) -> pd.DataFrame:
    """
    根据文件后缀自动选择读取方式。
    - .csv   -> pd.read_csv(encoding 优先 utf-8-sig，失败回退 gbk)
    - .xlsx  -> pd.read_excel(engine='openpyxl')
    - .xls   -> pd.read_excel(engine='xlrd')
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        # 优先 utf-8-sig；若失败尝试 gbk（常见于国标/Windows 导出的 CSV）
        try:
            return pd.read_csv(file_path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding="gbk")
    elif suffix in (".xlsx", ".xlsm"):
        try:
            return pd.read_excel(file_path, engine="openpyxl")
        except Exception as e:
            raise RuntimeError(f"读取 Excel(xlsx/xlsm) 失败，请确认已安装 openpyxl。原始错误：{e}")
    elif suffix == ".xls":
        try:
            return pd.read_excel(file_path, engine="xlrd")
        except Exception as e:
            raise RuntimeError(f"读取 Excel(xls) 失败，请确认已安装 xlrd。原始错误：{e}")
    else:
        raise ValueError(f"Unsupported file type: {suffix} (path={file_path})")


def main() -> None:
    # 1. 加载数据（自动适配 CSV / Excel）
    try:
        df = load_tabular(DATA_PATH)
    except Exception as e:
        print(f"[读取数据失败] {e}")
        return

    if df.shape[1] < 15:
        print(f"[数据列数不足] 需要至少 15 列，当前为 {df.shape[1]} 列。请检查数据文件：{DATA_PATH}")
        return

    # 2. 获取特征矩阵 X 和目标属性 Y
    #   与原脚本保持一致：第 2~14 列为特征，第 15 列为标签
    try:
        x = df.iloc[:, 1:14]
        y = df.iloc[:, 14]  # 若后续没用到，可不赋值
    except Exception as e:
        print(f"[切片出错] 请检查数据列数与位置。原始错误：{e}")
        return

    # 3. 数据处理：加载预处理器（poly）并转换
    #   原脚本使用 torch.load 读取 'shujcl.pth'，保持一致
    try:
        poly = torch.load(POLY_PATH)
    except Exception as e:
        print(f"[加载预处理器失败] 文件：{POLY_PATH}，原始错误：{e}")
        return

    try:
        x_train = poly.transform(x)
    except Exception as e:
        print(f"[特征变换失败] 请确认 poly 对象为可调用的转换器并与数据列数匹配。原始错误：{e}")
        return

    # 3.1 载入特征选择的列索引（Lasso 选择结果）
    try:
        final_column_indexs1 = np.loadtxt(FEAT_IDX_PATH, dtype=int)
        # 确保是一维索引数组
        final_column_indexs1 = np.atleast_1d(final_column_indexs1).astype(int)
    except Exception as e:
        print(f"[载入特征索引失败] 文件：{FEAT_IDX_PATH}，原始错误：{e}")
        return

    # 根据所选列索引裁剪特征
    try:
        x_train = x_train[:, final_column_indexs1]
    except Exception as e:
        print(f"[按索引裁剪特征失败] 请确认索引范围与 x_train 维度匹配。原始错误：{e}")
        return

    # 4. 调用模型 algo-gr3.pth
    try:
        algo2 = torch.load(MODEL_PATH)
    except Exception as e:
        print(f"[加载模型失败] 文件：{MODEL_PATH}，原始错误：{e}")
        return

    # 5. 供热数据预测
    try:
        # 若 algo2 是 sklearn 风格的模型：
        y_hat = algo2.predict(x_train)
    except Exception as e:
        print(f"[预测失败] 请确认模型接口为 .predict(...) 且与输入维度匹配。原始错误：{e}")
        return

    # 6. 查看结果
    print(y_hat)


if __name__ == "__main__":
    main()
