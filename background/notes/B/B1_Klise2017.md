# B1 — Klise, Bynum, Moriarty, Murray (2017) 精读笔记

> 配套文件：[`../../Literature/literature.md`](../../Literature/literature.md) §B1、[`../../README.md`](../../../README.md)、[`../../../plan1.md`](../../../plan1.md)
> 同组工具文献：`literature.md` §B2（EPANET 2.2 Manual，水质方程引擎）；§B3（WNTR User Manual，实操 API）
> 方法学呼应：[`../E/E1_Kavetski2006.md`](../E/E1_Kavetski2006.md)（不确定性框架）；`literature.md` §E6 Beven&Binley 1992（GLUE / Monte Carlo ensemble — 本项目 Plan A）
> PDF 路径：`../../Literature/B-软件/BBB1-Klise, Bynum, Moriarty, Murray (2017). A software framework for assessing the resilience of drinking water systems to disasters with an example earthquake case study. Env. Modelling & Software.pdf`
>
> **来源标签**（2026-06-01，已通读 PDF 12 页正文）：
> - `[原文]` 直接出自论文 PDF
> - `[元数据]` 来自期刊页眉 / CrossRef / 官方仓库
> - `[推断]` 与项目关联的延伸
> - `[需补]` 待后续文献或实验核对

---

## 0. 元数据（已验证）

| 字段 | 内容 | 来源 |
| --- | --- | --- |
| Title | **A software framework for assessing the resilience of drinking water systems to disasters with an example earthquake case study** | PDF cover |
| Authors | **Katherine A. Klise**, **Michael Bynum**, **Dylan Moriarty**, **Regan Murray** | PDF p.420 |
| Affiliation | Klise & Moriarty：Sandia National Laboratories（Albuquerque, NM）；Bynum：Purdue University 化工系；Murray：US EPA National Homeland Security Research Center（Cincinnati, OH） | PDF p.420 |
| Journal | *Environmental Modelling & Software* | PDF |
| Volume / Pages | **95**, **420–431** | PDF, CrossRef |
| Year | **2017-09**（online 2017-07-07；received 2016-12-02） | PDF |
| DOI | **`10.1016/j.envsoft.2017.06.022`** ⚠️ | PMC / Sandia / USEPA+sandialabs GitHub |
| 资金来源 | US EPA Office of Research and Development (DW8992450201) × DOE Sandia 跨机构协议 | PDF p.431 Acknowledgement |
| 软件仓库 | 原 `https://github.com/USEPA/WNTR`（2016-10 首次公开）；现 `https://github.com/sandialabs/WNTR` | PDF §3.1 + GitHub |
| 优先级 | **P0**（导师 2026-05-25 邮件明确推荐） | literature.md §B1 |
| 状态 | `read`（PDF 已通读 12 页） | — |

> ⚠️ **DOI 勘误**：`literature.md` §B1 原写 `10.1016/j.envsoft.2017.06.022` 的尾号为 **.023**，经 PMC（PMC6262876）、Sandia 出版页、USEPA/sandialabs 两个官方仓库的引用块交叉核对，**正确尾号是 .022**（.023 是同期另一篇文章）。已在本次同步修正 literature.md。

**为什么是 P0**：导师邮件原话——*"for citing the tool and understanding its design"*。这是 **WNTR 的官方引用论文**。本项目所有余氯仿真都跑在 **WNTR**（封装 EPANET 水质引擎）上，所以：

1. **引用**：论文 Methodology 写"We use WNTR (Klise et al., 2017) ..." 时，B1 是**唯一正确的工具引用**。
2. **理解设计**：B1 讲清楚了 WNTR 的**架构与数据结构**（NetworkX 拓扑 + Pandas 结果 + EPANET .inp 读入 + 自带 PDD 求解器 + **Monte Carlo 能力**）—— 知道这些才能正确扩展 `simulate_chlorine(kb, kw)` 并做 ensemble。
3. **方法模板**：B1 的核心 case study 就是 **27 个场景 × 50 次 Monte Carlo realization** 的不确定性传播 —— 与本项目 Plan A（ensemble-based uncertainty）**同构**，只是把"地震损伤"换成"`k_b`/`k_w` 参数 + 测量误差"。

> **关键定位**：B1 **不是**余氯论文，案例是地震韧性。它对本项目的价值在于 **工具引用 + 设计理解 + Monte Carlo ensemble 工作流模板**，而**不是**水质机理（机理看 A1/A6、B2）。

---

## 1. 原文 Abstract（英文，逐字）

