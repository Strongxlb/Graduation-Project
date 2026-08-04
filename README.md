# 分组一阶余氯壁衰减的不确定性感知校准与可辨识性研究（EPANET Net3 合成三区案例）

> 本 README 为 **2026-08 修订版**，反映导师 2026-07-25 论文评审后的实际研究内容（见 [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)）。
> 中文版（本文件） ｜ English: [`README.en.md`](./README.en.md)
> 配套执行计划：[`plan1.md`](./plan1.md) ｜ 文献清单：[`background/Literature/literature.md`](./background/Literature/literature.md)

## 0. 一句话概括

在 **EPANET Net3** 基准管网上，按节点坐标把管道分为 **old / average / new 三个合成空间区**（标签是人为赋予的，Net3 并无真实管龄/管材记录），用**已知的合成真值**生成含噪观测，系统研究一阶壁衰减系数 `k_w` 的**不确定性感知校准**与**可辨识性**：数据到底能约束哪些参数、**informal GLUE 与正式似然的差距有多大**、结构/系统/自相关/截断误差如何影响估计，以及**参数不确定性如何（不）传播到运营低余氯风险图**。主分析用 **censored 正式高斯似然**，informal GLUE 全程作为对照保留——两者的对比本身是一个结果。全部实验可复现、可脚本重跑并自动校验，结果记录在 [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)，对评审意见的逐条回应见 [`REVISION_RESPONSE_MATRIX.md`](REVISION_RESPONSE_MATRIX.md)。

## 1. 项目定位

本项目是 Imperial College London **CIVE70058 Research Dissertation – Environmental**（30 ECTS / 60 CATS）的硕士毕业研究。最终产出：

- **Research paper**：2026-08-21 12:00 前提交，接近科学期刊论文，最高 12,000 words。
- **Research poster**：2026-08-28 12:00 前提交。
- 已完成的中期检查点：2026-06-19 supervisor checkpoint、2026-07-03 student checkpoint。
- **当前阶段**：导师 2026-07-25 返回论文评审 + 修改版 Jupyter notebook；正在按评审意见完成**最终修订**（Priority 1 更正 + Priority 2 方法学补强），并把实验结果整合进正文。

本仓库管理毕设期间的代码、模型、结果图表、文献笔记与论文草稿；所有关键进展经 Git 留痕。

## 2. 研究主题

工作题目（修订）：**Uncertainty-aware calibration and identifiability of grouped first-order chlorine wall-decay coefficients — a controlled EPANET Net3 three-zone study**。

核心不是「估一个数」，而是回答：**在真实可得的监测密度与测量噪声下，分区 `k_w` 到底能不能被辨识，以及这对运营风险意味着什么**。为此使用**合成真值**（synthetic truth）作为受控试验台——因为真值已知，才能严格评估可辨识性、区分「精确」与「无偏」、并做诚实的验证。关键词：

- **EPANET / WNTR**：EPANET 2.2 水质引擎 + WNTR Python wrapper（`wntr 1.4.0`）。
- **First-order chlorine decay**：一阶 bulk (`k_b`) + 一阶 wall (`k_w`)（Rossman 1994 / EPANET 2.2 Manual）。
- **分区 `k_w`（三个合成空间区）**：按节点坐标（`y ≤ 10` → average；否则 `x ≤ 26` → new，其余 → old；跨区管道归给更新的一侧）把 Net3 分为 old / average / new 三个连续区，每区一个 `k_w`。**这些标签是为构造受控真值而人为赋予的，不是 Net3 的真实管龄或管材数据**——把「多 DMA 异质性」问题落到一个可控合成案例上。
- **三套推断口径并列**：主分析是 **censored 正式高斯似然**（零截断点用 `log Φ(−μ/σ)`）；`formal_iid` 用于隔离零截断处理的影响；**GLUE（informal likelihood）**（Beven & Binley 1992）作为**对照**保留，因为草稿用的是它，而两者的差距正是本研究的核心结果之一（Mantovan & Todini 2006 / Stedinger 2008 的批评在此有了定量实例）。
- **正式可辨识性工具**：Fisher information / Cramér–Rao 下界（CRLB）、profile likelihood、AR(1) 协方差修正。
- **测量误差进入 likelihood**：Gaussian 观测噪声、系统偏置、零截断（censored likelihood），避免对「完美观测」过度自信。
- **运营风险传播**：节点低于工作阈值 `0.2 mg/L` 的时长/深度/累计缺口，并用 water age 做水力佐证。

