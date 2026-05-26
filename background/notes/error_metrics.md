# 误差与拟合度评价指标速查 — Error & Goodness-of-Fit Metrics Reference

> 用途：本项目（Bristol 3-DMA chlorine calibration）的所有评价指标在一个文件里汇总；为 Methodology / Results 章节挑选 + 引用 + 公式书写做单一参考点。
> 覆盖：A6 Vasconcelos 1997、C1 Munavalli 2005、C2 Pasha 2010、E1 Kavetski 2006、E3 Huang 2007、E4 Kang 2009、E5 Sansone 2026、E6 Beven & Binley 1992（GLUE）、E7 Gelman BDA 等已读文献使用过的指标。
> 配套文件：[`../Literature/literature.md`](../Literature/literature.md)、[`../../README.md`](../../README.md)
> 最后更新：2026-05-26
>
> **符号约定**（全文统一）：
> - `y_i` = 第 i 个**观测**（observation），mg/L
> - `ŷ_i` = 第 i 个**模拟**（simulation / prediction），mg/L
> - `N` = 数据点总数（时间 × 空间）
> - `ȳ` = 观测均值
> - `σ_y` = 观测标准差
> - 区间评分中 `[L_i, U_i]` = 第 i 个点的 (lower, upper) 预测区间

---

## 0. 总览（什么时候用什么）

| 项目阶段 | 主要任务 | 推荐指标 | 文献依据 |
| --- | --- | --- | --- |
| **基线确定性校准（Plan baseline）** | 找一组 (k_b, k_w) 最佳值 | **RMSE / MAE + Pearson r** | A6 Vasconcelos 1997；C1 Munavalli 2005 |
| **目标函数选择** | 给优化器算最小化目标 | **WLS（加权最小二乘）** | A1 / A6 / Bayesian 也是 implicit WLS |
| **跨方法对比 / 报告** | 论文 Results 表展示模型好坏 | **NSE + RMSE + MAE + r** | E6 Beven & Binley 1992（NSE） |
| **GLUE Plan A — 不确定性输出** | 给参数和预测的不确定性区间 | **PICP + ARIL + CRPS** | E6 GLUE；E4 Kang 2009 |
| **Bayesian Plan B — 模型选择** | 比较一阶 vs 二阶；3 个 DMA 共享 k_b vs 不共享 | **WAIC / LOO-CV** | E7 Gelman BDA Ch 7 |
| **跨 DMA 可迁移性** | 验证集预测可信度 | **PICP + CRPS + reliability 分解** | 本项目独有 |

---

## §1. 点误差（Point Error Metrics）— 确定性校准核心

> 这一组指标在所有论文里**普遍**使用；A6 Vasconcelos 1997 Table 5 用的就是这组。

### 1.1 SSE — 误差平方和

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 误差平方和 | Sum of Squared Errors | **SSE**（也叫 SSR Sum of Squared Residuals） | (mg/L)² |

**公式**：

```
SSE = Σᵢ (yᵢ - ŷᵢ)²
```

**性质**：
- 范围：[0, +∞)，越小越好。
- **不可跨数据集比较**（依赖 N）。
- **优化目标的祖师爷**：经典最小二乘 = 最小化 SSE。
- A2 Hua 1999、A6 Vasconcelos 1997 都用 nonlinear least squares 拟合 k_b — 内核就是最小化 SSE。

### 1.2 MSE — 均方误差

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 均方误差 | Mean Squared Error | **MSE** | (mg/L)² |

**公式**：

```
MSE = SSE / N = (1/N) · Σᵢ (yᵢ - ŷᵢ)²
```

**性质**：
- 范围：[0, +∞)，越小越好。
- **N 归一化版的 SSE**，可跨数据集比较。
- 单位是观测值的平方 — **不直观**，所以论文里更常报 RMSE。

