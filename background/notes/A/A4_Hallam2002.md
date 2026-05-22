# A4 — Hallam, West, Forster, Powell, Spencer (2002) 精读笔记

> 配套文件：[`../Literature/literature.md`](../Literature/literature.md) §A4、[`../../README.md`](../../README.md)  
> 前置阅读：[`A1_Rossman1994.md`](A1_Rossman1994.md)（wall+传质）、[`A3_Powell2000.md`](A3_Powell2000.md)（同组 bulk）  
> PDF 路径：[`../Literature/A4-Hallam, West, Forster, Powell, Spencer (2002). The decay of chlorine associated with the pipe wall in water distribution systems.pdf`](../Literature/A4-Hallam,%20West,%20Forster,%20Powell,%20Spencer%20(2002).%20The%20decay%20of%20chlorine%20associated%20with%20the%20pipe%20wall%20in%20water%20distribution%20systems.pdf)
>
> **来源标签**（2026-05-20，已通读 PDF 10 页）：
> - `[原文]` 直接出自论文 PDF
> - `[元数据]` 来自期刊页眉 / CrossRef
> - `[推断]` 与项目关联的延伸
> - `[需补]` 待后续核对

---

## 0. 元数据（已验证）

| 字段 | 内容 | 来源 |
| --- | --- | --- |
| Title | The decay of chlorine associated with the pipe wall in water distribution systems | PDF p.3479 |
| Authors | **N. B. Hallam**, **J. R. West**, **C. F. Forster**\* , **J. C. Powell**, **I. Spencer** | PDF |
| Affiliation | Univ. of Birmingham；Powell：Binnie Black & Veatch；Spencer：Severn Trent | PDF |
| Journal | *Water Research* | PDF |
| Volume / Pages | **36**, **3479–3488** | PDF |
| Year | **2002**（收稿 2001-06-12，修回 2001-11-09，接受 2002-02-01） | PDF |
| DOI | `10.1016/S0043-1354(02)00056-8` | literature.md |
| PII | S0043-1354(02)00056-8 | PDF |
| 优先级 | **P1**（literature.md §A4） | 本项目 |
| 状态 | `read`（PDF 已通读） | — |

\*通讯作者：C. F. Forster（`c.f.forster@bham.ac.uk`）。

**为什么是 P1**：提供 **11 段管网现场 $k_w$**（54 次）+ **实验室管段 $k_w$** 的对照方法；给出 **管材分级**（无衬铸铁 vs PVC/MDPE/水泥衬）及 $k_w$ 与 **$C_0$、流速** 的关系。直接支撑 Net1/EPANET 中 `wall_coeff` 取值范围、管材差异和「高反应性管壁受传质限制」的论述 — 与 A1 Rossman 案例 $k_w \in [0.15, 0.45]$ **m/day** 可对照（注意单位体系不同，见 §7）。

---

## 1. 原文 Abstract（英文，逐字）

> Free chlorine decay rates in water distribution systems for bulk and wall demands should be modelled separately as they have different functional dependencies. Few good quality determinations of in situ wall demand have been made due to the difficulty of monitoring live systems and due to their complexity. Wall demands have been calculated from field measurements at 11 locations in a distribution system fed from a single source. A methodology for the laboratory determination has been evolved and shown to give results that are similar to the in situ results. Pipe materials were classified as either having high reactivity (unlined iron mains) or low reactivity (PVC, MDPE and cement-lined ductile iron). The results indicate that wall decay rates for the former are limited by chlorine transport and for the latter by pipe material characteristics. The wall decay rate is inversely related to initial chlorine concentration for low reactivity pipes. In general, water velocity increases wall decay rates though the statistical confidence is low for low reactivity pipes. A moderate biofilm coating did not influence the wall decay rate for low reactivity pipes.

> 来源：PDF p.3479。

---

## 2. 中文摘要（再表述）

`[原文]` bulk 与 wall 衰减机制不同，应**分开建模**（$k=k_b+k_w$）。高质量现场 $k_w$ 数据稀少。

