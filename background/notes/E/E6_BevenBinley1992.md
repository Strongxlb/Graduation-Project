# E6 — Beven & Binley (1992) GLUE 精读笔记

> 配套文件：`[../../Literature/literature.md](../../Literature/literature.md)` §E6
> PDF 路径：`[../../Literature/E-不确定性感知校准（Monte Carlo : Bayesian : GLUE）/EEEEE6-Beven, Binley (1992).The future of distributed models.pdf](../../Literature/E-不确定性感知校准（Monte%20Carlo%20:%20Bayesian%20:%20GLUE）/EEEEE6-Beven,%20Binley%20(1992)`.The%20future%20of%20distributed%20models.pdf)
>
> ⭐ **导师建议（2026-05-25 邮件）**：「your robust fallback method」— 即使 Plan B 的 MCMC 跑不通，也能保下界。
>
> **来源标签**（2026-06-05，已通读 PDF 21 页）

---

## 0. 元数据


| 字段          | 内容                                                                             |
| ----------- | ------------------------------------------------------------------------------ |
| Title       | The future of distributed models: model calibration and uncertainty prediction |
| Authors     | **Keith Beven**, **Andrew Binley**                                             |
| Affiliation | Centre for Research on Environmental Systems, Lancaster University, UK         |
| Journal     | *Hydrological Processes* 6(3): 279–298                                         |
| DOI         | `10.1002/hyp.3360060305`                                                       |
| Year        | 1992-07                                                                        |
| 页数          | 21（含图表与参考文献）                                                                   |
| 引用量         | > 7000（GLUE 奠基论文）                                                              |
| 优先级         | **P0**                                                                         |
| 状态          | `read`                                                                         |


**领域**：水文（IHDM 分布式降雨—径流模型，Gwy 实验流域 3.9 km²，mid-Wales）— 非供水管网；收录理由是 **GLUE 方法论**：用多组参数 Monte Carlo 抽样 + 似然加权得到参数与预测不确定性区间，**不要求似然解析**，是本项目 **Plan A**（ensemble-based 校准）的直接理论依据。

---

## 1. Abstract（原文要点）

`[原文]` 提出基于 **generalised likelihood measures** 的分布式模型校准与不确定性估计方法 GLUE。procedure 接受「多组参数值在给定模型结构、边界条件与观测误差下都可能等可能成为合格 simulator」的事实，给每组参数赋一个似然值。讨论了将不同类型观测纳入校准、用 Bayes 方法更新似然、评估额外观测价值的程序。计算量大但已在并行机上实现。以 Plynlimon Gwy 流域 + IHDM 为例验证。

---

## 2. 中文摘要

传统校准在高维参数空间寻找单一「最优」参数集，忽略了 **equifinality**（等效性）：在模型结构误差 + 边界/观测误差并存的情况下，参数空间中**多组解几乎等可能**。GLUE 放弃寻找最优点，转而：

1. 在合理先验范围内做大量 Monte Carlo 抽样；
2. 对每组参数赋予一个 **似然值**（可以是 NSE、RMSE 的负幂等任何「越好越大」的度量）；
3. 把似然值低于阈值的「non-behavioural」simulation 丢弃，剩下的 rescale 到和为 1；
4. 用这个加权集合在每个时间步/空间点上构造预测的 5/95 percentile 区间；
5. 新观测进来时用 Bayes 公式 multiplicatively 更新似然 → 后验越来越紧。

Gwy 实验流域 4 个 IHDM 参数 + 5 storms 校准 + 5 storms 验证，验证了 GLUE 能给出合理的预测区间，并能用 Shannon entropy / U-uncertainty 量化新观测的「信息价值」。重要洞察：**预测带有时反而变宽**——某次极端事件用过去的 likelihood weights 拟合不上，提示模型结构有限。

---

## 3. GLUE 核心方法（§概览 + §3–6）

### 3.1 与传统校准的对比


| 项目     | 传统优化              | GLUE                        |
| ------ | ----------------- | --------------------------- |
| 输出     | 一个「最优」参数 + 邻域置信区间 | 一组等可能参数 + 加权预测分布            |
| 似然假设   | 高斯、零均值、独立同分布      | **任意** 单调递增 goodness-of-fit |
| 多最优    | 难处理（局部极值、参数相关）    | 自然涵盖（多模似然）                  |
| 模型结构误差 | 通常忽略              | 隐式吸收进 likelihood weight     |
| 计算     | 1 次优化             | `N ~ 10³–10⁵` 次仿真           |


