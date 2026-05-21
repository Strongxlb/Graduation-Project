# A1 — Rossman, Clark, Grayman (1994) 精读笔记

> 配套文件：[`../Literature/literature.md`](../Literature/literature.md) §A1、[`../../README.md`](../../README.md)、[`../../plan1.md`](../../plan1.md)
> PDF 路径：[`../Literature/rossman-et-al-1994-modeling-chlorine-residuals-in-drinking-water-distribution-systems.pdf`](../Literature/rossman-et-al-1994-modeling-chlorine-residuals-in-drinking-water-distribution-systems.pdf)
>
> **来源标签**（更新于 2026-05-19，已通读 PDF 18 页正文）：
> - `[原文]` 直接出自论文 PDF
> - `[元数据]` 来自 CrossRef / OpenAlex
> - `[推断]` 仍属推断（项目最终所剩极少）
> - `[需补]` 仍需补充（清单见 §10）
>
> 之前未读 PDF 时大多数 `[推断]` 项都已对照原文核实并改为 `[原文]`；少数被修正之处（数值方法、测量方法等）在 §13「修正记录」中专门列出。

---

## 0. 元数据（已验证）

| 字段 | 内容 | 来源 |
| --- | --- | --- |
| Title | Modeling Chlorine Residuals in Drinking-Water Distribution Systems | CrossRef + PDF |
| Authors | **Lewis A. Rossman**, Robert M. Clark, Walter M. Grayman | CrossRef + PDF |
| Affiliation | US EPA Risk Reduction Engineering Lab, Cincinnati（第一、第二作者）；Grayman 为咨询工程师 | PDF 脚注 1–3 |
| Journal | *Journal of Environmental Engineering* (ASCE) | CrossRef |
| 提交 / 出版 | Submitted 1993-04-15；published Vol 120, No. 4, **1994-07/08** | PDF 脚注 |
| 页码 | 803–820（**18 页**） | PDF |
| DOI | `10.1061/(ASCE)0733-9372(1994)120:4(803)` | — |
| Paper No. | 5922 | PDF |
| 被引数 | **386 (CrossRef) / 494 (OpenAlex)**（截至 2026-04） | 两库 |
| 优先级 | **P0**（literature.md §A1） | 本项目 |
| 状态 | `read`（PDF 已通读） | — |

**为什么是 P0**：第一作者 Rossman 就是 EPANET 的作者本人，本文是 **EPANET water quality module** 的奠基论文。文中明确提到该模型已集成进 "a computer program called EPANET" `[原文]` p.69。

---

## 1. 原文 Abstract（英文，逐字）

> A mass transfer-based model is developed for predicting chlorine decay in drinking-water distribution networks. The model considers first-order reactions of chlorine to occur both in the bulk flow and at the pipe wall. The overall rate of the wall reaction is a function of the rate of mass transfer of chlorine to the wall and is therefore dependent on pipe geometry and flow regime. The model can thus explain field observations that show higher chlorine decay rates associated with smaller pipe sizes and higher flow velocities. It has been incorporated into a computer program called EPANET that can perform dynamic water-quality simulations on complex pipe networks. The model is applied to chlorine measurements taken at nine locations over 53 h from a portion of the South Central Connecticut Regional Water Authority's service area. Good agreement with observed chlorine levels is obtained at locations where the hydraulics are well characterized. The model should prove to be a valuable tool for managing chlorine-disinfection practices in drinking-water distribution systems.

> 来源：PDF p.803（与 OpenAlex 重建版本一致）。

---

## 2. 中文摘要（再表述）

`[原文]` 论文提出**以质量传递为基础**的余氯衰减模型，用于预测饮用水管网中的余氯浓度。模型把余氯衰减拆成两段一阶反应：

1. **bulk reaction**：发生在水体内的整体反应（与有机物等反应），速率系数 $k_b$；
2. **wall reaction**：发生在管壁的反应（与管壁腐蚀产物、生物膜等反应），速率系数 $k_w$。

**关键 insight**：wall reaction 的有效速率并非单纯由 $k_w$ 决定，而是受**水体→管壁的传质速率 $k_f$** 限制。$k_f$ 通过 Sherwood 数与 Reynolds 数关联，依赖**管径**和**流态**。这就解释了 1990 年代前的现场观察——**管径越小、流速越快，余氯衰减越快**。