## 3. 研究动机

供水管网余氯直接关系微生物安全。传统校准常把观测当作确定值、只报单点参数，容易给出**过度自信的参数**和**错误的风险判断**。两个被忽视的问题：

1. **可辨识性**：真实网络中监测点稀疏、误差不小，**并非所有分区 `k_w` 都能从数据里辨识出来**。若不检验，"校准成功"可能只是**先验居中**（prior centring）的假象。
2. **误差结构**：观测有系统偏置、时间自相关、以及在低余氯处的**零截断**（`C_obs = max(0, C_true+ε)`）；模型还有结构误差。这些都会让「拟合很好」与「参数正确」脱节（precise-but-biased）。

本项目用**已知真值的合成三区案例**把这两点讲透，并把结论一路推进到**运营风险图**：即便部分 `k_w` 辨识很差，风险热点是否仍稳健？`0.2 mg/L` 在本研究中是**选定的运营低余氯阈值示例**（representative operational threshold），不是法定/合规安全限。

## 4. 研究问题与目标

### 4.1 研究问题（对应已完成实验）

1. **基线与预热**：能否冻结一个可复现、且预热长度由收敛检验而非惯例决定的三区 baseline？（Step 0、1）
2. **可辨识性**：6 个监测点（每区 2 个）+ σ=0.1 噪声下，三个分区 `k_w` 分别能被约束到什么程度？（Step 2–4、7、7b）
3. **阈值/先验依赖**：behavioural 阈值怎么定才有原则？结论对阈值/先验稳健吗？（Step 3、4）
4. **误差来源敏感性**：结构误差、传感器系统偏置、`k_b` 误设（bulk–wall 补偿）、时间自相关 AR(1)、零截断，各自如何影响估计？（Step 5、7c、8、8b、9）
5. **所需传感器精度**（导师邮件问题）：要得到有用的余氯预测，传感器 σ 需要多小？（Step 6）
6. **风险传播与验证**：参数不确定性是否改变运营低余氯**风险热点排序**？风险图有无独立水力佐证？模型能否预测**未见**监测点？（Step 10、11）

### 4.2 总目标

建立一个**可复现、不确定性感知、以可辨识性为核心**的分区 `k_w` 校准与风险评估工作流，诚实地界定 GLUE 能做什么、数据能约束什么，并把参数不确定性一路传播到运营风险决策与预测验证。

## 5. 范围边界

### 5.1 范围内

- **EPANET Net3 基准网**（WNTR 自带 `.inp`），按坐标分 old/average/new 三连续区。
- **First-order** 动力学（bulk + wall）；`k_b` 固定为 `-0.5 day⁻¹`，估三个分区 `k_w`。
- **合成真值** + Gaussian 观测噪声（σ=0.1 mg/L 为**一个标准差**）；6 个监测点（每区 2 个）。
- **8192 组 scrambled-Sobol 先验抽样**，三套加权口径并列 + **正式可辨识性**（Fisher/CRLB、连续 profile、AR(1)）。
- 误差建模：系统偏置、`k_b` 误设、零截断（censored/Tobit-type likelihood）。
- 运营风险：低于 `0.2 mg/L` 的时长/深度/累计缺口 + water age 佐证 + LOO 预测验证。

### 5.2 范围外

- **不做水力校准**——需求与粗糙度信任既有模型。
- **不做 multi-species**（EPANET-MSX）、不做 TOC/DBP/生物膜耦合。
- **不做运营优化**（不优化布点/清管/加氯站）。
- 不把真实 Bristol 3-DMA 现场数据纳入本修订（本研究以 Net3 合成受控案例为载体来论证方法；真值已知是可辨识性分析的前提）。
- AI 工具仅用于代码辅助/语言润色/思路整理，按 Imperial/CEE 要求披露，不直接作为论文内容。