`[原文]` p.279–280：传统方法「treats the optimal solution as having likelihood 1 and all others as zero — an extreme case of GLUE」。

### 3.2 Five requirements（§GLUE Overview）

1. 形式化定义似然度量 `ℒ`
2. 定义先验参数范围 / 分布
3. 用似然权重做不确定性估计
4. 新数据来时递归 Bayes 更新
5. 评估额外数据价值的程序

### 3.3 似然度量候选（§Definition of the Likelihood Function）

> **符号约定**（与 `[../error_metrics.md](../error_metrics.md)` 保持一致）：
>
> - `θᵢ` = 第 i 组参数（本项目里是 `k_b, k_w, 源氯, 需水量乘子`）
> - `C_obs` = 观测余氯（mg/L）
> - `C_sim,i` = 用 θᵢ 跑 EPANET 得到的模拟余氯
> - `N` = 数据点总数（时间 × 空间）
> - `σ` = 观测误差标准差（mg/L），DPD 取 ~0.02（D2）；在线传感器更大（D5）
> - `ℒᵢ` = 第 i 组参数的似然值（GLUE 用作权重；越大越好）
> - `ℓᵢ` = 对数似然 = log(ℒᵢ)（数值稳定，**实际计算用这个**）

---

#### 3.3.0 ⭐ 本项目主推：高斯（Gaussian）log-likelihood

> 这是 GLUE 在余氯校准里**实际会用的形式**。先给出 RMSE，再用一行高斯似然把它变成权重。

**步骤 1**：算每组参数的 RMSE。

**公式**：

```
RMSE(θᵢ) = √[ (1/N) · Σ (C_obs − C_sim,i)² ]
```

**步骤 2**：把 RMSE 变成对数似然。

**公式**：

```
ℓᵢ = −(1/2) · (RMSE(θᵢ) / σ)²
```

**步骤 3**：取指数得到似然权重。

**公式**：

```
ℒᵢ = exp(ℓᵢ) = exp[ −(1/2) · (RMSE(θᵢ) / σ)² ]
```

**性质**：

- RMSE 越小 → ℓ 越大 → ℒ 越接近 1（好参数）。
- RMSE 大很多 σ → ℓ 极负 → ℒ ≈ 0（坏参数被自动剪掉）。
- σ 由仪器决定，**不是拟合得到**：DPD 用 0.02 mg/L（D2），在线传感器用相对误差 ~10%（D5）。
- **数值稳定**：直接算 `exp(-1e6)` 会下溢成 0；GLUE pipeline 里**保留 `ℓᵢ`**，归一化前先减去 `max(ℓᵢ)` 再 exp。

**例**（σ = 0.02 mg/L，DPD 假设）：


| 参数组 | RMSE | RMSE/σ | ℓ     | ℒ（归一化前） |
| --- | ---- | ------ | ----- | ------- |
| θ_A | 0.02 | 1      | -0.5  | 0.61    |
| θ_B | 0.04 | 2      | -2    | 0.135   |
| θ_C | 0.10 | 5      | -12.5 | 4×10⁻⁶  |
| θ_D | 0.20 | 10     | -50   | ~0（剪掉）  |


**与 §3.3.0 之外形式的关系**：

```
高斯 ℒ = exp[−(1/2)·(RMSE/σ)²] = exp[−SSE/(2·N·σ²)]
       ∝ Power likelihood（N=1, σ_e² = MSE）
```

也就是 §3.3 (b) 的 Power likelihood **在 N=1 + 高斯假设下等价于这里的高斯似然**。论文用 Power 是泛化形式；本项目用高斯版本是因为我们**有仪器 σ 的先验**（D2/D5），能直接量纲化。

---

#### 3.3.1 论文原文给的 3 种备选

> Beven & Binley 1992 §Definition of the Likelihood Function 列了下面 3 种。在余氯场景里 §3.3.0 的高斯形式更常用；下面三种作为 alternative 备查。

**(a) Nash–Sutcliffe 效率（NSE）**

**公式**：

```
ℒ₁(θ) = 1 − σ²_e(θ) / σ²_o
       = 1 − RMSE²(θ) / σ²_o
```

其中 `σ²_o` 是**观测自身的方差**（与 θ 无关，是常数）。

**性质**：