该模型已集成进 **EPANET** 软件，可对复杂管网做动态水质仿真。论文用 South Central Connecticut Regional Water Authority 的 **Cherry Hill/Brushy Plains** 服务区数据（9 个采样点、53 小时）做验证。

---

## 3. 论文解决了什么问题

`[原文]` PDF Introduction (p.803–804) 明确写出的「pre-1994 文献空白」：

| 1994 年之前的状况 | 本论文解决的问题 |
| --- | --- |
| Clark et al. (1993) 已经证明余氯在不同位置/不同时刻**变化大**，但**没有解释机理** | 提出 mass-transfer-based 模型，给出可预测的物理框架 |
| Wable et al. (1991) 发现**管内 decay rate 比同水样在 flask 内快若干倍** —— 说明管壁参与反应，但**没有定量模型** | 显式引入 wall reaction 项 $k_w$，并用 film resistance model 处理传质 |
| Hunt & Kroon (1991) 用**每根管一个独立 $k_b$** 来拟合观测，发现"小管需要更大的 $k_b$" —— 但**用大量参数硬拟合**，缺机理 | 用 mass-transfer 框架自然解释「小管 decay 快」，**全网只需 1 个 $k_b$ + 1 个 $k_w$**（parsimony） |
| Biswas et al. (1993) 在单根管 steady-state 给出 bulk + radial diffusion + wall reaction 模型，**但限于稳态、单管** | 推广到**非稳态、复杂管网、湍流 + 层流共存** |
| 缺少能跑复杂管网动态水质仿真的通用工具 | 把模型 + DVEM 数值方法集成进 **EPANET** |

---

## 4. 用了什么方法

### 4.1 模型框架 `[原文]` p.804（"MODEL DEVELOPMENT" 节）

假设：

- 余氯沿管段**一阶**衰减
- 反应同时发生在 **bulk flow** 和 **pipe wall**
- 壁面反应受 **film resistance mass transfer** 限制
- 忽略**轴向 dispersive flux**（典型工况下可忽略）
- 忽略**壁面物质向 bulk 输送**这条机制（"demands significantly more information"）

### 4.2 关键公式 `[原文]` p.804–805（Eq 1–10）

**沿管段的一维守恒方程**（Eq 1）：

$$\frac{\partial c}{\partial t} = -u\frac{\partial c}{\partial x} - k_b c - \frac{k_f}{r_h}(c - c_w)$$

**壁面质量平衡**（假设壁面浓度准稳态，Eq 2）：

$$k_f(c - c_w) = k_w c_w$$

→ 解出 $c_w$ 代入 Eq 1，得到**简洁形式**（Eq 3）：

$$\boxed{\frac{\partial c}{\partial t} = -u\frac{\partial c}{\partial x} - k_b c - \frac{k_w k_f}{r_h(k_w + k_f)}c}$$

对网络第 $i$ 根管段（Eq 9–10）：

$$\frac{\partial c_i}{\partial t} = -u_i\frac{\partial c_i}{\partial x_i} - K_i c_i, \quad K_i = k_b + \frac{k_w k_f}{r_{h,i}(k_w + k_f)}$$

**关键无量纲数**（Eq 4–8）：

$$k_f = \mathrm{Sh}\cdot \frac{D}{d}$$

$$\mathrm{Sh} = \begin{cases} 0.023\,\mathrm{Re}^{0.83}\,\mathrm{Sc}^{0.333}, & \mathrm{Re} > 2{,}300 \\[4pt] 3.65 + \dfrac{0.0668\,(d/L)\,(\mathrm{Re}\,\mathrm{Sc})}{1 + 0.04[(d/L)(\mathrm{Re}\,\mathrm{Sc})]^{2/3}}, & \mathrm{Re} < 2{,}300 \end{cases}$$

$$\mathrm{Re} = \frac{ud}{\nu}, \quad \mathrm{Sc} = \frac{\nu}{D}$$

> 关于水力半径：PDF p.804 写 "$r_h$ = hydraulic radius of pipe (one half the pipe radius)"，即 $r_h = d/4$（满管圆管）。

