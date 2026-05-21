# A3 — Powell, Hallam, West, Forster, Simms (2000) 精读笔记

> 配套文件：[`../Literature/literature.md`](../Literature/literature.md) §A3、[`../../README.md`](../../README.md)  
> 前置阅读：[`A2_Hua1999.md`](A2_Hua1999.md)（同组 Birmingham + Severn Trent bulk 瓶试）  
> PDF 路径：[`../Literature/A3-Powell et al. (2000). Factors which control bulk chlorine decay rates.pdf`](../Literature/A3-Powell%20et%20al.%20(2000).%20Factors%20which%20control%20bulk%20chlorine%20decay%20rates.pdf)
>
> **来源标签**（2026-05-20，已通读 PDF 10 页）：
> - `[原文]` 直接出自论文 PDF
> - `[元数据]` 来自期刊页眉 / literature.md
> - `[推断]` 与项目关联的延伸
> - `[需补]` 待后续核对

---

## 0. 元数据（已验证）

| 字段 | 内容 | 来源 |
| --- | --- | --- |
| Title | Factors which control bulk chlorine decay rates | PDF p.117 |
| Authors | **James C. Powell**, **Nicholas B. Hallam**, **John R. West**, **Christopher F. Forster**, **John Simms** | PDF |
| Affiliation | Binnie Black & Veatch；Univ. of Birmingham Civil Eng.；Severn Trent Water | PDF |
| Journal | *Water Research* | PDF |
| Volume / Issue / Pages | **34**(1), **117–126** | PDF |
| Year | **2000**（收稿 1998-07-01，修回 1999-02-01） | PDF |
| DOI | `10.1016/S0043-1354(99)00297-9` | literature.md |
| PII | S0043-1354(99)00097-4 | PDF |
| 优先级 | **P1**（literature.md §A3） | 本项目 |
| 状态 | `read`（PDF 已通读） | — |

\*通讯作者：J. C. Powell（Binnie Black & Veatch）`[原文]` p.117。

**为什么是 P1**：在 A2 单水源、小样本基础上，用 **207 次**瓶试、**32 个** Severn Trent 采样点，系统量化 **$k_b$ 随温度、TOC、UV、$C_0$** 的变化，并给出可写入管网模型的 **式 (8)(9)**。与 A2 同组，是本项目讨论「$k_b$ 时变 → 模型耐久性」和 EPANET `bulk_coeff` 更新的核心文献之一。

---

## 1. 原文 Abstract（英文，逐字）

> Several computer programs for modelling water distribution networks have been developed which incorporate a facility for modelling chlorine decay. Problems have been experienced with the calibration and durability of these models due to both temporal and spatial variability in the decay constants. Chlorine will decay either due to reactions at the pipe wall or due to reactions in the bulk water. The aim of the work presented in this paper is to investigate the factors which influence bulk decay. Over 200 determinations of bulk chlorine decay against time were performed on waters taken from 32 sampling locations within the Severn Trent region, U.K. The bulk decay constant was observed to show significant variation with temperature, the initial chlorine concentration and the organic content of the water. An equation was derived relating these parameters which could be used to update the decay constants in network models and improve their durability.

> 来源：PDF p.117。

---

## 2. 中文摘要（再表述）

`[原文]` 管网余氯模型常假设 **一阶** $k_b$ 恒定，但现场 $k_b$ **时空变异性大**，导致校准后模型**耐久性差**。本文仅研究 **bulk**（瓶试，与 wall 分离，式 $k=k_b+k_w$）。

- **数据规模**：1996-06 至 1997-09，**207 次**衰减测定，**32 处**采样点（Severn Trent）。
- **主要发现**：$k_b$ 显著依赖 **温度**、**初始氯浓度 $C_0$**、**有机物指标（TOC、UV）**。
- **产出**：含 Arrhenius 温度项、有机物线性项、$1/C_0$ 项的 **综合经验式 (8)(9)**，用于随水质/温度**更新**网络模型中的 $k_b$。
- **讨论**：表观一阶行为与 **二级动力学**（$dC/dt=-k_b C H$）部分矛盾；管网实用上仍用**变参数一阶**。

---

## 3. 论文解决了什么问题

