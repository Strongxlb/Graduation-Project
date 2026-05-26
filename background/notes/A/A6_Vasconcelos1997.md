# A6 — Vasconcelos, Rossman, Grayman, Boulos, Clark (1997) 精读笔记

> 配套文件：[`../../Literature/literature.md`](../../Literature/literature.md) §A6、[`../../README.md`](../../../README.md)、[`../../../plan1.md`](../../../plan1.md)
> 前置阅读：[`A1_Rossman1994.md`](A1_Rossman1994.md)（管网 bulk+wall+mass-transfer 理论框架）
> 同组延伸：[`A2_Hua1999.md`](A2_Hua1999.md)（实验室 bulk 动力学）；[`A4_Hallam2002.md`](A4_Hallam2002.md)（wall 异质性深入）
> PDF 路径：`../../Literature/A-Chlorine decay 机理（bulk : wall : 影响因素）/AAA6-Journal AWWA - 1997 - Vasconcelos - Kinetics of chlorine decay.pdf`
>
> **来源标签**（2026-05-26，已通读 PDF 12 页正文）：
> - `[原文]` 直接出自论文 PDF
> - `[元数据]` 来自期刊页眉 / CrossRef
> - `[推断]` 与项目关联的延伸
> - `[需补]` 待后续文献或实验核对

---

## 0. 元数据（已验证）

| 字段 | 内容 | 来源 |
| --- | --- | --- |
| Title | **Kinetics of chlorine decay** | PDF cover |
| Authors | **John J. Vasconcelos**, **Lewis A. Rossman**, **Walter M. Grayman**, **Paul F. Boulos**, **Robert M. Clark** | PDF p.55 |
| Affiliation | Vasconcelos：独立咨询工程师（Pasadena, CA）；Rossman & Clark：US EPA 水利与水资源研究部（Cincinnati, OH）；Grayman：咨询工程师（Cincinnati）；Boulos：MW Soft 副总裁 | PDF p.65 "About the authors" |
| Journal | *Journal AWWA*（American Water Works Association）| PDF |
| Volume / Issue / Pages | **89**(7), **54–65** | PDF, CrossRef |
| Year | **1997-07** | PDF |
| DOI | `10.1002/j.1551-8833.1997.tb08259.x` | literature.md, CrossRef |
| 资金来源 | AWWA Research Foundation contract 815-92；US EPA National Risk Management Research Lab | PDF p.64 Acknowledgment |
| 全文报告 | "Characterization and Modeling of Chlorine Decay in Distribution Systems"（AWWARF 报告 90705，Vasconcelos 1996）— 本论文是该报告的浓缩稿 | PDF p.55 脚注 |
| 优先级 | **P0**（导师 2026-05-25 邮件明确推荐） | literature.md §A6 |
| 状态 | `read`（PDF 已通读 12 页） | — |

**为什么是 P0**：导师邮件原话——*"bulk vs wall, and why first-order is the usual (but not only) choice"*。这是 A1 Rossman 1994 的**实证姐妹篇**：A1 推导了管网 bulk+wall+mass-transfer 数学框架，A6 拿这套框架去 **5 个真实管网**做现场标定，证明：

1. **一阶 bulk** 在 11 种源水里普遍适用，但 `k_b` 跨水源差 **200 倍**（0.08 → 17.7 /day）—— 必须每个源水单独烧瓶测，**不能套数值**。
2. **wall decay 在 5 个系统中 4 个显著**，且 wall 常数与 **Hazen–Williams 粗糙度系数成反比**（老管 / 腐蚀重的管 → 反应更快）。
3. **EPANET 默认的一阶 bulk + 一阶 wall + mass-transfer** 框架可把 5 个系统拟合到 **0.05–0.15 mg/L** 平均误差、**85–98%** 相关性 —— 这是本项目的**精度基线**。

---

## 1. 原文 Abstract（英文，逐字）