- 范围 (-∞, 1]，越大越好；**1 = 完美**，**0 = 跟报观测均值一样烂**，**< 0 直接丢弃**。
- 与 RMSE 的关系：`NSE = 1 − (RMSE/σ_o)²` — **NSE 是把 σ 选作 σ_o 的高斯 ℓ 的归一化版**。
- 跨数据集可比；论文 Results 表常用。

**(b) Power likelihood（论文实际使用）**

**公式**：

```
ℒ₂(θ) = [ σ²_e(θ) ]^(−N) = 1 / [ MSE(θ) ]^N
```

**性质**：

- N 是「锐度旋钮」：
  - N = 0 → 所有 θ 等权（不做加权）
  - N = 1 → 适中（约等于 §3.3.0 高斯，σ 由数据自己定）
  - N = 5 → 残差方差减半 ⇒ 似然 ×32（**重赏好、严罚差**）
  - N → ∞ → 只剩最优那一组（退化为传统单点优化）
- **缺点**：σ 是从拟合出来的（隐含 σ² = MSE），**没用到仪器先验**，所以本项目用 §3.3.0 高斯形式更合适。

**(c) Scaled max absolute residual（最大绝对残差）**

**公式**：

```
ℒ₃(θ) = max_t |C_obs(t) − C_sim,θ(t)|
```

**性质**：

- 「越大越差」（与 a/b 相反），使用时要再做变换或设上限。
- 适合「不允许任一时刻越界」的场景；余氯场景实用性低（DPD ±0.02 mg/L 容易整批拒）。

---

### 3.4 多观测合成（多个似然怎么变成一个）

**场景**：你既有 DPD grab samples，又有在线传感器，还有压力数据。每种数据自己有 RMSE 和 σ，怎么合成总似然？


| 方法                        | 公式（log-likelihood 加和等价于似然乘积） | 含义            | 何时用              |
| ------------------------- | ---------------------------- | ------------- | ---------------- |
| **乘积**（Pseudo-MLE）⭐       | `ℓ_total = Σⱼ ℓⱼ`            | 各源**全部都要**好   | **默认推荐**（假设各源独立） |
| **加权和**                   | `ℒ_total = Σⱼ Wⱼ · ℒⱼ`       | 各源加权平均        | 误差量级相近时          |
| **Set union（取最大）**        | `ℒ_total = max(ℒⱼ)`          | **任一源**好就接受   | 宽松、保留更多 θ        |
| **Set intersection（取最小）** | `ℒ_total = min(ℒⱼ)`          | **最差那一源**决定全局 | 严苛筛选             |


**本项目推荐：log-likelihood 加和**。

**公式**：

```
ℓ_total(θ) = ℓ_DPD(θ) + ℓ_sensor(θ) + ℓ_pres(θ)
           = −(1/2) · [ (RMSE_DPD/σ_DPD)²
                       + (RMSE_sensor/σ_sensor)²
                       + (RMSE_pres/σ_pres)² ]
```

**性质**：

- 每种仪器用**自己的 σ** 做权重——天然处理「DPD 准但稀 + 在线传感器密但糙」的差异。
- 加和比相乘**数值更稳**：避免 ℒⱼ 极小时乘积下溢。
- 等价于「多源观测相互独立，残差各自高斯」的最大似然推导。

`[原文]` 反复强调 **似然定义是主观选择**，不同方式得到不同区间宽度——论文 Methodology **必须写清楚用了哪一种**。

---

### 3.5 Bayes 更新（新数据来了，怎么用？）

**核心规则**：先验 × 新似然 → 归一化。

**公式**（log 形式，**实际代码用这个**）：

```
ℓ_post(θ) = ℓ_prior(θ) + ℓ_new(θ)            ← 旧 log-似然 + 新数据 log-似然
W = exp(ℓ_post − max(ℓ_post))                  ← 减去最大值后再 exp，防下溢
W = W / Σ W                                    ← 归一化，让 Σ W = 1
```

**性质**：

- ⊕ 在 log 域是加法、在 ℒ 域是乘法 — 一回事，加法更稳。
- 「先验」就是**上一轮的后验**，所以 GLUE 是个**无穷叠加**的 Bayes 链。
- 不需要解析后验密度（这是与 MCMC 的本质区别）。

**实现（每个 MC 样本独立更新）**：

```python
import numpy as np

# Day t 新数据来了
SSE_t = ((C_obs_t - C_sim[:, t_slice])**2).sum(axis=(1,2))
ell_new = -0.5 * SSE_t / sigma**2          # log-likelihood
ell_post = ell_post + ell_new              # 累加
W = np.exp(ell_post - ell_post.max())      # 防下溢
W = W / W.sum()                            # 归一化
```