| 背景问题 | 本文贡献 |
| --- | --- |
| 文献中 $k_b$ 文献值 **0.02–0.74 h⁻¹**（Table 1），差异大 | 大样本统计：90% 的 $k_b$ 在 **0.008–0.16 h⁻¹**（Fig. 1） |
| 温度、TOC 对 $k_b$ 的影响定性已知，缺可操作公式 | 实验室三水源 Arrhenius 拟合 $R^2>0.98$；推荐 **$E/R=7300$ °C**（平均最优） |
| AWWARF (1996) 提出 $k=a\,\mathrm{TOC}\,e^{-b/(T+273)}$ 但未给数据 | 本文给出 TOC/UV **不过原点** 的线性式 (5)(6) 及 Melbourne GAC 前后斜率变化 |
| $k_b$ 随 $C_0$ 变化（A2 已示）缺区域尺度验证 | **16 对**重复试验：高 $C_0$ → 低 $k_b$；$k_b C_0$ 配对 **$r^2=0.70$（剔除 1 对后 0.90）** |
| 模型校准后水质变化即失效 | 提出用式 (8)(9) **动态更新** $k_b$，改善 model durability |

---

## 4. 用了什么方法

### 4.1 瓶试规程 `[原文]` §MATERIALS AND METHODS

| 步骤 | 要点 |
| --- | --- |
| 器皿 | 超氯 10 mg/L 蒸馏水 24 h 清洗（DoE 1981 法） |
| 取样 | 2.5 L Winchester 均质 15 min → 8×125 mL 棕色瓶 |
| 恒温 | 培养箱 = 水样温度；现场用保温箱运回 |
| 读数间隔 | 使氯浓度每次约降 **10%** |
| 拟合 | Visual Basic 宏，最小化观测与模型浓度 **SSE** |
| 水样类型 | **60%** 测 ambient 氯；其余加氯至 **0.5–2.5 mg/L** |
| 静置 | 分装前均质 **15 min**（非 freshly dosed 瞬时衰减） |
| 质控 | 蒸馏水对照 $k_b<0.005$ h⁻¹；**21 次**重复，95% CI **±0.022 h⁻¹** |

**测量**：DPD + Hach 便携比色计，双样双机，精度 **±0.02 mg/L**（95%）；温度 ±1.8 °C；pH ±0.02；UV 254 nm（1 cm）；TOC 由 Severn Trent 实验室同日测。

### 4.2 一阶基线 `[原文]` 式 (1)–(2)

$$C = C_0 e^{-k_b t}, \quad k = k_b + k_w$$

（本文实验无管段，实际拟合 $k_b$。）

### 4.3 温度 — Arrhenius `[原文]` 式 (3)、Table 4

$$k_b = F \exp\left[-\frac{E/R}{T+273}\right]$$

- 实验室 3 水源 × 3 温度：$R^2>0.98$，最大偏差 0.004 h⁻¹  
- **$E/R$ 优化值** 4660–9560 °C → 10–20 °C 衰减约 **1.8–3.2 倍**  
- **$F$ 不稳定**（优化时 $F$ 可差 $10^7$ 倍）→ 固定 **$E/R=7300$ °C**（全数据平均）更稳  
- 对比：AWWARF $E/R=6000$ °C → 10–20 °C 约 **2 倍**；7300 °C → **2.5 倍**  
- **应用**：用式 (3) 将各次 $k_b$ **归算到 15 °C** 再与 TOC/UV/$C_0$ 比较；亦可反算用于模型温度更新

### 4.4 有机物 — TOC 与 UV `[原文]` 式 (5)(6)、Figs. 3–4

**不过原点**（与 AWWARF 比例式不同）：

$$\boxed{k_b = e\,(\mathrm{TOC} - f)} \tag{5}$$

$$\boxed{k_b = g\,(\mathrm{UV} - h)} \tag{6}$$

| 水源 | $e$ (mg/L·h) | $f$ (mg/L) | $g$ (cm/h) | $h$ (1/cm) |
| --- | --- | --- | --- | --- |
| Melbourne WTW **GAC 前** | 0.36 | 0 | — | — |
| Melbourne WTW **GAC 后** | 0.04 | −0.12 | — | — |
| Haresfield 进水 | — | — | 1.61 | 0.012 |