> Proper understanding, characterization, and prediction of water quality behavior in drinking water distribution systems are critical to ensure meeting regulatory requirements and customer-oriented expectations. This article investigates the factors leading to loss of chlorine residual in water distribution systems. Kinetic rate equations describing the decay of chlorine were developed, tested, and evaluated using data collected in field-sampling studies conducted at several water utility sites. Results indicated that chlorine decay in distribution systems can be characterized as a combination of first-order reactions in the bulk liquid and first-order or zero-order mass transfer–limited reactions at the pipe wall. Wall reaction kinetic constants were inversely proportional to pipe roughness coefficients. Wide variations in both bulk reaction constants and wall reaction constants were observed among the sites.

> 来源：PDF 封面页（p.54 头部摘要框）。

---

## 2. 中文摘要（再表述）

`[原文]` 余氯在管网中的衰减建模、表征与预测，对水质达标与用户体验至关重要。本研究：

1. **方法**：推导并测试动力学速率方程；用 **5 个美国水厂**（Bellingham WA、Harrisburg PA（Oberlin 区）、Fairfield CA（zone 3）、North Marin CA、North Penn PA）的现场数据 + **AWWARF/USEPA 修改版 EPANET** 评估。
2. **核心结论**：余氯衰减 = **一阶 bulk 反应** + **管壁一阶或零阶 mass-transfer 限制反应**。
3. **关键经验**：**wall 反应常数与管材 Hazen–Williams 粗糙度成反比** —— 老/腐蚀严重的管反应更剧烈。
4. **观察**：5 个系统的 `k_b`（11 种源水）跨度 **0.08–17.7 /day**；`k_w` 跨度同样大。"无通用值" → **必须现场标定**。

---

## 3. 论文解决了什么问题

`[原文]` Introduction（p.55–56）与 Findings（p.64）归纳的 1997 年前文献空白：

| 1997 年前的状况 | 本论文解决的问题 |
| --- | --- |
| Rossman 1994 (A1) 已给 bulk+wall+mass-transfer 数学模型，但**只在 South Central Connecticut 一个系统验证过** | 在 **5 个不同地区 / 不同管材 / 不同水源** 的真实管网验证模型适用性 |
| `k_b` 文献多停留在"温度敏感、与有机物相关"的定性描述 | 给出 **11 种源水的实测 `k_b`**（Table 2），揭示 200 倍跨度，明确"无通用值" |
| `k_w` 几乎无实测数据 | 给出 **5 个系统的 `k_w`**（Table 4），并发现与管材粗糙度的定量关系 |
| 一阶 vs 零阶 wall 模型谁更好？无定论 | 分别试验，发现零阶 + roughness 略优（但优势微小）—— **解释了为何 EPANET 默认一阶**：精度差不多，参数更稳健 |
| 全网络 `k_w` 单一值是否够？还是要分管分区？ | 试了 3 种 wall 参数化（全局 / 分区 / 与粗糙度成反比），**粗糙度参数化最经济**（仅 1 个全局比例常数 α） |
| 无操作性指南——如何用模型、如何标定、需要什么数据？ | **明确流程**：① 先做 tracer 水力标定；② 烧瓶测 `k_b`（不在水质标定中调整）；③ 调 `k_w` 拟合余氯观测 |

---

## 4. 用了什么方法

### 4.1 整体研究设计 `[原文]` Methods (p.56–61)

5 个 **真实管网** + **修改版 EPANET** + **烧瓶 + 现场采样** 三层数据：

| 系统 | 管材 / 管龄 | 主源水 | 监测点数 | tracer |
| --- | --- | --- | --- | --- |
| **Bellingham WA**（Dakin-Yew 区）| 6–8" 无衬里 cast iron, >40 年 | Watcom WTP 地表水 | 14 | 无 |
| **Fairfield CA**（zone 3）| 8–12" AC（石棉水泥），< 15 年 | Waterman WTP 地表水 | 15 | 氟化物 |
| **Harrisburg PA**（Oberlin 区）| 2–6" 无衬里 GI（镀锌铁），> 30 年 | Oberlin Booster 站 | 31 | 氟化物 |
| **North Marin CA**（zone 1）| 12–30" 无衬里 CI，> 40 年；AC | 2 个地表 + 18 口井 | 15 | 钠 |
| **North Penn PA**（Lansdale 低区）| 8–16" 水泥衬里 DI + 无衬里 CI | 2 个地表水 | 8 | 硬度 |

