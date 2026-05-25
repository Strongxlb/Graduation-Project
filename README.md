# 三 DMA 一阶余氯衰减的不确定性感知校准 — Bristol Water Field Lab

> 本 README 反映 **2026-05-25 导师邮件**确定的项目范围。
> 中文版（本文件） ｜ English: [`README.en.md`](./README.en.md)
> 配套执行计划：[`plan1.md`](./plan1.md) ｜ 文献清单：[`background/Literature/literature.md`](./background/Literature/literature.md)

## 1. 项目定位

本项目是 Imperial College London CIVE70058 Research Dissertation - Environmental 的硕士毕业研究项目，模块规模为 30 ECTS / 60 CATS。项目最终产出包括：

- Research paper：2026-08-21 12:00 前提交，论文形式接近技术/科学期刊论文，最高 12,000 words。
- Research poster：2026-08-28 12:00 前提交，用图表化方式说明研究动机、方法、结果和结论。
- 中期检查点：
  - 2026-06-19：Supervisor checkpoint / progress report。
  - 2026-07-03：Student checkpoint / reflection。

本仓库用于管理毕业设计期间的代码、模型、数据说明、结果图表和论文大纲。所有关键进展应通过 Git/GitHub 留痕，并在每周会议记录中同步。

## 2. 研究主题

工作题目：**Uncertainty-aware calibration of first-order chlorine residual decay modelling in the Bristol Water Field Lab — a three-DMA comparative study**（基于 Bristol Water Field Lab 三个 DMA 的一阶余氯衰减不确定性感知校准）。

研究使用 Imperial College / Bristol Water Field Lab 现有 EPANET 模型与 10 个 free chlorine 在线监测点。3 个 DMA 入口的实测余氯作为时变 source boundary 输入 WNTR/EPANET；下游监测点用于校准与验证。重点关键词：

- **EPANET / WNTR**：管网水力与水质模拟平台（EPANET 2.2 水质引擎 + WNTR Python wrapper）。
- **First-order chlorine decay**：仅考虑 first-order bulk (`k_b`) + first-order wall (`k_w`) + 边界层 mass-transfer 项（Rossman 1994 / EPANET 2.2 Manual）。
- **3-DMA comparative calibration**：管材、管龄异质 → `k_w` 异质 → 一个 `k_w` per DMA，再比较 cross-DMA 可迁移性。
- **Ensemble-based uncertainty**：用 GLUE（Plan A）或 Bayesian MCMC / hierarchical partial pooling（Plan B）量化参数与预测的不确定性。
- **Time-varying inlet boundary**：3 个入口监测器的实测余氯直接喂进 source pattern，**入口浓度不参与校准**。
- **DPD / colorimetric / online sensor uncertainty**：测量误差进入 likelihood，避免对"完美观测值"过度自信。

## 3. 研究动机

供水管网中的余氯浓度直接关系到饮用水微生物安全。传统余氯模型校准常以观测值作为确定值处理，但实际监测数据受传感器精度、DPD 比色法误差、采样位置、采样时间和模型结构误差影响。若忽略这些不确定性，校准结果可能给出过度自信的参数和错误的风险判断。

更关键的是：**真实管网由多个 DMA 组成，管材与管龄各异**。一个 DMA 上校准出的 `k_w` 不一定能预测另一个 DMA——这是文献里反复指出（Hallam 2002, Maleki 2023）但很少正面回答的问题。本项目利用 Bristol Water Field Lab 3-DMA 的天然多区结构，将"估一个 `k_w`"升级为：

1. **异质性问题**：3 个 DMA 的 `k_w` 之间差多少？是否有统计意义？
2. **可迁移性问题**：在 DMA-A 上校准的模型迁移到 DMA-B / C 上时，预测可靠性下降多少？
3. **不确定性是否改变结论**：当 `k_w` 带后验区间时，DMA 间的"差异"是真信号还是噪声？

会议中提到 `0.2 mg/L` 可作为 free chlorine residual 的工作阈值示例。该阈值在当前阶段仅作为建模和结果展示的占位假设，最终论文前需要与导师确认是否采用。

## 4. 研究问题与目标

### 4.1 研究问题

