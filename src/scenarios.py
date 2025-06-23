import os, sys
sys.path.insert(0, os.path.abspath('..'))
import json
import pandas as pd
from src.model import build_model, solve_model
from src.utils import compute_distance_matrix, diffusion_weights

def run_scenario(params_path: str, carbon_price: float, out_csv: str):
    # パラメータ読み込み
    with open(params_path) as f:
        params = json.load(f)

    regions = params['regions']
    # 先進国のみ carbon_price 設定
    cp = {
        r: (carbon_price if r in params['advanced_regions'] else 0.0)
        for r in regions
    }
    params['carbon_price'] = cp

    # 距離重み計算
    D = compute_distance_matrix(regions)
    params['W'] = diffusion_weights(D, phi=params['phi']).values.tolist()

    # モデル構築・carbon_price 更新
    model = build_model(params)
    for r, p in cp.items():
        model.carbon_price[r] = p

    # 解く
    model = solve_model(model, solver_name='ipopt')

    # 結果出力
    rows = []
    for t in range(params['time_horizon']+1):
        for r in regions:
            rows.append({
                'region': r,
                'time': t,
                'tech': model.Tech[r,t].value
            })
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"Saved {out_csv} (carbon_price={carbon_price})")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--params', default='../results/params.json')
    parser.add_argument('--out',    default='../results/bau_tech_time_series.csv')
    parser.add_argument('--price',  type=float, default=0.0)
    args = parser.parse_args()

    # BAU
    run_scenario(args.params, args.price, args.out)
    # Policy
    run_scenario(
        args.params, carbon_price=50.0,
        out_csv='../results/policy_tech_time_series.csv'
    )
