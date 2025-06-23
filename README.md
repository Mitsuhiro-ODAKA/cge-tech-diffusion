# CGE 技術拡散プロジェクト

## 概要  
Pyomo を使って「地域間技術拡散」を差分方程式でモデル化した動学的 CGE モデルです。  
- 3地域（または南アジア5国など任意の地域集合）× 資本・労働 × 技術  
- 生産関数は「完全代替型（線形式）」  
- 技術更新は「自己成長–減衰＋距離依存的拡散」  
- BAU（carbon_price=0） vs Policy（carbon_price>0）を比較  
- 感度分析やコロプレスマップを自動生成  

---

## 必要環境

- Python 3.8+
- pip または conda
- IPOPT（または任意の LP ソルバー）
- GeoPandas（コロプレスマップ用）
- JupyterLab / Jupyter Notebook

```bash
# 例: pip インストール
pip install -r requirements.txt
```

1. キャリブレーション
```bash
python src/calibration.py \
  --sam data/processed/sam.csv \
  --out results/params.json
```

2. シナリオ実行
```bash
# BAU (カーボンプライス 0)
python src/scenarios.py \
  --params results/params.json \
  --out results/bau_tech_time_series.csv \
  --price 0
```

```bash
# Policy (例: カーボンプライス 50)
python src/scenarios.py \
  --params results/params.json \
  --out results/policy_tech_time_series.csv \
  --price 50
```

3. Jupyter で可視化
- `01_data_inspection.ipynb`：SAM・距離行列確認
- `02_model_run.ipynb`：キャリブレーション→シナリオ実行
- `03_visualization.ipynb`：拡散曲線・差分・感度分析・コロプレス

!(imgs)[figures/tech_diffusion_bau_vs_policy.png]
!(imgs)[figures/sensitivity_south_asia.png]
!(imgs)[figures/choropleth_policy.png]