1. **基线问题**：基于现有 EPANET 模型 + WNTR `simulate_chlorine(kb, kw)`，能否复现 3 个 DMA 下游监测点的 free chlorine 时间序列？
2. **决定性校准**：在统一 `k_b` + 每 DMA 一个 `k_w` 的框架下，最佳拟合参数是多少？
3. **不确定性传播**：在显式建模 DPD / 在线传感器测量误差的前提下，参数后验/置信区间是什么？
4. **DMA 间异质性**：3 个 `k_w` 的后验分布是否显著不同？这种差异是否与管材/管龄信息一致（Hallam 2002 / Maleki 2023）？
5. **可迁移性**：从 DMA-A 学到的参数去预测 DMA-B / C 时，predictive RMSE 与覆盖率（CRPS）下降多少？
6. **阈值判断**：在不确定性下，节点低于 `0.2 mg/L` 的概率分布如何随空间和时间变化？

### 4.2 总目标

建立一个**可复现的、不确定性感知的、跨 DMA 比较**的 EPANET/WNTR 余氯校准工作流，输出每个 DMA 的 `k_w` 后验分布、跨 DMA 预测的可靠性指标、以及节点低于工作阈值的概率分布。

### 4.3 具体任务

- 完成文献综述：余氯衰减机理（A1/A2/A3/A4/A5/A6）、EPANET/WNTR（B1/B2/B3）、不确定性方法（E1/E3/E4/E5/E6/E7）、测量误差（D2/D3/D4/D5）、监管阈值（F1/F2）。
- 基线仿真：基于导师提供的 Jupyter notebook 跑通 `simulate_chlorine(kb, kw)`，先用 Net3 练手，再切换到 Bristol 3-DMA 模型。
- 数据组织：3 个入口监测 → time-varying source pattern；7 个下游监测 → 5 用于 calibration，2 用于 held-out validation（具体分配待 Week 5 确定）。
- **确定性校准（baseline）**：weighted least squares 估 `(k_b, k_w_A, k_w_B, k_w_C)`，目标函数 NSE / RMSE / MAE。
- **不确定性校准（Plan A）**：GLUE（Beven & Binley 1992，E6）—— Monte Carlo + likelihood 加权，得到参数与预测的 5–95% 区间。
- **不确定性校准（Plan B）**：Bayesian hierarchical model（Gelman BDA，E7 Ch5）—— 3 个 `k_w` 共享族先验，partial pooling 借力；MCMC 用 `emcee` 或 `pymc`。
- **cross-DMA 可迁移性评估**：在 DMA-A 上得到后验，分别对 DMA-B / C 做后验预测检查（PPC）。
- 结果解释：每 DMA 的 `k_w` 后验小提琴图、跨 DMA 预测的 CRPS / 覆盖率对比图、节点低于阈值的概率热力图。
- 论文写作：按 §7 结构整理。

## 5. 范围边界

### 5.1 范围内（导师邮件明确）

- 三个监测 DMA 的 EPANET 管网模型（**Bristol Water Field Lab 现有 `.inp` 文件**）。
- **First-order** chlorine kinetics（bulk + wall + mass-transfer）。
- 10 个 chlorine monitors 的连续观测：3 个用作 inlet boundary，7 个用作 calibration / validation。
- 参数校准目标：`k_b`（可能跨 DMA 共享） + `k_w` per DMA（3 个）。
- 不确定性方法：**ensemble-based**（GLUE 优先；Bayesian / hierarchical 进阶）。
- DPD / online sensor 测量误差建模（D2/D3/D4/D5 参考）。
- 结果图表、可复现实验流程、论文和 poster 所需材料。

### 5.2 范围外（导师邮件明确排除）

- **不做 hydraulic calibration**——节点需求与管段粗糙度信任既有 EPANET 模型。
- **不做 multi-species modelling**（EPANET-MSX）——不考虑 TOC、DBP、生物膜耦合。
- **不做 operational optimisation**——不优化传感器布点、不规划清管、不做 booster 优化。
- 不开发新的硬件传感器、不做完整实验室水化学实验体系。
- 不把 AI 工具输出直接作为论文内容提交；如使用 AI 进行代码辅助、语言润色或思路整理，需按 Imperial/CEE 要求披露和引用。

### 5.3 待确定（Tuesday 2026-06-02 会议清单）