> **观察**：5 个系统的**管材年龄**和**源水复杂度**差别巨大；这是本研究的**外部效度**保证。

### 4.2 关键方程（与 A1 一致，重排陈述）

#### Eq 1–2：经典一阶整体衰减

```
dC/dt = -k·C       →       C(t) = C₀·exp(-k·t)
```
- `k` 是表观整体一阶常数（1/day），**反映 bulk + wall + corrosion + mass-transfer 综合**。
- **缺陷**：`k` 是 site-specific 黑箱；不能预测拓扑变化后的余氯。

#### Eq 4：纯 bulk 一阶（烧瓶测 `k_b`）

```
dC/dt|bulk = -k_b · C
```

非线性最小二乘从 bottle test 拟合 `k_b`（mg/L vs time）。**全文 `k_b` 一旦定下，水质标定阶段不再动**。

#### Eq 5–6：壁面一阶 vs 零阶

```
一阶 wall：dC/dt|wall = -(k_{w,1} / r_h) · C_w    (Eq 5)
零阶 wall：dC/dt|wall = -(k_{w,0} / r_h)          (Eq 6)
```

其中 `r_h = D/4`（水力半径），`C_w` 是壁面浓度。
- **一阶**：合适于"氯是限制反应物"（如反应有机物的胞外酶）。
- **零阶**：合适于"氯瞬间氧化某还原剂、速率取决于还原剂供给速度"（如腐蚀诱导）。

#### Eq 7：边界层 mass transfer

```
dC/dt|mass-transfer = (k_f / r_h) · (C - C_w)
```

`k_f`（m/day）= 边界层质量传递系数；通过 Sherwood 数 Sh = k_f·d/D（D 为分子扩散系数）：
- **湍流**（Eq 9）：`Sh = 0.023 · Re^0.83 · Sc^0.33`
- **层流**（Eq 10，Edwards 等的参数拟合）：`Sh = 3.65 + 0.0668·(d/L)·Re·Sc / (1 + 0.04·[(d/L)·Re·Sc]^(2/3))`

#### Eq 11：一阶 wall 的整体串联

```
dC/dt = -[ k_b + (1/r_h) · (k_{w,1}·k_f) / (k_{w,1} + k_f) ] · C
```

物理意义：壁面反应**和** mass transfer 是**串联**——慢的那个限速。`k_{w,1} → ∞` 时退化为 `dC/dt = -(k_b + k_f/r_h)·C`（完全 mass-transfer 限制）；`k_f → ∞` 时退化为 `dC/dt = -(k_b + k_{w,1}/r_h)·C`（完全反应限制）。

> **这是 EPANET 至今的核心方程**。本项目 Plan A / Plan B 校准的目标参数就是 `k_b` 和 `k_{w,1}`（按 DMA 分组）。

#### Eq 14：wall 与管材粗糙度的反比（本论文核心创新）

```
Wall Rate Constant = α / Roughness   (Hazen–Williams C-factor)
```

α 是**全局比例常数**——只需标定一个参数，全网每根管的 `k_w` 自动按其粗糙度推算。
- **物理直觉**：粗糙度低（C-factor 大）= 管面光滑 = 新管 = 反应少
- **数据支持**：5 系统都成立，零阶版本略优

### 4.3 水质标定流程 `[原文]` p.60

```
Step 1 (水力):  hydraulic calibration via tracer (fluoride/sodium/hardness)
                调 baseline demand + 时间需水模式，直到 tracer 浓度匹配
Step 2 (bulk):  bottle test → 拟合 k_b （per source water），全程冻结
Step 3 (wall):  逐次调 k_w（三种参数化：全局 / 分区 / 与粗糙度反比），
                最小化预测-观测的平均绝对误差
Step 4 (eval):  统计 3 项指标：
                (a) 站均值相关系数, (b) 平均绝对误差, (c) 平均相对误差
```

