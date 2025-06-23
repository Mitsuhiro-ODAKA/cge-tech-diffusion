# src/utils.py

import pandas as pd
import numpy as np

def load_sam(path: str):
    """
    社会会計表（SAM）から地域ごとの資本・労働・技術初期値を読み込む
    Returns:
        regions: List[str]
        K0, L0, T0: dict(region->float)
    """
    df = pd.read_csv(path)
    regions = df['region'].tolist()
    K0 = dict(zip(regions, df['capital']))
    L0 = dict(zip(regions, df['labor']))
    T0 = dict(zip(regions, df['technology']))
    return regions, K0, L0, T0


def compute_distance_matrix(regions, base_dist=1.0, coords=None):
    """
    地理的距離行列を作成し、最大距離で正規化する。
    - regions: 地域リスト
    - base_dist: ダミー距離（coords 未指定時の off-diagonal）
    - coords: {region:(lat,lon)} を渡せば haversine で実距離を計算。None ならダミー。

    Returns:
      正規化後の距離 DataFrame （0～1 の値）
    """
    if coords:
        # 実距離を計算する例（コメントアウトして必要なら有効化）
        # from haversine import haversine
        # D = pd.DataFrame(index=regions, columns=regions, dtype=float)
        # for i in regions:
        #     for j in regions:
        #         D.loc[i,j] = haversine(coords[i], coords[j])
        raise NotImplementedError("coords 指定時の距離計算は必要に応じて実装してください")
    else:
        # ダミー：同一地域 0、他は base_dist
        D = pd.DataFrame(base_dist, index=regions, columns=regions)
        np.fill_diagonal(D.values, 0.0)

    # 正規化：最大距離で割って 0～1 に
    maxd = D.values.max()
    if maxd > 0:
        D = D / maxd

    return D


def diffusion_weights(distance_df: pd.DataFrame, phi=0.5):
    """
    距離に基づく拡散重み w_ij = exp( -phi * normalized_distance_ij )
    distance_df は compute_distance_matrix の出力（0～1 正規化済み）
    """
    # 各要素に対して exp(-phi * d_ij)
    W = pd.DataFrame(
        np.exp(-phi * distance_df.values),
        index=distance_df.index,
        columns=distance_df.columns
    )
    return W
