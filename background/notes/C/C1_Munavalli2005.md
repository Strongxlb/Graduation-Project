# C1 — Munavalli, Mohan Kumar (2005) 精读笔记

> 配套文件：[`../../Literature/literature.md`](../../Literature/literature.md) §C1、[`../../README.md`](../../README.md)
> PDF 路径：[`../../Literature/C-水质模型校准（确定性方法）/C1-Munavalli, Kumar (2005). Water quality parameter estimation in a distribution system under dynamic state.pdf`](../../Literature/C-水质模型校准（确定性方法）/C1-Munavalli, Kumar (2005). Water quality parameter estimation in a distribution system under dynamic state.pdf)
>
> **来源标签**（更新于 2026-05-19，已通读 PDF 12 页）：
> - `[原文]` 直接出自论文 PDF
> - `[元数据]` 来自 CrossRef / 期刊页眉
> - `[推断]` 项目延伸推断
> - `[需补]` 待核对项

---

## 0. 元数据（已验证）

| 字段 | 内容 | 来源 |
| --- | --- | --- |
| Title | Water quality parameter estimation in a distribution system under dynamic state | PDF |
| Authors | **G. R. Munavalli**, **M. S. Mohan Kumar** | PDF |
| Affiliation | Dept. Civil Eng., Indian Institute of Science, Bangalore | PDF |
| Journal | *Water Research* 39, 4287–4298 | PDF |
| 接收 / 接受 | Received 21 Aug 2003; revised 23 Mar 2005; accepted 27 Jul 2005 | PDF |
| DOI | `10.1016/j.watres.2005.07.043` | PDF 页眉 `[元数据]` |
| 页数 | **12 页** | PDF |
| 优先级 | **P0** | literature.md |
| 状态 | `read` | — |

**前置工作**：Munavalli & Kumar (2003) 同一 inverse model 的 **稳态** 版（JWRPM）；本文扩展至 **动态水力 + 动态水质** `[原文]`。

---

## 1. Abstract（原文要点）

`[原文]` 管网几何复杂、流量时变、氯反应机理多样，使余氯预测困难。bulk decay 可实验测定，**wall reaction 须由现场测量与模拟对比反推**。本文提出 **simulation–optimization** 工具：基于 **weighted least squares + Gauss–Newton** 自动校准。应用于真实系统表明：**测点数量、质量与位置** 对参数估计至关重要。

---

## 2. 中文摘要

本文在 Lagrangian 前向水质模型上，构建 **动态状态** 下的氯衰减参数反演框架。支持 overall / bulk+wall 多种反应形式（一阶 bulk、一阶或零阶 wall、二阶 bulk 等），用加权最小二乘目标函数与 Gauss–Newton 迭代替代手工 trial-and-error。Bangalore 合成网验证可快速收敛；Brushy Plain（EPANET 例网）与 Fairfield zone 3 现场网应用表明：全局/分区 wall 参数可自动估计，并与 Rossman et al. (1994) 手工校准区间一致。

---

## 3. 问题与动机

| 痛点 | 说明 | 来源 |
| --- | --- | --- |
| wall 参数不可测 | bulk 可 bottle test；overall/wall 只能校准 | `[原文]` §1 |
| trial-and-error 低效 | Clark et al. (1995) 等手工法 tedious | `[原文]` |
| 动态工况 | 此前 Zeirolf (1998)、Al-Omari (2001) 等多为稳态或简化 | `[原文]` |
| 多动力学选择 | 需判断一阶/零阶 wall、二阶 bulk 等何者适用 | `[原文]` §5 |

---

## 4. 方法

### 4.1 前向模型

- **水力**：Niranjan Reddy (1994) 静态模型扩展为 **extended period simulation** `[原文]` §2.1.1  
- **水质**：一维 advection-dominated；节点 **流量加权瞬时混合** `[原文]` Eq.(1)–(8)  
- **反应形式**（7 种组合）：overall 一阶；bulk 一阶 + wall 一阶/零阶；bulk 二阶 + wall 一阶/零阶；含 limiting concentration $C_L$ 的两组分二阶 bulk 等 `[原文]` §2.1.2  

