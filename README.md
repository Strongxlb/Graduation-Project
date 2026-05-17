# 不确定性感知的供水管网余氯模型校准

## 1. 项目定位

本项目是 Imperial College London CIVE70058 Research Dissertation - Environmental 的硕士毕业研究项目，模块规模为 30 ECTS / 60 CATS。项目最终产出包括：

- Research paper：2026-08-21 12:00 前提交，论文形式接近技术/科学期刊论文，最高 12,000 words。
- Research poster：2026-08-28 12:00 前提交，用图表化方式说明研究动机、方法、结果和结论。
- 中期检查点：
  - 2026-06-19：Supervisor checkpoint / progress report。
  - 2026-07-03：Student checkpoint / reflection。

本仓库用于管理毕业设计期间的代码、模型、数据说明、结果图表和论文大纲。所有关键进展应通过 Git/GitHub 留痕，并在每周会议记录中同步。

## 2. 研究主题

工作题目：**不确定性感知的供水管网余氯模型校准**。

研究主线是基于 EPANET/WNTR 建立供水管网水力与水质模型，重点模拟 free chlorine residual 在管网中的衰减和空间分布，并在模型校准中显式考虑测量不确定性。会议记录中反复出现的关键词包括：

- EPANET / WNTR：管网水力与水质模拟平台。
- free chlorine residual：本项目的主要水质变量。
- water quality model calibration：校准模型参数，使模拟结果与观测数据一致。
- DPD / colorimetric method：余氯测量方法之一，存在读数和方法误差。
- sensor uncertainty：传感器或采样测量的不确定性，需要进入模型校准和结果解释。
- uncertainty-aware calibration：不只追求单一最佳参数，而是同时输出估计值及其不确定性。

## 3. 研究动机

供水管网中的余氯浓度直接关系到饮用水微生物安全。传统余氯模型校准常以观测值作为确定值处理，但实际监测数据受传感器精度、DPD 比色法误差、采样位置、采样时间和模型结构误差影响。若忽略这些不确定性，校准结果可能给出过度自信的参数和错误的风险判断。

本项目希望回答：当余氯观测值本身带有不确定性时，管网水质模型应如何校准、如何表达预测置信度，以及如何判断管网中某些节点是否可能低于余氯控制阈值。

会议中提到 `0.2 mg/L` 可作为 free chlorine residual 的工作阈值示例。该阈值在当前阶段仅作为建模和结果展示的占位假设，最终论文前需要与导师确认是否采用。

## 4. 研究问题与目标

### 4.1 研究问题

1. 如何基于 EPANET/WNTR 构建可用于余氯衰减分析的供水管网模型？
2. 如何校准余氯水质模型中的关键参数，例如 bulk decay 和 wall decay？
3. DPD/colorimetric 测量误差和 sensor uncertainty 如何影响模型校准结果？
4. 相比只输出单一校准参数，uncertainty-aware calibration 能否更可靠地解释节点余氯是否低于阈值？
5. 如何将模型结果转化为清晰的图表和论文讨论，而不只停留在代码结果？

### 4.2 总目标

建立一个可复现的 EPANET/WNTR 管网余氯模型校准流程，在校准过程中显式考虑观测不确定性，并输出余氯预测值、参数不确定性和低于阈值的概率判断。

### 4.3 具体任务

- 完成文献综述：余氯衰减机理、管网水质模型、EPANET/WNTR 应用、传感器不确定性、Monte Carlo 或贝叶斯/概率校准方法。
- 搭建模型：准备或构造 EPANET `.inp` 管网模型，明确节点、管段、水源、水龄和余氯初始条件。
- 组织数据：整理观测余氯数据、采样时间、采样位置、测量方法和测量误差假设；若真实数据暂缺，则使用合成数据或公开 benchmark 数据作为阶段性替代。
- 参数校准：围绕 bulk decay、wall decay 或其他关键水质参数建立目标函数，比较确定性校准和不确定性感知校准。
- 不确定性分析：使用 Monte Carlo 或等价概率方法传播 sensor uncertainty，输出预测区间和节点低于 `0.2 mg/L` 的概率。
- 结果解释：用图表展示空间分布、时间序列、参数敏感性、误差带、阈值超限概率，并讨论工程意义。
- 论文写作：将方法、数据、结果和局限性整理成 research paper 结构。