### 1.3 RMSE — 均方根误差 ⭐

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 均方根误差 | Root Mean Squared Error | **RMSE** | mg/L（与观测同单位） |

**公式**：

```
RMSE = √MSE = √[ (1/N) · Σᵢ (yᵢ - ŷᵢ)² ]
```

**性质**：
- 范围：[0, +∞)，越小越好。
- **对大误差敏感**（平方放大离群点）— 适合"不希望出现大偏差"的场景。
- **本项目核心指标之一**：余氯论文里最常报。

### 1.4 MAE — 平均绝对误差 ⭐⭐（A6 Table 5 用）

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| **平均绝对误差** | **Mean Absolute Error** | **MAE** | mg/L |

**公式**：

```
MAE = (1/N) · Σᵢ |yᵢ - ŷᵢ|
```

**性质**：
- 范围：[0, +∞)，越小越好。
- **对离群点比 RMSE 鲁棒**（不平方）。
- A6 Table 5 给出的 "**average absolute error = 0.05–0.15 mg/L**" 就是 MAE — **本项目精度基线**。
- 几何意义：把误差点投影到 ŷ = y 直线的**平均垂直距离**（在 y - ŷ 平面）。

### 1.5 MAPE / MRE — 平均（绝对）相对误差 ⭐（A6 Table 5 用）

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| **平均相对误差** | **Mean Absolute Percentage Error** | **MAPE**（≡ MRE Mean Relative Error） | %（无量纲） |

**公式**（百分比形式）：

```
MAPE = (100/N) · Σᵢ |yᵢ - ŷᵢ| / |yᵢ|     [%]
```

**等价小数形式（MRE）**：

```
MRE = (1/N) · Σᵢ |yᵢ - ŷᵢ| / |yᵢ|
```

> **注意**：A6 论文用的 "average relative error" 就是 MAPE。Table 5 里 "**17–31 percent**" 即 MAPE 范围。

**性质**：
- 范围：[0, +∞)，越小越好。
- **当 y 接近 0 时不稳定**（分母小 → 数值爆炸）。**余氯接近阈值 0.2 mg/L 的点**会很敏感。
- **对小值的相对误差更敏感** — 适合"低浓度也要准"的应用（饮用水余氯就是这个场景）。
- **跨量纲可比较**（百分比无单位）。

### 1.6 BIAS / ME — 偏差均值

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 偏差均值（不取绝对值） | Mean Error / Bias | **ME** / **BIAS** | mg/L |

**公式**：

```
BIAS = (1/N) · Σᵢ (ŷᵢ - yᵢ)
```

> **注意**：定义为 ŷ - y（不是 y - ŷ）。BIAS > 0 表示模型**高估**；< 0 表示**低估**。

**性质**：
- 范围：(-∞, +∞)，越接近 0 越好。
- **不取绝对值** → 正负误差相互抵消；如果模型整体上一半高估一半低估，BIAS 会接近 0 但 MAE 可能很大。
- **必须和 RMSE/MAE 一起报**：单独看 BIAS 没意义。
- **诊断用途**：BIAS ≈ 0 但 RMSE 大 → 模型整体无偏但散布大；BIAS 与 RMSE 同量级 → 系统性偏差。

### 1.7 WLS — 加权最小二乘（目标函数）⭐⭐⭐

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 加权最小二乘 | Weighted Least Squares | **WLS** | 无量纲（已除以方差） |

**公式**：

```
WLS = Σᵢ [ (yᵢ - ŷᵢ) / σᵢ ]²
```

其中 `σᵢ` 是第 i 个观测点的**测量误差标准差**。

**为什么是项目核心**：
- **WLS 是 Gaussian likelihood 的 -2·log 项**：
  ```
  -2·log L = WLS + N·log(2π) + Σᵢ log(σᵢ²)
  ```
- **本项目 likelihood 模型**（结合 A6 + D2 + D3）：
  ```
  σᵢ(C) = √[ σ_min² + (σ_rel · Cᵢ)² ],  σ_min ≈ 0.02 mg/L, σ_rel ≈ 0.15
  ```
