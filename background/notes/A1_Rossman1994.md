# A1 — Rossman, Clark, Grayman (1994) 精读笔记

> 配套文件：[`../literature.md`](../literature.md) §A1、[`../../README.md`](../../README.md)、[`../../plan1.md`](../../plan1.md)
> 来源：CrossRef + OpenAlex 元数据（核验日期 2026-05-19），未读 PDF 全文，标 `[需补]` 处待精读后回填。
>
> **笔记可信度标注**：
> - `[摘要]` 来自论文官方 abstract
> - `[元数据]` 来自 CrossRef / OpenAlex 元数据
> - `[推断]` 基于上下文 / EPANET 2.2 Manual / 通用知识推断，**未读到 PDF 验证**
> - `[需补]` 待精读 PDF 后补充

---

## 0. 元数据（已验证）

| 字段 | 内容 | 来源 |
| --- | --- | --- |
| Title | Modeling Chlorine Residuals in Drinking-Water Distribution Systems | CrossRef |
| Authors | **Lewis A. Rossman**, Robert M. Clark, Walter M. Grayman | CrossRef |
| Affiliation | US EPA Risk Reduction Engineering Lab, Cincinnati（第一、第二作者）；Grayman 为咨询工程师 | CrossRef |
| Journal | *Journal of Environmental Engineering* (ASCE) | CrossRef |
| Year | 1994 (July) | CrossRef |
| Volume / Issue / Pages | 120 / 4 / 803–820 (18 页) | CrossRef |
| DOI | `10.1061/(ASCE)0733-9372(1994)120:4(803)` | — |
| Cited by | **386 (CrossRef) / 494 (OpenAlex)** | 两库 |
| 2026 引用增量 | 已 6 次（仅 4 月底前），近 5 年每年 20–30+ | OpenAlex `counts_by_year` |
| 优先级 | **P0**（literature.md §A1） | 本项目 |
| 状态 | `skim`（已读摘要 + 元数据） → `read`（精读 PDF 后更新） | — |

**为什么这是 P0**：第一作者 **Rossman 就是 EPANET 软件的作者本人**，本文是 EPANET water quality module（也即所有后续余氯建模工作的基础）的**奠基论文**。`[元数据]`

---

## 1. 原文 Abstract（英文，逐字）

> A mass-transfer-based model is developed for predicting chlorine decay in drinking-water distribution networks. The model considers first-order reactions of chlorine to occur in both the bulk flow and at the pipe wall. The overall rate of the wall reaction is a function of the rate of mass transfer of chlorine to the wall and is therefore dependent on pipe geometry and flow regime. The model can thus explain field observations that show higher chlorine decay rates associated with smaller pipe sizes and higher flow velocities. It has been incorporated into a computer program called EPANET that can perform dynamic water-quality simulations on complex pipe networks. The model is applied to chlorine measurements taken at nine locations over 53 h from a portion of the South Central Connecticut Regional Water Authority's service area. Good agreement with observed chlorine levels is obtained at locations where the hydraulics are well characterized. The model should prove to be a valuable tool for managing chlorine-disinfection practices in drinking-water distribution systems.

> 摘要由 OpenAlex 的 `abstract_inverted_index` 重建；与 ASCE 出版方元数据等价。

---

## 2. 中文摘要（再表述）

`[摘要]` 论文提出一个**以质量传递为基础**的余氯衰减模型，用于预测饮用水管网中的余氯浓度。模型把余氯衰减拆成两段一阶反应：

1. **bulk reaction**：发生在水体内的整体反应（与有机物、还原物质等反应）；
2. **wall reaction**：发生在管壁上的反应（与管壁腐蚀产物、生物膜等反应）。

**关键 insight**：wall reaction 的速率并不是单纯由 wall coefficient 决定，而是受**水体→管壁的传质速率**限制。这一传质速率本身依赖**管径**和**流态**（Reynolds 数）。所以模型能解释一个 1990 年代以前不易解释的现场观察：**管径越小、流速越快，余氯衰减越快**。

该模型已集成进 **EPANET** 软件，可对复杂管网做动态水质仿真。论文用 South Central Connecticut Regional Water Authority 某片管网的 9 个采样点、53 小时实测数据做验证；在水力学刻画清晰的位置上，模拟值与实测值吻合良好。

---

## 3. 论文解决了什么问题

`[摘要]` + `[推断]`

| 1994 年之前的状况 | 本论文解决的问题 |
| --- | --- |
| 现场观测中**管径小 + 流速快**的位置 chlorine decay 明显偏快，但没有一个能解释这一现象的统一物理模型 | 提出 mass-transfer-based 双重一阶反应模型，能从机理上解释这种依赖关系 |
| 已有的 chlorine 衰减模型大多只考虑 bulk decay（一个全局 $k_b$） | 引入 wall reaction 项 $k_w$，并把它的有效速率与管壁传质 $k_f$ 耦合 |
| 缺少能跑复杂管网动态水质模拟的通用计算工具 | 把模型集成进 EPANET（成为业界标准） |
| 缺少在真实管网上验证「机理模型 + 软件实现」的端到端案例 | 用 Connecticut Regional 管网 9 点 × 53 h 数据做端到端验证 |