## 5. 范围边界

### 5.1 范围内

- 供水管网中的 free chlorine residual 模拟。
- EPANET/WNTR 作为主要建模和仿真工具。
- 余氯衰减参数校准。
- DPD/colorimetric 或传感器读数的不确定性建模。
- Monte Carlo / 概率评估，用于解释传感器误差对校准和阈值判断的影响。
- 结果图表、可复现实验流程、论文和 poster 所需材料。

### 5.2 范围外

- 不开发新的硬件传感器。
- 不做完整实验室水化学实验体系。
- 不扩展到所有水质指标；当前聚焦 free chlorine residual。
- 不把 AI 工具输出直接作为论文内容提交；如使用 AI 进行代码辅助、语言润色或思路整理，需按 Imperial/CEE 要求披露和引用。

### 5.3 待确定

- 真实管网数据来源：TBD。
- 具体 EPANET `.inp` 文件：TBD。
- 余氯观测数据格式：TBD。
- 测量误差分布形式：TBD，例如固定误差、相对误差、正态分布或截断分布。
- 是否采用 `0.2 mg/L` 作为最终论文阈值：TBD，需与导师确认。

## 6. 方法框架

### 6.1 基准模型

1. 用 EPANET/WNTR 读取或创建管网模型。
2. 运行水力模拟，确认流量、压力、水龄和边界条件合理。
3. 加入 chlorine quality simulation，定义初始浓度、源头浓度、bulk decay 和 wall decay。
4. 选取观测节点和时间窗口，生成模型预测序列。

### 6.2 确定性校准

确定性校准将观测值视为真实值，目标是最小化模拟值和观测值之间的误差。可选指标包括 RMSE、MAE、bias 或加权误差。该结果作为 baseline。

### 6.3 不确定性感知校准

不确定性感知校准将每个观测值视为一个带误差范围的估计，而不是单一精确值。可行路线：

- 为每个观测值定义测量误差模型，例如 `observed chlorine = true chlorine + measurement error`。
- 通过 Monte Carlo 对观测值或模型参数进行重复采样。
- 每次采样后重新计算校准结果或模型预测。
- 汇总参数分布、预测区间和低于阈值的概率。

输出不应只给一个“最优参数”，而应包括：

- 参数估计值及不确定性范围。
- 各节点余氯预测均值和区间。
- 节点低于工作阈值的概率。
- 不确定性来源对结论的影响。

### 6.4 结果评价

核心评价内容包括：

- 模型是否能复现实测余氯的时间和空间变化。
- 不确定性处理是否改变了校准参数和风险判断。
- 哪些节点或时段更容易低于余氯阈值。
- 结果对传感器布设、采样策略或模型使用有什么启示。

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
  results/             # 校准结果、表格、统计输出
  figures/             # 论文和 poster 图表
  thesis/              # research paper 草稿和结构
  meetings/            # 每周会议纪要
```

当前这些目录尚未全部建立，后续可按需要逐步创建。

### 9.3 云端共享文件夹

建议云端共享文件夹按以下分类整理：

- background：论文、报告、文献笔记。
- data：原始数据、处理后数据、数据说明。
- code：与 GitHub 仓库对应的代码备份或链接。
- results + figures：可直接进入论文的图表和结果。
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

## 11. 当前优先事项

- [ ] 确认导师正式项目题目和最终研究范围。
- [ ] 确认是否有真实管网、传感器或 DPD/colorimetric 数据可用。
- [ ] 找到或创建可运行的 EPANET/WNTR 示例网络。
- [ ] 明确余氯阈值是否采用 `0.2 mg/L`。
- [ ] 建立第一版文献表和背景综述框架。
- [ ] 跑通一次 deterministic calibration baseline。
- [ ] 设计 sensor uncertainty 的误差分布和 Monte Carlo 流程。

## 12. AI 工具使用提醒

Imperial/CEE 允许在未被明确禁止时使用 generative AI 工具，但提交内容必须体现自己的理解、判断和表达。若使用 AI 工具进行代码生成、语法检查、语言润色、图表说明或思路整理，需要在最终提交材料中按学院要求披露用途并适当引用。所有 AI 生成内容都必须经过人工核查，不能替代文献阅读、模型判断或结果解释。