→ GAC 投运后 **TOC 仍变但斜率骤降**，说明**有机物化学矩阵**改变，不单是 TOC 总量。

### 4.5 初浓度 `[原文]` 式 (7)、Fig. 5

$$\boxed{k_b = m/C_0}$$

- 16 对「同批水、$C_0$ 差 >25%」：**$C_0$ 高者 $k_b$ 恒更低**  
- Haresfield 春季：$k_b$ vs $1/C_0$ 显著（Fig. 5）

### 4.6 综合模型 `[原文]` 式 (8)(9)

**TOC 形式**：

$$\boxed{k_b = p\,\frac{1}{C_0}\,(\mathrm{TOC}-f)\,\exp\left[-\frac{E/R}{T+273}\right]} \tag{8}$$

**UV 形式**：

$$\boxed{k_b = q\,\frac{1}{C_0}\,(\mathrm{UV}-h)\,\exp\left[-\frac{E/R}{T+273}\right]} \tag{9}$$

- $E/R = 7300$ °C 固定；$p,f$ 或 $q,h$ 优化  
- Melbourne：GAC 前后 **分别** 标定 $p,f$；Fig. 6：60% 点误差 ≤20%，最大约 80%  
- Haresfield 全数据：Fig. 7：60% 在 ±0.01 h⁻¹ 内，$R^2=0.60$（因 $k_b$ 均值仅 Melbourne 的 1/3）

### 4.7 再氯化效应 `[原文]` Fig. 8

水样衰减后再加氯至相近 $C_0$：**6 次试验 $k_b$ 均降低 ≥40%** → 超级氯化/管网中途加氯会改变后续衰减；可用 $k_b$ 解释氯能「推得更远」。

---

## 5. 关键数据摘录

| 指标 | 数值 |
| --- | --- |
| 试验次数 | 207 |
| 采样点 | 32 |
| $k_b$ 90% 区间 | 0.008–0.16 h⁻¹ |
| 平均 $C_0$ | **0.5 mg/L**（低于 AWWARF 1.0、Jadas-Hécart 4–15 mg/L） |
| 重复测定 95% CI | ±0.022 h⁻¹ |
| 推荐 $E/R$ | **7300 °C** |
| 10→20 °C $k_b$ 倍数 | **2.5×**（7300 °C） |
| pH | **无显著关系**（变化范围窄） |

**主要采样来源**（Table 2）：Melbourne WTW final/SP05/SP12、Ab Kettleby、Haresfield、Strensham、伯明翰大学龙头水等。

---

## 6. 得出了什么结论

`[原文]` §CONCLUSIONS 四条：

1. $k_b$ 随 **温度、TOC/UV、$C_0$** 变化；给出综合式，核心是 **Arrhenius（$E/R=7300$ °C）+ 有机物线性项 + $\propto 1/C_0$**。
2. **pH** 与 $k_b$ 无显著关系（观测范围窄）。
3. **再氯化** 降低 $k_b$（所有观测案例）。
4. 现象与**严格一阶**矛盾；**二级**可部分解释，但管网建模仍宜用 **$k_b(T,\mathrm{TOC\ or\ UV},C_0)$ 的一阶变参数**。

---

## 7. 关键公式 / 符号

| 符号 | 含义 | 单位 |
| --- | --- | --- |
| $k_b$ | bulk 一阶衰减常数 | h⁻¹ |
| $k_w$ | wall（本文未测） | h⁻¹ |
| $C_0$ | 初始游离氯 | mg/L |
| TOC | 总有机碳 | mg/L |
| UV | 254 nm 吸光度 | 1/cm |
| $E/R$ | Arrhenius 参数 | °C（与 $T$+273 配合） |
| $p,q,e,g,m,f,h$ | 经验拟合系数 | 见正文 |

**单位换算**：EPANET `bulk_coeff` 为 **1/day** → $k_{b,\mathrm{day}} = 24 \times k_{b,\mathrm{h}}$。例：$k_b=0.1$ h⁻¹ ≈ **2.4/day**（衰减，EPANET 取负号）。

---

## 8. 与本项目的关联