**关键工程决策**：`k_b` 来自瓶试、**不参与**水质标定调整。这避免了 `k_b` 与 `k_w` 的耦合（identifiability 问题）。
**→ 本项目可直接借鉴**：Bristol 3 DMA 同一水源 → 可考虑 `k_b` 由烧瓶测 + 文献先验 fix，只校准 `k_w_A / k_w_B / k_w_C`。

### 4.4 EPANET 修改要点 `[原文]` p.58

为做这个研究，作者改造了 EPANET，加了 4 个特性：

1. 任意阶 power-law bulk 反应
2. 零阶 mass-transfer 限制 wall 反应
3. wall 反应常数 = α × Roughness
4. 自动输出标定的拟合度统计

> **历史意义**：这些修改后来全部进了 **EPANET 2.0+ 主干**，成为今天 WNTR 调用的默认能力。所以本论文不仅是验证，也是 EPANET 水质引擎现代化的**直接前身**。

---

## 5. 关键数据与结果

### 5.1 Bulk 衰减常数 `k_b` 跨水源差 200 倍 `[原文]` Table 2

| 源水 | 温度 °C | TOC mg/L | C₀ mg/L | **k_b (1/day)** |
| --- | --- | --- | --- | --- |
| North Penn — Keystone 入水 | 16.2 | 0.79 | 1.65 | **0.082** |
| North Penn — Well W12 | 18.3 | 0.52 | 0.85 | 0.102 |
| Harrisburg — Oberlin 泵站 | 16.4 | 1.73 | 0.98 | 0.232 |
| North Penn — 50/50 blend | 14.7 | 1.23 | 1.38 | 0.264 |
| North Penn — Well W17 | 14.8 | 1.06 | 0.50 | 0.355 |
| North Penn — Forest Park | 13.2 | 1.64 | 1.30 | 0.767 |
| Bellingham — Watcom WTP | 17.4 | 0.84 | 0.72 | 0.833 |
| Fairfield — Waterman WTP | 17.9 | 1.87 | 1.73 | 1.16 |
| North Marin — Russian River | 22.2 | 0.56 | 0.31 | 1.32 |
| North Marin — 50/50 blend | 22.1 | 0.40 | — | 10.8 |
| **North Marin — Stafford Lake** | 21.9 | 3.55 | 0.49 | **17.7** |

**两个数量级以上的跨度**！Stafford Lake 水（TOC 3.55 mg/L，温度 22 °C）`k_b` 是 North Penn Keystone（TOC 0.79）的 **216 倍**。

**→ 工程含义**：你**不可能**从文献查"管网 `k_b` 推荐值"。每个源水必须烧瓶测。

> Bristol Water Field Lab 3 DMA **同一水源** → `k_b` 大概率**全网共享**。但仍需烧瓶/数据验证，是 Tuesday 会议 Q3 之一。

### 5.2 Wall 反应在 4/5 系统显著存在 `[原文]` Table 4

| 系统 | k_b (1/day) | k_w 一阶 (m/day) | k_w 零阶 (mg/m²/day) | α·roughness 系数 | % 管段需 wall reaction |
| --- | --- | --- | --- | --- | --- |
| **Fairfield**（新 AC） | 1.16 | 0.0 | 0.0 | — | **0** |
| Bellingham（老 CI） | 0.833 | 0.766 | 1215 | 17,216 | 95 |
| **Harrisburg**（老 GI） | 0.232 | 0.272 | 91.5 | 6,994 | **100** |
| **North Marin**（混合） | 1.52* | 198 | 215 | 27,976 | 13 |
| **North Penn**（混合） | * | 3.0 | 553.8 | 5,380 | 100 |

\* 多源水复杂

**两个关键观察**：