- Plan A (GLUE) 的 likelihood、Plan B (Bayesian) 的 likelihood，都基于 WLS。
- **如果所有 σᵢ 相等**，WLS = SSE / σ² → 退化为普通最小二乘。

---

## §2. 拟合度评分（Goodness-of-Fit Scores）

> 这一组指标把误差**归一化**到 [-∞, 1] 或 [0, 1] 区间，方便跨模型 / 跨数据集比较。

### 2.1 R² — 决定系数

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 决定系数 | Coefficient of Determination | **R²** | 无量纲 |

**公式**（拟合优度版本，**不是** Pearson r 的平方）：

```
R² = 1 - SSE / SST,    SST = Σᵢ (yᵢ - ȳ)²
```

**性质**：
- 范围：(-∞, 1]，越接近 1 越好。
- R² = 1 → 完美拟合；R² = 0 → 模型 = 取均值；R² < 0 → **模型比取均值还差**。
- **对线性回归**：R² ∈ [0, 1] 且 = Pearson r²。但对非线性模型 R² 可以为负。
- A2 Hua 1999 报的 "r² > 0.93" 就是这个。

### 2.2 Pearson r — 皮尔逊相关系数 ⭐⭐（A6 站均值相关性 用）

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| **（线性）相关系数** | **Pearson correlation coefficient** | **r** | 无量纲 |

**公式**：

```
r = Σᵢ (yᵢ - ȳ)(ŷᵢ - ŷ̄) / [ √Σᵢ (yᵢ - ȳ)² · √Σᵢ (ŷᵢ - ŷ̄)² ]
```

**性质**：
- 范围：[-1, 1]，**绝对值**越接近 1 越好。
- 只测 **线性相关性** —— **不关心 ŷ 是否等于 y**，只关心趋势。
- **r = 1 不代表模型准** —— ŷ = 2·y 时 r = 1 但模型显然不对。
- **必须和 RMSE/MAE 配对使用**。
- A6 Table 5 的 "**correlation between predicted and observed means**" = **站均值相关性** = Pearson r of (per-station mean of ŷ vs y)。这一项 A6 报 85–98%。

**A6 站均值相关性的精确算法**：

```python
y_station_means  = [mean(y) for each station]      # 7 个站均值
yhat_station_means = [mean(ŷ) for each station]    # 7 个站均值
r_station = pearson_r(y_station_means, yhat_station_means)
```

> **本项目可直接照用**：3 个 DMA × 每个 DMA 多个监测点 → 站均值相关性是评估"模型在站间的相对排序"是否正确的好指标。

### 2.3 Spearman ρ — 斯皮尔曼秩相关

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 秩相关系数 | Spearman rank correlation | **ρ** / **r_s** | 无量纲 |

**公式**：把 yᵢ 和 ŷᵢ 都转成**秩**（rank），再做 Pearson r：

```
ρ = Pearson r(rank(y), rank(ŷ))
```

**性质**：
- 范围：[-1, 1]，越接近 1 越好。
- **不假设线性关系**，只测单调一致性。
- 对离群点不敏感。
- 本项目可作为 Pearson r 的鲁棒补充。

### 2.4 NSE — 纳什-萨特克利夫效率 ⭐⭐（GLUE / Plan A 标准）

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| **纳什-萨特克利夫效率** | **Nash-Sutcliffe Efficiency** | **NSE** | 无量纲 |

**公式**（数值上与 R² 相同，但**概念不同**）：

```
NSE = 1 - Σᵢ (yᵢ - ŷᵢ)² / Σᵢ (yᵢ - ȳ)²
```