| 模块 | 关联 |
| --- | --- |
| **T2** | 说明为何固定 `bulk_coeff=-0.5/day` 只是占位；应用式 (8)(9) 或至少 $k_b(T)$ 更新 |
| **T3** | 合成数据时可对 TOC/温度/$C_0$ 设协变量，模拟 **spatial-temporal $k_b$ 变异性** |
| **T4** | 校准时若只拟合单一 $k_b$，可能过拟合某日水质；A3 支持 **时变 $k_b$ 先验** |
| **T5** | 测量 ±0.02 mg/L + $k_b$ 0.008–0.16 宽范围 → 参数后验会很宽，利于论证不确定性校准 |
| **vs A2** | A2：机理推导 + 小样本；A3：**区域尺度经验回归** + 模型耐久性 |
| **vs A4** | A3 bulk；A4 wall。Hallam 2002 引用本文 [2] 为同系列 |

---

## 9. 可借鉴 / 可批判

### 9.1 可借鉴

- **207 次**数据支撑「$k_b$ 不是常数」的论述。  
- **归算 15 °C** 再比较有机物 — 温度分层分析范例。  
- GAC 前后斜率变化 — Discussion 里「处理工艺变 → 化学矩阵变」的论据。  
- 再氯化降 $k_b$ — 解释 booster chlorination 与模型失配。

### 9.2 可批判

| 局限 | 本项目 |
| --- | --- |
| 仅 Severn Trent，2000 年前水质 | 外推需新数据或 Bayesian 先验加宽 |
| 经验式系数分水源标定 | 层级模型：区域超参数 |
| 仍用一阶拟合曲线 | 可与 A2 二阶模型、E3 贝叶斯二阶对照 |
| UV/TOC 非在线常规监测 | 敏感性分析：哪些协变量最省传感器 |

---

## 10. 已答复 + 仍需补充

### 10.1 已答复

- ✅ 瓶试流程、207 次规模、Fig. 1 分布  
- ✅ 式 (8)(9) 完整形式及 $E/R=7300$ °C  
- ✅ TOC/UV/$C_0$/再氯化结论  

### 10.2 仍需补充

- [ ] 读 Powell et al. (2000) ASCE **kinetic models comparison** [Ref. 11 in A4]  
- [ ] 将式 (9) 在 Haresfield 典型 UV/$C_0$/T 下算出 $k_b$ 区间，与 Net1 `bulk=-0.5/day` 对照  
- [ ] 核对 Melbourne GAC 时间线与 thesis Powell (1998) 是否同一数据集  

---

## 11. 思考题

1. 若管网温度冬夏差 10 °C，仅温度项即可使 $k_b$ 变 2.5 倍 — **确定性校准**在冬季数据上得到的 $k_b$ 在夏季预测会怎样？  
2. 式 (8) 在 TOC<$f$ 时 $k_b$ 可为负 — 物理上无效；模型实现需 **截断或先验**。  
3. 本项目 **sensor uncertainty** 与 ±0.02 mg/L 相比，在低 $C_0$ 节点是否主导 $k_b$ 估计方差？  

---

## 12. 引用模板

**Vancouver**：

> Powell JC, Hallam NB, West JR, Forster CF, Simms J. Factors which control bulk chlorine decay rates. *Water Res*. 2000;34(1):117–126. doi:10.1016/S0043-1354(99)00297-9

**BibTeX**（拟写入 `../../thesis/refs.bib`）：

```bibtex
@article{Powell2000BulkChlorine,
  author  = {Powell, James C. and Hallam, Nicholas B. and West, J. R. and Forster, C. F. and Simms, John},
  title   = {Factors Which Control Bulk Chlorine Decay Rates},
  journal = {Water Research},
  volume  = {34},
  number  = {1},
  pages   = {117--126},
  year    = {2000},
  doi     = {10.1016/S0043-1354(99)00297-9},
  publisher = {Elsevier}
}
```

---

## 13. 修正记录

| # | 说明 |
| --- | --- |
| 1 | 全文基于 PDF 提取；$E/R$ 单位为论文所用 **°C**（与 $T+273$ 联用），非 J/mol |
| 2 | literature 关键词「TOC、温度、初始浓度」已覆盖；补充 **UV、模型耐久性、再氯化** |