1. **现场**：Leicester 地区 Melbourne 水源管网，**11 段管、54 次** in situ $k_w$（1996-06—1999-03）。  
2. **实验室**：100 mm × 450 mm 管段 demand monitor（磁搅拌），与现场结果**量级一致**。  
3. **管材**：**高反应性** — 无衬铸铁（CI、SI）；**低反应性** — PVC、MDPE、水泥衬铸铁（DICL/CICL）。  
4. **机理**：高反应性管壁衰减受 **氯传质** 限制；低反应性管壁受 **管材反应性** 限制。  
5. **$C_0$**：低反应性管（尤其 PVC 现场）$k_w$ 与 $C_0$ **反相关**；实验室 CICL/MDPE/PVC 用幂函数拟合。  
6. **流速**：无衬铸铁 $k_w$ 随流速**显著升高**；低反应性管趋势弱。  
7. **生物膜**：中等量（51–670 pg ATP/cm²）对低反应性管 **$k_w$ 无显著影响**。

---

## 3. 论文解决了什么问题

| 空白 | 本文贡献 |
| --- | --- |
| 现场 $k_w$ 少、误差大（氯测量、旅行时间、$k_b$ 扣除） | 给出可重复 **in situ 五步规程** + 误差预算（§4.1） |
| 实验室管段与现场是否可比 | 同材质 **lab ≈ field**（Fig. 5–6） |
| 管材对 $k_w$ 影响定性 | 定量排序：**CI > SI > DICL > PVC > MDPE**（Fig. 5） |
| $k_w$ 是否随 $C_0$、流速变 | 分管材给出经验关系（有限 $C_0$/v 范围） |
| 生物膜是否显著耗氯 | 中等生物膜下 **低反应性管** 无显著效应 |

---

## 4. 用了什么方法

### 4.1 现场 in situ $k_w$ `[原文]` §2.1、Fig. 1、Table 1

**五步**（Powell [3] 博士论文方法）：

1. 在 A 点测 **bulk** $k_b$（瓶试）。  
2. 测上游/初始浓度 $C_0$（**≥20 min** 平均）。  
3. 由流量计或 **氯示踪** 得 A→B **旅行时间** $t$。  
4. 在 B 点测下游浓度 $C$（示踪时取 trace 到达前时段）。  
5. $k = \frac{1}{t}\ln(C_0/C)$，$k_w = k - k_b$。

**示踪氯**：加氯 spike 0.5–1.0 mg/L × 15 min，或关氯 30 min 造成 dip；消火栓采样 ≤6 L/min。

**低 bulk 背景**：使用 **1/4 强度 Ringer** 溶液加氯，三次瓶试 $k_b \le 0.006$ h⁻¹（< 平均 $k_w$ 的 6%）。

**管网**：Melbourne WTW → Ragdale 水库 → Leicester 系统（Fig. 1，11 段）。

**管材与管段**（Table 1 摘录）：

| 管段 | 直径 (mm) | 长度 (m) | 材料 | 次数 |
| --- | --- | --- | --- | --- |
| Ab Kettleby–Melton | 298 | 3505 | DICL 1991 | 7 |
| Melton–Ashfordby | 180 | 2610 | MDPE 1985 | 7 |
| Ab Kettleby–Long Clawson | 150 | 2300 | PVC 1979 | 6 |
| Saxelby 1–2 | 200 | 2284 | **SI** 1959 | 5 |
| Willoughby 2–3 等 | 100 | 515–925 | **CI** 1960 | 多段 |
| Great Glen 1–2 | 200 | 865 | PVC 1991 | 2 |

### 4.2 实验室 wall demand 仪 `[原文]` §2.2、Fig. 2

- **管段**：100 mm 内径 × **450 mm** 长；PVC 底板 + Perspex 锥盖；进水、出水、排气阀；**磁力搅拌**。  
- **水体**：10 L 1/4 Ringer + 次氯酸钠，静置 10 min。  
- **取样**：从顶部出口阀（**非管壁点**），双 Hach DPD。  
- **新管**：78% 超氯 48 h 预处理；20% 在网运行 3 周养 **生物膜**；2% 旧管切割。  
- **重复性**：6 对同条件试验，95% CI **±0.016 h⁻¹**。