**性质**：
- 范围：(-∞, 1]，越接近 1 越好。
- NSE = 1 → 完美；NSE = 0 → 不如取均值；NSE < 0 → 模型很差。
- **hydrology 领域标准**（Nash & Sutcliffe 1970）；**GLUE 论文 E6 Beven & Binley 1992 用 NSE 作 likelihood**。
- 经验阈值：NSE > 0.5 → 可接受；NSE > 0.7 → 良好；NSE > 0.9 → 优秀。

**GLUE 中的特殊用法（Plan A）**：

```
behavioural threshold:  NSE > NSE_min（如 0.6）
non-behavioural samples 直接丢弃；
保留样本按 likelihood weight ∝ NSE 加权
```

### 2.5 KGE — 克林-古普塔效率（现代版 NSE）

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 克林-古普塔效率 | Kling-Gupta Efficiency | **KGE** | 无量纲 |

**公式**（分解为相关性 + 偏差 + 离散度 3 项）：

```
KGE = 1 - √[ (r - 1)² + (α - 1)² + (β - 1)² ]
其中  α = σ_ŷ / σ_y     (离散度比)
      β = ȳ_ŷ / ȳ_y    (均值比)
      r = Pearson r
```

**性质**：
- 范围：(-∞, 1]，越接近 1 越好。
- KGE > -0.41 → 比取均值好。
- **比 NSE 更全面**：r 测趋势、α 测变异度、β 测偏差。**Gupta et al. 2009** 出名。
- 本项目**可选**：Plan A/B 写 Results 时与 NSE 并列报，体现方法学严谨。

### 2.6 Willmott d — 一致性指数

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 一致性指数 | Willmott's Index of Agreement | **d** | 无量纲 |

**公式**：

```
d = 1 - Σᵢ (yᵢ - ŷᵢ)² / Σᵢ ( |ŷᵢ - ȳ| + |yᵢ - ȳ| )²
```

**性质**：
- 范围：[0, 1]，越接近 1 越好。
- **比 NSE 对 BIAS 更敏感**。
- 在水质 / 大气模型中常见；余氯文献用得不多 — **本项目可选**。

---

## §3. 区间 / 不确定性评分（Interval Scores）— Plan A/B 核心

> 这一组**只在不确定性方法**（GLUE、Bayesian）里用：评价**预测区间**的好坏，而不是单点估计。

### 3.1 PICP — 区间覆盖率 ⭐⭐⭐

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| **预测区间覆盖率** | **Prediction Interval Coverage Probability** | **PICP**（也叫 **CR** Coverage Ratio） | % 或 [0,1] |

**公式**：

```
PICP = (1/N) · Σᵢ 𝟙{ Lᵢ ≤ yᵢ ≤ Uᵢ }
```

其中 `𝟙{·}` = indicator function（在范围内 = 1，否则 = 0）。

**性质**：
- 范围：[0, 1]，**目标值 = nominal coverage level**（如 95%）。
- 如果给 95% 区间，理想 PICP ≈ 0.95。
  - PICP > 0.95 → **区间太宽**，不确定性高估
  - PICP < 0.95 → **区间太窄**，模型过度自信（**最危险**）
- **本项目 Plan A/B 的核心评价**。

### 3.2 AIW / MPI — 平均区间宽度

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 平均区间宽度 | Average Interval Width / Mean Prediction Interval | **AIW** / **MPI** | mg/L |

**公式**：

```
AIW = (1/N) · Σᵢ (Uᵢ - Lᵢ)
```

**性质**：
- 范围：[0, +∞)，**越小越好**（但要在 PICP 达标的前提下）。
- **PICP 和 AIW 是 trade-off**：
  - 把区间放无穷大 → PICP = 100%（无信息）
  - 把区间收为单点 → AIW = 0（但 PICP 趋于 0）
- 必须**联合报告**：PICP ≈ 95% **且** AIW 最小，才是"恰好的不确定性"。

### 3.3 ARIL — 平均相对区间长度

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 平均相对区间长度 | Average Relative Interval Length | **ARIL** | 无量纲 |

**公式**：