> Water utilities are vulnerable to a wide variety of human-caused and natural disasters. The Water Network Tool for Resilience (WNTR) is a new open source Python™ package designed to help water utilities investigate resilience of water distribution systems to hazards and evaluate resilience-enhancing actions. In this paper, the WNTR modeling framework is presented and a case study is described that uses WNTR to simulate the effects of an earthquake on a water distribution system. The case study illustrates that the severity of damage is not only a function of system integrity and earthquake magnitude, but also of the available resources and repair strategies used to return the system to normal operating conditions. While earthquakes are particularly concerning since buried water distribution pipelines are highly susceptible to damage, the software framework can be applied to other types of hazards, including power outages and contamination incidents.

> 来源：PDF p.420 摘要框。

---

## 2. 中文摘要（再表述）

`[原文]` 供水系统易受多种人为/自然灾害冲击。**WNTR（Water Network Tool for Resilience，读作 "winter"）** 是一个新的开源 Python 包，帮助水务公司评估管网对灾害的韧性、并比较增强韧性的措施。本文：

1. **介绍 WNTR 建模框架**：把"灾害损伤模型 + 水力/水质仿真 + 修复响应 + 韧性指标"整合进**单一平台**。
2. **地震 case study**：在一个真实管网（15.2 万用户、3323 节点、3829 管段）上模拟 M6.0/6.5/7.0 地震 × 3 个震中位置 × 3 种修复策略，每个场景跑 **50 次 Monte Carlo**。
3. **核心论点**：灾损程度不仅取决于系统完整性和震级，还**强烈取决于可用资源与修复策略**（节水、抗震管改造能大幅缩短恢复时间）。
4. **通用性**：框架不限地震，也适用于**停电、污染事件**等。

---

## 3. 论文解决了什么问题

`[原文]` Introduction + Literature review（p.420–422）指出的工具空白：

| 2017 年前的状况 | WNTR 解决的问题 |
| --- | --- |
| EPANET 等主流仿真是 **demand-driven (DD)**：无论压力够不够，都假设需水**总能满足** | WNTR 自带 **pressure-driven demand (PDD)** 求解器：低压时按 Wagner (1988) 方程给"打折"的水量 —— 灾害/低压场景更真实 |
| 已有地震韧性工具（GIRAFFE、REVAS.NET 等）多为 **quasi-PDD**，且**只管水力**、不集成损伤/修复/水质 | WNTR 把**损伤模型 + fragility 曲线 + 控制逻辑 + 漏损 + PDD 水力 + 韧性指标 + Monte Carlo** 集成进**一个 Python 框架** |
| 仿真过程**不能中途改运行规则**（要重跑） | WNTR 可**暂停仿真 → 改控制/操作 → 续跑**（修复响应建模必需） |
| 缺少面向 utility 的、可脚本化/并行化的开源工具 | **纯 Python + 开源**：可循环、可并行、可读 EPANET `.inp`、结果存 Pandas 便于时序分析 |

> **对本项目的意义**：本项目用 WNTR **不是为了 PDD/地震**，而是看中它的 **(a) EPANET 水质引擎封装、(b) Python 可脚本化做 Monte Carlo ensemble、(c) Pandas 结果便于和 SCADA 实测余氯比对**。

---

## 4. WNTR 的设计与组件（重点：理解 design）

### 4.1 七大建模组件 `[原文]` p.421

WNTR 的 primary modeling components：

1. **灾害模型**（如地震衰减模型，预测地动）
2. **fragility / survival 曲线**（给组件分配损伤概率）
3. **灵活的 controls**（时间/条件触发，改组件状态与设置）
4. **漏损模型**（节点/管段漏水）
5. **PDD 水力仿真**（低压条件下的真实送水量）
6. **韧性指标**（评估灾损与修复效果）
7. **Monte Carlo 仿真能力** ← **本项目直接相关**

### 4.2 技术栈与数据结构 `[原文]` p.421（**"understanding its design" 的核心**）