Wall 一阶项含 Rossman (2000) 的 **mass transfer coefficient** $k_f$。

### 4.2 反演 / 优化

**目标函数**（加权最小二乘）：

$$J = \sum_{j=1}^{N_m} w_j \left( C_{obs,j} - C_{sim,j}(\theta) \right)^2$$

`[原文]` §2.2 — $w_j$ 为测点权重；$\theta$ 为待估反应参数（global 或 zoned）。

- **求解**：Gauss–Newton + **parameter perturbation** 求灵敏度 `[原文]` §2.2.2  
- **输出**：参数点估计、95% 置信带、校准统计（RMS、$R^2$ 等）  

### 4.3 与 EPANET 关系

`[推断]` 自研 Lagrangian 前向模型，**非 EPANET 内核**；但 Example 1 直接采用 **EPANET 手册 Brushy Plain 网** 与 Rossman et al. (1994) 观测数据。

---

## 5. 数据与案例

| 案例 | 网络 | 要点 | 来源 |
| --- | --- | --- | --- |
| 验证网 | Bangalore（Datta & Sridharan 1994） | 二阶 bulk + 分区 wall；合成数据反演收敛至真值 | `[原文]` §3.1 |
| Example 1 | Brushy Plain（EPANET 例） | $C_{in}=1.15$ mg/L；$k_{b,1}=0.55$ d⁻¹；8 节点 55 h 观测 | `[原文]` §4.1 |
| Example 2 | Fairfield zone 3 | 126 pipes, 111 nodes；石棉水泥大管径；$k_b=1.16$ d⁻¹；Rossman 提供数据 | `[原文]` §4.2 |

**Example 1 关键结果** `[原文]` Table 4–5：

| 参数 | 估计值 | 单位 |
| --- | --- | --- |
| $k_0$ (overall) | 2.5169 | d⁻¹ |
| $k_{w,1}$ | **0.3654** | m/d |
| $k_{w,0}$ | 201.61 | mg/m²/d |

Rossman et al. (1994) 手工校准 $k_{w,1}$ 范围 **0.15–0.45 m/d**；本文自动估计 **0.3654 m/d** 落在区间内。RMS 约 **0.192 mg/L**（对应下界 0.15 m/d）。

**分区 wall**（按管径两组）：大管径组 $k_w \approx 0.33$ m/d，小管径 **0.50 m/d** — 小管 wall 贡献更大，与 Rossman et al. (1994) 一致 `[原文]` §4.1.2。

**Example 2**：overall $k_0=1.25$ d⁻¹，略高于 bulk 1.16 d⁻¹ → wall 贡献可忽略；分 wall 模型时 wall 参数 **negligibly small** `[原文]` §4.2。

---

## 6. 结论（作者）

1. simulation–optimization 可替代 trial-and-error，收敛快。  
2. 可估计 global / zoned 的 overall、一阶 wall、零阶 wall 参数。  
3. 校准统计与参数不确定性有助于 **选择反应动力学形式**。  
4. 测点 **数量、质量、位置** 影响可识别性。  

---

## 7. 符号速查

| 符号 | 含义 | 单位 |
| --- | --- | --- |
| $k_0$ | overall 一阶衰减 | d⁻¹ |
| $k_{b,1}$, $k_{b,2}$ | bulk 一阶 / 二阶 | d⁻¹, L/mg·d |
| $k_{w,1}$, $k_{w,0}$ | wall 一阶 / 零阶 | m/d, mg/m²/d |
| $k_f$ | 传质系数 | m/d |
| $C_L$ | 氯下限浓度 | mg/L |

---

## 8. 与本项目的关系