## 6. 方法框架与关键设定

### 6.1 冻结基线（Step 1）

- 合成真值：`k_b = -0.5 day⁻¹`（固定）；`k_w`：old `-1.0`、average `-0.1`、new `-0.05`（`m/day`）。
- 监测点（每区 2 个）：new `107/113`、old `15/145`、average `209/231`。
- 时序：**168 h 仿真、120 h 预热** → **49 个报告点 = 48 h 窗口**；观测噪声 `σ = 0.1 mg/L`。预热长度由 Step 0 的收敛检验决定而非沿用惯例（见 §6.6）；因为 `168 − 120 = 72 − 24 = 48`，残差数 `N = 6 × 49 = 294` 不变。
- 抽样：**8192 = 2¹³ 组 scrambled Sobol**（不是伪随机）——正式似然远比 informal 评分尖锐，2000 组抽样下它的有效样本量只有约 37。Sobol 的前 `2^k` 子集本身是平衡设计，这让收敛检验可以精确比较 1024/2048/4096/8192。缓存**每组在全网 92 个节点的预测**，后续实验直接复用缓存、无需重跑 EPANET。

先验范围（`m/day`）：

```
old      : [-1.5,  -0.2 ]
average  : [-0.2,  -0.04]
new      : [-0.10, -0.005]
```

### 6.2 三套加权口径（Step 1–3）

**主分析：censored 正式高斯似然。** 未截断点用高斯密度，被传感器下限截到 0 的点用左截断概率：

```
ℓ(θ) = −½ · Σ_{y>0} ((y − μ)/σ)²  +  Σ_{y=0} log Φ(−μ/σ)
```

**对照：informal GLUE 评分**（草稿用的那个），加上行为阈值：

```
GLUE:  w_i ∝ exp[ −½ · (RMSEᵢ/σ)² ] · 1[ RMSEᵢ < RMSE_thr ]
阈值:   RMSE_thr = σ · (1 + z/√(2·N_resid))     # z=1.645；σ=0.1, N=294 → 0.107
```

**为什么这不是一回事。** informal 评分等于正式高斯似然**除以 `N = 294`**——也就是假设观测误差标准差为 `σ√N = 1.71 mg/L`，是传感器噪声的 17 倍、比进水口浓度 1.0 mg/L 还大。所以它在行为集内部几乎是平的，报出来的主要是先验盒子而不是数据。

阈值**只属于对照组**：正式似然不带硬截断，因为硬截断是行为加权的特征而非似然的特征。`0.107` 的含义要说准——它是「真值在 95% 的噪声实现下会被接受」，不是参数的 95% 可信区间；`0.12` 是草稿用的较松值，保留以便复现那套配置。

### 6.6 预热长度与工具链验证（Step 0 / Step 13）

这两项不是评审意见，但是上面所有数字可信的前提。

- **Step 0 预热选择**：需求模式与泵排班都是 24 h 周期，正确判据是**逐日周期场重现**（容差事先写死）。120 h 时余氯浓度场达到预设容差，但累计缺口仍有约 **5.5%** 的周期漂移、水龄 p95 仍差 **12.8 h**——因此 120 h 是有限时域的务实选择，不是「完全周期稳态」。硬约束：泵 10 的绝对时刻控制只列到 159 h，超过 168 h 泵会永久停转。
- **Step 13 已知答案测试**：单管一阶衰减有闭式解 `C = C₀·exp(k_b·t_res)`，用来验证「以 1/day 写入、除以 86400 交给 WNTR」的系数真的被 EPANET 实现为那个系数。wall 臂只验证符号/单调/有界，不做精确解析匹配。
- **Step 14 重复噪声校准**：对同一候选库重抽 100 组噪声，检查 formal 后验均值的偏差、经验 SD 与 Case-A CRLB 之比、以及名义 90%/95% 区间覆盖率。

### 6.3 可辨识性：正式工具（Step 7 / 7b / 7c）