| 层 | 依赖 | 在 WNTR 里的角色 | 对本项目的用法 |
| --- | --- | --- | --- |
| 模型输入 | **EPANET `.inp`** | 可从 EPANET 格式文件构建水网模型；兼容 EPANET 全部单位约定 | **Bristol 3-DMA 模型以 `.inp` 形式交付** → 直接 `wntr.network.WaterNetworkModel(inp)` |
| 拓扑 | **NetworkX** | 网络连通性存为 NetworkX 图对象，可做图论分析（最短路径、割点等） | DMA 边界、监测点连通性、source-to-sensor 路径分析 |
| 结果 | **Pandas** | 水力/水质仿真结果存为 Pandas 对象，便于节点/管段属性的**时序分析** | 仿真余氯 `results.node['quality']` → 直接对齐 SCADA 时序、算残差/likelihood |
| 数值 | **NumPy / SciPy** | 高效数值计算；PDD 非线性方程组用 **Newton–Raphson** 解 | ensemble 里成百上千次 `sim.run_sim()` 的底层 |
| 绘图 | **Matplotlib** | 网络图、动画 | 拓扑图、余氯时空分布图（见 `learning/net3_topology.png`） |
| 并行 | 标准 Python (multiprocessing 等) | 仿真可在循环或并行中跑 | **Plan A ensemble 的天然实现方式** |

> `[原文]` p.421：WNTR 既能**调用 EPANET 做 DD 仿真**，也能用**自带求解器做 PDD 仿真**。对比 OOPNET（也是面向对象 EPANET 的 Python 封装）只支持 DD。
> **→ 本项目**：余氯仿真走 **EPANET 水质引擎**（`EpanetSimulator`），水力假设既有模型已标定（导师明确**排除** hydraulic calibration），故 PDD 与否对本项目不是重点。

### 4.3 Monte Carlo 仿真能力 `[原文]` §3.8（**本项目 Plan A 的工具基础**）

`[原文]` 为处理灾害建模的不确定性，WNTR 支持**多次 realization**：
- 场景特征可**从统计分布抽样**（损伤位置/严重度来自 fragility 曲线、持续时间来自分布等）。
- 兼容多种统计分布与随机抽样方法。
- 可**暂停 → 改操作 → 续跑**；模型与结果可存盘/重载。
- 可用标准 Python 工具**并行**跑。

> **→ 直接映射到本项目**：把"从 fragility 抽损伤"换成"从先验抽 `k_b`、`k_w_A/B/C`，并对仿真余氯叠加 DPD 测量误差"，就是 **Plan A（GLUE / ensemble）** 的实现骨架。B1 证明 WNTR 的 Monte Carlo 工作流是**官方设计意图内**的用法，不是 hack。

### 4.4 与本项目无关但需知道的组件（地震专用）

`[原文]` §3.2–3.7：PGA/PGV **衰减模型**（Eq 1–5）、**pipe repair rate**（Eq 6–8）、**fragility 曲线**、**leak 模型**（Eq 9，Crowl & Louvar 孔口流）、**PDD 方程**（Eq 10，Wagner 1988）、**韧性指标**（WSA Eq 11、population Eq 12、population impacted Eq 13）。

> 这些是**地震 case study 专用**。本项目**不用** PGA/fragility/leak/repair。唯一值得借鉴的是 **§3.7 韧性指标的"系统级 vs 节点级"区分**思路（对余氯，可类比"全网达标率 vs 单监测点达标率"）。`[推断]`

---

## 5. 关键案例与结果（地震 case study，了解即可）

### 5.1 实验设计 `[原文]` §4

- **真实管网**：1 水库、2 阀、34 水箱、61 泵、3323 节点、3829 管段；服务 ~152,000 人；管材 cast iron / ductile iron / polyethylene。
- **场景矩阵**：3 震级（6.0/6.5/7.0）× 3 震中（南/中/北）× 3 修复策略（RS1 常规 / RS2 节水 40% / RS3 抗震管改造）= **27 场景**。
- **每场景 50 次 Monte Carlo realization**（损伤位置、火灾需求随机）。
- PDD：最小压力 0、额定压力 25 psi；仿真震后 14 天。

### 5.2 主要发现 `[原文]` §4.3 + Table 1–2

| 发现 | 数据 |
| --- | --- |
| 震级↑ → 水服务可用性(WSA)↓、受影响人口↑ | M6.0 仅 2–15% WSA 下降、<3.4 万人；M7.0 >85% 用户受影响、WSA 0.27–0.35、>14 天恢复 |
| **修复策略比震级更可控** | 中央 M6.5：RS1 ~9 万人受影响/恢复 7 天 → RS2 节水 ~5.3 万人/4 天 → **RS3 抗震管 <2.6 万人/1.6 天** |
| 同一场景结果**分布很宽** | 震后 1 天 WSA 在单一场景下从 ~45% 到 >60%（50 次 realization 的离散度） |

> **→ 对本项目的唯一启示**（方法论层面，非内容）：**"中位数 + 5/25/75/95 百分位带"** 的呈现方式（Fig 6–8）正是 ensemble 不确定性结果的**标准画法**。本项目的余氯后验预测区间图可**照此风格**：黑线=中位数、深灰=IQR、浅灰=90% 区间。`[推断]`