**节点边界条件**（Eq 11）：完全瞬时混合假设。
**储水罐模型**（Eq 12–13）：完全混合、可变体积反应器。

### 4.3 数值方法 — **DVEM（Discrete Volume Element Method）** `[原文]` p.808

不是有限体积也不是 method of characteristics，而是 Rossman 等 1993 年在 *J. Water Resour. Plng. Mgmt.* 发表的 **DVEM**。要点：

- 每个水力时段内，把每根管段按其体积、流速、最短传输时间分成若干 segment；
- 每个 segment 当作一个完全混合反应器；
- 每个 timestep 先做 segment 内反应，再向下游 segment 传输；
- 接入 junction 时与从其他管来的水流瞬时混合；
- 水力条件变化时重新分段。

这套 DVEM 后来就成了 EPANET water quality engine 的核心算法。

### 4.4 案例验证流程 `[原文]` p.809–814

**两阶段校准**：

1. **水力校准（用 fluoride 作 conservative tracer）**：
   - 8/13 9:00 a.m. 关闭 Saltonstall 厂的 fluoride 投加
   - 调整节点用水量 + 部分管段粗糙度系数，使模拟 fluoride 序列与实测一致
   - 校准好坏在 Figs. 4–7（PDF p.810–812）展示
2. **水质校准**：
   - $k_b$ **独立**由 SCCRWA 实验室 beaker test 测得（不调）
   - $k_w$ 在 0.15–0.45 m/day 范围内手动 sweep，**没有用 formal optimization**
   - 与 8 个节点的实测 chlorine 对比

---

## 5. 测了什么、在哪测、测多久（已大幅修正）

`[原文]` p.809–812

| 维度 | 内容 |
| --- | --- |
| 网络 | **Cherry Hill/Brushy Plains Service Area**, SCCRWA, 康涅狄格州 |
| 服务区规模 | 5.2 km²（2 平方英里），几乎全为住宅区 |
| 平均用水 | 20.2 L/s (0.46 mgd) |
| 干管管径 | 20.3 cm (8 in) 与 30.5 cm (12 in) |
| 水源 | Saltonstall 处理厂 |
| 泵站 | Cherry Hill Pump Station，标称 61.3 L/s (1.4 mgd) |
| 水塔 | Brushy Plains Tank，容积 3,800,000 L (1,000,000 gal) |
| 泵控制 | 水位低于 17.1 m → 开；高于 19.8 m → 关 |
| 采样日期 | **1991 年 8 月 13–15 日** |
| 采样点 | 9 个：1 个泵站、1 个水塔、7 个消火栓 |
| 采样频次 | 每条 1.5–2 h，整个 circuit 每 ~3 h 重复一轮 |
| 观测时长 | **53 h** |
| 总样本数 | **181 对**（chlorine + fluoride） |
| 进水 chlorine | 维持 **1.1 mg/L** |
| **测量方法（关键 update）** | **混合方法**：泵站 + 水塔用**连续电化学余氯分析仪**（Rosemount Model 4024 + free chlorine 特定膜电极 90243-116）；其余 7 个 hydrant 取 grab samples 用 **DPD 比色法**（Hach Model 46700-05） |
| Fluoride 测量 | 水塔用 ion-selective electrode 连续监测；其他点用 SCCRWA 实验室离子电极 grab samples |

---

## 6. 得出了什么结论

`[原文]` p.815–818 (Analysis + Summary)

### 6.1 校准结果（关键数字）

- **$k_b = 0.55$ /day**（实验室 beaker test 独立测定）
- **$k_w \in [0.15, 0.45]$ m/day**（网络拟合的合理区间）
- **RMSE**：
  - $k_w = 0.45$ m/day → **0.186 mg/L**
  - $k_w = 0.15$ m/day → **0.211 mg/L**
- 高 $k_w$ 平均误差小，但**对节点 11/19/25 的峰值匹配较差**——拟合存在权衡
- **拟合好的节点**：3, 6, 11, 19, 25（这些节点水力学刻画清晰）
- **拟合差的节点**：10, 28, 34（位于人口稀疏的死端，需水量估计困难，水力校准本身就差——参见 §4.4 Figs. 4–7）

### 6.2 反应贡献分解 `[原文]` p.817 Fig 14