| 项目环节 | 可借鉴点 |
| --- | --- |
| **确定性校准 baseline** | WLS + Gauss–Newton 是 C 类「标准做法」参照；本项目可在 WNTR 上实现类似目标函数 |
| **wall vs bulk 可识别性** | Example 1 显示 wall 主导时 $k_0 \gg k_b$；与 A1/A4 机理一致 |
| **测点设计** | 作者强调测点布局 — 对接 D 类测量误差 + 未来传感器位置讨论 |
| **与 C2 对照** | C1 点估计；C2 说明同一参数多解时 MCS 输出仍窄 — 需 **Bayesian / 多参数联合**（E 类） |
| **动态扩展** | 本文 dynamic state 对应本项目 extended period 校准需求 |

### 可参考要点（写论文 / 做实验时可直接引用）

1. **T4 baseline 实现**：在 WNTR 上实现 **加权最小二乘** $J=\sum w_j(C_{obs}-C_{sim})^2$，用 `scipy.optimize.least_squares` 或 Gauss–Newton；C1 是 Plan A **确定性校准的 direct template**。
2. **文献数值对照**：Brushy Plain 自动得 $k_{w,1}=0.3654$ m/d，落在 Rossman (1994) 手工 **0.15–0.45** m/d — baseline 结果应与此 **同量级**。
3. **权重 $w_j$**：结合 D2，设 $w_j=1/\sigma^2$，$\sigma=0.02$ mg/L — Methodology 写「C1 目标函数 + D2 误差权重」。
4. **测点设计（M1 报告）**：引用「测点数量、位置影响参数估计」— 合成数据实验可故意 **减少节点** 展示 identifiability 下降。
5. **Extended period**：校准用 **55 h+ 动态水力**（与 demo 24 h 对比）— Week 3–4 扩展仿真时长时可引用 C1。
6. **Global vs zoned**：Example 1 按 **管径分区** $k_w$ — 若 Net1 材质信息不足，至少做 global vs 2-zone sensitivity。
7. **Discussion 局限**：C1 未建模 DPD 误差 → 自然过渡到 **T5 不确定性感知**（C2 + E1 + D2）。

---

## 9. 批判性阅读

**优点**：自动校准、多动力学、真实网验证、给出置信带。  
**局限**：
- 自研模型，与 WNTR/EPANET 方程细节需逐项对照 `[推断]`  
- 假设 Gaussian 型残差 + WLS，**未显式建模 DPD 测量误差** `[推断]`  
- 分区仅按管径/水源分组，未考虑管材年龄 `[推断]`  
- Fairfield 数据经 Rossman 私人通信， reproducibility 有限 `[原文]` Acknowledgement  

---

## 10. 待办

- [ ] 核对 literature.md 中 DOI 是否为 `07.043`（PDF 页眉）  
- [ ] 将 Brushy Plain 参数映射到 WNTR `01_demo_wntr.py` 做 WLS 试跑  
- [ ] 读 Munavalli (2003) 稳态版对比 dynamic 扩展差异  

---

## 11. 思考题

1. 若观测噪声 $\sigma=0.05$ mg/L，WLS 权重 $w_j=1/\sigma^2$ 应如何写入本项目 likelihood？  
2. Example 2 wall 可忽略时，继续拟合 $k_w$ 是否 ill-posed？  
3. Gauss–Newton 对非凸目标（多 zone $k_w$）会否陷入局部最优？  

---

## 12. 引用模板

**Vancouver**：

> Munavalli GR, Mohan Kumar MS. Water quality parameter estimation in a distribution system under dynamic state. *Water Res*. 2005;39(17):4287–4298. doi:10.1016/j.watres.2005.07.043

**BibTeX**：

```bibtex
@article{Munavalli2005DynamicWQ,
  author  = {Munavalli, G. R. and Mohan Kumar, M. S.},
  title   = {Water quality parameter estimation in a distribution system under dynamic state},
  journal = {Water Research},
  volume  = {39},
  number  = {17},
  pages   = {4287--4298},
  year    = {2005},
  doi     = {10.1016/j.watres.2005.07.043}
}
```

---

## 13. 修正记录

| # | 原值 | 修正后 |
| --- | --- | --- |
| 1 | literature.md DOI `…07.022` | PDF 页眉为 **`10.1016/j.watres.2005.07.043`** — 建议更新 literature.md |