**与现场差异**：多为新管、更高 $C_0$、更长试验时间、平均 **19±1 °C**、搅拌近似流动。

### 4.3 误差预算 `[原文]` §1、Powell [3]

| 来源 | 不确定度 |
| --- | --- |
| 氯浓度（双 Hach） | ±0.01 mg/L |
| 旅行时间（流量计） | ±15% |
| 旅行时间（示踪） | ±5% |
| bulk $k_b$ | ±0.01 h⁻¹ |
| 铸铁有效直径腐蚀 | 约 −30% |

---

## 5. 主要结果

### 5.1 $k_w$ 量级 `[原文]` §3、Figs. 3–5

| 类型 | in situ $k_w$ (h⁻¹) | 说明 |
| --- | --- | --- |
| 全体 | 0.00–**1.64** | 70% < 0.4 |
| 高值管段 | Willoughby CI 100 mm、Old Dalby CI 150 mm | 均 >0.4 |
| **CI 平均** | **0.67** | Fig. 5 |
| **SI 平均** | 0.33 | |
| **DICL** | 0.13 | |
| **PVC** | 0.09 | |
| **MDPE** | 0.05 | |

**实验室**（新 PVC/CICL/MDPE）：0.01–0.78 h⁻¹；同材质现场 **0.00–0.26** h⁻¹。

**管材反应性排序**：**CI > SI > DICL > PVC > MDPE**；水泥衬层显著降低铁管 $k_w$（相对无衬铸铁 4–100 倍文献差异与 AWWARF 一致）。

### 5.2 高 / 低反应性分类与传质 `[原文]` Abstract、§3

- **高反应性（无衬铁）**：$k_w$ 随 **流速** 显著上升（Fig. 9，99% 显著）→ **氯传质到管壁** 为限速（与 A1 mass-transfer 叙事一致）。  
- **低反应性（塑料/水泥衬）**：$k_w$ 低；流速关系 **$R^2=0.26$** → **管材反应** 为限速。  
- 作者**否定**「高 $C_0$ 因浓度差减小传质」的简单解释（高 $C_0$ 应增大传质驱动力，却观测到 $k_w$ 下降）。

### 5.3 $k_w$ 与初始氯浓度 `[原文]` Figs. 7–8、Table 2

**现场 PVC**（$C_0$ 约 0.15–0.3 mg/L）：

$$k_w = 0.26 - 0.73\,C_0 \quad (99\%\ \mathrm{显著})$$

→ 外推 $k_w=0$ 在 $C_0>0.36$ mg/L（作者强调**仅在线性区间内**有代表性）。

**实验室**（$C_0$ 0.16–1.95 mg/L），幂函数（Table 2）：

| 管材 | 回归式 | $R^2$ |
| --- | --- | --- |
| CICL | $y = 0.05\,x^{-1.17}$ | 0.48 |
| PVC | $y = 0.02\,x^{-1.55}$ | 0.67 |
| MDPE | $y = 0.02\,x^{-1.75}$ | 0.52 |

→ **$C_0$ 越高，表观 $k_w$ 越低**（低反应性管存在「管壁摄取速率上限」）。无衬铸铁现场**未**见显著 $C_0$ 关系。

### 5.4 流速与 Reynolds `[原文]` Fig. 9

- **CI、SI**：$k_w$ vs 流速 0.2–0.45 m/s 近似线性（99% 显著）；低于 0.15 m/s 外推为零不现实。  
- **Re**：$1.7\times10^4$–$1.7\times10^5$（过渡流）；Re 与 $k_w$ 关系与流速类似，低反应性管拟合差。

### 5.5 管径、温度、TOC、生物膜

- **管径**：调查管径范围窄，**无显著**直径效应。  
- **温度 / TOC**：散点大，**无结论**。  
- **生物膜**（51–670 pg ATP/cm²，PVC/MDPE/CICL）：12 次有膜 vs 无膜，**仅 1 次** $k_w$ 超出无膜范围 → **中等生物膜对低反应性管 $k_w$ 影响可忽略**。