**为什么便宜**：参数 θᵢ 对应的 `C_sim` 已经在 Step 1 跑过、存到磁盘里。Day 2 的数据来了，**只读 CSV、算 SSE、更新 W**——不重跑 EPANET。一个 5000 样本的 GLUE 跑完，之后每加一天数据只需几秒。

### 3.6 不确定性区间（§Uncertainty estimation）

每个时间步 `t`：

1. 把 `N` 个 sim 的预测值按大小排序；
2. 按 likelihood weight 累加得到加权 CDF；
3. 取 5/95 percentile → 90% 不确定性带；
4. **每个时间步的「最优」simulation 可能不同** — 区间不能简单用某一条 sim 的方差代替。

### 3.7 Resampling（§Resampling）

Bayes 更新会让大多数样本被淘汰 → 有效样本数下降。对策：

- 在已知后验形状上 **重新均匀抽样**；
- 用最近邻插值（论文用 10 个最近邻 + 距离平方反比）估计新点的似然；
- 似然显著的接受为新样本，否则重抽。

### 3.8 Shannon Entropy / U-uncertainty —— 量化「不确定性总量」

**问题**：怎么用一个数字告诉自己「我现在对参数还有多不确定」？答：用**信息熵** H。

**公式**：

```
H = − Σᵢ Wᵢ · log₂(Wᵢ)
```

其中 `Wᵢ` 是第 i 组参数的归一化权重（`Σ Wᵢ = 1`），`M` 是样本总数。

**性质**：

- 「权重越平均 → H 越大 → 越不确定」「权重越集中 → H 越小 → 越确定」。
- 极大值：所有 θ 等权 → `H = log₂ M`（先验状态，什么都没学到）。
- 极小值：1 组 θ 权重 = 1、其余为 0 → `H = 0`（信息完全确定）。

**例**（`M = 5000`，对应论文 Plan A 设定）：


| 阶段         | 大致情况                | H                    |
| ---------- | ------------------- | -------------------- |
| 先验（均匀）     | 5000 组等权            | log₂ 5000 ≈ **12.3** |
| Day 1 数据后  | 800 组高权重，4200 组 ≈ 0 | ≈ **8**              |
| Day 7 数据后  | 50 组高权重，其余几乎 0      | ≈ **5**              |
| Day 30 数据后 | H 不再下降              | 数据**饱和**             |


**判断逻辑**（GLUE 最值钱的副产物之一）：


| 新数据后现象     | 解释                            |
| ---------- | ----------------------------- |
| H **下降**   | 新数据**有用**，参数后验收紧 ✅            |
| H **几乎不变** | 新数据没新信息（传感器位置不好 / 时段冗余）       |
| H **反而上升** | 新数据与现有似然**矛盾** → 模型结构疑似有问题 ⚠️ |


---

**第二个度量 U-uncertainty**（论文给出但用得少，`[备查]`）：

**公式**：

```
U = Σᵢ (W*ᵢ − W*ᵢ₊₁) · log₂(i)
```

其中 `W*ᵢ` 是把权重**从大到小排序**后的第 i 个，约定 `W*_{M+1} = 0`。

**性质**：

- 与 H 同方向：均匀先验时最大、单点最优时为 0；趋势与 H 一致即可。
- 强调**排序不一致性**而不是分布形状。

---

> **本项目用法**：在论文 Results 画一张「**H 随观测数据增多而下降的曲线**」——是「校准在持续学习」的最直接证据。若某次新数据让 H 不降反升，就是 Discussion 里讨论模型结构限制的信号（呼应 §4.2 Storm 4 反例）。

---

## 4. 案例：Gwy catchment + IHDM（§Modelling the Gwy catchment）

### 4.1 设定


| 项目  | 内容                                                                          |
| --- | --------------------------------------------------------------------------- |
| 流域  | Gwy, Plynlimon mid-Wales, **3.9 km²**                                       |
| 模型  | IHDM4：1D kinematic wave + 2D Richards equation（hillslope 5 段 + channel 3 段） |
| 数据  | 10 storms（5 校准 + 5 验证）                                                      |
| 参数  | 4 个：`Ks`（饱和导水率）、`θs`（饱和含水量）、`ψ_in`（初始基质势）、`fm`（漫流糙率）                        |
| 先验  | 全部 **uniform**（见 Table II）                                                  |
| 计算  | Lancaster Meiko parallel computer, 50 transputers, **每场 storm 30–60 h**     |