---

## 6. 与本项目（Bristol 3-DMA 余氯不确定性）的连接

| B1 内容 | 对本项目的指导 |
| --- | --- |
| WNTR = 官方 Python 工具，B1 = 其引用论文 | **Methodology 引用 WNTR 必引 B1**（外加 B3 User Manual 作实操出处） |
| WNTR 读 EPANET `.inp`、兼容 EPANET 单位 | Bristol `.inp` 直接载入；余氯单位、`k_b`/`k_w` 单位沿用 EPANET 约定（注意 1/day ↔ 1/s 换算，见 starter notebook §2 与 A6 §9） |
| 结果存 **Pandas** 时序对象 | 仿真余氯 ↔ SCADA 实测余氯**按时间戳对齐**做残差/likelihood，Pandas 是天然载体 |
| **Monte Carlo** 是设计内能力、可并行 | **Plan A（GLUE/ensemble）直接落地**：先验抽 `k` → 批量 `run_sim` → likelihood 加权 → 后验区间 |
| 拓扑存 **NetworkX** | DMA 划分、source→monitor 路径、监测点覆盖度分析可用图算法 |
| 自带 PDD 求解器 vs 调 EPANET 做 DD/水质 | 本项目**水质仿真走 EPANET 引擎**；水力当作"已标定输入"（导师排除 hydraulic calibration） |
| case study 的"百分位带"可视化 | 余氯后验预测图照搬"中位数 + IQR + 90% 带"画法 |
| WNTR 可暂停→改操作→续跑 | `[推断]` 可用于建模**时变入口加氯 pattern**或二次加氯（exercises 4 的延伸） |

### 6.1 Methodology 引用建议

写论文 §3 Methodology（工具与实现）时：

> "All hydraulic and water-quality simulations are performed with the Water Network Tool for Resilience (WNTR), an open-source Python package that wraps the EPANET solver and exposes network topology, controls, and time-series results as native Python objects (Klise et al., 2017). WNTR's built-in support for Monte-Carlo simulation underpins our ensemble-based uncertainty quantification (Plan A)."

并在脚注/相邻句指明实操出处为 **B3（WNTR User Manual）**、水质方程出处为 **B2（EPANET 2.2 Manual）/ A1 / A6**。

### 6.2 边界与诚实声明 `[推断]`

- B1 的**案例内容**（地震、PGA、fragility、leak、PDD）**与本项目无关**，不要在 Methodology 里误引这些为"余氯方法"。
- B1 **不**讨论水质反应动力学；`k_b`/`k_w`/mass-transfer 的理论与数值出处是 **A1 Rossman 1994 + A6 Vasconcelos 1997 + B2 EPANET Manual**，B1 只负责"工具是什么、怎么设计的"。

---

## 7. 与已读文献的关系

```
 ┌──────────────────────────────────────────────────────────────┐
 │                   本项目工具/方法依赖图                        │
 ├──────────────────────────────────────────────────────────────┤
 │                                                                │
 │   理论/机理              工具/实现             不确定性         │
 │   ─────────              ─────────             ────────         │
 │   A1 Rossman 1994   ┐                                          │
 │   A6 Vasconcelos 97 ├─→  B2 EPANET 2.2 Manual                  │
 │   (bulk+wall+MT)    ┘    (水质数值引擎)                        │
 │                              │                                 │
 │                              ▼                                 │
 │                     ★ B1 Klise 2017 (本笔记)                   │
 │                       WNTR = EPANET 的 Python 封装             │
 │                       + NetworkX/Pandas + Monte Carlo          │
 │                              │                                 │
 │                              ├──→ B3 WNTR User Manual (实操API) │
 │                              │                                 │
 │                              ▼                                 │
 │                     Plan A: GLUE/ensemble  ←─ E6 Beven&Binley  │
 │                     Plan B: Bayesian/MCMC  ←─ E1/E7            │
 │                              │                                 │
 │                              ▼                                 │
 │                  Bristol 3-DMA 余氯后验预测区间                │
 └──────────────────────────────────────────────────────────────┘
```

- **A1/A6/B2** 给"算什么"（水质方程）；**B1/B3** 给"用什么算"（WNTR）；**E6/E1/E7** 给"怎么量化不确定性"。
- B1 是连接**机理**与**不确定性方法**的**工具枢纽**。

---

## 8. 批判性评价

### 8.1 强项

