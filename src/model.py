import numpy as np
from pyomo.environ import (
    ConcreteModel, Set, Param, Var, Constraint,
    NonNegativeReals, SolverFactory, RangeSet
)

def build_model(params):
    model = ConcreteModel()

    # 時間軸 0～T
    T = params['time_horizon']
    model.T = RangeSet(0, T)

    # 地域集合
    regions = params['regions']
    model.R = Set(initialize=regions)

    # パラメータ群
    model.alpha  = Param(initialize=params['alpha'])
    model.phi    = Param(initialize=params['phi'])
    model.gamma  = Param(initialize=params['gamma'])
    model.delta  = Param(initialize=params['delta'])

    # carbon_price：先進国のみ後から設定可能に
    cp0 = {r: 0.0 for r in regions}
    model.carbon_price = Param(
        model.R, initialize=cp0, mutable=True
    )

    # 初期 SAM
    model.K0 = Param(model.R, initialize=params['K0'])
    model.L0 = Param(model.R, initialize=params['L0'])
    model.T0 = Param(model.R, initialize=params['T0'])

    # 距離重み W[r,j]
    W = np.array(params['W'])
    model.W = Param(
        model.R, model.R,
        initialize=lambda m,i,j: float(W[regions.index(i)][regions.index(j)])
    )

    # 変数
    model.K    = Var(model.R, model.T, domain=NonNegativeReals)
    model.L    = Var(model.R, model.T, domain=NonNegativeReals)
    model.Tech = Var(model.R, model.T, domain=NonNegativeReals)
    model.Y    = Var(model.R, model.T, domain=NonNegativeReals)

    # 初期値制約
    model.K_init = Constraint(
        model.R, rule=lambda m,r: m.K[r,0] == m.K0[r]
    )
    model.L_init = Constraint(
        model.R, rule=lambda m,r: m.L[r,0] == m.L0[r]
    )
    model.T_init = Constraint(
        model.R, rule=lambda m,r: m.Tech[r,0] == m.T0[r]
    )

    # 生産関数（線形式）
    model.Prod = Constraint(
        model.R, model.T,
        rule=lambda m,r,t: m.Y[r,t] == (
            m.Tech[r,t] *
            (m.alpha*m.K[r,t] + (1-m.alpha)*m.L[r,t])
        )
    )

    # 技術更新：拡散＋自律成長－減衰
    def tech_update(m, r, t):
        if t == 0:
            return Constraint.Skip
        diff = sum(
            m.W[r,j] * (m.Tech[j,t-1] - m.Tech[r,t-1])
            for j in m.R
        )
        growth = 1 + m.gamma * m.carbon_price[r] - m.delta
        return m.Tech[r,t] == growth * m.Tech[r,t-1] + m.phi * diff

    model.TechUpdate = Constraint(
        model.R, model.T, rule=tech_update
    )

    return model

def solve_model(model, solver_name='ipopt'):
    solver = SolverFactory(solver_name)
    solver.solve(model, tee=False)
    return model