- **Fisher / CRLB（先验，a priori）**：`F = Jᵀ J / σ²`，用 Schur 补做边际化，评估在给定灵敏度与噪声下的**理论最小方差**。
- **Profile likelihood（后验/实用，a posteriori）**：固定一个系数、重优化其余，`ΔNLL ≤ 1.92` 给 95% 区间。
- **AR(1) 自相关**：用协方差 `Σ[t,s]=σ²ρ^|t−s|` 重算 `F=JᵀΣ⁻¹J` 与 profile，量化区间膨胀（非机械地统一乘一个因子）。

分两层解读：**(1) 受控 baseline 可辨识性**（Fisher A ↔ profile ↔ GLUE 同条件）；**(2) 现实性敏感性**（+`k_b`、+传感器偏置、AR(1)、截断）。

### 6.4 误差来源敏感性（Step 5 / 8 / 8b / 9）

结构误差（管级抖动 / 长度相关异质）、系统传感器偏置、`k_b ±20%`（bulk–wall 补偿）、零截断的 censored likelihood：

```
未截断 (obs>0): 高斯项       -½·((obs-μ)/σ)²
截断  (obs=0):  P(Y*≤0)     log Φ(-μ/σ)      # scipy log_ndtr
```

### 6.5 运营风险与验证（Step 6 / 10 / 11）

- **所需精度扫描**：σ = 0.02 / 0.05 / 0.10 / 0.15，阈值随 σ 缩放。
- **风险指标**（梯形积分于 48 h 窗口）：低于 `0.2 mg/L` 的**时长**、**最低浓度**、**累计缺口** `∫max(0,0.2−C)dt`；集合加权期望 + 5–95% 区间。
- **water age**：独立于反应系数的水力诊断，做风险格局的**物理佐证**（Spearman 秩相关）。
- **leave-one-monitor-out（LOO）**：留一个监测点、用其余 5 个校准再预测，检验样本外预测误差与带宽覆盖。

复现方式见 §9 与 [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md) 顶部「Files and how to reproduce」。

## 7. 主要发现（Step 0–14 摘要）

> 完整数据、表格与图见 [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)；对评审逐条回应见 [`REVISION_RESPONSE_MATRIX.md`](REVISION_RESPONSE_MATRIX.md)。以下为要点。

