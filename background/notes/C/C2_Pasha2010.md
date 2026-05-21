# C2 — Pasha, Lansey (2010) 精读笔记

> 配套文件：[`../../Literature/literature.md`](../../Literature/literature.md) §C2
> PDF 路径：[`../../Literature/C-水质模型校准（确定性方法）/C2-Pasha, Lansey (2010). Effect of parameter uncertainty on water quality predictions. J. Hydroinformatics.pdf`](../../Literature/C-水质模型校准（确定性方法）/C2-Pasha, Lansey (2010). Effect of parameter uncertainty on water quality predictions. J. Hydroinformatics.pdf)
>
> **来源标签**（2026-05-19，已通读 PDF 21 页）

---

## 0. 元数据

| 字段 | 内容 |
| --- | --- |
| Title | Effect of parameter uncertainty on water quality predictions in distribution systems—case study |
| Authors | **M. F. K. Pasha**, **K. Lansey** (corresp.) |
| Affiliation | Univ. of Arizona, Tucson |
| Journal | *Journal of Hydroinformatics* 12(1), 1–21 |
| DOI | `10.2166/hydro.2010.053` |
| 页数 | 21 |
| 优先级 | **P0** |
| 状态 | `read` |

---

## 1. Abstract（原文要点）

`[原文]` 用 **Monte Carlo simulation (MCS)** 分析稳态与非稳态下 **参数不确定性** 对水质预测的影响。不确定来源：bulk/wall decay、管径、糙率、节点需水量（含时空变异）。两系统结果表明：单参数扰动时输出 **相对稳健**；**多参数联合** 或 **流态改变**（尤其水箱/混合供水）时不确定性显著增大。**wall decay** 影响最大且最难测。对校准启示：正常工况下 **多组参数可拟合同一观测**，唯一性弱。

---

## 2. 中文摘要

本文在 EPANET 上建立 MCS 框架，对 NET2A（35 管、30 节点）与更大 Example 2 网，在 CV=0.1 下扰动 decay、水力与需求参数，考察节点余氯均值与标准差。稳态下单参数不确定性对浓度影响小；decay 系数（尤其 wall）通常主导。非稳态下流型切换导致标准差 **非加性**（全部参数不确定时反而可能低于单参数）。离水源越远、水龄越长，相对标准差越大。作者指出：正常工况校准得到的 wall 参数 **对极端工况可能不可靠**。

---

## 3. 问题

- 1990 年后 SDWA 推动 distribution **水质** 与压力同等重要 `[原文]`  
- 既有不确定性研究多针对 **水力/可靠性**（Bao & Mays 1990; Xu & Goulter 1998），**水质 MCS 很少** `[原文]`  
- Pasha & Lansey (2005) 仅有稳态；本文补 **unsteady**  

---

## 4. 方法

### 4.1 模型

- **EPANET**（Rossman 2002）+ **EPANET Toolkit** 批跑 MCS `[原文]`  
- 一阶 bulk + **global wall** decay；源/库浓度固定  
- Example 1：**NET2A**（手册网）；$k_b=-0.3$ d⁻¹，$k_w=-0.3$ d⁻¹；源 1.0 mg/L，库 0.5 mg/L `[原文]` §Application  
- 节点 26 下游层流管截断，需求 lump 至 26 `[原文]`  

### 4.2 不确定性设定

| 参数 | 分布 | CV |
| --- | --- | --- |
| bulk / wall decay | Normal | **0.1** |
| 糙率 $C_{HW}$ | Truncated normal (80–140) | 0.1 |
| 管径 | Uniform ±12.7 mm | — |
| 节点需求 | Normal（空间 $q_j^n$ + 时间 $q_{t,j}^f$） | 0.1 |
| 参数相关性 | **假设不相关** | `[原文]` |

每实验 **10,000** 次实现；decay 相关系数 PCC/RCC 对节点 12–27 报告 `[原文]` Table 2。

### 4.3 实验设计

- **稳态**：72 h 至水质稳态；单参数 vs 全参数 uncertain  
- **非稳态**：库改 tank + 三泵；24 h 循环需求；考察 node 11/24/26 等  
- **敏感性**：应急库容、需求季节型、输入 CV 0.05→0.2  

---

## 5. 主要结果

### 5.1 稳态 Example 1