1. **Fairfield**（新 AC 石棉水泥管、< 15 年、大管径 8–12"）→ `k_w = 0`，wall 不参与衰减。**只有 bulk 模型就够**。说明**管材 + 管龄真的关键**。
2. **Harrisburg**（老 GI 镀锌铁管、> 30 年、小管径 2–6"）→ **100% 管段需 wall**，`k_w,zero-order` = 91.5 mg/m²/day，是数据集中最显著的 wall 衰减。

**→ 直接对接 A4 Hallam 2002**：管材 / 管龄 / 管径**三联手**决定 wall。本项目 Bristol 3 DMA 大概率落在 Bellingham–Harrisburg 之间（英国管网 cast iron + DI 居多）。

### 5.3 标定精度 — 余氯模型能做多准 `[原文]` Table 5

5 个系统用 "bulk + zero-order wall + α·roughness" 模型的标定统计：

| 系统 | 平均绝对误差 (mg/L) | 平均相对误差 (%) | 站均值相关性 (%) |
| --- | --- | --- | --- |
| Bellingham | 0.11 | 28 | 96 |
| Fairfield | 0.15 | 23 | 96 |
| Harrisburg | 0.09 | 29 | 97 |
| North Marin | 0.05 | 31 | 85 |
| North Penn | 0.14 | 17 | 98 |
| **范围** | **0.05–0.15** | **17–31** | **85–98** |

**→ 这就是本项目的"工程精度基线"**：

- 如果本项目（uncertainty-aware Bristol 3-DMA）能跑到 **平均绝对误差 ≤ 0.10 mg/L、相关性 ≥ 95%**，就**与最先进对手齐平**。
- 如果只能到 0.15–0.20 mg/L，说明还有 unmodeled physics（biofilm / nitrification / 入口测量误差）。

### 5.4 测量误差边界 `[原文]` p.63（**项目关键**）

> "For the DPD colorimetric method used in this study, **variability can be as high as 15 percent**."（引用 Gordon et al. 1992, AWWARF 90528）

**→ 这一句话是本项目"测量误差模型"的直接文献依据**：

- 用 DPD 比色法 grab sample：**σ_meas / C ≈ 0.15**（相对误差 15%）
- 加上**绝对误差下限**（约 ±0.02 mg/L，A2 Hua 1999 提到的 Hach 比色计精度）

likelihood 模型可以写成（其中 σ_min ≈ 0.02、σ_rel ≈ 0.15）：

```
σ_meas(C) = sqrt( σ_min² + (σ_rel · C)² )
y_obs | y_sim ~ Normal(y_sim, σ_meas(y_sim)²)
```

---

## 6. 与本项目（Bristol 3-DMA）的连接

| A6 结论 | 对本项目的指导 |
| --- | --- |
| 一阶 bulk + 一阶 wall + mass-transfer **能拟合到 0.05–0.15 mg/L 平均误差** | **项目精度目标定到此范围** —— 论文 Results 用这个 benchmark 评估 |
| `k_b` 跨源水差 200 倍、必须烧瓶测 | Tuesday 会议 Q3：**3 个 DMA 是否共享 `k_b`？是否有烧瓶数据？** |
| wall 反应在 4/5 真实系统显著（除非新 AC 管） | Bristol 3 DMA（英国 + 混合管材）**几乎肯定需要 `k_w`** |
| **`k_w` 与 Hazen–Williams 粗糙度成反比**（α·roughness 参数化） | **可作为 informative prior 的形式**：如果 Bristol 给出每根管的 C-factor，可用 `k_w_pipe = α / C_factor`；Bayesian 把 α 当超参数估 |
| `k_b` 来自瓶试 + 不参与水质标定（避免与 `k_w` 耦合） | **Plan A/B 直接照抄**：`k_b` 用先验固定 + 弱先验扰动；专心校准 `k_w` |
| DPD 变异性 ~15% | **likelihood 的 σ_rel 取 0.15** 是有文献依据的合理初值 |
| Fairfield 用一阶 bulk 就够（新 AC 管）；其他 4 个都需要 wall | **如果 3 个 DMA 里有"新管 DMA"**，可能 `k_w_DMA-X ≈ 0`，这是个有意义的发现 |
| 零阶 wall 略优但优势微小 | **本项目沿用 EPANET 默认一阶 wall**——优势微小、一阶 EPANET-MSX 不需要、文献多用、对 Bayesian 先验也更自然（正常分布而非截断） |
| 水力标定必须先做（tracer study） | **本项目不做** — 导师明确排除 hydraulic calibration，假设既有模型已经标过 |
| 现场标定 = 唯一可行的 `k_w` 估法 | **整个 Plan A/B 校准的存在性都依赖这个事实** |