- **数据交付时间与格式**：10 个监测点的实时数据何时拿到？CSV 还是 SCADA dump？采样频率？时间跨度？
- **EPANET 模型获取**：`.inp` 文件在哪？管材、管径、管龄信息齐全度？
- **`k_b` 共享假设**：3 个 DMA 是否共用同一 `k_b`（同一水源）？还是各自估？
- **"ensemble-based method" 具体定义**：导师心目中是 GLUE / ensemble Kalman / approximate Bayesian 哪一种？
- **WP（Work Package）正式结构**：WP5 = hierarchical Bayesian；WP1–WP4 如何对应？
- 是否采用 `0.2 mg/L` 作为最终论文阈值：TBD，需与导师确认。

## 6. 方法框架

### 6.1 基线建模

1. 用 WNTR 读取 Bristol 3-DMA EPANET `.inp` 模型，确认 3 个 DMA 拓扑（入口节点 + 下游监测节点编号）。
2. 把 3 个入口监测器的余氯时间序列写成 source pattern（time-varying boundary），喂给水质引擎。
3. 跑 `simulate_chlorine(kb, kw)`：设 EPANET water-quality option `CHEMICAL`、`BULK ORDER 1`、`WALL ORDER 1`，给初始 `(k_b, k_w)` 试值（如 `k_b = -0.5/day`，`k_w = -0.15 m/day`）。
4. 输出 7 个下游监测点的模拟浓度序列，肉眼对照实测，确认幅值/趋势合理。

### 6.2 确定性校准（baseline）

最小化模拟与观测的 weighted residual：

```
J(k_b, k_w_A, k_w_B, k_w_C) = Σ_{节点 i, 时间 t} [ (y_obs - y_sim) / σ_i ]²
```

其中 `σ_i` 从测量误差模型（DPD ±0.02 mg/L 或在线传感器 ±5% 满量程）来。输出单点估计 `(k_b^*, k_w^*)`，用 RMSE / MAE / NSE 评估。**这是 baseline，不是最终结果**。

### 6.3 不确定性感知校准

#### Plan A — GLUE（Beven & Binley 1992，E6）

1. 在先验范围内 LHS / 均匀抽样 `(k_b, k_w_A, k_w_B, k_w_C)` 共 `N ≈ 10⁴` 组。
2. 对每组运行 `simulate_chlorine(kb, kw)`。
3. 用 NSE 或 Gaussian likelihood 计算 likelihood weight；NSE < 阈值（如 0.6）的样本视为 non-behavioural 弃掉。
4. 加权得到参数边缘分布 + 预测 5–95% 区间。

#### Plan B — Bayesian hierarchical MCMC（Gelman BDA，E7 Ch5/Ch11）

```
k_w_d ~ Normal(μ_kw, τ_kw²)              # DMA d ∈ {A, B, C} 共享族先验
μ_kw  ~ Normal(0.15, 0.10²)              # 来自 Hallam 2002 / Maleki 2023 范围
τ_kw  ~ HalfNormal(0.05)                 # DMA 间异质性的尺度
k_b   ~ LogNormal(log 0.5, 0.5²)         # 全网共享 (水源相同假设)
y_obs ~ Normal(y_sim(k_b, k_w_d), σ_meas²)
```

用 `emcee` 或 `pymc` 跑 ≥ 4 chains × 5,000 samples（含 warmup），监控 `R̂ < 1.05`、ESS > 1000。后验输出：每 DMA `k_w` 的 50% / 95% 区间 + `τ_kw` 后验（量化 DMA 间异质性）。

### 6.4 跨 DMA 可迁移性评估

把 calibration 数据按 DMA 切分：
- 在 DMA-A 数据上得到后验 → 对 DMA-B / C 做后验预测检查（posterior predictive check）。
- 报告：每 DMA 后验预测 RMSE、CRPS、95% 区间覆盖率（calibration coverage）。
- 异质性显著 ⇒ 单一 `k_w` 模型不可迁移 ⇒ 必须 per-DMA 校准；否则可考虑 pooled `k_w` 简化。

### 6.5 结果评价

核心评价内容包括：

- 模型是否能复现 7 个下游监测点的余氯时间序列（hourly / sub-hourly 量级）。
- `k_w` per DMA 是否显著不同（用 `τ_kw` 后验是否远离 0 判断）。
- 跨 DMA 预测的可靠性（CRPS / 覆盖率）下降幅度。
- 哪些节点或时段更容易低于 `0.2 mg/L` 阈值；阈值超限概率图。
- 结果对 Bristol Water 运营的工程意义（如哪种管材最值得优先翻新）。

