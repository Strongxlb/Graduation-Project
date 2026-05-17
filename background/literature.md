# 文献清单 - Literature List

> 配套文件：[`../README.md`](../README.md)、[`../plan1.md`](../plan1.md)
> 本文件目的：在动手写综述前，先把要读的文献按主题分组列清楚。
> 维护规则：
> - 每条至少包含 **作者 + 年份 + 标题 + DOI/链接 + 一行收录理由**。
> - 状态字段使用：`todo`（未读）/ `skim`（略读）/ `read`（精读）/ `cited`（已引用）。
> - 优先级：`P0` 必读，`P1` 重要，`P2` 备读。
> - BibTeX 统一存入 `../thesis/refs.bib`，本文件只做导览。

---

## A. Chlorine decay 机理（bulk / wall / 影响因素）

> 目标：理解一阶/多阶衰减模型、bulk vs wall coefficient 的物理意义、温度与有机物的影响。

| # | Citation | DOI / Link | 主题关键词 | 优先级 | 状态 | 收录理由 |
| - | --- | --- | --- | --- | --- | --- |
| A1 | Rossman, Clark, Grayman (1994). Modeling chlorine residuals in drinking-water distribution systems. *J. Env. Eng.* | 10.1061/(ASCE)0733-9372(1994)120:4(803) | 一阶衰减、bulk + wall | P0 | todo | 余氯衰减建模的奠基论文，必读。 |
| A2 | Hua et al. (1999). Modelling of chlorine decay in municipal water supplies. *Water Research* | 10.1016/S0043-1354(99)00094-4 | 衰减动力学、温度修正 | P0 | todo | 奠定 bulk decay 拟合方法。 |
| A3 | Powell et al. (2000). Factors which control bulk chlorine decay rates. *Water Research* | 10.1016/S0043-1354(99)00297-9 | TOC、温度、初始浓度 | P1 | todo | 用于讨论 decay 与水质参数的相关性。 |
| A4 | _待补 - 一篇关于 wall decay 系数实测值范围的综述_ | TBD | wall coefficient | P1 | todo | 写 Methodology 时需要参考典型取值范围。 |

## B. EPANET / WNTR 工具与方法学

> 目标：掌握 EPANET 2.2 水质方程、WNTR Python API 的边界与扩展点。

| # | Citation | DOI / Link | 主题关键词 | 优先级 | 状态 | 收录理由 |
| - | --- | --- | --- | --- | --- | --- |
| B1 | Klise, Bynum, Moriarty, Murray (2017). A software framework for assessing the resilience of drinking water systems to disasters with an example earthquake case study. *Env. Modelling & Software* | 10.1016/j.envsoft.2017.06.023 | WNTR 介绍论文 | P0 | todo | WNTR 工具引用首选。 |
| B2 | Rossman, Woo, Tryby, Shang, Janke, Haxton (2020). EPANET 2.2 User Manual. *US EPA*. | https://www.epa.gov/water-research/epanet | EPANET 数值方法 | P0 | todo | 余氯传输方程权威参考。 |
| B3 | Klise et al. (2018). Water Network Tool for Resilience (WNTR) User Manual. *Sandia / EPA*. | https://wntr.readthedocs.io | WNTR API | P1 | todo | 写 Methodology 时引用。 |
| B4 | _待补 - WNTR 在水质 / 不确定性 / 校准方向的近期 case study_ | TBD | 应用案例 | P2 | todo | 补充近 5 年 WNTR 应用方向的代表作。 |

## C. 水质模型校准（确定性方法）

> 目标：理解最小二乘、加权最小二乘、可识别性、敏感性分析的标准做法。

| # | Citation | DOI / Link | 主题关键词 | 优先级 | 状态 | 收录理由 |
| - | --- | --- | --- | --- | --- | --- |
| C1 | Munavalli, Kumar (2005). Water quality parameter estimation in a distribution system under dynamic state. *Water Research* | 10.1016/j.watres.2005.07.022 | 动态校准、参数估计 | P0 | todo | 余氯参数动态校准经典案例。 |
| C2 | Pasha, Lansey (2010). Effect of parameter uncertainty on water quality predictions. *J. Hydroinformatics* | 10.2166/hydro.2010.053 | 参数不确定性传播 | P0 | todo | 桥接确定性校准与不确定性分析。 |
| C3 | _待补 - 一篇关于 sensitivity analysis (Morris / Sobol) 在 WNT 校准中的应用_ | TBD | SA / SALib | P1 | todo | Week 5 之前要看，决定 Sobol vs Morris。 |
| C4 | _待补 - 一篇关于 chlorine calibration 中观测网络设计 (sensor placement) 的综述_ | TBD | 采样点设计 | P2 | todo | Discussion 里讨论采样策略时引用。 |