### 6.1 Methodology 引用建议

写论文 §3 Methodology 时，A6 至少在 3 处必引：

1. **§3.1 模型框架**：
   > "We adopt the first-order bulk + first-order wall decay model with mass-transfer formulation introduced by Rossman et al. (1994) and empirically validated across five US distribution systems by Vasconcelos et al. (1997)."

2. **§3.2 参数策略（`k_b` 烧瓶测、`k_w` 校准）**：
   > "Following Vasconcelos et al. (1997), bulk decay coefficients `k_b` are estimated from independent bottle-test data and held fixed during calibration; only wall decay coefficients `k_w` per DMA enter the inference."

3. **§3.4 测量误差模型**：
   > "We model DPD colorimetric variability as a multiplicative 15% relative error, consistent with Gordon et al. (1992) and reaffirmed by Vasconcelos et al. (1997)."

### 6.2 Discussion 引用

`[推断]` 我们可以**反过来**把 Bristol 结果与 Vasconcelos 1997 的 5 系统对比：

- 如果 Bristol 3 DMA 的 `k_w` 都落在 Bellingham（老 CI）和 Harrisburg（老 GI）之间 → 与文献吻合，说明项目方法可信。
- 如果存在某 DMA 的 `k_w` 显著低于 Harrisburg（< 0.1 m/day），可能是衬里 / 新管 / 不锈钢 → 工程含义。
- 如果某 DMA 的 `k_w` **比 Bellingham 高 5 倍以上** → 异常，需要诊断（是否水力模型有错？是否有未建模的 booster / 二次加氯？）

---

## 7. 与已读文献的关系

```
 ┌────────────────────────────────────────────────────────────┐
 │                  EPANET 水质引擎家族树                       │
 ├────────────────────────────────────────────────────────────┤
 │                                                              │
 │  A1 Rossman 1994     ──→ 推导 bulk+wall+MT 数学框架          │
 │    (理论)               + 单一系统验证                        │
 │      │                                                       │
 │      ▼                                                       │
 │  A6 Vasconcelos 1997 ──→ 5 系统真实管网实证                  │
 │    (本论文)             + 提出 α·roughness 参数化            │
 │      │                  + 给出 EPANET 修改版（后并入主干）   │
 │      ├──────────┬──────────────┐                             │
 │      ▼          ▼              ▼                             │
 │  A2 Hua 1999  A3 Powell 2000  A4 Hallam 2002                 │
 │  (Birmingham  (bulk 因子      (wall 异质性 +                 │
 │   bulk 烧瓶)    系统化)        管材/管龄定量)                │
 │                                  │                           │
 │                                  ▼                           │
 │                            A5 Maleki 2023                    │
 │                            (魁北克 full-scale                │
 │                             20 年后实证升级)                  │
 │                                                              │
 │  本项目 Bristol 3-DMA：A1+A6（理论/方法）+ A4（异质性论据）  │
 │                       + A5（管材分类经验）+ E6/E7（不确定性） │
 └────────────────────────────────────────────────────────────┘
```

---

## 8. 批判性评价

### 8.1 论文的强项

1. **跨多系统外部效度**：5 个不同管材 / 不同源水 / 不同气候的真实管网 —— 1997 年文献里独一无二。
2. **完整方法链**：bottle test → 烧瓶 `k_b` → tracer 水力标定 → wall 反演 → 拟合统计 —— 至今**仍是行业标准流程**。
3. **EPANET 修改回馈主干**：研究成果直接催化 EPANET 2.0 的能力提升，影响 30 年。
4. **承认局限**：明确写出"DPD 变异 15%"作为 unaccounted error 的下限，**对不确定性研究极友好**。