## 7. 论文结构

### 7.1 Introduction

需要回答：

- 为什么供水管网余氯建模重要？
- 为什么测量不确定性会影响模型校准？
- 本项目的研究问题、目标和贡献是什么？

建议内容：

- 背景：饮用水安全、消毒余氯、管网水质风险。
- 问题：传统校准忽略观测误差，可能导致错误判断。
- 贡献：建立 uncertainty-aware calibration 流程，并用 EPANET/WNTR 案例展示。

### 7.2 Background / Literature Review

需要回答：

- 余氯在管网中如何衰减？
- EPANET/WNTR 如何进行水质模拟？
- 现有研究如何处理校准和不确定性？

建议内容：

- Chlorine decay：bulk decay、wall decay、水龄、温度、有机物和管壁影响。
- Water quality modelling：EPANET 的水质传输和反应模型，WNTR 的 Python 工作流。
- Calibration methods：最小二乘、优化算法、敏感性分析。
- Uncertainty methods：sensor uncertainty、measurement error、Monte Carlo、probabilistic risk。

### 7.3 Methodology

需要回答：

- 使用什么网络模型、数据和参数？
- 如何运行仿真？
- 如何做确定性校准和不确定性感知校准？

建议内容：

- 数据和模型来源。
- 参数范围和校准变量。
- 误差模型假设。
- Monte Carlo 或概率分析流程。
- 评价指标和图表输出。

### 7.4 Results

需要回答：

- 模型运行和校准结果是什么？
- 不确定性对结果产生了什么影响？

建议图表：

- 管网拓扑与传感器/采样节点。
- 观测值与模拟值时间序列对比。
- 校准前后误差指标。
- 参数分布或敏感性结果。
- 余氯预测区间。
- 低于阈值概率的节点空间分布。

### 7.5 Discussion

需要回答：

- 结果在工程上意味着什么？
- 不确定性处理是否值得？
- 方法有什么局限？

建议讨论：

- sensor uncertainty 对校准可信度的影响。
- `0.2 mg/L` 阈值判断从确定性判断变成概率判断后的变化。
- 数据质量、模型结构、参数可识别性和真实管网适用性的限制。

### 7.6 Conclusion

需要回答：

- 本项目完成了什么？
- 得到哪些主要结论？
- 后续工作可以如何扩展？

建议内容：

- 回答每个研究问题。
- 总结 uncertainty-aware calibration 的价值。
- 提出未来工作：更多实测数据、在线传感器、贝叶斯校准、更复杂管网案例。

## 8. 时间计划

项目从 2026-05-15 左右开始，至 2026-08-21 research paper 提交约 13 周，poster 截止为 2026-08-28。

| 阶段 | 时间 | 目标 | 产出 |
| --- | --- | --- | --- |
| Week 1 | 2026-05-15 至 2026-05-22 | 明确论文结构、研究问题和工具链 | README 大纲、文献清单、初步 Git/GitHub 仓库 |
| Week 2 | 2026-05-23 至 2026-05-29 | 完成背景阅读和方法路线选择 | Introduction/Background 草稿，EPANET/WNTR 示例跑通 |
| Week 3-4 | 2026-05-30 至 2026-06-12 | 建立或整理管网模型与数据格式 | 可运行 `.inp` 模型，数据 schema，baseline simulation |
| Week 5 | 2026-06-13 至 2026-06-19 | 准备 supervisor checkpoint | 进度总结、问题清单、下一步校准方案 |
| Week 6-7 | 2026-06-20 至 2026-07-03 | 完成确定性校准并准备 student checkpoint | baseline calibration，student reflection |
| Week 8-9 | 2026-07-04 至 2026-07-17 | 加入 sensor uncertainty 和 Monte Carlo | 参数分布、预测区间、阈值概率结果 |
| Week 10 | 2026-07-18 至 2026-07-24 | 完成主要结果图 | Results 图表和初步讨论 |
| Week 11 | 2026-07-25 至 2026-07-31 | 集中写 Methodology / Results / Discussion | 论文主体初稿 |
| Week 12 | 2026-08-01 至 2026-08-07 | 完成完整论文初稿 | Full draft 给导师反馈 |
| Week 13 | 2026-08-08 至 2026-08-21 | 修改、校对、提交 research paper | 最终 research paper |
| Poster | 2026-08-22 至 2026-08-28 | 制作和提交 poster | 最终 research poster |