```
ARIL = (1/N) · Σᵢ (Uᵢ - Lᵢ) / |yᵢ|
```

**性质**：
- 范围：[0, +∞)，越小越好。
- AIW 的**百分比版**，跨数据集可比。
- E4 Kang, Pasha, Lansey 2009 用过。
- 注意：yᵢ ≈ 0 时同样会爆。

### 3.4 CRPS — 连续秩概率评分 ⭐⭐（Bayesian 论文标准）

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| **连续秩概率评分** | **Continuous Ranked Probability Score** | **CRPS** | mg/L |

**公式**（对单个观测 yᵢ 与其预测 CDF Fᵢ）：

```
CRPS(Fᵢ, yᵢ) = ∫_{-∞}^{+∞} [ Fᵢ(z) - 𝟙{z ≥ yᵢ} ]² dz
```

总分（平均所有点）：

```
CRPS̄ = (1/N) · Σᵢ CRPS(Fᵢ, yᵢ)
```

**蒙特卡洛估计**（实际计算用）：从后验抽 M 个 ŷᵢ^(m)：

```
CRPS(Fᵢ, yᵢ) ≈ (1/M) · Σₘ |ŷᵢ^(m) - yᵢ| 
              - (1/(2M²)) · Σₘ Σₘ' |ŷᵢ^(m) - ŷᵢ^(m')|
```

**性质**：
- 范围：[0, +∞)，**越小越好**。
- **同时**测量 reliability（区间正确性）+ sharpness（区间紧致）。
- 当预测退化为单点时，CRPS = MAE → **是 MAE 的概率版广义化**。
- **Plan B Bayesian 的金牌指标**；E5 Sansone 2026 / Gelman BDA 都推荐。

### 3.5 Reliability + Sharpness 分解

不是单一指标，而是把 CRPS / 其它综合分数拆开两件事：

| 概念 | 含义 |
| --- | --- |
| **Reliability**（可靠性）| 标称 95% 区间是否真的包含 95% 的观测 → 用 **PICP** |
| **Sharpness**（锐度）| 区间多窄 → 用 **AIW** |

**Plan A/B 报告时**：先说"95% 区间的实际覆盖率为 X%（reliability），平均宽度为 Y mg/L（sharpness）"，比单报一个数字更可信。

---

## §4. Bayesian 模型评分（Plan B 选型）

> 这一组只在 Plan B（Bayesian MCMC）里用。**比较不同模型结构**（如一阶 vs 二阶；3 个 k_w 独立 vs partial pooling），不能直接比"哪个 MAE 小"，因为复杂模型总是过拟合。

### 4.1 log-likelihood — 对数似然

| 中 | 英 | 缩写 | 单位 |
| --- | --- | --- | --- |
| 对数似然 | log-likelihood | **log L** | 无量纲 |

**Gaussian 残差假设下**：

```
log L(θ | y) = -N/2 · log(2π) - Σᵢ log(σᵢ) - (1/2) · Σᵢ [ (yᵢ - ŷᵢ(θ)) / σᵢ ]²
            = const - (1/2) · WLS
```

**性质**：
- 范围：(-∞, +∞)，**越大越好**。
- 不能跨数据集比较，只能在同一数据集上比较模型。
- **MCMC 输出每个 sample 的 log L** → 进入下面所有 Bayesian 评分。

### 4.2 DIC — 偏差信息准则

| 中 | 英 | 缩写 |
| --- | --- | --- |
| 偏差信息准则 | Deviance Information Criterion | **DIC** |

**公式**：

```
DIC = D̄ + p_D,    D̄ = -2 · mean(log L),   p_D = D̄ - D(θ̄)
```

**性质**：
- 范围：(-∞, +∞)，**越小越好**。
- 经典 Bayesian 模型选择（WinBUGS 标配）；**E3 Huang & McBean 2007** 用 DIC。
- 已**被 WAIC / LOO-CV 取代**（Gelman BDA 3rd ed. 不推荐 DIC）。