### 8.2 论文的局限（本项目可补的 gap）

| A6 局限 | 本项目如何补 |
| --- | --- |
| 校准给的是**单点估计**，无后验区间 | **本项目 Plan A (GLUE) / Plan B (Bayesian) 显式给后验区间** |
| 测量误差仅一句话提及"15%"，未进入 likelihood | **本项目把 DPD ± 在线传感器误差**正式建模进 likelihood |
| 5 系统横向比较，但**未做"DMA 间可迁移性"**（A 系统 `k_w` 能预测 B 系统吗？） | **本项目专门做 cross-DMA posterior predictive check** |
| 用单一 Hazen-Williams 关系，未尝试 hierarchical / partial pooling | **本项目 Plan B Bayesian hierarchical** 把 3 个 `k_w` 视为家族先验 |
| 1997 年没有 Python / WNTR / 现代 MCMC | **本项目 stack**：WNTR + emcee/pymc + SALib + 真实在线传感器数据 |
| Bottle test 一次性测，未考虑温度日变化 | `[需补]` 可在 Discussion 提及温度 / TOC 的次要变异（A2 Hua 1999 给的范围） |

### 8.3 对方法学的影响（深远）

A6 的 3 个永续遗产：

1. **"bottle test + field calibration"** 是今天 EPANET / WNTR 工作流的**事实标准**——本项目也将复刻。
2. **"wall × inverse roughness"** 是把"看不见的"`k_w` 与"看得见的"管材结构挂钩的第一个有效经验关系——A4 Hallam 2002 把它精细化为分管材公式，A5 Maleki 2023 进一步用 full-scale 真实数据细化。
3. **"`k_b` 与 `k_w` 解耦"**（先固定 `k_b`，再调 `k_w`）—— 这是解决 identifiability 的最早、最有效的工程办法，**本项目沿用**。

---

## 9. 关键公式速查表

| 符号 | 单位 | 含义 | 取值或测法 |
| --- | --- | --- | --- |
| `k`（综合） | 1/day | 整体表观一阶常数 | site-specific 反推 |
| `k_b` | 1/day | bulk 一阶 | **烧瓶 bottle test** |
| `k_{w,1}` | m/day | wall 一阶 | **现场反演**；与 1/roughness 成正比 |
| `k_{w,0}` | mg/m²/day | wall 零阶 | 现场反演；零阶版本 |
| `k_f` | m/day | 边界层传质 | `Sh · D / d`（Eq 8） |
| `r_h` | m | 水力半径 = D/4 | 几何 |
| `D`（扩散） | m²/s | 自由氯分子扩散系数 | ~1.25 × 10⁻⁹ m²/s（25 °C） |
| `Re` | — | 雷诺数 | `ρ·v·d / μ`（流体常识） |
| `Sc` | — | Schmidt 数 | `μ / (ρ·D)`，自由氯 ~700 |
| `Sh` | — | Sherwood 数 | 湍流 Eq 9；层流 Eq 10 |
| `α` | (mg/m²/day) × C-factor | 粗糙度比例常数 | 5,380–27,976（5 系统范围，Table 4） |

> **单位陷阱提醒**：EPANET 内部用 **SI 1/s**；论文/笔记用 **1/day**。换算：`k_per_sec = k_per_day / 86400`。**衰减传负值**。详见 starter notebook §2。

---

## 10. 一句话总结

> **A6 = A1 的实证证明 + EPANET 的实战手册**：5 个系统证明"一阶 bulk + 一阶/零阶 wall + mass-transfer + 1/roughness"在真实管网普遍有效；标定可达 0.05–0.15 mg/L 平均误差、85–98% 相关；`k_b` 烧瓶测，`k_w` 现场反演——这套流程统治了之后 30 年的 chlorine modeling，本项目 Plan A/B 也照此结构展开，只是把"单点估计"升级为"后验分布"。