## D. 测量不确定性 (DPD / colorimetric / 在线传感器)

> 目标：了解 DPD 比色法精度、典型固定/相对误差、在线探头的偏差与漂移。

| # | Citation | DOI / Link | 主题关键词 | 优先级 | 状态 | 收录理由 |
| - | --- | --- | --- | --- | --- | --- |
| D1 | APHA / AWWA / WEF (2017). Standard Methods for the Examination of Water and Wastewater, 23rd ed., Method 4500-Cl G (DPD colorimetric). | https://www.standardmethods.org | DPD 标准方法 | P0 | todo | DPD 测量精度与干扰来源的权威说法。 |
| D2 | _待补 - 一篇定量 DPD 比色法误差区间的实验研究_ | TBD | DPD precision | P0 | todo | 用作误差模型的标准差先验。 |
| D3 | _待补 - 一篇关于在线 free chlorine 传感器精度 / 漂移的论文_ | TBD | 在线传感器 | P1 | todo | 若数据来自在线探头，需要这条。 |

## E. 不确定性感知校准（Monte Carlo / Bayesian / GLUE）

> 目标：决定 Plan A (MC + 最小二乘) vs Plan B (Bayesian / MCMC) 的取舍。

| # | Citation | DOI / Link | 主题关键词 | 优先级 | 状态 | 收录理由 |
| - | --- | --- | --- | --- | --- | --- |
| E1 | Beven, Binley (1992 / 2014). The future of distributed models: model calibration and uncertainty prediction (GLUE). *Hydrological Processes* | 10.1002/hyp.3360060305 | GLUE | P1 | todo | 概率校准的早期、可读性高。 |
| E2 | Kavetski, Kuczera, Franks (2006). Bayesian analysis of input uncertainty in hydrological modeling. *Water Resources Research* | 10.1029/2005WR004368 | Bayesian / 输入不确定性 | P0 | todo | 对照 hydrology 领域怎么处理观测误差。 |
| E3 | Vrugt (2016). Markov chain Monte Carlo simulation using the DREAM software package. *Env. Modelling & Software* | 10.1016/j.envsoft.2015.08.013 | DREAM / MCMC | P1 | todo | 备用 MCMC 工具栈参考。 |
| E4 | _待补 - 一篇关于 chlorine model Bayesian calibration 的论文_ | TBD | 余氯贝叶斯校准 | P0 | todo | 若存在直接相关工作，必须引。 |
| E5 | _待补 - 一篇关于 Monte Carlo 在管网水质中的应用_ | TBD | MC 传播 | P1 | todo | Methodology 引用 baseline。 |

---

## 本周必读（Week 1 → Week 2 之间）

仅从上表选 3 篇，作为本周末到 Week 2 中段的精读对象。建议挑选时遵循「一类一篇 + 必须 P0」：

- [ ] **A1** Rossman et al. 1994 — 衰减模型基础
- [ ] **B2** EPANET 2.2 Manual — 工具方程基础（只读 Water Quality 章节即可）
- [ ] **C2** Pasha & Lansey 2010 — 参数不确定性传播（连接 T4 与 T5）

精读笔记按以下结构存到 `notes/`（待 Week 2 创建）或追加到本文件末尾：

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

- [ ] 把所有 P0 论文的 BibTeX 加到 `thesis/refs.bib`
- [ ] 找 1–2 篇 BWSN benchmark 上的余氯校准论文（用于支撑选用 BWSN 的合理性）
- [ ] 找 1 篇 Imperial / 英国管网余氯监管阈值的政策性文件
- [ ] 找 1 篇关于 free chlorine 在线监测传感器市场综述（指明 DPD vs amperometric vs 其它）
