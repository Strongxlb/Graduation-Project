# 分组一阶余氯壁衰减的不确定性感知校准与可辨识性研究（EPANET Net3 合成三区案例）

> 本 README 为 **2026-08 修订版**，反映导师 2026-07-25 论文评审后的实际研究内容（见 [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)）。
> 中文版（本文件） ｜ English: [`README.en.md`](./README.en.md)（英文版尚未同步到本修订）
> 配套执行计划：[`plan1.md`](./plan1.md) ｜ 文献清单：[`background/Literature/literature.md`](./background/Literature/literature.md)

## 0. 一句话概括

在 **EPANET Net3** 基准管网上，按管材/管龄把管道分为 **old / average / new 三个连续区**，用**已知的合成真值**生成含噪观测，系统研究一阶壁衰减系数 `k_w` 的**不确定性感知校准**与**可辨识性**：数据到底能约束哪些参数、GLUE 的诚实局限在哪、结构/系统/自相关/截断误差如何影响估计，以及**参数不确定性如何（不）传播到运营低余氯风险图**。全部实验可复现、可脚本重跑，结果记录在 [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)。

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
- **分区 `k_w`（material/age zones）**：按节点坐标把 Net3 分为 old / average / new 三个连续区，每区一个 `k_w`——把「多 DMA 异质性」问题落到一个可控合成案例上。
- **GLUE（informal likelihood）**：Beven & Binley 1992；本项目正面讨论其统计低效与阈值/先验依赖。
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

1. **基线复现**：能否复现三区下游监测点的余氯时序，并冻结一个可复现的 GLUE baseline？（Step 1）
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
- **GLUE**（2000 组均匀先验）+ **正式可辨识性**（Fisher/CRLB、profile、AR(1)）。
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
- 时序：72 h 仿真、24 h 预热 → **49 个报告点 = 48 h 窗口**；观测噪声 `σ = 0.1 mg/L`。
- GLUE：2000 组均匀先验抽样，缓存**每组在全网 92 个节点的预测**，后续实验直接复用缓存、无需重跑 EPANET。

先验范围（`m/day`）：

```
old      : [-1.5,  -0.2 ]
average  : [-0.2,  -0.04]
new      : [-0.10, -0.005]
```

### 6.2 GLUE 与 behavioural 阈值（Step 2–3）

informal Gaussian 加权与行为阈值：

```
w_i ∝ exp[ -½ · (RMSEᵢ / σ)² ] · 1[ RMSEᵢ < RMSE_thr ]
RMSE_thr = σ · (1 + z / √(2·N_resid))      # z=1.645 → 单侧 95% 带；σ=0.1, N_resid=294 → 0.107
```

主阈值 `0.107`（草稿曾用较松的 `0.12`，保留作对照）。

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

## 7. 主要发现（Step 1–11 摘要）

> 完整数据、表格与图见 [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)；以下为要点。

1. **只有主导的 old 系数被明显约束**：GLUE 下 old 后验明显收窄，average/new 基本停留在先验（弱信息）；草稿里「三个都恢复得不错」部分是**先验居中**造成的假象（Step 2、4）。
2. **阈值/风险稳健**：原则化阈值 `0.107`（噪声底之上 95% 带）；收紧阈值主要让 old 变尖，风险热点排序对阈值稳健（Step 3）。
3. **old 是单侧可辨识**：观测能从弱衰减一侧把 old 拉回真值附近，但强衰减侧约束很弱（Step 4/4b）。
4. **结构误差 → precise-but-biased**：对称抖动下稳健；长度相关的区内异质会让 GLUE **精确但有偏**地追随长度加权均值（Step 5）。
5. **所需精度**：σ ≲ 0.05 才能收紧决定风险图的低余氯节点；`±0.1` 只能恢复 old + 粗略风险格局；`±0.15` 基本回到先验（Step 6，回应导师邮件）。
6. **正式 vs 非正式**：理想 baseline 下 Fisher（CRLB/prior 0.25/0.29/0.29）与 profile 都认为三者可辨识；GLUE 明显更宽、更依赖先验（informal likelihood 丢了 `N` 因子的统计低效）。现实性因素（`k_b`、传感器偏置、AR(1)）会显著削弱 average/new，唯 old 相对稳健（Step 7/7b/7c）。
7. **系统误差**：node 15 注入 `+0.05` 偏置把 old 推移约 0.5 个 behavioural SD、`+0.10` 约 1.4 SD；`k_b ±20%` 通过 bulk–wall 补偿把 `k_w` 推 ∓0.03–0.04；两者都**不改变**风险热点排序（Step 8/8b）。
8. **零截断（L=0）稳健性**：校准用的 294 点中仅 8 个被截到 0（全在 old 区；完整记录 28/438）；把 0 当精确值 vs censored likelihood，`k_w`、profile、node-15 风险、热点排序**几乎一致**——原处理未实质推偏结论（Step 9）。
9. **风险图物理锚定**：时长/深度给出比单一概率更细的风险刻画；风险与 water age 的秩相关 `Spearman 0.73`（n=92, bootstrap `[0.63,0.80]`）——风险由**停留时间 + 可辨识的 old 衰减**主导（Step 10）。
10. **样本外验证**：LOO 预测未见监测点的 RMSE ≈ 噪声底 `0.1`，90% 带覆盖 92–94%，参数稳定——**old 仅在拿掉 old 区监测点时才微变**，独立印证其信息定位（Step 11）。
11. **总主线**：参数不确定性**确实传播**进风险指标的**数值**（见 5–95% 带），但在已测扰动（阈值、`k_b`、偏置、噪声）下**主要风险热点的排序稳定**。