### 4.2 关键发现

1. **Equifinality 实证**（Figure 7）：在 `Ks–ψ_in` 投影上，似然分布有 **多个高似然区域**——传统优化会随机落到其中一个并误以为是「全局最优」。
2. **Storm 4 反例**（极端事件，重现期 50–100 yr）：使用 storm 1–3 后验做 storm 4 预测，区间 **变宽**——说明 IHDM 参数在极端事件下不通用，**模型结构边界被触及**。
3. **Behavioural vs non-behavioural**（Figure 8 + Kolmogorov–Smirnoff Table III）：`θs` 和 `ψ_in` 的两组累积分布显著不同（`p < 0.05`），说明这些参数对响应敏感；`Ks` 和 `fm` 不显著 → 数据无法约束。
4. **新数据并不总是减小不确定性**（Figure 10）：`H` 和 `U` 随 storm 数加入并非单调下降，与 BATEA (E1) 中 Potomac 雪缺失案例呼应——**数据多 ≠ 模型变好**。

---

## 5. 结论（§Concluding Discussion）

GLUE 的核心贡献：

1. **承认并量化** equifinality（不同参数集等可能）；
2. **接受非高斯/有偏/异方差** 残差结构（隐式吸收进 likelihood）；
3. **多源数据整合** 用 Bayes 递归更新，无需解析似然；
4. **数据价值评估** 通过似然分布前后对比量化；
5. **敏感性分析** 直接由 behavioural / non-behavioural 子集做（Hornberger–Spear GSA 推广）。

要求 modeller **explicit** 声明：(A) 联合先验；(B) 似然函数定义。

---

## 6. 迁移到本项目的映射

### 6.1 类比对照表


| 水文 GLUE                       | 本项目（余氯 / WNTR）                                                |
| ----------------------------- | ------------------------------------------------------------- |
| IHDM 4 参数（`Ks, θs, ψ_in, fm`） | **每 DMA 的 `k_b, k_w`**（按管材分组）+ 源氯 bias                        |
| 流域出口 hydrograph               | **节点 free Cl grab samples**（D2/D3 误差）                         |
| Storm = 校准 episode            | **24 h 监测段** 或 **每个校准日**                                      |
| Uniform prior                 | `k_b ∈ [-2, 0]` /day（A2 Hua）；`k_w ∈ [-1, 0]` m/day（A4 Hallam） |
| 高斯 log-likelihood             | `ℓ(θ) = −(1/2)·(RMSE/σ)²`，`σ` 取 D2 的 0.02 mg/L（见 §3.3.0）      |
| Behavioural threshold         | `NSE > 0.5` 或 `RMSE < 2·σ_obs`                                |
| 5/95 区间                       | 每个 junction 每小时的 **余氯预测带**（Result 主图）                         |
| Bayes 多 storm 更新              | 多日 / 多 DMA 数据递归更新后验权重                                         |
| 模型结构疑点                        | EPANET 一阶 decay 简化（A2 警告二阶）                                   |


### 6.2 Plan A 完整 pipeline（GLUE on WNTR）

```text
1. 抽样：LHS 生成 N ≈ 5000 组 (k_b, k_w, source_Cl_bias, demand_mult)
2. 仿真：WNTR EpanetSimulator 跑每组，得到 C_sim(node, t)
3. 似然：L_i = exp(-Σ(C_obs - C_sim_i)² / (2 σ²)) ；σ = max(0.02, 0.05·C_obs)
4. 阈值：保留 L_i > 5%·max(L) 的样本（behavioural set）
5. 加权：W_i = L_i / ΣL_i
6. 输出：每个 junction × hour 的 W-加权 CDF → P5 / P50 / P95
7. 阈值概率：Pr(C(node) < 0.2 mg/L) = Σ W_i · 1{C_sim_i < 0.2}
```

### 6.3 可参考要点（写论文 / 做实验时可直接引用）