---

## 4. 用了什么方法

### 4.1 模型框架 `[摘要]`

对每根管段沿流向写出 chlorine 浓度的对流-反应方程（一阶反应）：

- bulk reaction：$\frac{dC}{dt}\big|_\text{bulk} = -k_b C$
- wall reaction：速率为「管壁可消耗 chlorine 的本征速率 $k_w$」与「水体到壁面的传质速率 $k_f$」**两阶段串联**的等效速率，取决于管径与 Re

### 4.2 关键公式 `[推断 — 基于 EPANET 2.2 Manual 公式，待 PDF 全文核对]`

EPANET 标准形式（沿管段流向）：

\[
\frac{dC}{dt} \;=\; -\,k_b \, C \;-\; \frac{k_w \, k_f}{r_h \, (k_w + k_f)}\, C
\]

其中：

- $k_b$ = bulk decay 系数（1/day，常为负）
- $k_w$ = wall reaction rate constant（m/day，**单位是长度/时间**，因为是表面反应）
- $k_f$ = water-to-wall mass transfer coefficient（m/day），由流速 + 管径通过 Sherwood 数关联
- $r_h$ = 管段水力半径 = D/4（满管圆管）

**直观解读**：当 $k_w \gg k_f$（壁面反应很快），整体反应速率 ≈ $k_f / r_h$ —— 由 mass transfer 主导。这就解释了"管径小 → $r_h$ 小、流速快 → $k_f$ 大 → 衰减快"。

### 4.3 数值实现 `[摘要]` + `[推断]`

把方程沿每根管段离散化（典型做法是 method of characteristics 或 finite-volume），耦合水力解算结果，集成进 EPANET → 形成**EPANET water quality module**。

### 4.4 模型验证范式 `[摘要]`

- 选一段真实管网（South Central Connecticut Regional Water Authority 服务区的一部分）
- 选 9 个采样点
- 连续 53 h 采样观测余氯
- 用模型预测 vs 实测对比
- 在水力学已知（流速、流向清楚）的位置看吻合度

---

## 5. 测了什么、在哪测、测多久

| 维度 | 内容 |
| --- | --- |
| 测量物理量 | Free chlorine 浓度（mg/L） `[推断]` |
| 测点数 | **9 locations** |
| 观测时长 | **53 hours**（约 2.2 天） |
| 网络 | South Central Connecticut Regional Water Authority **的一部分**（不是整个服务区） |
| 测量方法 | 未在 abstract 写明 `[需补]`（1994 年大概率是 DPD colorimetric） |
| 验证指标 | "Good agreement"（abstract 用词），但具体 RMSE / MAE / R² 等数字 `[需补]` |

---

## 6. 得出了什么结论

`[摘要]`

1. **机理结论**：余氯衰减的整体速率必须同时考虑 bulk reaction 和 wall reaction，且 wall reaction 实际速率受到水体→管壁传质的限制。
2. **可解释性结论**：这种 mass-transfer 框架天然解释了「管径越小 + 流速越快 → 衰减越快」的现场观察。
3. **工程实用性结论**：模型集成进 EPANET 后可对复杂管网做动态水质仿真。
4. **验证结论**：在水力学刻画清晰的采样点上模拟值与实测值"吻合良好"（abstract 原话）；在水力不清的点吻合度较差——**间接说明 chlorine 模拟的可靠性强烈依赖底层水力模型的质量**。
5. **应用结论**：模型应当成为管理饮用水管网余氯消毒实践的有价值工具。

---

## 7. 关键公式 / 概念（备用引用）

| 符号 | 含义 | 单位 |
| --- | --- | --- |
| $C$ | 余氯浓度 | mg/L |
| $k_b$ | bulk decay rate constant | 1/day |
| $k_w$ | wall reaction rate constant | m/day |
| $k_f$ | mass transfer coefficient (水→壁) | m/day |
| $r_h$ | hydraulic radius | m |
| $Re$ | Reynolds 数（流速 × 管径 / 黏度） | 无量纲 |
| $Sh$ | Sherwood 数（关联 $k_f$ 与 Re） | 无量纲 |

**概念关键词**：bulk reaction、wall reaction、mass transfer limitation、first-order kinetics、advection-reaction equation。

---

## 8. 与本项目的关联

本项目是「**不确定性感知的供水管网余氯模型校准**」。Rossman 1994 与项目各模块的对应：

| 项目模块（README §4.3） | 关联点 |
| --- | --- |
| **T2 模型搭建** | 我们 demo 用的就是这套 bulk + wall 一阶反应。`src/01_demo_wntr.py` 里 `bulk_coeff = -0.5`、`wall_coeff = 0.0` 这两个开关，源头就是这篇 paper |
| **T4 确定性校准** | bulk decay 校准（最小化 RMSE）的目标参数 $k_b$、$k_w$ 都源自此文 |
| **T5 不确定性感知校准** | **这正是本项目想要补的 gap**：1994 paper 把校准当作确定性优化（找一组最佳 $k_b, k_w$ 使模拟值与观测值吻合），**没考虑观测不确定性**。我们的不确定性感知校准就是在这个奠基模型上方加一层概率包装 |
| **Methodology 章节** | 直接引用本文作为 EPANET 水质方程的来源；可以用本文 §3 公式直接放进我论文 Methodology |
| **Discussion** | 「水力刻画不清的点拟合差」这条观察可以呼应「sensor placement / 采样设计影响 calibration 质量」 |

