"""
预测服务：
- 仅动态替换天气（明日/今日的最低最高气温），其余特征先用内置默认值。
- 加载 poly、特征索引与模型，执行 transform -> 选列 -> predict。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np

try:
    import torch  # type: ignore
except Exception:  # 允许环境暂时没有 torch
    torch = None  # type: ignore


_ARTIFACTS = {
    'loaded': False,
    'poly': None,
    'feat_idx': None,
    'model': None,
}


def _get_model_dir() -> Path:
    # 相对当前位置：dataservice/predict/model
    here = Path(__file__).resolve().parent
    return here / 'predict' / 'model'


def load_model_artifacts() -> None:
    if _ARTIFACTS['loaded']:
        return
    if torch is None:
        raise RuntimeError('PyTorch 未安装，无法加载预测模型')

    model_dir = _get_model_dir()
    poly_path = model_dir / 'shujcl.pth'
    feat_idx_path = model_dir / 'algo-gr3.txt'
    model_path = model_dir / 'algo-gr3.pth'

    # 兼容 sklearn 对象序列化
    from sklearn.preprocessing import PolynomialFeatures  # type: ignore
    torch.serialization.add_safe_globals([PolynomialFeatures])

    poly = torch.load(poly_path, weights_only=False)
    feat_idx = np.loadtxt(feat_idx_path, dtype=int)
    feat_idx = np.atleast_1d(feat_idx).astype(int)
    model = torch.load(model_path, weights_only=False)

    _ARTIFACTS['poly'] = poly
    _ARTIFACTS['feat_idx'] = feat_idx
    _ARTIFACTS['model'] = model
    _ARTIFACTS['loaded'] = True


def build_feature_row(min_temp_c: float, max_temp_c: float) -> np.ndarray:
    """
    构造 13 维特征行，顺序与 grcs20251.csv 的第 2~14 列保持一致：
    [日最低气温, 日最高气温, 汉沽日计划, 生态城日计划, 宁河日计划,
     前一日汉沽日供热量, 前一日生态城日供热量, 前一日宁河日供热量,
     昨日供热量, #3机>930MW时长, #3机<400MW时长, #4机>900MW时长, #4机<400MW时长]
    其余参数先用经验/样例值，可后续改为从数据库读取。
    """
    # 基于样例行的合理缺省（单位与原表一致）
    hg_plan = 19000.0
    stc_plan = 14000.0
    nh_plan = 11500.0

    prev_hg = 18500.0
    prev_stc = 17200.0
    prev_nh = 16900.0
    yest_total = 54000.0

    dur_3_gt930 = 40.0
    dur_3_lt400 = 20.0
    dur_4_gt900 = 55.0
    dur_4_lt400 = 10.0

    row = np.array([
        float(min_temp_c),
        float(max_temp_c),
        hg_plan,
        stc_plan,
        nh_plan,
        prev_hg,
        prev_stc,
        prev_nh,
        yest_total,
        dur_3_gt930,
        dur_3_lt400,
        dur_4_gt900,
        dur_4_lt400,
    ], dtype=float)
    return row


def predict_heat_gj(min_temp_c: float, max_temp_c: float) -> float:
    """
    返回预测日供热量（GJ）。
    """
    load_model_artifacts()
    poly = _ARTIFACTS['poly']
    feat_idx = _ARTIFACTS['feat_idx']
    model = _ARTIFACTS['model']

    x_row = build_feature_row(min_temp_c, max_temp_c)
    X = np.expand_dims(x_row, axis=0)
    X_poly = poly.transform(X)
    X_sel = X_poly[:, feat_idx]
    y_hat = model.predict(X_sel)
    try:
        val = float(np.ravel(y_hat)[0])
    except Exception:
        val = float(y_hat)
    return val