| 损失来源 | $k_w = 0.45$ m/day | $k_w = 0.15$ m/day |
| --- | --- | --- |
| Pipe wall | **67%** | 48% |
| Bulk flow | 12% | 19% |
| Tank | 21% | 33% |

→ **wall reaction 在这套管网里占主导**（不论 $k_w$ 取高还是低）。

### 6.3 反应限制机制 `[原文]` p.816 Fig 13

- $k_w = 0.15$ m/day：曲线随流速基本水平 → **wall rate limited**（反应是瓶颈，传质富余）
- $k_w = 0.45$ m/day：曲线随流速明显上升 → **mass-transfer limited**（传质是瓶颈）

### 6.4 工程结论

- 在该系统，**改水塔操作（缩短水龄）作用有限**——因为 wall 占 67% 而 tank 只占 21%
- **管道清洗 / 替换** 在这里更有效
- 模型**强烈依赖于水力刻画的质量**：水力差的位置（死端）模型也差

### 6.5 摘要式结论 `[原文]` p.815（"SUMMARY AND CONCLUSIONS"）

1. 双段一阶 + mass transfer 模型能解释"小管/高速 → 高 decay"
2. 仅需估计两类 rate constants：$k_b$, $k_w$
3. SCCRWA 案例 53 h × 8 点验证，在水力清晰处吻合好
4. **强调先要拿到准确的水力学信息**才能跑水质模型
5. **承认局限**：单一 $k_w$ 用于全网未必合适，建议未来研究 $k_w$ 与管龄/管材/生物膜/腐蚀的关系

---

## 7. 关键公式 / 符号（论文 Appendix II Notation，完整版）

| 符号 | 含义 | 单位 |
| --- | --- | --- |
| $c$ | bulk flow 浓度 | M L⁻³ (mg/L) |
| $c_w$ | wall 浓度 | M L⁻³ |
| $D$ | molecular diffusivity | L² T⁻¹ |
| $d$ | pipe diameter | L |
| $K$ | overall decay constant | T⁻¹ |
| $k_b$ | bulk decay rate constant | T⁻¹ |
| $k_f$ | mass-transfer coefficient | L T⁻¹ |
| $k_w$ | wall decay rate constant | **L T⁻¹**（注意单位！） |
| $L$ | pipe length | L |
| $M$ | 节点外部 mass inflow | M T⁻¹ |
| $q$ | flow rate | L³ T⁻¹ |
| $\mathrm{Re}$ | Reynolds number | 无量纲 |
| $r_h$ | hydraulic radius (= d/4) | L |
| $S$ | 节点外部 flow rate | L³ T⁻¹ |
| $\mathrm{Sc}$ | Schmidt number | 无量纲 |
| $\mathrm{Sh}$ | Sherwood number | 无量纲 |
| $u$ | flow velocity | L T⁻¹ |
| $V$ | tank volume | L³ |
| $\nu$ | kinematic viscosity | L² T⁻¹ |

> 来源：PDF Appendix II（p.820）。

---

## 8. 与本项目的关联

本项目是「**不确定性感知的供水管网余氯模型校准**」。Rossman 1994 与项目各模块的对应：

| 项目模块（README §4.3） | 关联点 |
| --- | --- |
| **T2 模型搭建** | 我们 demo 用的就是 Eq 3。`src/01_demo_wntr.py` 里 `bulk_coeff` 与 `wall_coeff` 两个开关对应 $k_b$ 与 $k_w$ |
| **T2 — 数值方法** | EPANET 引擎跑的就是 DVEM。我们不用自己写 |
| **T3 数据组织** | Cherry Hill 数据集（53 h, 181 对实测）是经典 benchmark；如能拿到原始数据可作为本项目可重复实验的对照 |
| **T4 确定性校准** | $k_b$ 独立 lab 测定 + $k_w$ 手动 sweep 范围——这正是 baseline 校准的范式；可作为我 Plan A 的最简对照 |
| **T5 不确定性感知校准** | **这正是本项目要补的 gap**：1994 paper 把校准当作确定性 + 手动 sweep，没考虑测量不确定性、没给出 $k_w$ 的后验分布。本项目用 MC / Bayesian 直接补这条 |
| **Methodology 章节** | 可直接引用 Eq 3 + DVEM 作为 EPANET 水质方程的来源 |
| **Discussion** | 「水力刻画差的点 → 水质模型也差」这条观察可呼应「sensor placement / 采样设计影响 calibration 质量」 |