- 单参数 uncertain 时，各节点浓度标准差 **整体较小** `[原文]` Fig. 3  
- **Wall decay** 的 PCC/RCC 常最高（如 node 15: wall 0.98）— 大于 bulk、糙率、需求 `[原文]` Table 2  
- **全参数同时 uncertain** 时标准差 **大于** 任一单参数（稳态 Eq. 12 梯度连续）  

### 5.2 非稳态

- 流型变化（泵/库）导致标准差 **阶跃**；此时 **全参数不确定的标准差可小于单参数**（lagging effect）`[原文]` §Conclusions 第 4 点  
- 离源远的节点（node 79 等）相对不确定性更大  

### 5.3 校准含义（Discussion 核心）

`[原文]` 强调 **identifiability 困境**：

> 合理范围的 wall decay 等参数可产生 **相似水质** → 现场余氯校准 **难以得到唯一 $k_w$**；对正常运营可接受，对 **极端工况/改运营** 风险大。

建议：**tracer + 水质同步测试**；但需求不确定仍限制 wall 估计 robustness。

---

## 6. 结论（四条 + 延伸）

1. 两系统上 **输入不确定对输出的相对影响偏小**（正常工况）。  
2. **Decay 系数**（尤其 wall）影响通常最大；流型改变时 **需求不确定** 升高。  
3. 稳定流态下，输出标准差与 **离源距离** 正相关。  
4. 非稳态下多参数不确定 **非加性**。  

额外：增大应急库容 → 下游节点相对不确定性上升；CV 从 0.05→0.1 可使输出 std **约翻倍** `[原文]` sensitivity section。

---

## 7. 符号

| 符号 | 含义 |
| --- | --- |
| $k_b$, $k_w$ | global bulk / wall 一阶衰减系数 |
| $q_j^n$, $q_{t,j}^f$ | 空间 / 时间随机需求因子 |
| CV | coefficient of variation = $\sigma/\mu$ |

---

## 8. 与本项目的关系

| 环节 | 联系 |
| --- | --- |
| **C → E 桥接** | 本文是 literature 收录理由中的「确定性校准 ↔ 不确定性分析」桥梁 |
| **先验范围** | CV=0.1 可作为 MCS/Bayesian 中 $k_b,k_w$ 先验宽度的 **文献参照** |
| **可识别性** | 支持 thesis 论点：仅 fit 余氯不足以唯一确定 wall + bulk → 需要 **观测误差模型 (D) + 贝叶斯 (E)** |
| **EPANET/WNTR** | 与 `01_demo_wntr.py` 同一工具链；NET2A 可作第二 benchmark |
| **0.2 mg/L 阈值** | 本文未用监管阈值，但讨论「小幅浓度变化可检测污染」— 与 operational residual 监测逻辑相关 |

---

## 9. 批判性阅读

**优点**：EPANET MCS 系统全面；稳态+非稳态；直接讨论 calibration identifiability。  
**局限**：
- 参数 **独立** 假设过强 `[原文]` 已承认  
- decay 仅 global 一阶，未分区 wall / 二阶 bulk  
- Example 2 细节在 PDF 后部，与 Net1/BWSN 无直接对照  
- 未纳入 **测量误差**（D2/D3）— 与本项目 gap 明确  

---

## 10. 待办

- [ ] 在 WNTR 复现 NET2A + CV=0.1 单参数 wall MCS  
- [ ] 对比 C1 点估计 $k_w$ 与 C2 后验 spread 是否覆盖  
- [ ] 读 Pasha (2006) PhD  dissertation 获取更多网详情  

---

## 11. 引用

> Pasha MFK, Lansey K. Effect of parameter uncertainty on water quality predictions in distribution systems—case study. *J Hydroinformatics*. 2010;12(1):1–21. doi:10.2166/hydro.2010.053

```bibtex
@article{Pasha2010UncertaintyWQ,
  author  = {Pasha, M. F. K. and Lansey, K.},
  title   = {Effect of parameter uncertainty on water quality predictions in distribution systems-case study},
  journal = {Journal of Hydroinformatics},
  volume  = {12},
  number  = {1},
  pages   = {1--21},
  year    = {2010},
  doi     = {10.2166/hydro.2010.053}
}
```

---

## 13. 修正记录

| # | 说明 |
| --- | --- |
| 1 | 标题中 "distribution systems" 与 "case study" 之间原文有换行，无 em dash — 引用按期刊为准 |