1. **「数据无法辨识 average/new」是关于评分的陈述，不是关于数据的。** 同一批观测、同一批抽样：informal GLUE（草稿阈值 `0.12`）保留了先验宽度的 **86 / 98 / 98%**，而 censored 正式似然只保留 **25 / 31 / 28%**。数据一直含有信息，是 informal 评分没有把它提取出来（Step 1–3）。
2. **正式后验宽度与 Case-A CRLB 局部一致，不是「证明估计高效」。** 单实现经验 SD 与 CRLB 相差 1–5%（比值 0.99 / 1.05 / 0.98）；100 次重复噪声下经验估计 SD / CRLB ≈ 1.04 / 1.06 / 1.12，名义 90% 覆盖约 0.85–0.89。informal 宽度是下界的约 2.8–3.1 倍，靠「更宽」而不是「更准」拿到高覆盖（Step 7 / 7b / 14）。
3. **任何阈值都修不好一个低效的评分。** 从 `0.12` 收紧到 `0.107` 对 old 只挽回约七分之一的差距、对 average/new 几乎为零；换成正式似然把三个标准差全部压到三分之一。所以阈值扫描现在被定位为「**对照组对分析者选择有多敏感**」（Step 3）。
4. **预热 24 h 不够；120 h 是有限时域务实选择，不是完全收敛。** 余氯浓度场在 **120 h** 达到预设容差，但累计缺口仍有约 **5.5%** 周期漂移；水龄周期差在 120–144 h 仍有 12.8 h，外推约 **600 h**，远超模型 168 h 上限。绝对水龄绝不能当稳态值引用（Step 0）。
5. **对称异质性不产生可检测的结构偏差；有结构的异质性才产生方向性偏移。** ±20% 对称抖动在 **25 个独立异质性场**上的结构增量是 `+0.0107 ± 0.0335`（`|均值|/标准差 = 0.32`），检测不到；把异质性与**管长**相关起来后，齐次估计向 **length-weighted proxy** 移动。这里测的是一种合成的长度相关结构，**不是** flow-path、residence-time 或 Jacobian 加权——不能说已经验证了真实的有效系数（Step 5c / 5d）。
6. **所需精度（修订后）：σ ≈ 0.10 在 formal 主口径下已经有用。** formal 在 σ = 0.10 保留先验宽度的 **27 / 30 / 29%**；原先「需要 σ ≲ 0.05」是 informal 评分的产物（同条件下 informal 报 65 / 91 / 87%）。σ ≤ 0.05 在固定 Sobol 库上是 sampling-limited（formal ESS median ≈ 21 / 1.8），只能表示方向（Step 6）。
7. **未校正的传感器偏置毁掉系数，却几乎不动全网风险排序。** node 15 注入 `+0.05` 把 old 推移 **2.19 个后验标准差**、`+0.10` 推 **3.87 个**；但即使在 ±0.10，92 节点风险排序的 Spearman 仍是 0.999、Kendall ≥ 0.988。响应是**凹**的且**不对称**，所以偏置结果必须带符号引用。六监测点双侧扫描下**标准化影响最大的并不是 node 15**，而是 average 区的 **node 231（−0.10 时 −5.94 个后验标准差）**；跨区泄漏按标准差衡量也不小（最大 2.7 个 SD），正是 Fisher 最松方向指出的 average↔new 混淆（Step 8 / 8c）。
8. **传感器漂移「就是它自己的均值」。** 把漂移建模为窗口内的线性斜坡 `b(t)=D·(t−t₀)/48`，并与**同噪声下的两个常数对照**比较：漂移造成的位移是**均值等价常数偏置**的 **0.98–0.99**（node 231）/ **0.89–0.91**（node 15），约为终值等价的一半。所以 Step 8 的常数偏置扫描可以直接迁移到漂移上（按漂移的均值取值），漂移不是需要另起炉灶的现象。偏离均值的地方由**截断**造成——斜坡只有一部分时间处在极端偏置，截断点数比同终值常数少（6→10 对 5→13）（Step 8d）。
9. **零截断：影响可测但很小，且不再局限于 old 区。** 校准用的 294 点中有 **10** 个被截到 0（old 9、average 1；完整记录 43/1014）。censored 把 old 的加权均值移动 **−0.0116**，风险排序不变（Step 9）。
10. **风险图的物理佐证与三种网络均值。** 风险与 water age 的描述性 Spearman ρ = 0.73（**空间 block bootstrap 95% `[0.455, 0.897]`**，10 个 k-means 空间块、2000 次重抽；这是保守的描述性宽度，**不是显著性区间**）；普通 p-value 与 iid 节点 bootstrap 都已删除，因为 92 个 junction 共享管道与流路。三种网络均值往相反方向走——仅消费节点更差、需求加权更好——说明风险集中于小用户（Step 10）。
11. **预测成功不能证明参数可辨识。** 留一监测点看起来很好；但去掉某区两个监测点后，该区系数退回先验中点（old → −0.850，SD 保留 100%），而预测几乎不变。空间预测和参数辨识是两个独立主张（Step 11a–d）。
12. **风险结论对预热与加权口径修正都稳健。** 12 °C baseline 21 nodes / 36.3 L/s at risk；heatwave 29 / 47.8；heat + ageing 31 / 49.4。测试范围内 +30% source dose 改善连续严重度，但未恢复 baseline demand-at-risk（Step 10 / 12）。
13. **`k_b` ±20% 的影响取决于用哪个风险指标——两个指标给出不同答案。** 正式加权、30 次噪声、按中位风险场排序。全网 Spearman 在两个指标上都高（P_bar 0.976 / 0.933；E[A] 0.980 / 0.935）。但**领先名单不同**：按**时长概率 `P_bar`** 排序时 top-6 两侧都只保留 6 个中的 4 个（Jaccard 0.50），且 k=3 时更差（**0.20**）、参考第 4 名跌到**第 20** 名——**不是** cut-off 假象；按**累计缺口 `E[A]`**（Step 10 标题表实际使用的指标）排序时，`−0.4` 下 top-6 **完全不变**，`−0.6` 下只换 1 个，且是第 6/7 名互换（143 出、129 入），top-3 与 top-5 不变。两个指标的差别有机制解释：`P_bar` 只数小时数，对阈值附近的大量节点极敏感；`E[A]` 按深度加权，领先者靠深度拉开距离。**因此「`k_b` 会/不会改变热点名单」这句话，不指明指标就没有意义。**旧结论「排序不变」的病因另有其一：它在列出三组明显不同的节点集之后写了「top nodes unchanged」，文字与自己的表格矛盾（Step 8b）。
14. **数值层面的两处修正。** 连续 profile 相对 21 点网格把 95% 半宽外扩 **15–39%**（censored 主口径）；Fisher 原始条件数 215 在先验标准化后只有 **3.2**（Step 7 / 7b）。
15. **方法论教训。** 单实现结果在审查中被推翻过两次，informal 评分在**三处**反转结论（阈值、结构误差、偏置曲率），第四处只是低估幅度而非反转。还有一类错误与方法无关：**总结句不忠实于自己上方的表格**（Step 8b）。有效防御是配对控制、对任意选择做 ensemble、用正式似然、多路径互证，以及逐行核对文字与表格。

