# C5 — Ostfeld et al. (2008) BWSN 精读笔记

> 配套文件：[`../../Literature/literature.md`](../../Literature/literature.md) §C5
> PDF 路径：[`../../Literature/C-水质模型校准（确定性方法）/C5-2008-the-battle-of-the-water-sensor-networks-(bwsn)-a-design-challenge-for-engineers-and-algorithms.pdf`](../../Literature/C-水质模型校准（确定性方法）/C5-2008-the-battle-of-the-water-sensor-networks-(bwsn)-a-design-challenge-for-engineers-and-algorithms.pdf)
>
> **来源标签**（2026-05-19，已通读 PDF 13 页）

---

## 0. 元数据

| 字段 | 内容 |
| --- | --- |
| Title | The Battle of the Water Sensor Networks (BWSN): A Design Challenge for Engineers and Algorithms |
| Authors | **Ostfeld**, **Uber**, **Salomons** 等 **35 位**（多机构） |
| Journal | *J. Water Resour. Plann. Manage.* ASCE 134(6):556–568 |
| DOI | `10.1061/(ASCE)0733-9496(2008)134:6(556)` |
| 页数 | 13 |
| 活动 | 2006-08-27–29 Cincinnati, **WDSA Symposium** 第八届 |
| 优先级 | **P0** |
| 状态 | `read` |

**定位**：**传感器布点** benchmark 总结文，**不是**余氯校准论文；但 **BWSN1/BWSN2 网络** 已成为后续水质/余氯研究的 **标准 EPANET 模型来源** `[推断]`（含 Hermes 2025 C6、本项目 Net1 选型）。

---

## 1. Abstract（原文要点）

9/11 后水质 **故意污染** 威胁推动在线监测研究。优化算法很多，但 **算法 vs 人工设计** 缺乏客观对比。BWSN 邀请 **15 组** 对 **两个真实匿名化管网** 提交 5 / 20 传感器方案，用 **统一评价程序** 比较。

---

## 2. 中文摘要

BWSN 定义四类定量目标（期望检测时间、期望受影响人口、期望污染水量、检测概率），在 EPANET 2.00.10 上模拟污染注入场景。Network 1（126 节点）与 Network 2（12,523 节点）各设 Base case A 与衍生 B/C/D。15 支队伍方法从启发式到 NSGA-II、混合整数规划不等。结论：**无单一最优解**（多目标 Pareto）；**不能仅靠工程直觉**布点；不同算法常选中 **相近节点**；传感器 **不必集中在竖向设施**（源、塔、泵）。网络 INP 公开于 Exeter CWS（现多镜像为 BWSN1/BWSN2）。

---

## 3. 设计目标 $Z_1$–$Z_4$

| 目标 | 含义 | 优化方向 |
| --- | --- | --- |
| **$Z_1$** | 期望检测时间 $E[t_d]$ | min |
| **$Z_2$** | 检测前期望受影响人口 | min |
| **$Z_3$** | 检测前期望超标用水量（阈值 $C$） | min |
| **$Z_4$** | 检测概率 | max |

`[原文]` 污染质量摄入用 Murray et al. (2006) dose–response；摄入率随节点需求变化。

**重要局限**：未检测事件 **不纳入期望** → 目标有 **截断/删失偏差** `[原文]` Design Objectives 段；Krause et al. 指出未检测场景可能最关键。

---

## 4. 案例设定（Base Case A）

`[原文]` §Design Assumptions：

| 项 | 值 |
| --- | --- |
| 模拟软件 | **EPANET 2.00.10** |
| 注入 | 单点、任意节点/时刻等概率；125 L/h；230,000 mg/L；持续 **2 h** |
| 污染物 | 注入后 **保守** |
| 水质步长 | 5 min |
| $Z_2$ 参数 | $\bar q=300$ L/d cap；$\gamma=2$ L/d；$D_{50}=41$ mg/kg；$W=70$ kg |
| **$Z_3$ 阈值** | **$C=0.3$ mg/L** |
| 传感器 | 瞬时检测任意非零浓度；检测后 **立即停止暴露** |

**衍生案例**：
- **B**：注入 10 h  
- **C**：检测后 **3 h** 响应延迟  
- **D**：**双点** 同步注入  

