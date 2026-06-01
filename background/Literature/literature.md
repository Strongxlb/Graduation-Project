# 文献清单 - Literature List

> 配套文件：`[../README.md](../README.md)`、`[../README.en.md](../README.en.md)`、`[../plan1.md](../plan1.md)`
> 本文件目的：在动手写综述前，先把要读的文献按主题分组列清楚。
> 维护规则：
>
> - 每条至少包含 **作者 + 年份 + 标题 + DOI/链接 + 一行收录理由**。
> - **下载 / 阅读 / 理解** 三列：`✓` = 已完成；**空白** = 未完成（勿填 `✗`）。
> - **下载**：`Literature/` 对应子文件夹内已有匹配 PDF（或 F2 的 WHO 背景文件）。
> - **阅读**：`notes/` 内已有精读笔记（通读 PDF 后整理）。
> - **理解**：能向导师讲清「问题—方法—结论—与本项目关系」；通常晚于阅读。
> - 优先级：`P0` 必读，`P1` 重要，`P2` 备读。
> - **⭐ 导师建议** = 2026-05-25 邮件明确推荐的 9 篇 reading list 项目（A1, A6, A4, A3, B2, B1, B3, E6, E7）；这些条目已置于各分类最前，并在「收录理由」列加 ⭐ 标记与原文引用。
> - BibTeX 统一存入 `../thesis/refs.bib`，本文件只做导览。

---

## A. Chlorine decay 机理（bulk / wall / 影响因素）

> 目标：理解一阶/多阶衰减模型、bulk vs wall coefficient 的物理意义、温度与有机物的影响。


| #   | Citation                                                                                                                                                                                  | DOI / Link                              | 主题关键词                                                                        | 优先级 | 下载  | 阅读  | 理解  | 收录理由                                                                                                                                                                                                                                                                                                                                                              |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------- | --- | --- | --- | --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A1  | Rossman, Clark, Grayman (1994). Modeling chlorine residuals in drinking-water distribution systems. *J. Env. Eng.*                                                                        | 10.1061/(ASCE)0733-9372(1994)120:4(803) | 一阶衰减、bulk + wall                                                             | P0  | ✓   | ✓   | ✓   | **⭐ 导师建议（2026-05-25 邮件）** · "the foundational paper introducing the wall-reaction + mass-transfer formulation EPANET uses"。余氯衰减建模的奠基论文，必读。精读笔记：`[../notes/A/A1_Rossman1994.md](../notes/A/A1_Rossman1994.md)`。                                                                                                                                                    |
| A6  | Vasconcelos, Rossman, Grayman, Boulos, Clark (1997). Kinetics of chlorine decay. *Journal AWWA* 89(7):54–65                                                                               | 10.1002/j.1551-8833.1997.tb08259.x      | bulk vs wall、first-order vs higher-order、bottle test、5-system 实证、α·roughness | P0  | ✓   | ✓   | ✓   | **⭐ 导师建议（2026-05-25 邮件）** · "bulk vs wall, and why first-order is the usual (but not only) choice"。A1 Rossman 1994 的**实证姐妹篇**：5 个真实美国管网验证 first-order bulk + first-order/zero-order wall + mass-transfer 模型，给出 `k_b` 跨水源 200 倍差、`k_w` 与 Hazen-Williams 粗糙度成反比、DPD 测量误差 15% 等本项目方法学基线。精读笔记：`[../notes/A/A6_Vasconcelos1997.md](../notes/A/A6_Vasconcelos1997.md)`。 |
| A4  | Hallam, West, Forster, Powell, Spencer (2002). The decay of chlorine associated with the pipe wall in water distribution systems. *Water Research*                                        | 10.1016/S0043-1354(02)00056-8           | wall coefficient、管材、现场/实验测定                                                  | P1  | ✓   | ✓   | ✓   | **⭐ 导师建议（2026-05-25 邮件）** · "the key wall-decay heterogeneity paper (material and age dependence). This directly justifies one kw per DMA"。给出现场与实验 wall demand 估计，支撑 wall decay 取值范围与管材差异。精读笔记：`[../notes/A/A4_Hallam2002.md](../notes/A/A4_Hallam2002.md)`。                                                                                                      |
| A3  | Powell et al. (2000). Factors which control bulk chlorine decay rates. *Water Research*                                                                                                   | 10.1016/S0043-1354(99)00297-9           | TOC、温度、初始浓度                                                                  | P1  | ✓   | ✓   | ✓   | **⭐ 导师建议（2026-05-25 邮件）** · "the bulk side, bottle tests, and temperature sensitivity (relevant to fixing kb)"。用于讨论 bulk decay 与水质参数的相关性。精读笔记：`[../notes/A/A3_Powell2000.md](../notes/A/A3_Powell2000.md)`。                                                                                                                                                       |
| A2  | Hua et al. (1999). Modelling of chlorine decay in municipal water supplies. *Water Research*                                                                                              | 10.1016/S0043-1354(99)00094-4           | 衰减动力学、温度修正                                                                   | P0  | ✓   | ✓   |     | 奠定 bulk decay 拟合方法。精读笔记：`[../notes/A/A2_Hua1999.md](../notes/A/A2_Hua1999.md)`。                                                                                                                                                                                                                                                                                   |
| A5  | Maleki, Ardila, Argaud, Pelletier, Rodriguez (2023). Full-scale determination of pipe wall and bulk chlorine degradation coefficients for different pipe categories. *Water Supply* (IWA) | 10.2166/ws.2023.020                     | full-scale、管材/管龄分类、kw 实测、Université Laval                                    | P1  |     |     |     | A4 Hallam 2002 的 20 年后实证版：加拿大魁北克全尺度真实管网，按管材（grey-cast iron / ductile cast iron / PVC）与安装年代分类拟合 kw/kb；**安装年代**是 kw 的显著影响因素，老灰口铁管 wall 可吃掉 ~97% 余氯，新管 bulk 占比可达 ~35%。直接支撑本项目「分管材 / 分管龄 k_w」思路。                                                                                                                                                                      |