---

## 9. 可借鉴 / 可批判之处

### 9.1 可借鉴

- **公式紧凑**：Eq 3 把传质 + 反应揉成一条等价一阶项，对工程师友好
- **fluoride 作 conservative tracer 先校水力、再校水质**：两阶段校准范式非常清晰
- **$k_b$ 用 lab beaker test 独立测定**：把校准变量减为 1 个 $k_w$，避免参数互相补偿
- **承认局限**：明确写出"水力差则水质差""死端节点拟合差"、"单一 $k_w$ 不一定全网都对"
- **贡献分解（Fig 14）思路**：可在我们的论文里用同样的图说明 wall/bulk/tank 各自占比

### 9.2 可批判（也是我们要改进的）

| 1994 论文的局限 | 本项目对应的补强 |
| --- | --- |
| 校准是**确定性的手动 sweep**（仅在 0.15–0.45 之间试几个值） | T5：用 MC + Bayesian 给出 $k_w$ 的**后验分布**，而不是单点估计 |
| 没有考虑**观测不确定性**（RMSE 报了，但没把 DPD/电化学探头误差作为模型输入） | T5：把 D5 (Guigues 2022) 的 6–38% 不确定度做成测量误差先验 |
| 单一 $k_b$、$k_w$ 应用于全网 | T4 之后：考虑分管径段或分管材的 $k_w$（呼应 A4 Hallam 2002 的实测分布） |
| 仅一个 SCCRWA 子区域案例 | 本项目：Net1 + Net3 (+BWSN 若可) 对照 |
| 校准 $k_w$ 时未做敏感性分析 | T4 校准前用 SALib (Morris/Sobol) 做参数可识别性分析 |
| 反应贡献 67% wall 的结论建立在**只跑了两个 $k_w$ 值**上 | 用 MC 重新采样 $k_w$ 区间，给出贡献分解的不确定性区间 |
| 没看测量误差怎么影响校准 | T5 论文核心：测量误差 → 校准参数 → 节点低于阈值的概率 |

---

## 10. 已答复事项 + 仍需补充

### 10.1 已答复（之前的 `[需补]` 项）

- ✅ Eq 推导 → §4.2
- ✅ 数值方法 = **DVEM**（不是 method of characteristics）→ §4.3
- ✅ 测量方法 = 连续 Rosemount 电化学 + DPD Hach 比色法（**混合**）→ §5
- ✅ $k_b$ 具体取值 = **0.55 /day**，方法 = beaker test → §6.1
- ✅ $k_w$ 取值范围 = **0.15–0.45 m/day** → §6.1
- ✅ RMSE = **0.186 / 0.211 mg/L** → §6.1
- ✅ 哪些点拟合差 = **10, 28, 34（死端，水力差）** → §6.1
- ✅ 作者承认的局限 → §6.5 + §9.2

### 10.2 仍需补充 / 下一步

- [ ] 把 Cherry Hill 网络拓扑文件（如果有 EPANET `.inp` 版本流传）找出来，复刻该案例做不确定性校准对照
- [ ] 通读 Clark et al. 1993（contaminant propagation）与 Grayman & Clark 1993（tank effect）以理解前置工作
- [ ] 通读 Hallam et al. 2002（A4），对照 SCCRWA 推出的 $k_w \approx 0.15$–$0.45$ m/day 是否仍在该论文给出的实测分布内
- [ ] 通读 Rossman, Boulos, Altman 1993 (DVEM 原文)，必要时在 Methodology 简述 DVEM
- [ ] 通读 EPANET 2.2 Manual（B2），核对 EPANET 现行 implementation 是否仍是 DVEM

---

## 11. 思考题（精读后更新）