### 4.3 WAIC — Widely Applicable Information Criterion ⭐

| 中 | 英 | 缩写 |
| --- | --- | --- |
| 广义可应用信息准则 | Widely Applicable Information Criterion | **WAIC** |

**公式**（lppd = log pointwise predictive density）：

```
WAIC = -2 · ( lppd - p_WAIC )
lppd = Σᵢ log( (1/M) · Σₘ p(yᵢ | θ^(m)) )
p_WAIC = Σᵢ var_m( log p(yᵢ | θ^(m)) )
```

**性质**：
- 范围：(-∞, +∞)，越小越好。
- **Gelman BDA 推荐的现代版 DIC**（E7 Ch 7）。
- **本项目 Plan B 模型选择主用**：比较 "3 个 k_w 完全独立" vs "partial pooling" vs "完全共享 k_w" 时直接用 WAIC。

### 4.4 LOO-CV — Leave-One-Out Cross-Validation ⭐⭐

| 中 | 英 | 缩写 |
| --- | --- | --- |
| 留一交叉验证 | Leave-One-Out Cross-Validation | **LOO** / **LOO-CV** |

**公式**（lpd = log predictive density）：

```
LOO_lpd = Σᵢ log p(yᵢ | y_{-i})
```

其中 y_{-i} 表示**除了第 i 个**的所有观测。

**实战做法**：用 **PSIS-LOO**（Pareto Smoothed Importance Sampling）从一次 MCMC 跑里近似 LOO，无需重复抽样 N 次。Python 包 `arviz.loo()` 提供。

**性质**：
- 比 WAIC 更稳健（特别在有强先验或层级模型时）。
- **E7 Gelman BDA 推荐**。
- **本项目 Plan B 的金牌模型选择指标**。

### 4.5 Bayes Factor / posterior odds — 贝叶斯因子

| 中 | 英 | 缩写 |
| --- | --- | --- |
| 贝叶斯因子 | Bayes Factor | **BF** |

**公式**：

```
BF₁₂ = p(y | M₁) / p(y | M₂)
```

p(y | M) = **模型 M 下的边际似然**（积分掉参数）。

**性质**：
- 范围：(0, +∞)，BF > 1 → 偏好 M₁。
- 解读：BF ∈ (1, 3) 弱证据；(3, 10) 中等；(10, 100) 强；> 100 极强（Jeffreys 1961）。
- **难以计算**（需要边际似然，是高维积分）。
- **本项目不推荐主用**，作为可选补充。

---

## §5. 速查总表（按"指标 vs 用途"）

| 指标 | 范围 | 优 | 单位 | 用在哪 |
| --- | --- | --- | --- | --- |
| **SSE** | [0, ∞) | 0 | (mg/L)² | 优化目标 |
| **MSE** | [0, ∞) | 0 | (mg/L)² | 中间量 |
| **RMSE** ⭐ | [0, ∞) | 0 | mg/L | **必报** |
| **MAE** ⭐ | [0, ∞) | 0 | mg/L | **必报**（与 A6 对标） |
| **MAPE / MRE** ⭐ | [0, ∞) | 0 | % | **必报**（与 A6 对标） |
| **BIAS** | (-∞, ∞) | 0 | mg/L | 诊断系统偏差 |
| **WLS** | [0, ∞) | min | 无量纲 | 优化目标（带误差） |
| **R²** | (-∞, 1] | 1 | — | 经典报 |
| **Pearson r** ⭐ | [-1, 1] | 1 | — | **必报**（与 A6 对标） |
| **Spearman ρ** | [-1, 1] | 1 | — | 可选（鲁棒） |
| **NSE** ⭐ | (-∞, 1] | 1 | — | **GLUE 必报** |
| **KGE** | (-∞, 1] | 1 | — | 可选（hydro 现代） |
| **Willmott d** | [0, 1] | 1 | — | 可选 |
| **PICP** ⭐⭐ | [0, 1] | 0.95（标称值）| — | **Plan A/B 必报** |
| **AIW** ⭐⭐ | [0, ∞) | 小 | mg/L | **Plan A/B 必报**（与 PICP 配） |
| **ARIL** | [0, ∞) | 小 | — | 可选 |
| **CRPS** ⭐⭐ | [0, ∞) | 0 | mg/L | **Plan B 必报** |
| **log L** | (-∞, ∞) | 大 | — | MCMC 中间量 |
| **DIC** | (-∞, ∞) | 小 | — | 旧式 Bayesian 选模型 |
| **WAIC** | (-∞, ∞) | 小 | — | **Plan B 选模型** |
| **LOO-CV** ⭐⭐ | (-∞, ∞) | 小 | — | **Plan B 选模型最佳** |
| **Bayes Factor** | (0, ∞) | > 1 | — | 可选 |