## 8. 论文结构（对齐实际结果）

- **Introduction**：余氯安全、为什么测量不确定性会影响校准、分区 `k_w` 的可辨识性问题与本项目贡献。
- **Background / Literature**：一阶余氯衰减、EPANET/WNTR 水质模拟、GLUE 与其批评（Mantovan & Todini 2006 / Stedinger 2008）、Fisher/CRLB 与 profile likelihood、测量误差与截断。
- **Methodology**：Net3 三区设定、合成真值与噪声、GLUE + 阈值推导、Fisher/profile/AR(1)、误差敏感性（结构/偏置/`k_b`/截断）、风险指标与 LOO。
- **Results**：Step 1–11（可辨识性 → 误差敏感性 → 所需精度 → 风险与验证）。
- **Discussion**：informal GLUE 的统计低效（有 CRLB 对照的定量实例）、可辨识性梯度、precise-but-biased 只在异质性**有结构**时出现、预测成功与参数辨识必须分开、`k_b` 误设会换掉热点、所需传感器精度对水安全计划的意义、局限（AR(1) 的 `ρ` 是假设值而非估计值、**水龄在本模型的 168 h 上限内无法收敛**、sensor drift 未建模、无任何实测验证）。
- **Conclusion**：回答每个研究问题；uncertainty-aware calibration 的价值；未来工作（真实多 DMA 数据、贝叶斯分层、更长仿真达稳态水龄、更密集集合）。

## 9. 复现方式

代码在 [`Net3/`](Net3/)，conda 环境 `water-supply`（`python 3.13.12`, `numpy 2.4.2`, `scipy 1.17.1`, `wntr 1.4.0`）。[`environment.yml`](environment.yml) 声明该环境，[`environment.lock.yml`](environment.lock.yml) 是完整传递解。网络文件是冻结副本 `models/net3_frozen/Net3.inp`，import 时校验 SHA-256，所以升级 WNTR 不会悄悄改变模型。核心文件：

- [`Net3/wq_common.py`](Net3/wq_common.py)：冻结的三区 baseline 配置 + WNTR/EPANET 助手（监测点、分区、种子、先验、时序、三套加权）。
- `Net3/step1_freeze_baseline.py`：建合成真值 + 含噪观测 + **8192 组 Sobol** 候选库，缓存全网预测。
- `Net3/step3 … step14_*.py`：阈值、位移先验、结构误差、噪声扫描、Fisher/profile/AR(1)、传感器偏置、`k_b`、censored、风险、LOO、情景、已知答案、重复噪声校准。
- [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)：**所有实验的方法、表格、图与结论**（顶部有完整文件清单、推断口径约定与运行命令）。
- [`Net3/provenance.py`](Net3/provenance.py)：记录 git commit / tree hash / dirty diff hash、冻结 `.inp` 哈希、`wq_common` 与 step 脚本哈希、精确 numpy/scipy 版本，以及 **config 哈希**。
- [`Net3/validate_artifacts.py`](Net3/validate_artifacts.py)：注册声明、加权字段、数字漂移、禁用措辞等检查；**不能**证明语义一致性。
- `Net3/baseline_cache/`：缓存（`baseline.npz` 约 124 MB 等），使后续实验无需重跑 EPANET。