## 9. 工作流

### 9.1 Git/GitHub

- 使用 Git/GitHub 记录代码和文档变更。
- 每个阶段至少提交一次有意义的 commit。
- 不把大型原始数据、临时输出和隐私数据直接提交到仓库。
- 代码、图表和论文草稿需要保持可追踪来源。

### 9.2 建议目录结构

```text
codes/
  README.md
  background/          # 文献笔记、关键概念、公式整理
  data/                # 数据说明、清洗脚本、小型示例数据
  models/              # EPANET .inp 或模型配置
  src/                 # Python/WNTR 分析代码
  results/             # 图表、表格、统计输出
  thesis/              # research paper 草稿和结构
  meetings/            # 每周会议纪要
```

当前这些目录尚未全部建立，后续可按需要逐步创建。

### 9.3 云端共享文件夹

建议云端共享文件夹按以下分类整理：

- background：论文、报告、文献笔记。
- data：原始数据、处理后数据、数据说明。
- code：与 GitHub 仓库对应的代码备份或链接。
- results：可直接进入论文的图表、表格与结果。
- thesis：论文草稿、导师反馈、版本记录。
- weekly meetings：每周会纪要、问题清单、行动项。

## 10. 每周会议模板

会议形式：weekly F2F 或 Teams，优先保持固定节奏。

```markdown
## Meeting YYYY-MM-DD

### 1. 上周完成了什么？
- 

### 2. 遇到了什么问题？
- 

### 3. 我建议如何解决？
- 

### 4. 导师反馈
- 

### 5. 下周计划
- 

### 6. 需要导师确认的事项
- 
```

每次会议前应准备三件事：

1. 上周实际完成内容。
2. 当前最阻碍进展的问题。
3. 自己提出的解决方案，而不是只带问题去会议。

## 11. 当前优先事项（2026-05-25 更新）

### 已确认 ✓

- [x] 项目正式题目与范围：3-DMA + first-order + ensemble-based + 排除水力 / MSX / 运营优化（2026-05-25 supervisor email）
- [x] 文献清单 v1 完成（A1–A6 / B1–B4 / C1–C6 / D1–D5 / E1–E7 / F1–F2）
- [x] 6 篇核心论文精读笔记入库（A1 / A2 / A3 / A4 / C1 / C2 / C5 / D2 / E1 / E3 / E5 / F2）

### Tuesday 2026-06-02 会议前必做

- [ ] **跑通导师 Jupyter notebook** `simulate_chlorine(kb, kw)`（Net3 练手）
- [ ] **下载并速读** B1 Klise 2017（WNTR 论文）+ B2 EPANET 2.2 Manual（仅水质章节）+ A6 Vasconcelos 1997
- [ ] **整理给导师的问题清单**（在 `meetings/2026-06-02.md` 预填）：数据格式、`.inp` 文件、`k_b` 共享假设、"ensemble-based" 具体定义、WP 结构、阈值定义

### Week 3–4（06-02 → 06-12）

- [ ] 拿到 Bristol 3-DMA `.inp` + 10 个监测点数据
- [ ] 把 `simulate_chlorine` 从 Net3 切到真实模型并跑通
- [ ] 实现 inlet → time-varying source pattern 的数据管线
- [ ] baseline 确定性校准（WLS）

### Week 5+（M1 之后）

- [ ] Plan A 跑通：GLUE Monte Carlo + likelihood 加权
- [ ] Plan B 跑通：Bayesian hierarchical MCMC（`emcee` 或 `pymc`）
- [ ] 跨 DMA 可迁移性评估（后验预测检查）

## 12. AI 工具使用提醒

Imperial/CEE 允许在未被明确禁止时使用 generative AI 工具，但提交内容必须体现自己的理解、判断和表达。若使用 AI 工具进行代码生成、语法检查、语言润色、图表说明或思路整理，需要在最终提交材料中按学院要求披露用途并适当引用。所有 AI 生成内容都必须经过人工核查，不能替代文献阅读、模型判断或结果解释。