## B. EPANET / WNTR 工具与方法学

> 目标：掌握 EPANET 2.2 水质方程、WNTR Python API 的边界与扩展点。


| #   | Citation                                                                                                                                                                                            | DOI / Link                                                                             | 主题关键词                  | 优先级 | 下载  | 阅读  | 理解  | 收录理由                                                                                                                                                                                                       |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ---------------------- | --- | --- | --- | --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B2  | Rossman, Woo, Tryby, Shang, Janke, Haxton (2020). EPANET 2.2 User Manual. *US EPA*.                                                                                                                 | [https://www.epa.gov/water-research/epanet](https://www.epa.gov/water-research/epanet) | EPANET 数值方法            | P0  | ✓   | ✓   | ✓   | **⭐ 导师建议（2026-05-25 邮件）· "read the two references first"** · "the definitive account of first-order bulk/wall decay and the mass-transfer term the code relies on"（water-quality 章节是 exercises 3 & 4 的参考）。 |
| B1  | Klise, Bynum, Moriarty, Murray (2017). A software framework for assessing the resilience of drinking water systems to disasters with an example earthquake case study. *Env. Modelling & Software*  | 10.1016/j.envsoft.2017.06.022                                                          | WNTR 介绍论文              | P0  | ✓   | ✓   |     | **⭐ 导师建议（2026-05-25 邮件）** · "for citing the tool and understanding its design"。WNTR 工具引用首选。精读笔记：`[../notes/B/B1_Klise2017.md](../notes/B/B1_Klise2017.md)`。                                                                                                                |
| B3  | Klise et al. (2018). Water Network Tool for Resilience (WNTR) User Manual. *Sandia / EPA*.                                                                                                          | [https://usepa.github.io/WNTR/](https://usepa.github.io/WNTR/)                         | WNTR API               | P0  | 收藏夹 |     |     | **⭐ 导师建议（2026-05-25 邮件）** · "the water-quality and reactions sections plus the simulator API — the practical companion to the script"。                                                                     |
| B4  | Riyadh, Zayat, Chaaban, Peleato (2024). Improving chlorine residual predictions in water distribution systems using recurrent neural networks. *Environmental Science: Water Research & Technology* | 10.1039/D4EW00329B                                                                     | EPANET-WNTR、余氯预测、全尺度数据 | P2  |     |     |     | 近期将 EPANET-WNTR 与高频实测余氯数据结合的案例，可作为 process-based 与 data-driven 对照。                                                                                                                                         |


## C. 水质模型校准（确定性方法）

> 目标：理解最小二乘、加权最小二乘、可识别性、敏感性分析的标准做法。


| #   | Citation                                                                                                                                                                                                                                                  | DOI / Link                              | 主题关键词                                     | 优先级 | 下载  | 阅读  | 理解  | 收录理由                                                                                                                              |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ----------------------------------------- | --- | --- | --- | --- | --------------------------------------------------------------------------------------------------------------------------------- |
| C1  | Munavalli, Kumar (2005). Water quality parameter estimation in a distribution system under dynamic state. *Water Research*                                                                                                                                | 10.1016/j.watres.2005.07.043            | 动态校准、参数估计                                 | P0  | ✓   | ✓   |     | 余氯参数动态校准经典案例。精读笔记：`[../notes/C/C1_Munavalli2005.md](../notes/C/C1_Munavalli2005.md)`。                                             |
| C2  | Pasha, Lansey (2010). Effect of parameter uncertainty on water quality predictions. *J. Hydroinformatics*                                                                                                                                                 | 10.2166/hydro.2010.053                  | 参数不确定性传播                                  | P0  | ✓   | ✓   |     | 桥接确定性校准与不确定性分析。精读笔记：`[../notes/C/C2_Pasha2010.md](../notes/C/C2_Pasha2010.md)`。                                                   |
| C3  | Frankel, Katz, Kinney, Werth, Zigler, Sela (2023). A framework for assessing uncertainty of drinking water quality in distribution networks with application to monochloramine decay. *Journal of Cleaner Production*                                     | 10.1016/j.jclepro.2023.137056           | Morris、MC、水质不确定性                          | P1  |     |     |     | 用 Morris 筛选化学参数并用 Monte Carlo 传播水力/水质不确定性，可借鉴敏感性分析流程。                                                                             |
| C4  | Adedoja, Hamam, Khalaf, Sadiku (2019). A state-of-the-art review of an optimal sensor placement for contaminant warning system in a water distribution network. *Urban Water Journal*                                                                     | 10.1080/1573062X.2019.1597378           | sensor placement、water quality monitoring | P2  |     |     |     | 综述水质传感器布设目标和优化方法，Discussion 可用来限定采样点设计不是本项目主线。                                                                                    |
| C5  | Ostfeld, Uber, Salomons, Berry, Hart, Phillips, Watson, Dorini, Jonkergouw, Kapelan, et al. (2008). The Battle of the Water Sensor Networks (BWSN): A Design Challenge for Engineers and Algorithms. *Journal of Water Resources Planning and Management* | 10.1061/(ASCE)0733-9496(2008)134:6(556) | BWSN benchmark、网络、奠基                      | P0  | ✓   | ✓   |     | BWSN 测试网络（BWSN1/BWSN2）的奠基论文，后续余氯/水质 benchmark 工作普遍引用此文作为模型来源。精读笔记：`[../notes/C/C5_Ostfeld2008.md](../notes/C/C5_Ostfeld2008.md)`。 |
| C6  | Hermes, Artelt, Vrachimis, Polycarpou, Hammer (2025). A Benchmark for Physics-informed Machine Learning of Chlorine Concentration States in Water Distribution Networks. *SN Computer Science*                                                            | 10.1007/s42979-025-04008-y              | chlorine benchmark、PhML、GNN/RNN           | P2  |     |     |     | 最新公开的余氯浓度估计 benchmark（Hanoi、Net1、CY-DBP 三网 18,000 场景），可作为本项目数据驱动 baseline 对照。                                                     |


## D. 测量不确定性 (DPD / colorimetric / 在线传感器)

> 目标：了解 DPD 比色法精度、典型固定/相对误差、在线探头的偏差与漂移。


| #   | Citation                                                                                                                                                                                                                                                                | DOI / Link                                                         | 主题关键词                                        | 优先级 | 下载  | 阅读  | 理解  | 收录理由                                                                                                                              |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------- | --- | --- | --- | --- | --------------------------------------------------------------------------------------------------------------------------------- |
| D1  | APHA / AWWA / WEF (2017). Standard Methods for the Examination of Water and Wastewater, 23rd ed., Method 4500-Cl G (DPD colorimetric).                                                                                                                                  | [https://www.standardmethods.org](https://www.standardmethods.org) | DPD 标准方法                                     | P0  |     |     |     | DPD 测量精度与干扰来源的权威说法。                                                                                                               |
| D2  | Soares, Arruda, Lobón, Scalize (2016). Avaliação de métodos para determinação de cloro residual livre em águas de abastecimento público [Evaluation of methods for determining free residual chlorine in public water supply]. *Semina: Ciências Exatas e Tecnológicas* | 10.5433/1679-0375.2016v37n1p119                                    | DPD precision、visual vs digital、reagent form | P0  | ✓   | ✓   |     | 比较 DPD 视觉/数字设备与粉剂/片剂读数差异，可为现场 DPD 误差模型提供经验依据。原文为葡萄牙语，方括号内为英译标题。精读笔记：`[../notes/D/D2_Soares2016.md](../notes/D/D2_Soares2016.md)`。 |
| D3  | Aisopou, Stoianov (2024). Evaluation of Free-Chlorine Data from Online Sensors in a Water Supply Network. *Engineering Proceedings*                                                                                                                                     | 10.3390/engproc2024069144                                          | 在线传感器、electrochemical、Bland-Altman           | P1  |     |     |     | 使用 UK 管网在线 free chlorine 传感器与 DPD grab samples 对比，直接支撑 sensor uncertainty 讨论。Imperial College 同组工作。                               |
| D4  | Wilson, Stoianov, O'Hare (2019). Continuous Chlorine Detection in Drinking Water and a Review of New Detection Methods. *Johnson Matthey Technology Review*                                                                                                             | 10.1595/205651318X15367593796080                                   | DPD vs amperometric、sensor fouling、综述        | P1  |     |     |     | 同行评议综述，系统对比 DPD、amperometric、polarographic 及新兴方法，并指出 fouling 是连续监测的主要障碍。Imperial College 与 D3 同组，可作为方法学综述引用。                      |
| D5  | Guigues, Chabrol, Lavaud, Raveau, Magar, Lalere, Vaslin-Reimann (2022). Assessing the performances of on-line analyzers can greatly improve free chlorine monitoring in drinking water. *Accreditation and Quality Assurance*                                           | 10.1007/s00769-021-01488-2                                         | 在线分析仪、EN 17075、不确定度量化                        | P2  |     |     |     | 按 EN 17075 标准对 7 台 amperometric + 1 台 colorimetric 分析仪做 7 个月实地比测，给出 6–38% 扩展不确定度和 P90 相对偏差 10–19%，可作为 sensor error model σ 的经验先验。 |


## E. 不确定性感知校准（Monte Carlo / Bayesian）

> 目标：决定 Plan A (MC + 最小二乘) vs Plan B (Bayesian / MCMC) 的取舍。


| #   | Citation                                                                                                                                                                                                                            | DOI / Link                                                              | 主题关键词                                                     | 优先级 | 下载  | 阅读  | 理解  | 收录理由                                                                                                                                                                                                                                             |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------- | --- | --- | --- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| E6  | Beven, Binley (1992). The future of distributed models: model calibration and uncertainty prediction. *Hydrological Processes* 6(3):279–298                                                                                         | 10.1002/hyp.3360060305                                                  | GLUE、ensemble、likelihood weighting、distributed model      | P0  | ✓   |     |     | **⭐ 导师建议（2026-05-25 邮件）· "your robust fallback method"** · GLUE（Generalised Likelihood Uncertainty Estimation）原始论文：用大量 Monte Carlo 抽样 + likelihood 加权得到参数与预测不确定性区间，不要求似然函数解析或先验严格。本项目 **Plan A**（ensemble-based）的直接理论依据；Bayesian MCMC 跑不通时的备份方案。 |
| E7  | Gelman, Carlin, Stern, Dunson, Vehtari, Rubin (2013). *Bayesian Data Analysis*, 3rd ed. (book) Chapman & Hall / CRC                                                                                                                 | 10.1201/b16018                                                          | Bayesian、hierarchical model、partial pooling、MCMC、textbook | P0  | 收藏夹 |     |     | **⭐ 导师建议（2026-05-25 邮件）· "only need the relevant chapters"** · Ch 5 Hierarchical Models（partial pooling → 3 个 DMA 共享族先验） + Ch 11 Basics of MCMC（Plan B 的 hierarchical/partial-pooling 概念）。**不要通读**，只需以上两章即可。                                     |
| E1  | Kavetski, Kuczera, Franks (2006). Bayesian analysis of input uncertainty in hydrological modeling. *Water Resources Research*                                                                                                       | 10.1029/2005WR004368（理论）；已下载 Paper 2 Application：`10.1029/2005WR004376` | Bayesian / 输入不确定性                                         | P0  | ✓   | ✓   |     | 对照 hydrology 领域怎么处理观测误差（BATEA）。精读笔记：`[../notes/E/E1_Kavetski2006.md](../notes/E/E1_Kavetski2006.md)`（基于 Paper 2）。                                                                                                                                |
| E2  | Vrugt (2016). Markov chain Monte Carlo simulation using the DREAM software package. *Env. Modelling & Software*                                                                                                                     | 10.1016/j.envsoft.2015.08.013                                           | DREAM / MCMC                                              | P1  |     |     |     | 备用 MCMC 工具栈参考。                                                                                                                                                                                                                                   |
| E3  | Huang, McBean (2007). Using Bayesian statistics to estimate the coefficients of a two-component second-order chlorine bulk decay model for a water distribution system. *Water Research*                                            | 10.1016/j.watres.2006.10.027                                            | Bayesian、MCMC、chlorine decay                              | P0  | ✓   | ✓   |     | 直接将 Bayesian/MCMC 用于 chlorine decay 参数估计，是 Plan B 贝叶斯校准的核心对照文献。精读笔记：`[../notes/E/E3_HuangMcBean2007.md](../notes/E/E3_HuangMcBean2007.md)`。                                                                                                      |
| E4  | Kang, Pasha, Lansey (2009). Approximate methods for uncertainty analysis of water distribution systems. *Urban Water Journal*                                                                                                       | 10.1080/15730620802566844                                               | Monte Carlo、LHS、FOSM、EPANET                               | P1  |     |     |     | 比较 MC、LHS 和 FOSM 对压力、水龄、余氯预测不确定性的效果，用于 Methodology 选择 MC baseline。                                                                                                                                                                               |
| E5  | Sansone, Cozzolino, Padulano, Di Cristo, Del Giudice (2026). Detection of deteriorated areas in water distribution networks exploiting chlorine measurements in a Bayesian framework. *Engineering Proceedings* (CSDU-CSSI DAYS 25) | 10.3390/engproc2026135007                                               | Bayesian、MCMC、Metropolis–Hastings、kwall、管道老化              | P0  | ✓   | ✓   |     | 与 E3 Huang 2007 并列的**最新且最直接对手**：把 chlorine 测量喂进 MCMC（Metropolis–Hastings），反演每根管的 k_wall，并据此分类管道老化状态。**Gap（你要补的）**：该文用合成观测、未显式建模 DPD 测量误差，也未做参数可识别性 / 后验区间分析——本项目正是补这条。精读笔记：`[../notes/E/E5_Sansone2026.md](../notes/E/E5_Sansone2026.md)`。       |


## F. 监管与阈值（policy / regulation）

> 目标：找到能直接为论文中 `0.2 mg/L` 工作阈值背书的法规与指南；这类是「灰文献」，多无 DOI，用官方 URL + 出版机构 + 版本。


| #   | Citation                                                                                                                                                                               | DOI / Link                                                                                                                                                                                                                                                                                                         | 主题关键词                           | 优先级 | 下载  | 阅读  | 理解  | 收录理由                                                                                                                                                                                                                                                                                        |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------- | --- | --- | --- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F1  | UK Statutory Instrument (2016). The Water Supply (Water Quality) Regulations 2016, SI 2016 No. 614, Part 8 (Water treatment) Reg. 26 + Schedule 1.                                     | [https://www.legislation.gov.uk/uksi/2016/614/contents](https://www.legislation.gov.uk/uksi/2016/614/contents)                                                                                                                                                                                                     | UK 法规、disinfection、Schedule 1   | P0  |     |     |     | 英国（项目所在地）饮用水水质的现行法定要求，定义运营商必须维持的处理与监测义务，论文 Introduction / Discussion 引用本国法规的首选。                                                                                                                                                                                                             |
| F2  | World Health Organization (2022). Guidelines for Drinking-water Quality: 4th ed. incorporating the first and second addenda. (Chlorine: §8 + WHO/SDE/WSH/03.04/45 background document) | [https://www.who.int/publications/i/item/9789240045064](https://www.who.int/publications/i/item/9789240045064) ；chlorine 背景文件：[https://cdn.who.int/media/docs/default-source/wash-documents/wash-chemicals/chlorine.pdf](https://cdn.who.int/media/docs/default-source/wash-documents/wash-chemicals/chlorine.pdf) | WHO、free chlorine 残余、≥ 0.2 mg/L | P0  | ✓   | ✓   |     | WHO 推荐管网末端 free chlorine ≥ 0.2 mg/L、接触 30 min 后 ≥ 0.5 mg/L（pH < 8），是本项目 `0.2 mg/L` 工作阈值的国际依据。**已读** 背景文件 `F2.2chlorine.pdf`（health GV 5 mg/L；0.2 为典型浓度非 formal residual — 见笔记）。GDWQ 全书仍待下载。精读笔记：`[../notes/F/F2_WHO2003ChlorineBackground.md](../notes/F/F2_WHO2003ChlorineBackground.md)`。 |


---

## 本周必读（Week 1 → Week 2 之间）

仅从上表选 3 篇，作为本周末到 Week 2 中段的精读对象。建议挑选时遵循「一类一篇 + 必须 P0」：

- **A1** Rossman et al. 1994 — 衰减模型基础（已有精读笔记）
- **B2** EPANET 2.2 Manual — 工具方程基础（只读 Water Quality 章节即可）
- **C2** Pasha & Lansey 2010 — 参数不确定性传播（连接 T4 与 T5）

精读笔记按以下结构存到 `notes/<章节>/`（如 `notes/A/`）或追加到本文件末尾：

```
### A1 - Rossman 1994
- 问题：
- 方法：
- 关键公式：
- 与本项目关联：
- 可借鉴/可批判之处：
```

---

## 待补字段（持续维护）

- 把所有 P0 论文的 BibTeX 加到 `thesis/refs.bib`
- 找 1–2 篇 BWSN benchmark 上的余氯校准论文（用于支撑选用 BWSN 的合理性） — 见 C5（Ostfeld 2008 奠基）、C6（Hermes et al. 2025 PhML chlorine benchmark）
- 找 1 篇 Imperial / 英国管网余氯监管阈值的政策性文件 — 见 F1（UK SI 2016/614）、F2（WHO GDWQ 4th ed）
- 找 1 篇关于 free chlorine 在线监测传感器市场综述（指明 DPD vs amperometric vs 其它） — 见 D4（Wilson 2019 JMTR）、D5（Guigues 2022 AQA）

---

## 验证日志（2026-05-18）

> 用 CrossRef API（`https://api.crossref.org/works/<DOI>`）逐条核验 A4 / B4 / C3 / C4 / D2 / D3 / E3 / E4；同样方法验证新增 C5 / C6 / D4 / D5。F1 / F2 为法规与 WHO 指南，无 DOI，通过 `legislation.gov.uk` 与 `who.int` 的官方页面校对。


| #                      | 字段                  | 原值                                               | 修正后                                                                                  | 来源                                                 |
| ---------------------- | ------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------ | -------------------------------------------------- |
| A4                     | 作者列表                | Hallam, Powell, West, Spencer                    | Hallam, **West, Forster, Powell, Spencer**（漏 Forster；顺序按 CrossRef 还原）                | CrossRef `10.1016/S0043-1354(02)00056-8`           |
| A4                     | 标题                  | "... in distribution systems"                    | "... in **water** distribution systems"                                              | 同上                                                 |
| B4                     | 作者列表                | Riyadh, Chaaban, Zayat, Peleato                  | Riyadh, **Zayat, Chaaban**, Peleato（second 与 third 互换）                               | CrossRef `10.1039/D4EW00329B`                      |
| B4                     | 标题                  | "Improving **Chlorine Residual Predictions**..." | "Improving **chlorine residual predictions**..."（小写，按出版字段）                           | 同上                                                 |
| D2                     | 标题语言                | 仅英文                                              | 补回葡萄牙语原标题 + 方括号英译 + 注释                                                               | CrossRef `10.5433/1679-0375.2016v37n1p119`（原文葡萄牙语） |
| C3 / C4 / D3 / E3 / E4 | —                   | —                                                | 全部字段（作者、年份、标题、期刊）与 CrossRef 元数据一致，无需修改                                               | 各自 DOI 的 CrossRef 记录                               |
| 移除 E1（原）               | Beven & Binley GLUE | —                                                | **已自清单删除**（无阅读权限）；原 E2–E5 重编号为 E1–E4                                                 | 2026-05-20                                         |
| 新增 C5                  | —                   | —                                                | Ostfeld 等 30+ 位作者；2008-11；J. Water Resour. Plann. Manage. 134(6):556–568；442 引用      | CrossRef `10.1061/(ASCE)0733-9496(2008)134:6(556)` |
| 新增 C6                  | —                   | —                                                | **一作 Hermes**（不是 Artelt）；2025-06；SN Computer Science 6(5)；测试网络 Hanoi / Net1 / CY-DBP | CrossRef `10.1007/s42979-025-04008-y`              |
| 新增 D4                  | —                   | —                                                | Wilson, Stoianov, O'Hare；2019-04；JMTR 63(2):103–118；Imperial College                 | CrossRef `10.1595/205651318X15367593796080`        |
| 新增 D5                  | —                   | —                                                | Guigues 等 7 人；**2022-02 出版**（online 2022-01-13）；AQA 27(1):43–53                      | CrossRef `10.1007/s00769-021-01488-2`              |
| 新增 F1                  | —                   | —                                                | UK SI 2016 No. 614，2016-06-27 生效，Part 8 + Schedule 1                                 | legislation.gov.uk 官方页面                            |
| 新增 F2                  | —                   | —                                                | WHO GDWQ 4th ed + 1st & 2nd Addenda（2022 合订版）；chlorine 背景文件 WHO/SDE/WSH/03.04/45     | who.int 官方页面                                       |


复核标准：作者、年份、标题、期刊四项与 CrossRef 一致即 `verified`；任一不一致以 CrossRef 字段为权威覆写。下次更新本文件时若新增条目，请在此追加一行。

---

## 入库核对日志（2026-05-20）

> 根据 `Literature/` 子文件夹内实际文件与 `notes/` 精读笔记核对「下载」「阅读」列。


| #          | 本地 PDF                     | 精读笔记                              |
| ---------- | -------------------------- | --------------------------------- |
| A1–A4      | ✓                          | ✓（`notes/A/`）                     |
| C1, C2, C5 | ✓                          | ✓（`notes/C/`）                     |
| D2         | ✓                          | ✓（`notes/D/`）                     |
| E1         | ✓                          | ✓（`notes/E/`；Paper 2 Application） |
| F2         | ✓（`F2.2chlorine.pdf`，背景文件） | ✓（`notes/F/`）                     |
| 其余         |                            |                                   |


---

## 入库核对日志（2026-05-25）

> 下载并通读 **E3 Huang & McBean 2007** + **E5 Sansone 2026**，精读笔记入库。两篇 PDF 文件名与 literature.md 条目对应正确。


| #   | 本地 PDF                                                                                                           | 精读笔记                                                                      |
| --- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| E3  | ✓（`E-不确定性感知校准（Monte Carlo : Bayesian : GLUE）/E3-Huang, McBean (2007). Using Bayesian statistics...`）             | ✓（`[../notes/E/E3_HuangMcBean2007.md](../notes/E/E3_HuangMcBean2007.md)`） |
| E5  | ✓（`E-不确定性感知校准（Monte Carlo : Bayesian : GLUE）/E5-Sansone, Cozzolino, Padulano, Di Cristo, Del Giudice (2026)...`） | ✓（`[../notes/E/E5_Sansone2026.md](../notes/E/E5_Sansone2026.md)`）         |


---

## 验证日志（2026-05-25）

> 新增 A5（Maleki 2023）与 E5（Sansone 2026）两条；通过 CrossRef API 验证。两篇均未下载、未阅读。
>
> A5 是 A4 Hallam 2002 的 20 年后实证版（按管材/管龄分类的 full-scale k_w 测定，魁北克）；E5 是与 E3 Huang 2007 并列的最新 Bayesian/MCMC k_wall 校准工作（2026-04-29 发表）。两篇共同构成本项目研究 gap 论证的关键对照文献。


| #     | 字段  | 原值  | 修正后                                                                                                                                              | 来源                                   |
| ----- | --- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 新增 A5 | —   | —   | Maleki, Ardila, Argaud, Pelletier, Rodriguez（5 人，Université Laval / 加拿大魁北克）；2023-02-01 出版；*Water Supply* 23(2):657–670                           | CrossRef `10.2166/ws.2023.020`       |
| 新增 E5 | —   | —   | Sansone, Cozzolino, Padulano, Di Cristo, Del Giudice（5 人，意大利团队）；**2026-04-29 出版**（Engineering Proceedings vol 135 art 7，CSDU-CSSI DAYS 25 会议论文集） | CrossRef `10.3390/engproc2026135007` |


---

## 验证日志（2026-05-25 · 导师邮件追加）

> 收到导师 2026-05-25 邮件，明确推荐 8 篇阅读材料；其中 5 篇已在清单内（A1 / A3 / A4 / B1 / B2），新增 3 条（A6 / E6 / E7）。E6 是之前自清单删除的 Beven & Binley GLUE，导师亲自要求重新加入。
>
> 项目正式 scope 同步收窄：聚焦 Bristol Water Field Lab 的 3 个 DMA、10 个 chlorine monitors、first-order EPANET kinetics、ensemble-based uncertainty；明确排除 hydraulic calibration / MSX / operational optimisation。详见 `../../README.md` 与 `../../plan1.md`。


| #     | 字段  | 原值  | 修正后                                                                                                                                      | 来源                                            |
| ----- | --- | --- | ---------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| 新增 A6 | —   | —   | Vasconcelos, Rossman, Grayman, Boulos, Clark（5 人）；1997-07 出版；*Journal AWWA* 89(7):54–65                                                  | CrossRef `10.1002/j.1551-8833.1997.tb08259.x` |
| 新增 E6 | —   | —   | Beven, Binley（2 人）；1992-07 出版；*Hydrological Processes* 6(3):279–298（**自清单恢复**：之前因无 PDF 删除，现导师邮件明确要求重新加入）                                 | CrossRef `10.1002/hyp.3360060305`             |
| 新增 E7 | —   | —   | Gelman, Carlin, Stern, Dunson, Vehtari, Rubin（6 人）；2013 出版；*Bayesian Data Analysis* 3rd ed.，Chapman & Hall / CRC（**教材**，仅需 Ch 5 + Ch 11） | CrossRef `10.1201/b16018`                     |


---

## 排序变更日志（2026-05-25 · 导师推荐置顶）

> 根据导师 2026-05-25 邮件的 reading list，将 9 篇被明确推荐的文献移至各自分类**最前**，并在「收录理由」列前缀 **⭐ 导师建议（2026-05-25 邮件）** 标记 + 邮件原文短引（便于会议时直接对照）。文献**编号保持不变**（A1, A3, A4, ..., E6, E7），仅行序变化；下游 notes / verification logs 内的代号引用不受影响。


| 分类  | 新顺序                                  | ⭐ 标记数 | 优先级调整                                     |
| --- | ------------------------------------ | ----- | ----------------------------------------- |
| §A  | **A1 → A6 → A4 → A3** → A2 → A5      | 4     | 无                                         |
| §B  | **B2 → B1 → B3** → B4                | 3     | B2、B3 **P1 → P0**（导师明确"read these first"） |
| §E  | **E6 → E7** → E1 → E2 → E3 → E4 → E5 | 2     | 无                                         |


§C、§D、§F 未在导师 reading list 中出现，顺序与优先级保持不变。