**模拟时长**：Network 1 → **96 h**；Network 2 → **48 h** `[原文]` §Case Studies。

---

## 5. 两个 Benchmark 网络

| 网络 | 规模 | 说明 |
| --- | --- | --- |
| **Network 1** (BWSN1) | 126 nodes, 168 pipes, 1 source, 2 tanks, 2 pumps, 8 valves | 较小；全事件矩阵可枚举（Case A–C） |
| **Network 2** (BWSN2) | 12,523 nodes, 14,822 pipes, 2 sources, 2 tanks | 大网；Case A 仅 **25,054** 随机事件，为全空间一小部分 |

INP 下载：`http://www.exeter.ac.uk/cws/bwsn/` `[原文]`（现常用 BWSN1.inp / BWSN2.inp 镜像）。

**网络特性** `[原文]` §Discussion：平均污染羽 **很小**（Net2 约 **2%** 节点，许多仅 **0.2%**）；流型 24 h 内较 homogeneous — **比真实多压力分区网简单**。

---

## 6. 主要结论

1. 传感器布点是 **多目标** 问题，只能比较 **非支配解集** 的广度与相似性。  
2. **通用布点准则不可行**；直觉须由 **定量分析** 支撑。  
3. 传感器 **无需** 聚类或放在竖向资产；多算法常选 **相同/邻近节点**（Fig. 3 等）。  
4. 146 个非支配解汇总（Table 5）— 方法间仍有显著差异。  

**未来方向** `[原文]`：风险 vs 期望、传感器可靠性（误报/漏报）、运行工况与定位、删失时间处理、威胁/保护优先级加权。

---

## 7. 与本项目的关系

| 环节 | 联系 |
| --- | --- |
| **Benchmark 合法性** | 引用 C5 说明选用 **BWSN1/Net1/Hanoi** 等公开网是社区惯例 |
| **非主线** | 本文优化 **污染检测传感器**，不是余氯校准 — Discussion 可声明 sampling design 非 core |
| **EPANET 生态** | 确认 BWSN 网与 **EPANET 2.x** 标准输入；与 WNTR 兼容 `[推断]` |
| **阈值参照** | $Z_3$ 用 **0.3 mg/L** 危害阈值 — 与项目 **0.2 mg/L** operational residual（F 类）不同用途 |
| **C6 衔接** | Hermes 2025 在 Hanoi/Net1/CY-DBP 做氯浓度 PhML benchmark — 网络谱系延续 BWSN |

---

## 8. 批判性阅读

**优点**：大规模盲测、统一评价、开源网络、多机构参与。  
**局限**：
- 目标函数对 **未检测事件** 的处理有偏  
- 污染物 **保守** + 瞬时传感器 — 与 **余氯 decay / DPD 噪声** 场景不同  
- Net2 仍比真实 UK/US 巨型网简单  
- **不含** wall/bulk 校准或氯衰减参数 `[推断]`  

---

## 9. 待办

- [ ] 下载 BWSN1.inp 与当前 Net1.inp 对比节点/拓扑  
- [ ] 读 C6 (Hermes 2025) 看 Net1 在氯 benchmark 中的用法  
- [ ] 勿将 BWSN 传感器目标与 thesis 校准目标混淆 — Introduction 写清边界  

---

## 10. 引用

> Ostfeld A, Uber JG, Salomons E, et al. The Battle of the Water Sensor Networks (BWSN): A Design Challenge for Engineers and Algorithms. *J Water Resour Plann Manage*. 2008;134(6):556–568. doi:10.1061/(ASCE)0733-9496(2008)134:6(556)

```bibtex
@article{Ostfeld2008BWSN,
  author  = {Ostfeld, Avi and Uber, James G. and Salomons, Elad and others},
  title   = {The Battle of the Water Sensor Networks (BWSN): A Design Challenge for Engineers and Algorithms},
  journal = {Journal of Water Resources Planning and Management},
  volume  = {134},
  number  = {6},
  pages   = {556--568},
  year    = {2008},
  doi     = {10.1061/(ASCE)0733-9496(2008)134:6(556)}
}
```

---

## 13. 修正记录

| # | 说明 |
| --- | --- |
| 1 | 一作 **Ostfeld**（非 Artelt）；C6 一作 Hermes — 与 literature 验证日志一致 |
