import os, sys
sys.path.insert(0, os.path.abspath('..'))
import json
from src.utils import load_sam

def calibrate(sam_path: str, output_path: str):
    """
    SAM を読み込んで初期パラメータ JSON を生成
    """
    regions, K0, L0, T0 = load_sam(sam_path)
    params = {
        'regions': regions,
        'K0': K0,
        'L0': L0,
        'T0': T0,
        # 線形生産関数の係数
        'alpha': 0.36,
        # 拡散強度
        'phi': 0.1,
        # 自律成長係数
        'gamma': 0.0005,
        # 技術減衰率（Depreciation）
        'delta': 0.001,
        # シミュレーション期間
        'time_horizon': 20,
        # 自律成長を適用する先進国
        'advanced_regions': ['A', 'B']
    }
    with open(output_path, 'w') as f:
        json.dump(params, f, indent=2)
    print(f"Calibration output -> {output_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sam', default='../data/processed/sam.csv')
    parser.add_argument('--out', default='../results/params.json')
    args = parser.parse_args()
    calibrate(args.sam, args.out)