典型运行（`Net3/` 目录下）：

```
conda activate water-supply
cd Net3
export MPLCONFIGDIR=../.mplcache
python step0_warmup_convergence.py     # 预热收敛检验（决定 WARMUP_H）
python step1_freeze_baseline.py        # ~280 s（8192 次 168 h EPANET）
python step7b_profile.py               # 21³ 网格 + 连续 profile
python step10_risk_metrics.py          # 风险指标 + water age + 报告步长敏感性
python step11_loo.py                   # 留一监测点/分区/未监测节点验证
python step13_known_answer.py          # 解析已知答案测试
python step14_repeated_noise.py        # 100 次重复噪声校准（无 EPANET）
python provenance.py                   # 刷新 cache_manifest.json
python validate_artifacts.py           # 校验日志与产物一致
```

两个 step 脚本**不能在同一目录并行运行**：WNTR 把 EPANET 临时文件写成 `Net3/temp.inp|rpt|bin`，并发会互相覆盖。

## 10. 时间计划（修订，2026-08）

下表的「阶段」指论文工作阶段；`Step N` 一律指 `Net3/stepN_*.py` 脚本，两者不再混用编号。

| 阶段 | 状态 |
| --- | --- |
| 预热收敛检验 + 冻结基线（Step 0–1） | ✅ 完成 |
| 三套加权口径 + 阈值/位移先验（Step 2–4） | ✅ 完成 |
| 误差敏感性（结构/噪声/Fisher/偏置/`k_b`/截断，Step 5–9） | ✅ 完成 |
| 风险指标 + water age + 四层验证（Step 10–11） | ✅ 完成 |
| 温度/管龄情景 + 工具链已知答案测试（Step 12–13） | ✅ 完成 |
| 重复噪声校准（Step 14） | ✅ 完成 |
| 可复现基础设施（冻结模型、provenance、自动校验） | ✅ 完成（clean release tag 仍待做） |
| **重写 Results / Discussion / Conclusion（论文正文）** | ⏳ 进行中 |
| 压缩篇幅至 30 页、标题样式、图表编号、参考文献补 Stedinger 2008 / Mantovan & Todini 2006 | ⏳ 待做 |
| Research paper 提交 | 截止 2026-08-21 |
| Research poster 提交 | 截止 2026-08-28 |

**代码/产物侧的科学主线与 formal 主口径已对齐**；仍需在 clean working tree 上做最终 release 重跑与人工语义审查。逐条状态与仍存在的限制见 [`REVISION_RESPONSE_MATRIX.md`](REVISION_RESPONSE_MATRIX.md)。论文正文整合仍是主要剩余工作。

## 11. 工作流

- **Git/GitHub**：每阶段至少一次有意义 commit；不提交大型原始数据/临时输出/隐私数据；代码、图表、草稿保持可追溯。
- **结果留痕**：所有数值由脚本生成并写入 `baseline_cache/`；转抄进 `RESULTS_LOG.md` 的部分由 `validate_artifacts.py` 逐个数字对回产物（这一步是必要的——上一轮审查在日志里查出 93 处因重跑而过期的数字）。注意它保证的是**一致性**而非正确性：产物本身错了，它只会确认日志忠实抄录了一个错误的数字。
- **建议目录**：`background/`（文献）｜`Net3/`（代码+缓存+结果）｜`thesis/`（论文草稿与图）｜`meetings/`（会议纪要）。

## 12. AI 工具使用提醒

Imperial/CEE 允许在未被明确禁止时使用 generative AI，但提交内容必须体现自己的理解、判断与表达。若用 AI 做代码生成、语法检查、语言润色、图表说明或思路整理，需在最终材料中按学院要求披露用途并适当引用；所有 AI 产出都须经人工核查，不能替代文献阅读、模型判断或结果解释。