---

## §6. Python 实现速查

> 用 `cive70058` env 里已经装好的库（numpy, scipy, scikit-learn）；Bayesian 评分用 `arviz`（待装：`pip install arviz`）。

```python
import numpy as np
from scipy.stats import pearsonr, spearmanr

y    = np.array([...])    # observations
yhat = np.array([...])    # simulations

# ============ §1. Point error ============
SSE   = np.sum((y - yhat)**2)
MSE   = np.mean((y - yhat)**2)
RMSE  = np.sqrt(MSE)
MAE   = np.mean(np.abs(y - yhat))
MAPE  = np.mean(np.abs(y - yhat) / np.abs(y)) * 100   # %
BIAS  = np.mean(yhat - y)

# Weighted least squares (assuming sigma per point)
sigma = np.sqrt(0.02**2 + (0.15 * y)**2)  # A6 + D2 启发的误差模型
WLS   = np.sum(((y - yhat) / sigma)**2)

# ============ §2. Goodness of fit ============
SST = np.sum((y - np.mean(y))**2)
R2  = 1 - SSE / SST

r_pearson, _  = pearsonr(y, yhat)
r_spearman, _ = spearmanr(y, yhat)

NSE = 1 - SSE / SST   # NSE = R² 数值上但概念不同

# KGE
alpha = np.std(yhat) / np.std(y)
beta  = np.mean(yhat) / np.mean(y)
KGE   = 1 - np.sqrt((r_pearson - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)

# 站均值相关性（按 A6）
def station_mean_correlation(y_dict, yhat_dict):
    """y_dict / yhat_dict: {station_id: array of measurements over time}"""
    y_means    = [np.mean(y_dict[s])    for s in y_dict]
    yhat_means = [np.mean(yhat_dict[s]) for s in y_dict]
    r, _ = pearsonr(y_means, yhat_means)
    return r

# ============ §3. Interval scores ============
# 假设你有 N×M 的 ensemble（N 个时间点，M 个 MC/MCMC 抽样）
ensemble = np.array([...])   # shape (N, M)
lower    = np.percentile(ensemble, 2.5,  axis=1)
upper    = np.percentile(ensemble, 97.5, axis=1)

PICP = np.mean((y >= lower) & (y <= upper))
AIW  = np.mean(upper - lower)
ARIL = np.mean((upper - lower) / np.abs(y))

# CRPS (蒙特卡洛估计版)
def crps_mc(obs, ensemble_row):
    """obs: scalar; ensemble_row: array of M samples"""
    M = len(ensemble_row)
    term1 = np.mean(np.abs(ensemble_row - obs))
    term2 = np.mean(np.abs(ensemble_row[:, None] - ensemble_row[None, :])) / 2
    return term1 - term2

CRPS = np.mean([crps_mc(y[i], ensemble[i, :]) for i in range(len(y))])

# ============ §4. Bayesian scores (use arviz) ============
# import arviz as az
# trace = ...  # your MCMC trace as arviz InferenceData
# az.waic(trace)
# az.loo(trace)
```