---

## 6. 得出了什么结论

`[原文]` §4 要点：

1. 建立了可接受的 **in situ** 与 **实验室** $k_w$ 测定法；二者结果可互证。  
2. **管材**是 $k_w$ 主控因素：无衬铁 **高反应** vs 塑料/水泥衬 **低反应**。  
3. 高反应管：**传质限制**；低反应管：**材料反应限制**。  
4. 低反应管 $k_w$ 与 $C_0$ **反相关**（现场 PVC 线性段；实验室幂律）。  
5. **流速**升高一般增大 $k_w$（无衬铁显著）。  
6. **TOC、管径、温度**：未见可靠关系；温度可能增加变异性。  
7. **中等生物膜**不改变低反应性管 $k_w$。

---

## 7. 关键公式 / 符号与单位对照

| 符号 | 含义 | 本文单位 |
| --- | --- | --- |
| $k$ | 总一阶衰减常数 | h⁻¹ |
| $k_b$ | bulk | h⁻¹ |
| $k_w$ | wall | h⁻¹ |
| $C_0$, $C$ | 上下游氯浓度 | mg/L |
| $t$ | 旅行时间 | h |

**与 A1 Rossman (1994) 对照** `[需补]` 精细换算：

| 体系 | Rossman 1994 | Hallam 2002 |
| --- | --- | --- |
| wall 参数 | $k_w$：**0.15–0.45 m/day**（传质-反应综合模型中的 wall 速率常数） | 表观 **$k_w$：0.05–0.67 h⁻¹**（一阶 $k=k_b+k_w$ 分解） |
| 模型结构 | $k_b + k_w k_f/(r_h(k_w+k_f))$ | 简单相加 |

→ 写作时勿直接把 **0.67 h⁻¹** 填入 EPANET `Global Wall` 而不查手册单位；应通过 **同一网络复现** 或 EPANET 文档换算。Net1 原始 `.inp` **Global Wall = −1**（US）≈ WNTR **−0.3048 m/day** 与 Hallam 现场 CI 量级需单独对标。

---

## 8. 与本项目的关联

| 模块 | 关联 |
| --- | --- |
| **T2** | `02_demo_wntr_original.py` 开 wall；A4 给出 **关 wall 的代价** 与材质敏感性 |
| **T3** | 合成观测时可按 **管材** 分层 $k_w$；CI 段 vs PVC 段 |
| **T4** | 单一全局 $k_w$ 在混合管材网络中不可识别 — 支持 A1/A4「parsimony vs 现实」讨论 |
| **T5** | 旅行时间 ±5–15% + 氯 ±0.01 mg/L → $k_w$ 后验应很宽；不确定性校准的动机 |
| **结果解释.md** | 原始版开 wall、修改版关 wall 的差异可与 **wall 占比** 定性对照 |
| **vs A3** | 同组 Severn Trent；bulk (A3) + wall (A4) 拼完整 $k=k_b+k_w$ |

### 可参考要点（写论文 / 做实验时可直接引用）

1. **T2 对照实验**：`02_demo_wntr_original.py`（开 wall）vs `01_demo_wntr.py`（关 wall）— Results 引用本文 **CI 高 $k_w$、PVC 低 $k_w$** 解释两版 Net1 浓度差。
2. **T4 分区校准**：勿用单一 global `wall_coeff` 拟合混合管材网 — Methodology 写 **按 CI / PVC 分组** 或至少 sensitivity 对比 global vs zoned。
3. **单位陷阱**：本文 $k_w$ 为 **h⁻¹**；EPANET/WNTR `wall_coeff` 为 **m/day（US）** — 论文中必须给 **换算表或复现验证**，不可直接填 0.67。
4. **Methodology — in situ 思路**：demand monitor（$C_0$、$C$、旅行时间）估 $k_w=k-k_b$ — 即使无 Leicester 数据，合成场景可 **模仿该实验设计**。
5. **T5 不确定性**：旅行时间 ±5–15%、氯 ±0.01 mg/L 时 $k_w$ 不确定 — Discussion 引用为 **wall 参数后验应宽** 的文献依据。
6. **低浓度敏感**：PVC 段 $C_0$–$k_w$ 关系 — 解释管网末端接近 **0.2 mg/L** 时 wall 校准更不稳定。
7. **Discussion 简化假设**：生物膜贡献有限 — 可写「首版模型不对 biofilm 单独加项」，与 EPANET 一阶 wall 一致。