1. **Methodology 段**：把 GLUE 写成 Plan A baseline；明确写 likelihood 形式（Eq. above）和 behavioural threshold；引用 Beven & Binley 1992。
2. **Results 主图**：「P5–P95 chlorine band + 0.2 mg/L 阈值线」直接对应 §3.6 Figure 4 风格——**可以借这个图的视觉语法**。
3. **阈值超限概率图**：把每个 junction 的 `Pr(C < 0.2)` 画到管网上 → GLUE 的天然产物，比单点估计更有「risk-aware」工程价值。
4. **Sensitivity analysis**：用 behavioural / non-behavioural 子集做 Kolmogorov–Smirnoff 检验，判断 `k_b` vs `k_w` 哪个更可识别（接 C2 Pasha 的可识别性发现）。
5. **Discussion — equifinality 段**：直接引用 Beven 1989a/1992 的 equifinality 立论，说明「为什么单一参数估计不可靠」——这是论文核心动机的之一。
6. **vs Plan B（E3/E5 MCMC）**：写「GLUE 是 informal Bayesian；MCMC 是 formal Bayesian。两者结果对比可作为 robustness check」——E1 Kavetski 也持类似视角。
7. **Honest limitation**：引用 §Uncertainty and Model Structural Error 段——若区间始终覆盖不到观测，提示模型结构有缺陷（如忽略二阶 decay 或 wall）；不要靠放宽 likelihood 「漂亮地」掩盖。
8. **Computing**：本文用 50 transputers ≈ 50 hr/storm；现代笔记本 + 多进程 ≈ 几分钟跑 5000 sim — **算力已不是瓶颈**，可在 thesis 提一句。

---

## 7. 批判性阅读

**优点**

- 哲学清晰：直面 equifinality + 模型结构误差，**不假装** 单点最优有意义。
- 方法极通用：似然定义自由、不需要 conjugate prior、不需要 MCMC。
- 计算并行天然友好：每组参数独立运行，可任意 scale。
- 配 Bayes 更新与数据价值评估，工程闭环完整。

**局限 / 后续争议**

- **似然定义主观**：Mantovan & Todini (2006, J Hydrol) 批评 GLUE 不是严格 Bayesian，似然不是真正的概率，多次更新可能不收敛到真后验。回应：Beven 等坚持「fuzzy / informal」立场。
- **Behavioural threshold 任意**：5% / 10% / 20% 都没有理论指导，结果对阈值敏感。
- **样本量 vs 维数**：4 个参数尚可，10+ 维（每根管 1 个 `k_w`）需指数级样本——本项目要么按 DMA 分组降维，要么 LHS / Sobol 抽样。
- **非高斯似然不能复用 χ² / F 检验**：要做 hypothesis test 时较麻烦。
- **资料不更新文献**：1992 写的，后续 GLUE2 / DREAM 等已更优；当 fallback 用即可，主结果建议跑 MCMC（E3/E5）。

---

## 8. 待办

- [ ] 在 `src/` 下实现 GLUE pipeline（Week 6–7 T4 后接 T5 即可）
- [ ] 与 C2 Pasha 的「参数 MCS」做术语区分写进 Methodology
- [ ] 读 Beven & Binley **2014** 「GLUE, 20 years on」（Hydrological Processes 28(24):5897–5918, doi:10.1002/hyp.10082）— 看作者 20 年后的反思
- [ ] 若导师建议同时跑 MCMC，把 GLUE bands 与 MCMC bands 并排画作 robustness check（呼应 E1 Kavetski 多方法对照思路）
- [ ] 在 `results/` 出一张「P5–P95 chlorine band 示意图」作为 thesis Methodology figure 模板

---

## 9. 引用

> Beven KJ, Binley A. The future of distributed models: model calibration and uncertainty prediction. *Hydrological Processes*. 1992;6(3):279–298. doi:10.1002/hyp.3360060305

```bibtex
@article{BevenBinley1992GLUE,
  author  = {Beven, Keith J. and Binley, Andrew},
  title   = {The future of distributed models: Model calibration and uncertainty prediction},
  journal = {Hydrological Processes},
  volume  = {6},
  number  = {3},
  pages   = {279--298},
  year    = {1992},
  doi     = {10.1002/hyp.3360060305}
}
```

---

## 10. 修正记录


| #   | 说明                                                                                        |
| --- | ----------------------------------------------------------------------------------------- |
| 1   | 文献清单 §E6 行的「下载 ✓ / 阅读 — / 理解 —」需更新为 **下载 ✓ / 阅读 ✓ / 理解 ✓**，并加上本笔记链接                       |
| 2   | 文献清单底部 验证日志「移除 E1（原）Beven & Binley GLUE — 已自清单删除（无阅读权限）」一行已过时——**已重新引入并精读**，建议在下一次维护时归档说明 |