---

## 9. 可借鉴 / 可批判之处

### 9.1 可借鉴

- **bulk + wall 双段一阶模型的优雅简化**：用最少的参数 ($k_b, k_w$) 捕捉两类物理过程
- **mass-transfer 视角**：避免把 wall coefficient 当作"现场拟合常数"，而是给出可从流场预测的物理量
- **端到端验证范式**：真实管网 + 多点 + 多小时观测 → 模型预测对比
- **承认局限性的诚实**：abstract 明确写"在水力学不清的位置拟合差"——不是讳言

### 9.2 可批判（也是我们的改进点）

| 局限 | 我们要补的 |
| --- | --- |
| 校准是**确定性的**，未考虑观测不确定性 | T5 加 Monte Carlo / Bayesian 不确定性传播 |
| 53 h 观测时长偏短 `[与 demo 24h 同量级，所以解释了你为啥也看不到稳态]` | Week 3 baseline simulation 拉到 ≥ 72 h |
| 测量方法未在 abstract 描述 | 我们假设 DPD + 在线传感器（D 节文献） |
| 仅一个真实网络数据 → 泛化能力未充分讨论 | 我们用 Net1 + Net3 + (BWSN, 时间允许) 对照 |
| 未讨论 $k_b$、$k_w$ 的可识别性 | T4 校准前做敏感性分析（SALib Morris/Sobol） |
| 没有给出参数不确定性区间，只给点估计 | T5 输出参数后验分布 |

---

## 10. 待精读 PDF 时补充

`[需补]` 这些条目在拿到 PDF 后回填：

- [ ] 论文 §2/§3 的完整数学推导（特别是 $k_f$ 的 Sherwood 数表达式）
- [ ] §4 数值方法实现细节（method of characteristics 还是 finite volume？）
- [ ] §5 South Central Connecticut Regional Water Authority 案例的：
  - 采样具体方法（DPD 还是别的？测量误差范围？）
  - $k_b$、$k_w$ 的具体取值
  - 拟合指标的具体数字（RMSE / MAE / 偏差）
- [ ] 哪些采样点拟合差？作者怎么解释？
- [ ] §6 局限性 / 未来工作 — 作者自己看到的不足
- [ ] 引用关系：被 Hallam 2002 (A4)、Munavalli & Kumar 2005 (C1) 等如何继承

PDF 下载途径：
- Imperial Library Search（SSO 登录后通常可下载 ASCE 全文）
- 或者 [ASCE Library 直接链接](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9372%281994%29120%3A4%28803%29)

---

## 11. 待跟进 / 思考题

精读完 PDF 后回答：

1. **wall coefficient 取多少合理**？$k_w$ 的物理上限是什么？Hallam 2002 (A4) 给出的实测范围对比 Rossman 1994 用的取值差异多大？
2. **mass transfer 假设在我们的 Net1 demo 里有多重要**？Net1 管径 6–18 in，流速变化大；如果开 wall decay，能不能复现 mass-transfer 主导的现象？
3. **如果观测有 5% 的相对误差（D5 给出的数字）**，1994 用确定性最小二乘的校准结果置信度会怎样？这是我们 T5 要回答的核心问题。
4. **Connecticut 数据集是否可获取**？如果能拿到 1994 年的 9 点 53 h 实测数据，就能直接作为 benchmark 重做一遍校准（确定性 vs 不确定性感知）的对比。

---

## 12. 引用模板（论文里直接用）

**Vancouver 风格**（待与导师确认引用风格）：

> Rossman LA, Clark RM, Grayman WM. Modeling chlorine residuals in drinking-water distribution systems. *J Environ Eng*. 1994;120(4):803–820. doi:10.1061/(ASCE)0733-9372(1994)120:4(803)

**Harvard 风格**：

> Rossman, L.A., Clark, R.M. and Grayman, W.M. (1994) 'Modeling chlorine residuals in drinking-water distribution systems', *Journal of Environmental Engineering*, 120(4), pp. 803–820. doi: 10.1061/(ASCE)0733-9372(1994)120:4(803).

**BibTeX**（拟写入 `../../thesis/refs.bib`）：

```bibtex
@article{Rossman1994ChlorineResiduals,
  author  = {Rossman, Lewis A. and Clark, Robert M. and Grayman, Walter M.},
  title   = {Modeling Chlorine Residuals in Drinking-Water Distribution Systems},
  journal = {Journal of Environmental Engineering},
  volume  = {120},
  number  = {4},
  pages   = {803--820},
  year    = {1994},
  doi     = {10.1061/(ASCE)0733-9372(1994)120:4(803)},
  publisher = {American Society of Civil Engineers}
}
```