1. **集成度**：首个把损伤+水力+水质+修复+韧性指标+Monte Carlo 装进单一开源 Python 框架的工具论文。
2. **可复现/可扩展**：纯 Python、开源、读 EPANET `.inp`、用主流科学栈（NumPy/SciPy/Pandas/NetworkX/Matplotlib）——这正是本项目能在其上做 ensemble 的前提。
3. **不确定性意识**：case study 用 50×27 Monte Carlo 呈现结果分布，而非单点——与本项目哲学一致。
4. **PDD 的工程严谨**：指出 Wagner PDD 方程在 P0/Pf 处导数不连续，用 **cubic Hermite spline** 强制连续性以保 Newton–Raphson 收敛（数值细节扎实）。

### 8.2 局限（与本项目的关系）

| B1 局限 | 与本项目的关系 |
| --- | --- |
| case study 是**地震韧性**，非水质/余氯 | 本项目只借**工具与 MC 工作流**，不借案例内容 |
| 论文层面**未深入水质反应**（水质仿真一笔带过） | 余氯机理/数值另查 A1/A6/B2；B1 不够 |
| Monte Carlo 用于**前向不确定性传播**（已知分布→输出分布），**非参数反演/校准** | 本项目要做的是**反问题**（观测→参数后验），需在 WNTR 之上自建 GLUE/Bayesian 层（E6/E1/E7） |
| 2017 年版本，API 已演进（如 reactions/water-quality 接口、`WaterNetworkModel` 细节） | **实操以 B3 最新 User Manual + 当前安装版本为准**；B1 只锁"设计意图"，不锁 API 细节 `[需补]` |
| 论文未给水质仿真的精度/验证 | 余氯精度基线看 **A6**（0.05–0.15 mg/L 平均误差） |

### 8.3 对本项目方法学的影响

1. **确立工具合法性**：用 WNTR 做余氯 + Monte Carlo 有官方论文背书（B1），审稿/答辩时是稳的引用。
2. **确立结果呈现范式**：百分位带（median + IQR + 90%）是 ensemble 结果的标准画法，本项目后验预测图照此。
3. **确立实现路径**：Pandas 结果 + 可并行 `run_sim` → 几百到几千次仿真的 ensemble 在工程上完全可行。

---

## 9. 关键事实 / API 速查表

| 项 | 内容 | 用途 |
| --- | --- | --- |
| 工具名 | **WNTR**（Water Network Tool for Resilience，读 "winter"） | 论文里写全称 + 缩写 |
| 引用 | Klise, Bynum, Moriarty, Murray (2017), *Env. Model. Softw.* **95**, 420–431, **doi:10.1016/j.envsoft.2017.06.022** | Methodology 工具引用 |
| 仓库 | `github.com/sandialabs/WNTR`（原 `USEPA/WNTR`） | 安装、API 文档 |
| 输入 | EPANET `.inp` 文件 | `wntr.network.WaterNetworkModel(inp_file)` |
| 拓扑 | NetworkX 图 | 连通性/路径分析 |
| 结果 | Pandas 对象（节点/管段 × 时间） | 时序分析、对齐 SCADA |
| 水力 | EPANET（DD）或 WNTR 自带（PDD，Newton–Raphson + cubic Hermite spline） | 本项目水质走 EPANET 引擎 |
| 不确定性 | 内建 Monte Carlo + 可并行 | **Plan A ensemble 的基础** |
| 依赖 | Python 2.7/3.4/3.5（论文版）+ NumPy/SciPy/Pandas/NetworkX/Matplotlib | 现版本要求更高，以当前安装为准 |

> **单位提醒**：WNTR 兼容 EPANET 单位约定；余氯衰减常数论文/笔记常用 **1/day**，EPANET 内部 **1/s**，换算 `k_per_sec = k_per_day / 86400`，衰减取负。详见 A6 §9 与 starter notebook §2。

---

## 10. 一句话总结

> **B1 = WNTR 的"出生证明"**：它把 EPANET 水质/水力引擎封装进 Python（NetworkX 拓扑 + Pandas 结果 + 内建 Monte Carlo + 可并行），并用一个 27 场景 × 50 realization 的地震案例演示"前向不确定性传播"。本项目**不关心地震**，只借三样东西——**官方工具引用、WNTR 的设计与数据结构、Monte Carlo ensemble 工作流**——在其之上叠加 GLUE/Bayesian 反演（E6/E1/E7），用 A1/A6/B2 的余氯方程，对 Bristol 3-DMA 做带后验区间的余氯预测。