---

## 9. 可借鉴 / 可批判

### 9.1 可借鉴

- **现场−实验室对照**方法论，可在 thesis Methodology 占一小节。  
- 管材二分（高/低反应）简化工程决策。  
- PVC $C_0$–$k_w$ 关系解释低浓度区校准敏感性。  
- 生物膜结论支持「不必为 biofilm 单独加项」的初步假设（中等负荷）。

### 9.2 可批判

| 局限 | 本项目 |
| --- | --- |
| 仅 Leicester 单一水源、11 段 | BWSN/Net3 多材质 |
| 新管实验室占 78% | 现场老旧 CI 更 relevant |
| $C_0$、v 经验式外推范围窄 | 敏感性 + 先验截断 |
| 一阶 $k_w$ 与 A1 传质模型结构不同 | 讨论 EPANET 实现层级差异 |
| Intro 引 [2] Powell 2000 为 wall 现场 — 该文实为 **bulk**；现场 wall 方法应见 Powell PhD [3] | 引用时核对 |

---

## 10. 已答复 + 仍需补充

### 10.1 已答复

- ✅ in situ 五步、54 次、11 段  
- ✅ 实验室 demand monitor 示意图与流程  
- ✅ 管材排序、$k_w$ 范围、$C_0$/流速/生物膜结论  

### 10.2 仍需补充

- [ ] 读 Powell (1998) PhD 核对 in situ 原始公式与误差  
- [ ] EPANET 2.2 中 `wall_coeff` 单位与 Hallam $k_w$ (h⁻¹) 的换算表  
- [ ] 将 Table 1 管段参数映射到简易 EPANET 子模型做 $k_w$ 敏感性  

---

## 11. 思考题

1. Net1 管龄/材质信息与 BWSN 相比过于简化 — A4 结论如何支撑「换网后必须重校 $k_w$」？  
2. 若测量误差 ±0.01 mg/L，当 $C_0-C$ 很小时，$k_w=k-k_b$ 是否被 **bulk 扣除** 放大？  
3. 不确定性校准时，是否应对 **CI 段** 与 **PVC 段** 设不同 $k_w$ 先验？  

---

## 12. 引用模板

**Vancouver**：

> Hallam NB, West JR, Forster CF, Powell JC, Spencer I. The decay of chlorine associated with the pipe wall in water distribution systems. *Water Res*. 2002;36(14):3479–3488. doi:10.1016/S0043-1354(02)00056-8

**BibTeX**（拟写入 `../../thesis/refs.bib`）：

```bibtex
@article{Hallam2002WallChlorine,
  author  = {Hallam, N. B. and West, J. R. and Forster, C. F. and Powell, J. C. and Spencer, I.},
  title   = {The Decay of Chlorine Associated with the Pipe Wall in Water Distribution Systems},
  journal = {Water Research},
  volume  = {36},
  number  = {14},
  pages   = {3479--3488},
  year    = {2002},
  doi     = {10.1016/S0043-1354(02)00056-8},
  publisher = {Elsevier}
}
```

---

## 13. 修正记录

| # | literature / 旧认知 | PDF 核对后 |
| --- | --- | --- |
| 1 | 作者 Hallam, Powell, West, Spencer | 完整五人：**Forster 通讯**；Powell、Spencer 在 Severn Trent / BBV |
| 2 | 标题 "... in distribution systems" | 官方为 **"... in water distribution systems"** |
| 3 | 仅「wall coefficient、管材」 | 补充 **in situ 方法、$C_0$/流速/生物膜、传质 vs 反应限制** |
| 4 | — | $k_w$ 单位 **h⁻¹**（一阶和模型），与 Rossman **m/day** wall 系数非直接数值对标 |