## 8. 论文结构（对齐实际结果）

- **Introduction**：余氯安全、为什么测量不确定性会影响校准、分区 `k_w` 的可辨识性问题与本项目贡献。
- **Background / Literature**：一阶余氯衰减、EPANET/WNTR 水质模拟、GLUE 与其批评（Mantovan & Todini 2006 / Stedinger 2008）、Fisher/CRLB 与 profile likelihood、测量误差与截断。
- **Methodology**：Net3 三区设定、合成真值与噪声、GLUE + 阈值推导、Fisher/profile/AR(1)、误差敏感性（结构/偏置/`k_b`/截断）、风险指标与 LOO。
- **Results**：Step 1–11（可辨识性 → 误差敏感性 → 所需精度 → 风险与验证）。
- **Discussion**：GLUE 的保守性与统计低效、可辨识性梯度、precise-but-biased、所需传感器精度对水安全计划的意义、局限（AR(1) 使理想区间偏乐观、水龄未达稳态等）。
- **Conclusion**：回答每个研究问题；uncertainty-aware calibration 的价值；未来工作（真实多 DMA 数据、贝叶斯分层、更长仿真达稳态水龄、更密集集合）。

## 9. 复现方式

代码在 [`Net3/`](Net3/)，conda 环境 `water-supply`（`numpy 2.4.2`, `wntr 1.4.0`）。核心文件：

- [`Net3/wq_common.py`](Net3/wq_common.py)：冻结的三区 baseline 配置 + WNTR/EPANET 助手（监测点、分区、种子、先验、时序）。
- `Net3/step1_freeze_baseline.py`：建合成真值 + 含噪观测 + 2000 组 GLUE，缓存所有预测。
- `Net3/step3 … step11_*.py`：阈值、位移先验、结构误差、噪声扫描、Fisher/profile/AR(1)、传感器偏置、`k_b`、censored、风险指标、LOO。
- [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)：**所有实验的方法、表格、图与结论**（每个数字都由脚本产生，顶部有完整文件清单与运行命令）。
- `Net3/baseline_cache/`：缓存（`baseline.npz` 等），使后续实验无需重跑 EPANET。

典型运行（`Net3/` 目录下）：

```
export MPLCONFIGDIR=/tmp/mpl
python step1_freeze_baseline.py        # ~40 s（2000 次 EPANET）
python step7b_profile.py               # 建 21³ 网格
python step10_risk_metrics.py          # 风险指标 + water age
python step11_loo.py                   # 留一验证
```

## 10. 时间计划（修订，2026-08）

| 阶段 | 状态 |
| --- | --- |
| 基线复现 + GLUE（Step 1–2） | ✅ 完成 |
| 可辨识性 + 阈值/位移先验（Step 3–4） | ✅ 完成 |
| 误差敏感性（结构/噪声/Fisher/偏置/`k_b`/截断，Step 5–9） | ✅ 完成 |
| 风险指标 + water age + LOO 验证（Step 10–11） | ✅ 完成 |
| **重写 Results / Discussion / Conclusion（Step 12）** | ⏳ 进行中 |
| 图表统一/单位/压缩篇幅/Word 格式（Step 13） | ⏳ 待做 |
| Research paper 提交 | 截止 2026-08-21 |
| Research poster 提交 | 截止 2026-08-28 |

## 11. 工作流

- **Git/GitHub**：每阶段至少一次有意义 commit；不提交大型原始数据/临时输出/隐私数据；代码、图表、草稿保持可追溯。
- **结果留痕**：所有数值由脚本生成并写入 `RESULTS_LOG.md` 与 `baseline_cache/`，杜绝手工填数。
- **建议目录**：`background/`（文献）｜`Net3/`（代码+缓存+结果）｜`thesis/`（论文草稿与图）｜`meetings/`（会议纪要）。

## 12. AI 工具使用提醒

Imperial/CEE 允许在未被明确禁止时使用 generative AI，但提交内容必须体现自己的理解、判断与表达。若用 AI 做代码生成、语法检查、语言润色、图表说明或思路整理，需在最终材料中按学院要求披露用途并适当引用；所有 AI 产出都须经人工核查，不能替代文献阅读、模型判断或结果解释。