---

## §7. 项目报告组合建议（按章节）

### Results 章必报"标定精度"小节（与 A6 对标）

```
| Metric                       | Value             | A6 5-system range |
|------------------------------|-------------------|-------------------|
| RMSE (mg/L)                  | 0.XX              | —                 |
| MAE (mg/L)                   | 0.XX              | 0.05–0.15         |
| MAPE (%)                     | XX                | 17–31             |
| BIAS (mg/L)                  | ±0.XX             | —                 |
| Pearson r (station means)    | 0.XX              | 0.85–0.98         |
| NSE                          | 0.XX              | —                 |
```

### Results 章 Plan A (GLUE) 不确定性小节

```
| Metric                       | Value             |
|------------------------------|-------------------|
| 95% PICP (reliability)       | XX %  (nominal 95%) |
| AIW (sharpness)              | 0.XX mg/L           |
| CRPS                         | 0.XX mg/L           |
```

### Results 章 Plan B (Bayesian hierarchical) 模型选择小节

```
| Model                                  | WAIC   | LOO   | dWAIC  | dLOO  |
|----------------------------------------|--------|-------|--------|-------|
| M1: no pooling (3 independent k_w)     | xxx.x  | xxx.x | 0      | 0     |
| M2: partial pooling (hierarchical)     | xxx.x  | xxx.x | -X     | -X    |
| M3: complete pooling (one global k_w)  | xxx.x  | xxx.x | +X     | +X    |
```

dWAIC < 0（且 SE 显著）→ M2 优。

---

## §8. 哪些**不用**

避免下面这些"看起来很厉害但本项目不适用"的指标：

| 指标 | 为什么不用 |
| --- | --- |
| **F1 / Precision / Recall** | 分类指标，本项目是回归 |
| **AUC / ROC** | 分类指标 |
| **KL divergence** | 需要两个分布，单点观测无法算 |
| **MAPE 当观测含 0** | 分母爆炸，对余氯接近 0 时不稳定 — 改用 **加权 MAE** 或 sMAPE |

**sMAPE（symmetric MAPE）补救**（当余氯接近 0 时）：

```
sMAPE = (100/N) · Σᵢ |yᵢ - ŷᵢ| / [ (|yᵢ| + |ŷᵢ|) / 2 ]   [%]
```

---

## 参考文献

- **A6** Vasconcelos et al. 1997 — MAE, MAPE, station-mean correlation（Table 5）
- **C1** Munavalli & Kumar 2005 — RMSE, parameter estimation
- **C2** Pasha & Lansey 2010 — sensitivity / uncertainty propagation
- **E1** Kavetski, Kuczera & Franks 2006 — Bayesian likelihood with input uncertainty
- **E3** Huang & McBean 2007 — DIC（已被 WAIC 替代）
- **E4** Kang, Pasha & Lansey 2009 — ARIL
- **E5** Sansone et al. 2026 — Bayesian posterior, MCMC
- **E6** Beven & Binley 1992 — NSE-based GLUE likelihood
- **E7** Gelman et al. *Bayesian Data Analysis* — log-pointwise predictive density, WAIC, LOO-CV (Ch 7)
- Gupta, Kling, Yilmaz & Martinez 2009 — KGE
- Gneiting & Raftery 2007 — CRPS (Strictly Proper Scoring Rules)
- Vehtari, Gelman & Gabry 2017 — PSIS-LOO

---

## 一句话总结

> **本项目报告组合 = (RMSE + MAE + MAPE + Pearson r + NSE + BIAS) for baseline; + (PICP + AIW + CRPS) for Plan A; + (WAIC + LOO-CV) for Plan B 模型选择**；其中 MAE、MAPE、Pearson r 与 A6 Vasconcelos 1997 Table 5 对标可比。