1. **关于 mass-transfer 限制在 Net1 demo 的表现**：Net1 管径 6–18 in（与 Cherry Hill 8/12 in 同量级），如果开 wall decay 并设 $k_w$ 在 0.15–0.45 m/day 区间，应能复现 Fig 13 的 transition；这可以是 Week 3 baseline 的一组对照实验。
2. **关于不确定性的传播**：如果观测有 5–10% 相对误差（D5 给出的实测数），$k_w$ sweep 的 0.186 vs 0.211 mg/L 这种 RMSE 差异**可能在噪声水平内**——意味着 1994 paper 选哪个 $k_w$ 都"无法被数据拒绝"。这是 T5 的核心 motivation：**确定性校准在嘈杂数据下给出的"最佳值"可能不显著优于一个区间**。
3. **关于 wall 67% 的稳健性**：如果用 MC 在 $k_w \in [0.15, 0.45]$ 均匀采样 1000 次，wall 占比的 90% CI 可能横跨 48–67%——这一区间是否会改变"应优先做管道清洗"的工程建议？
4. **关于 Cherry Hill 数据可获取性**：是否有公开 `.inp` 版本？BWSN 不是这一个网络，需要单独找。可问导师或邮件 SCCRWA archives。

---

## 12. 引用模板

**Vancouver 风格**：

> Rossman LA, Clark RM, Grayman WM. Modeling chlorine residuals in drinking-water distribution systems. *J Environ Eng*. 1994;120(4):803–820. doi:10.1061/(ASCE)0733-9372(1994)120:4(803)

**Harvard 风格**：

> Rossman, L.A., Clark, R.M. and Grayman, W.M. (1994) 'Modeling chlorine residuals in drinking-water distribution systems', *Journal of Environmental Engineering*, 120(4), pp. 803–820. doi: 10.1061/(ASCE)0733-9372(1994)120:4(803).

**BibTeX**（拟写入 `../../thesis/refs.bib`）：

```bibtex
@article{Rossman1994ChlorineResiduals,
  author    = {Rossman, Lewis A. and Clark, Robert M. and Grayman, Walter M.},
  title     = {Modeling Chlorine Residuals in Drinking-Water Distribution Systems},
  journal   = {Journal of Environmental Engineering},
  volume    = {120},
  number    = {4},
  pages     = {803--820},
  year      = {1994},
  doi       = {10.1061/(ASCE)0733-9372(1994)120:4(803)},
  publisher = {American Society of Civil Engineers}
}
```

---

## 13. 修正记录（2026-05-19 通读 PDF 后）

| # | 旧版（基于摘要 + 推断） | 新版（基于 PDF 原文） |
| --- | --- | --- |
| 1 | §4.3 数值方法 = "method of characteristics 或 finite volume" `[推断]` | DVEM (Discrete Volume Element Method)，Rossman et al. 1993 JWRPM `[原文]` |
| 2 | §5 测量方法 = "1994 年大概率是 DPD" `[推断]` | **混合**：泵站 + 水塔用 Rosemount 4024 + 膜电极（连续电化学）；7 个 hydrant 用 Hach 46700-05 DPD 比色法 `[原文]` |
| 3 | §5 "53 h, 9 点" | 同上，且补充：**181 对**测值、Aug 13–15 1991、Cherry Hill/Brushy Plains 子区 `[原文]` |
| 4 | §5 "$k_b$、$k_w$ 具体值 `[需补]`" | $k_b = 0.55$ /day（lab beaker test）；$k_w \in [0.15, 0.45]$ m/day（网络 sweep）`[原文]` |
| 5 | §6 "good agreement, 具体 RMSE 待补" | RMSE = 0.186 mg/L（$k_w = 0.45$）vs 0.211 mg/L（$k_w = 0.15$）`[原文]` |
| 6 | §4.2 Eq 形式 `[推断]` | **与论文 Eq 3 完全一致** —— 推断正确 ✅ |
| 7 | §4.2 $k_f$ 的 Sherwood 数关联 `[推断]` | 与论文 Eq 4–8 一致 —— 推断正确 ✅ |
| 8 | 全文 8 节缺反应贡献分解数据 | 已补：wall 67% / bulk 12% / tank 21%（at $k_w = 0.45$）`[原文]` |
| 9 | 全文 缺 wall-rate vs mass-transfer-rate 转折机制 | 已补 §6.3：低 $k_w$ wall rate limited；高 $k_w$ mass-transfer limited（Fig 13）`[原文]` |
| 10 | 全文 缺"参数 parsimony"明确论述 | 已补 §3 / §9.2：作者明确说 "in the spirit of model parsimony they were kept constant" `[原文]` |
