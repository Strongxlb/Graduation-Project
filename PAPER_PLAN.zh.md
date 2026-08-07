# 论文重构方案（Net3 壁衰减校准研究）

**状态**：2026-08-06 定稿的写作提纲，取代 `Ruixin_Peng_Draft_FINAL.docx` 的旧叙事。
**配套文件**：`REVISION_RESPONSE_MATRIX.md`（逐条审稿回应）、`Net3/RESULTS_LOG.md`（实验全记录）、
`Net3/baseline_cache/*.json`（数值来源）。
**完整性**：全部十一节已录入（图表规划与修改优先级于 2026-08-06 第二次传入后补齐）。

---

## 0. 数字核对结论（2026-08-06）

方案中引用的每一个数值都对照了 `Net3/baseline_cache/` 下的 artifact。**核心结论全部成立**，
下列九项需要在落笔时修正或补充。

### 0.1 已核实无误（抽样 40+ 项）

| 主张 | artifact 来源 | 核对 |
|---|---|---|
| prior SD 0.375 / 0.046 / 0.027 | `baseline_meta.json` | 0.37528 / 0.04619 / 0.02742 ✓ |
| formal censored −0.9876±0.0938、−0.1091±0.0142、−0.0440±0.0078 | 同上 | ✓ |
| formal SD retained 25.0% / 30.7% / 28.3% | 同上 `sd_retained` | 0.24995 / 0.30654 / 0.28308 ✓ |
| informal@0.12 SD retained 85.8% / 98.4% / 98.0% | 同上 `informal_glue_draft_thr` | 0.85813 / 0.98419 / 0.98033 ✓ |
| 4096→8192 中位数移动约 0.01 prior SD | `sampling_convergence` | 最大 0.0096（avg）✓ |
| formal displaced-prior recovery 88%–112%，宽度 25%–29% | `step4d_displaced_robust.json` | gap 0.884–1.116；sd_ret 0.248–0.289 ✓ |
| informal 的 `old ≫ new > avg` 梯度只出现在 comparator | 同上 | OLDUP@0.107：0.849 / 0.661 / 0.434 ✓ |
| continuous profile 95% 区间 old [−1.1720,−0.8106]、avg [−0.1373,−0.0821]、new [−0.0599,−0.0294] | `step7b_profile.json` | ✓，三者均覆盖真值 |
| grid 区间较连续区间窄 15%–39% | 同上 `half_width_change_vs_grid_frac` | 0.390 / 0.149 / 0.281 ✓ |
| repeated-noise empirical SD / CRLB ≈ 1.04 / 1.06 / 1.12 | `step14_repeated_noise.json` | 1.035 / 1.064 / 1.116 ✓ |
| 90% coverage 0.89 / 0.88 / 0.85 | 同上 | ✓ |
| AR(1) ρ=0.4 使 CRLB 扩大 1.44–1.49 倍 | `step7c_ar1.json` | 1.437 / 1.486 / 1.485 ✓；`crlb_over_prior` 仍 <1 |
| Case B 中 avg/new 的 CRLB 扩大幅度大于 old | `step7_fisher.json` | ×1.84 / ×1.84 vs old ×1.19 ✓ |
| σ=0.10 formal SD retained ≈27%/30%/29%；σ=0.15 ≈38%–45% | `step6_noise_sensitivity.json` | 0.270/0.295/0.291；0.381/0.449/0.431 ✓ |
| σ≤0.05 受固定候选库限制 | 同上 | ESS 中位数 1.8（σ=0.02）、20.9（σ=0.05），`sampling_limited: true` ✓ |
| 25 场 ±20% 结构增量 +0.0107±0.0335、+0.0002±0.0046、−0.0005±0.0021 | `step5c_jitter_sweep.json` | ✓ |
| 单场结果在 25 场后符号反转 | 同上 | 单场 old 增量 −0.0325，25 场均值 +0.0107 ✓ |
| 结构化异质性使 old 移动 gap 的 60%、约 1.29 posterior SD | `step5d_structured.json` | 0.6007；0.1444/0.1123 = 1.286 ✓ |
| node 15 +0.05 → 2.19 SD；+0.10 → 3.87 SD | `step8_sensor_bias.json` | 2.187 / 3.873 ✓ |
| node 231 最大 5.94 SD | `step8c_bias_bynode.json` | `max_own_shift_over_sd` = −5.941 ✓ |
| drift ≈ 0.89–0.99 × mean-equivalent 常量偏差 | `step8d_sensor_drift.json` | 0.886–0.985 ✓ |
| 10/294 clipped；censoring 使 old 移动 −0.0116 m/day | `step9_zeroclip.json` | `cal_zero` 10；`delta_median` −0.011597 ✓ |
| k_b ±20%：avg/new 1.4–1.6 SD，old 0.56–0.66 SD | `step8b_kb_sensitivity.json` | 1.409–1.577；0.564–0.665 ✓ |
| `P_bar` top-6 两方向都只保留 4 个 | 同上 | Jaccard 0.5 = 4/8 ✓ |
| `E[A]` top-6 在 k_b=−0.4 完全不变，k_b=−0.6 只发生第 6/第 7 交换 | 同上 | Jaccard 1.0；129(ref#7) 进、143(ref#6) 出 ✓ |
| sensor bias 下 `E[A]` top-6 在 23/24 arms 不变 | `step8c_bias_bynode.json` | 仅 node 15 @+0.10 变化 ✓ |
| LOO RMSE 0.092–0.103 | `step11_loo.json` | 0.0922–0.1026 ✓ |
| LOZO：old/average 回到先验中点、保留 100% 先验 SD | 同上 | k=−0.8508（中点 −0.85）、−0.1200（中点 −0.12）；`own_sd_retained` 1.000/1.001 ✓ |
| LOZO 预测 RMSE 仍约 0.10 | 同上 | 0.0999 / 0.0988 / 0.1006 ✓ |
| new 存在有限 upstream borrowing | 同上 | `own_sd_retained` 0.573 ✓ |
| 异质真值 + LOZO 下未监测节点误差 0.8%–1.2% | 同上 | 0.82% / 1.16% / 1.11% ✓ |
| water age 与风险 Spearman 0.72–0.73 | `step10_risk_metrics.json` | 0.7285(dur) / 0.7219(def) ✓ |
| demand-weighted E[D] 1.23 h < consumer-only 4.46 h | 同上 | 1.2311 / 4.4610 ✓ |
| node 145 深而短、node 129 长而浅 | 同上 `top10` | 145：12.0 h / minC 0.031；129：24.0 h / minC 0.147 ✓ |
| 情景表 21/28/29/31 节点、55.4/64.7/67.8/69.4 L/s、E[A] 0.2216/0.3645/0.5218/0.5790 | `step12_scenarios.json` | 全部逐项吻合 ✓ |
| +30% 投加后 demand at risk 仍 64.7 L/s > baseline 55.4 | 同上 | 64.7；`dosing_restores_baseline: false` ✓ |
| 暖机：severity 残余漂移 5.1%、water-age p95 仍差 12.8 h | `step0_warmup_convergence.json` | 0.05087；末周期 12.81 h ✓ |
| 单位修正前后最大相对差 2.3×10⁻⁷ | `step15_unit_equivalence.json` | 2.327×10⁻⁷ ✓（该数值以同步收紧 tolerance 为前提，方案已正确注明） |
| informal score 丢失 N 因子 ⇒ σ_eff = σ√N ≈ 1.7 mg/L | `Net3/wq_common.py:160-163` | ✓ |
| 旧稿 11 624 words、限制 12 000 words | 记忆 + `REVISION_RESPONSE_MATRIX.md` §6 | docx 实测约 11 464 words ✓ |

### 0.2 落笔时必须修正的九项

1. **删掉 Bristol Water Field Lab / 三个真实 DMA 那一行。** `Ruixin_Peng_Draft_FINAL.docx` 中
   "Bristol"、"Field Lab" 出现 **0 次**，"DMA" 仅 1 次且是 Future Work 里的一句建议。这条处理项
   针对的是不存在的内容，写进对照表只会误导。

2. **未监测节点相对误差应写 0.8%（formal），不是 "0.6%–0.8%"。**
   `step11_loo.json` 的 `mean_abs_rel_error` 中位数：formal 0.833%、informal 0.641%。
   0.6% 是 comparator 的数字。方案自己的规则要求 comparator 必须标注，这里混了两种权重。

3. **LOO 覆盖率写 0.90–0.94 是四舍五入后的结果**，实测中位数 0.898–0.939（node 113 为 0.898）。
   若要写区间，写 0.90–0.94 需接受把 0.898 进位；更稳妥是 "均在 0.86–0.96 的 IQR 内，中位数 0.90 左右"。

4. **k_b 下 informal 低估倍数是 3.8–5.5 倍，不是 "4–5 倍"。**
   逐项：old 4.38 / 4.91，avg 5.52 / 4.88，new 3.92 / 3.78。写 "接近四到五倍" 可以，写死 "4–5" 会被查。

5. ~~结构化异质性不能只报 old~~ —— **2026-08-06 已决：正文报告三个参数，主数字用 net-of-control。**
   见 §2 发现 4 与 §4.2.2 的改写。图、表、脚本文案已全部同步。

6. **传感器偏差要双侧报告。** 方案只引了正向 arm（+0.05 → 2.19 SD、+0.10 → 3.87 SD）。
   node 15 负向为 −2.59 / −3.82 SD，且 `step8_sensor_bias.json` 的 `symmetry_check` 明确记录了
   censoring 造成的不对称（|ratio| 1.14–1.19）。Figure 5A 若只画单侧，就丢掉了这个刻意测出来的效应。

7. **Case C 的 Fisher 数字用 2.24 / 1.09**，不是 RESULTS_LOG 里残留的 2.30 / 1.10
   （见 `Net3/RESULTS_LOG.md:1347` 的已知 stale 值，artifact 为准）。方案本身没引这两个数，
   但写 §4.2 时会用到。

8. **§4.1.1 的 25.0/30.7/28.3 与 §4.2.1 的 27/30/29 是两个不同的量**，前者是 seed-42 单次实现，
   后者是 30 次实现的中位数。两节相邻出现而不加说明，读者会以为数字对不上。至少加一句脚注。

9. **基线本身的 ESS = 156.7 / 8192（1.9%）应当写进 Methods 和 Limitations。**
   方案只在 §5.7.4 提了 "σ≤0.05 sampling-limited"，但正式后验在**基线**上也只有约 157 个有效样本
   （Step 12 保留 2196 draws）。这是审稿人一定会问的数，主动写出来比被问出来好。

### 0.3 方案未引用但值得进正文的三个数

- **informal GLUE 的 ESS = 4782.9（58.4%）vs formal 的 156.7（1.9%）**（`step10_risk_metrics.json`）。
  这一对数字比任何文字都更直接地说明 "informal score 几乎是平的"。
- **cross-scheme top-10 Jaccard = 0.8182 = 9/11**，即两种权重的前十名共享 **九个**节点
  （注意：`RESULTS_LOG.md:1905/2009` 写的 "eight of ten" 是错的，见记忆中的第 2 条待修项）。
- **informal GLUE 在 repeated-noise 中的 `within_over_empirical` = 4.70**，即它报告的宽度是其
  真实抽样波动的 4.7 倍——这是 "宽区间 ≠ 诚实不确定性" 的直接量化。

---

## 1. 论文定位与研究问题

### 1.1 定位

不再写成 "用 GLUE 估计三个 `k_w` 并绘制低余氯风险图"。新定位：

> 在一个可知真值、可受控施加误差的 EPANET Net3 合成试验中，研究**推断规则**和**误差结构**
> 如何决定分组余氯壁衰减系数的**实际可辨识性**，以及参数不确定性**何时会、何时不会**传递到
> 空间预测和低余氯风险排序。

三层逻辑：统计可辨识性 → 实用稳健性 → 决策稳健性。

### 1.2 核心问题

> How do inference formulation and realistic error structures affect the practical identifiability of
> grouped chlorine wall-decay coefficients, and when do the resulting parameter uncertainties alter
> spatial prediction and operational low-chlorine risk prioritisation?

### 1.3 研究问题

**RQ1 — 基线可辨识性与推断规则.** Under the controlled baseline assumptions, how much information do
the six monitored chlorine time series contain about the three grouped wall-decay coefficients, and how
does this conclusion depend on the inference formulation?
*策略*：formal / informal 对照 + displaced prior + Fisher/profile/repeated-noise 三角验证。

**RQ2 — 现实误差下的实用稳健性.** How robust is the baseline identifiability to measurement error,
temporal correlation, sensor bias and drift, bulk-decay misspecification, censoring, and within-zone
structural heterogeneity?
*策略*：noise / AR(1) / heterogeneity / bias / drift / censoring / `k_b` 逐项分解。

**RQ3 — 参数、预测与决策的关系.** Do parameter errors necessarily degrade spatial prediction or
operational risk prioritisation, and how does this depend on the chosen risk metric?
*策略*：LOO / LOZO / 未监测节点 + 多风险指标。

---

## 2. 七项核心发现

1. **原稿的 "不可辨识性" 主要由推断规则造成。** 同一观测、同一候选库：informal@0.12 保留
   85.8/98.4/98.0% 先验 SD，formal censored 压到 25.0/30.7/28.3%。
   严格结论只能是：在本合成基线、给定先验、固定 `k_b`、正确模型结构、已知噪声和六监测点条件下，
   三个分组参数均包含可提取的信息。

2. **正式似然的基线结果有五条独立证据支持**：prior contraction、displaced-prior recovery、
   Fisher/CRLB、continuous profile likelihood、100 次 repeated-noise。三者互相一致，
   但只能主张局部一致性，不能主张一般统计效率。

3. **应从 "可辨识性梯度" 改写为 "实用稳健性梯度"。** 基线下三参数相对精度相近；
   真正的差别在于对混杂因素的稳健性：加 `k_b` 后 avg/new 的 CRLB 扩大约 1.84 倍而 old 仅 1.19 倍；
   `k_b` 误设 ±20% 时 avg/new 移动 1.4–1.6 SD 而 old 仅 0.56–0.66 SD；加六个 monitor offsets 后
   avg/new 的实用可辨识性显著恶化（Case C：avg 2.24、new 1.09 倍先验 SD）。

4. **结构误差是否造成偏差，取决于异质性是否有结构。** 25 个 ±20% 对称、均值为零的场没有产生
   超过场间变异的系统偏差（增量均值仅为场间 SD 的 0.32/0.04/0.24 倍）；与长度相关的异质性则使
   **三个系数都发生同量级位移**，而拟合残差仍接近噪声水平。

   位移幅度：old / average / new 分别为 **−1.55 / −1.89 / −1.65** 基线后验 SD（单次实现，
   净控制），三者同量级。

   **走过差距的比例必须用 30 次噪声实现的中位数，不能用单次实现。**
   `CORR=0.50` 时 raw 中位数 86% / 112% / 92%（净控制 91% / 73% / 130%），
   而单次实现 raw 为 60% / 147% / 45%（净控制 65% / 108% / 83%）。
   净控制 5–95 区间为 old [17%, 151%]、average [−45%, 205%]、new [34%, 216%]——**大幅重叠，
   分区之间没有被分辨**。跨 `CORR` 0.25/0.50/0.75 三档，中位数始终在 0.74–1.26（raw）区间内，
   `CORR=0.75` 时三个 raw 区间全部排除零。

   > ⚠ **2026-08-06 更正**：本节曾一度写成"average 略微越过 proxy"。那是**单次噪声抽样的产物**——
   > 30 次中位数下越过 proxy 的是 **new** 而不是 average。任何分区之间的排序都不可主张。
   > 这正是 §5.6 记录过两次的失败模式，第三次。

   可支持的表述：*三个系数都沿 length-weighted 方向移动，中位走过比例接近 1。*
   不可支持的：*哪个分区越过 / 不足；proxy 不是共同终点。*
   proxy 不是 estimand 这条边界仍然成立，但**理由是 length ≠ residence time**，不是 overshoot。
   本研究没有计算 sensitivity/flow/residence-time/Jacobian 加权的有效系数。

5. **系统偏差比随机误差危险数倍，但参数损坏不必然破坏风险图。** node 15 +0.10 mg/L → old 移动 3.87 SD；
   node 231 −0.10 → 本区参数移动 5.94 SD，且跨分区污染（node 107 偏差使 avg 移动 1.59 SD）。
   然而 24 个 bias arms 中 `E[A]` top-6 有 23 个完全不变，Spearman ≥ 0.9993。

6. **良好预测不能证明参数被识别。** LOO RMSE 0.092–0.103 mg/L；但 LOZO 中 old/average 在失去本区
   两个监测点后**完全回到先验中点、保留 100% 先验 SD**，预测 RMSE 仍约 0.10。
   原因是先验靠近真值、输出对部分参数组合存在补偿、留出指标无法区分 "正确参数" 与 "正确预测"。

7. **风险稳定性必须同时说明指标和比较尺度。** `k_b ±20%`：全网 Spearman 0.93–0.98，
   但 `P_bar` top-6 两方向都只保留 4 个节点；`E[A]` top-6 在 −0.4 时完全不变、
   在 −0.6 时只发生第 6/第 7 名交换。持续时间型指标对接近阈值的节点敏感，累计缺口指标强调深度。

---

## 3. 贡献与主张边界

### 3.1 四项贡献

1. **Inference contribution** — 在同一观测、先验和候选库上定量展示 informal RMSE-based GLUE score
   与 censored Gaussian likelihood 对信息利用程度的差异。
   *落笔建议*：不要只写 "正式似然更窄"（那是 Stedinger 2008 / Mantovan & Todini 2006 的已知结论，
   会被批为教科书内容）。要写**结论反转**：recovery 随方向和阈值变化、`k_b` 敏感度被低估 3.8–5.5 倍、
   结构偏差被掩盖、报告宽度是真实抽样波动的 4.7 倍。
2. **Identifiability contribution** — 五种诊断联用，区分理想基线可辨识性与现实实用稳健性。
3. **Robustness contribution** — 系统分解随机噪声、时间相关、系统偏差、漂移、censoring、
   `k_b` 误设与结构异质性。
4. **Decision contribution** — 证明参数识别、空间预测和运营风险排序不能互相替代。

复现工具、单位检查、known-answer test、provenance、artifact validation 属于**可信度支撑**，
不与上述并列为 novelty。

### 3.2 主张边界

| 可以主张 | 不能主张 |
|---|---|
| 本研究实现的 informal GLUE score 没有充分利用 294 个残差 | GLUE 方法整体无效 |
| 三个 `k_w` 在受控合成基线下均有可辨识信息 | 三个壁衰减参数在真实管网中普遍可辨识 |
| 正式似然在合成生成模型下接近无偏并与局部 CRLB 一致 | 已证明估计器普遍有效或达到全局统计效率 |
| 对称均值为零异质性在本案例中未造成可检测系统偏差 | 管网异质性通常无关紧要 |
| 长度相关异质性使估计向 length-weighted proxy 移动 | 估计量等于真实的 hydraulic effective coefficient |
| 内部留出预测表现良好 | 已完成真实外部验证 |
| 0.2 mg/L 是本研究采用的示例运营阈值 | 0.2 mg/L 是本文证明的法律安全界限 |
| 风险排序在特定指标和扰动下较稳健 | 该网络 "安全" 或风险图普遍可靠 |
| 温度/老化为 stress-test scenarios | 已预测真实热浪或真实管龄老化后果 |
| water age 与风险相关 | water age 是对余氯风险的独立实测验证 |

---

## 4. 标题

**首选**

> **Inference-Rule Dependence, Practical Identifiability, and Risk Propagation in Grouped Chlorine
> Wall-Decay Calibration: A Controlled EPANET Net3 Study**

**备选**

1. From Parameter Identifiability to Operational Risk: Uncertainty-Aware Calibration of Grouped
   Chlorine Wall Decay in EPANET Net3 —— 工程可读性强，但不体现推断规则差异。
2. When Good Predictions Do Not Identify Parameters: Grouped Chlorine Wall-Decay Calibration in a
   Controlled Distribution-Network Study —— 记忆点强，但会弱化结构误差与风险指标部分。
3. Robustness of Grouped Chlorine Wall-Decay Calibration to Measurement and Model Error: An EPANET
   Net3 Case Study —— 覆盖 RQ2，但丢掉 RQ1 和 RQ3。
4. Likelihood Choice and Low-Chlorine Hot-Spot Ranking in Uncertainty-Aware Distribution-Network
   Calibration —— 易被误读为以风险制图为主体。

---
## 5. 章节框架（严格按官方 layout，四个编号一级标题）

课程说明书规定的 layout 是 Abstract → Introduction → **Method and approach** →
**Results and discussion** → Conclusions → Acknowledgements and References → Appendices。
因此取消原方案的独立 Background 与独立 Discussion：Background 并入 Introduction 与 Method；
Discussion 分散到各 Results 小节的即时解读，加 §3.6 承接综合讨论、局限与 future work。

正文只编号 1–4；Abstract、Acknowledgements、AI statement、References 不编号。

```
Abstract
1. Introduction
2. Method and approach
3. Results and discussion
4. Conclusions
Acknowledgements
Statement on the use of generative AI
References
Appendices A–H
```

### Abstract（230–250 words）

五件事：①问题——分组 `k_w` 校准结果可能同时受推断公式、测量误差与模型结构影响；
②做了什么——Net3 合成三区、已知真值、六监测点，对比 censored Gaussian likelihood 与 informal
GLUE，并用 Fisher / profile / repeated-noise 三角验证，再做误差敏感性与风险传播；
③核心结果——formal likelihood 明显提取出三个参数的信息，informal 的宽分布主要反映 score
formulation；sensor bias、`k_b` 误设与 structured heterogeneity 可显著移动参数；良好预测与稳定风险图
不能自动证明参数正确；④运营意义——参数识别、预测准确与风险优先级必须分开验证，排序稳定性取决于
所用风险指标；⑤范围——controlled synthetic study，非 field validation，情景是 stress tests。

**四个数字锚点**：formal 保留 25%–31% prior SD；informal 保留 86%–98%；repeated-noise
empirical SD/CRLB 1.04–1.12；`k_b` 或 sensor bias 可移动参数 1–6 posterior SD 而预测/风险排序未必同步。

**避免**：Step 编号、罗列全部实验、完整参数表、所有情景数字、"GLUE is invalid"、
"the network is safe/unsafe"、把 0.2 mg/L 写成法规限值。

---

### 1. Introduction（1 300–1 500 words）

原独立 Background 全部压入本节，但每段文献必须直接服务于研究空白，不写 dissertation 式综述。
识别性三分类与风险指标的**形式定义**移到 §2.4 与 §2.6，本节只作概念铺垫。

- **1.1 Chlorine residual modelling in distribution networks.** 余氯的工程意义；bulk decay、
  wall decay、输运与停留时间的共同作用；EPANET 一阶反应；`k_b` [day⁻¹] 与 `k_w` [m/day] 的区别；
  `k_w` 为何需要反演；为何用 grouped coefficients 而非逐管估计。
  *核心论点*：Chlorine calibration is not curve-fitting; it is an inverse problem whose parameters
  are then used for spatial prediction and operational risk screening.
  *文献*：Rossman；Vasconcelos；Hallam；Powell；EPANET/WNTR；grouped wall coefficient calibration。
  *避免*：过多饮用水一般背景；把 old/average/new 说成 Net3 真实管龄或材质；提前介绍全部实验。
- **1.2 Uncertainty and identifiability in chlorine-model calibration.**
  - 1.2.1 *Measurement and model uncertainty*：random noise、sensor bias、drift、时间相关、
    reporting floor、`k_b` 不确定性、grouped-model 结构误差、within-zone heterogeneity。
    重点不是清单，而是：即便拟合很好参数仍可能有偏；即便参数有偏预测也可能仍准。
  - 1.2.2 *Parameter identifiability*：a-priori/local、practical/a-posteriori、prior dominance、
    predictive adequacy、repeated-sampling calibration。说明为何仅报 RMSE、best-fit 参数或
    "posterior mean 接近真值"都不足以证明参数被识别。
  - 1.2.3 *Uncertainty propagation to decisions*：全网 Spearman、top-k membership、
    absolute severity 是三个不同的稳定性问题。
- **1.3 Methodological gap**（本节核心）。
  - *Gap 1*：推断规则可能制造"不可辨识"——同一观测同一候选库下两种公式给出完全不同的 prior
    contraction，因此不能在未审查推断公式的情况下把宽分布解释成"数据无信息"。
  - *Gap 2*：理想可辨识性 ≠ 实际稳健性——加入 `k_b`、sensor offsets、AR(1)、structured
    heterogeneity 后结论可能明显减弱。
  - *Gap 3*：prediction、parameters 与 risk decisions 常被混为一谈。
- **1.4 Aim, research questions and contributions.**
  - 1.4.1 *Aim*：This study investigates how inference formulation and realistic error structures
    affect the practical identifiability of grouped chlorine wall-decay coefficients, and whether the
    resulting parameter uncertainty propagates to spatial prediction and operational low-chlorine
    risk prioritisation.
  - 1.4.2 *RQ1–RQ3*（见 §1）。
  - 1.4.3 *Contributions*：四项（见 §3.1）。
  - 1.4.4 *Scope*：synthetic Net3；synthetic location-based zones；six monitors；first-order
    chemistry；no hydraulic calibration；no field observations；no external validation；
    temperature/ageing/dosing 为 illustrative stress tests。

---
### 2. Method and approach（2 500–2 800 words）

只回答"如何做"，不写结果。与 §3 严格一一对应（见本节末的对照表）。
**最容易犯的错是 Method 与 Results 重复**：Method 写"如何选 120 h"，Results 写"120 h 时哪些判据
过了、哪些没过"；Method 写"两种规则用同一候选库"，Results 写"保留比例分别是多少"。

- **2.1 Study framework and controlled Net3 system**
  - 2.1.1 *EPANET Net3 network and hydraulic model*：Net3 规模；WNTR/EPANET；source 与 tanks；
    水力设置（hydraulic 3600 s、report 3600 s、quality 300 s）；**不做 hydraulic calibration**。
  - 2.1.2 *Synthetic three-zone wall-decay representation*：old/average/new 三个 synthetic zones；
    zone assignment rule 与跨区管道归类；三个 true `k_w`；`k_b = −0.5 day⁻¹` 固定。
    **强调标签不是真实 pipe age/material 记录。**
  - 2.1.3 *Monitoring configuration*：六监测点 107、113（new）/ 15、145（old）/ 209、231（average）；
    每区两个及其理由；每点 49 个观测；合计 294 residuals。→ **Table 1**、**Figure 1A**
- **2.2 Forward simulation and synthetic observation generation** ←→ §3.1
  - 2.2.1 *Forward chlorine simulation*：给定 true `k_w`、fixed `k_b`、inlet 与 tank initial
    chlorine，运行 EPANET chlorine transport 生成 $C_\text{true}(n,t)$；保存六条 monitor 轨迹
    与全网轨迹。**不写哪个节点最危险、哪个监测点响应最大——那是 Results。**
  - 2.2.2 *Warm-up and assessment-window selection*：**写如何判断 warm-up 足够**——六条预先声明的
    cyclostationarity 判据（tank level、monitor chlorine、network p95 chlorine、tank chlorine、
    risk-severity change、water-age change），逐周期比较 cycle k 与 k+1，取满足全部浓度判据的
    最早 warm-up。最终配置：168 h / 120 h / 120–168 h 评估窗、49 reports、48 intervals。
    **具体数值（5.1% 漂移、12.8 h 水龄差）属于 §3.1.2，不在此处给。**
  - 2.2.3 *Synthetic measurement-error model*：
    $C_\text{obs} = \max[0,\ C_\text{true} + \epsilon]$，$\epsilon \sim N(0,\sigma^2)$，
    baseline $\sigma = 0.1$ mg/L。写明 σ 是 **one standard deviation**；non-negative floor；
    零值为 censored observations；baseline seed 与 repeated-noise 用不同 seeds。
    **实际出现多少零值、realised noise RMSE、最优拟合是否触及噪声底 → §3.1.3。**
  - 2.2.4 *Numerical and unit verification*（**150–250 words**）：mg/L ↔ WNTR kg/m³ 边界转换；
    quality tolerance 同步缩放；single-pipe known-answer test；wall-reaction 单调性检查；
    frozen network file；report timestep 验证。这是可信度保障不是研究主线，详情 → **Appendix B**。
- **2.3 Parameter sampling and inference formulations** ←→ §3.2
  - 2.3.1 *Priors and Sobol candidate library*：三维先验箱；8192 scrambled Sobol；
    **同一候选库供全部权重规则使用**；全网预测缓存；2^k sampling convergence。
  - 2.3.2 *Censored Gaussian likelihood*（primary）：给出公式；无 behavioural threshold；
    uniform priors；log-sum-exp 正规化；输出 weighted mean / SD / quantiles / ESS。
  - 2.3.3 *Formal iid Gaussian comparator*：仅在零值处理上不同，**用于隔离 censoring 的影响**。
  - 2.3.4 *Informal GLUE behavioural comparator*：pseudo-likelihood 与 indicator；
    thresholds 0.107 / 0.110 / 0.120；**仅作 comparator**。
    禁用 "baseline GLUE"、作为头条的 "GLUE posterior"、泛指全部 ensembles 的 "behavioural ensemble"。
- **2.4 Identifiability analysis** ←→ §3.2
  - 2.4.1 *Prior contraction*：定义 $R_\text{SD} = \sigma_\text{post}/\sigma_\text{prior}$。
    **术语固定为 SD retained / prior-SD retention，禁用 prior width retained。**
  - 2.4.2 *Displaced-prior tests*：**必须准确描述两个 arm**——
    *DOWN*：三个先验同时向 stronger decay 移动一个 prior SD；
    *OLDUP*：**只有 old** 向 weaker decay 移动，average 与 new **保持 DOWN 的先验**，
    因此这是 old 的方向检验而非第二次三参数试验；非正上界使 old 的实际位移降至约 0.92 prior SD。
    30 次噪声实现。
  - 2.4.3 *Fisher information and CRLB*：Case A / B / C；numerical Jacobian；按参数尺度的有限差分；
    Schur complement；CRLB 以 prior SD 归一。
  - 2.4.4 *Continuous profile likelihood*：固定一个、优化其余两个；ΔNLL ≤ 1.92；Brent bisection
    求连续端点；**coarse grid 只作可视化，不得作为区间**。
  - 2.4.5 *Repeated-noise calibration*：100 次独立噪声；同一候选库；bias；empirical SD；
    CRLB 比较；名义覆盖率；**shared-library limitation**。
- **2.5 Robustness to measurement and nuisance errors** ←→ §3.3
  - 2.5.1 *Sensor precision*：σ = 0.02 / 0.05 / 0.10 / 0.15；30 realisations；ESS 与 sampling limit。
  - 2.5.2 *Temporal autocorrelation*：AR(1) ρ = 0.4 与 ρ sweep。**与 2.5.1 分开，因为一个是测量精度、
    另一个是协方差结构。必须写明 ρ 是 assumed value，不是估计值。**
  - 2.5.3 *Sensor bias and drift*：双侧常量偏差；六监测点 sweep；线性 drift；
    mean-equivalent 与 end-equivalent 对照。
  - 2.5.4 *Zero censoring*：censored vs exact-zero likelihood。**单独列出，因为它对应 primary
    likelihood 的设计选择。**
  - 2.5.5 *Bulk-decay misspecification*：fitted `k_b = −0.4 / −0.5 / −0.6`，观测仍在 −0.5 生成；
    30 realisations。
  - 本节所有参数偏移统一以 **baseline posterior SD** 标准化，并写明其定义（homogeneous baseline 下
    30 次实现的 within-realisation posterior SD 中位数）。
- **2.6 Structural heterogeneity experiments** ←→ §3.4
  —— **从一般 robustness 中独立出来**，因为它已成为独立的研究发现。
  - 2.6.1 *Symmetric within-zone heterogeneity*：per-pipe jitter；jitter = 0 control；
    ±20% / ±35% / ±50%；±20% 下 25 个独立场。
  - 2.6.2 *Length-correlated structured heterogeneity*：区内长管衰减更强；**算术均值固定**；
    length-weighted proxy 移动；仍用均质分组模型拟合；同一噪声；减去 homogeneous baseline offset；
    CORR dose-response 0 / 0.25 / 0.50 / 0.75 × 30 次噪声。
  - 2.6.3 *Structural-effect metrics*（**定义放这里，Results 不再解释**）：
    raw bias $\Delta k_\text{raw} = \hat k_{w,\text{struct}} - k_{w,\text{arith}}$；
    net-of-control shift $\Delta k_\text{struct} = \Delta k_\text{raw} - \Delta k_\text{hom}$；
    standardised shift $Z_\text{struct} = \Delta k_\text{struct}/\sigma_\text{baseline}$；
    proxy-gap fraction $f_\text{proxy} = \Delta k_\text{struct}/(k_{w,\text{length}}-k_{w,\text{arith}})$。
    **必须写明报告口径**：$Z_\text{struct}$ 报单次实现；$f_\text{proxy}$ **报 30 次噪声的中位数与
    5–95 区间**，因为单次抽样无法给分区排序。
    并声明：length-weighted value is an illustrative directional proxy, not the hydraulically
    effective coefficient, an estimand, or a bound.
- **2.7 Prediction validation** ←→ §3.5
  - 2.7.1 *Leave-one-monitor-out*；2.7.2 *Leave-one-zone-out*；
    2.7.3 *Unmonitored-junction validation*（20 个 never-calibrated junctions）；
    2.7.4 *Validation under heterogeneous truth*。
    统一报 parameter shift、prior-SD retention、predictive RMSE、coverage、unmonitored relative error。
- **2.8 Operational risk assessment** ←→ §3.6
  - 2.8.1 *Low-chlorine metrics*：`P_min`（48 h 内至少一次低于阈值）、`P̄ = E[D]/48`、`E[D]`、
    `E[A]`、minimum concentration。`C_crit = 0.2 mg/L` **必须称 selected representative
    operational threshold**，不是 legal safety limit。
  - 2.8.2 *Water-age and demand-based interpretation*：water age 作为 hydraulic diagnostic；
    unweighted / consumer-only / pattern-aware demand-weighted 三种汇总。
  - 2.8.3 *Ranking robustness*：**提前定义 Spearman、Kendall、top-k Jaccard**，
    使 §3.6.2 不必重复解释统计量。
  - 2.8.4 *Temperature, ageing and dosing stress tests*：12 / 16 / 20 °C；20 °C + ageing；
    Arrhenius scaling；activation-energy uncertainty；source 1.00 / 1.15 / 1.30 mg/L；
    common random numbers。**ageing multipliers are illustrative；scenarios are stress tests；
    dosing 是 control-measure evaluation 而非运营建议。**

### Method ←→ Results 一一对应

| Method | Results |
|---|---|
| 2.1–2.2 正向系统与观测生成 | 3.1 Forward baseline and synthetic observations |
| 2.3–2.4 推断规则与可辨识性 | 3.2 Inference formulation determines apparent identifiability |
| 2.5 测量与 nuisance 误差 | 3.3 Practical identifiability under measurement and nuisance errors |
| 2.6 结构异质性 | 3.4 Structural heterogeneity and grouped effective parameters |
| 2.7 预测验证 | 3.5 Predictive accuracy is not parameter identification |
| 2.8 运营风险 | 3.6 Propagation to operational low-chlorine risk |
| —— | 3.7 Integrated implications, limitations and future work |

---

### 3. Results and discussion（5 400–5 900 words）

**每个结果后立即解释**，不再把解释全部留到独立 Discussion。
每个三级小节四段式：①研究问题 → ②数值结果 → ③解释与文献联系 → ④适用边界与下节衔接。

- **3.1 Forward-model baseline and synthetic observations（650–720 words）** ←→ 2.1–2.2 ✅ 已完成
  - 3.1.1 *Baseline chlorine dynamics across the monitored network*。全网中位数 0.761、
    5–95 为 0.168–0.956；六监测点均值 0.845 / 0.827 / 0.717 / 0.374 / 0.251 / 0.355；
    21/92 节点跌破 0.2。**关键观察**：node 231 低于 node 145 尽管系数更弱——浓度顺序不是分区的
    干净签名，停留时间与位置作用同样大。→ **Figure 1**
  - 3.1.2 *Warm-up and assessment-window adequacy*。三条浓度判据 120 h 首次通过；
    **water age 与 risk deficit 在 168 h 内从未通过**（p95 水龄末周期仍差 12.8 h、缺口漂移 5.1%）；
    pump 10 的绝对时间控制只列到 159 h 因此时域不可延长。
    **写明不对称后果**：§3.2–3.4 的推断结果建立在已收敛的浓度场上；§3.6 的绝对水龄与绝对严重度
    继承时域依赖，只用于情景间比较，绝不作为标定量值。
  - 3.1.3 *Signal and noise characteristics of the synthetic observations*。294 residuals；
    噪声 RMSE 0.0973 而候选库最优 0.0971——**库中已有拟合到噪声底的成员，拟合优度本身几乎不含信息**，
    这是 §3.5 precise-but-biased 的量化基础；node 107 的 σ 占均值 12%、node 15 占 40%；
    10 个零值全部落在 old（9）与 average（1）区。
- **3.2 Inference formulation determines apparent identifiability（1 100–1 180 words）** ←→ 2.3–2.4 ✅ 已完成
  - 3.2.1 同一观测三种权重规则 → **Table 2**、**Figure 2**
  - 3.2.2 阈值不能替代被省掉的信息因子（DOWN / OLDUP 两个 arm 须分开陈述）→ **Appendix C**
  - 3.2.3 三种进一步诊断与基线一致 → **Figure 3**
- **3.3 Practical identifiability under measurement and nuisance errors（880–960 words）** ←→ 2.5
  - 3.3.1 *Sensor precision and temporal autocorrelation* → **Figure 4**
  - 3.3.2 *Sensor bias, drift and censoring* → **Appendix F**
  - 3.3.3 *Bulk–wall compensation*
- **3.4 Structural heterogeneity and grouped effective parameters（730–800 words）** ←→ 2.6
  - 3.4.1 *Symmetric mean-zero heterogeneity averages out*
  - 3.4.2 *Structured heterogeneity displaces all three grouped coefficients* → **Figure 5**
    > ⚠ **禁用**："average overshot / slightly passed the proxy"、"the proxy is not a common
    > endpoint"、"the fit moved towards the proxy without landing on it"。第一条是单次抽样的产物
    > （30 次中位数下越过 proxy 的是 **new**），第三条被中位数接近 1 否定。见 §2 发现 4 的更正框。
  - 3.4.3 *What does a grouped coefficient represent?*（论证靠 length ≠ residence time，
    不靠任何 overshoot 观察）
- **3.5 Predictive accuracy is not parameter identification（680–760 words）** ←→ 2.7
  - 3.5.1 *Leave-one-monitor-out*（不得写成 parameter validation）
  - 3.5.2 *Leave-one-zone-out and unmonitored predictions* → **Figure 6**、**Table 4**
  - 3.5.3 *Implications for model validation*
- **3.6 Propagation to operational low-chlorine risk（900–980 words）** ←→ 2.8
  - 3.6.1 *Duration, depth and hydraulic interpretation*
  - 3.6.2 *Network-scale stability versus operational shortlist* → **Figure 7**、**Table 3**
    （`k_b` 结果必须始终指明用的是 `P_bar` 还是 `E[A]`）
  - 3.6.3 *Temperature, ageing and dosing stress tests* → **Appendix H**
- **3.7 Integrated implications, limitations and future work（520–580 words）**
  - 3.7.1 *Overall interpretation*（baseline identifiability / practical robustness /
    decision robustness 三层，不重复数字）
  - 3.7.2 *Methodological implications*（含 artifact–prose consistency，
    以及"总结段与详细节一致性"这一类）
  - 3.7.3 *Limitations and generalisability*（synthetic design / error assumptions /
    grouping and structure / numerical and operational 四类）
  - 3.7.4 *Future work*

> 分项上限之和为 5 980，略高于 5 900 —— **不能所有小节都取上限**。

---

### 4. Conclusions（400–500 words，无三级标题，四段）

①**答 RQ1**：同一六监测点数据在 formal likelihood 下对三个 `k_w` 都含信息；原稿 informal GLUE 的
宽分布主要反映 inference formulation；threshold 调整不能替代正确的信息累积。
②**答 RQ2**：baseline identifiability 并非在所有误差下都稳健；sensor bias、`k_b` 误设与 structured
heterogeneity 影响最大；structured heterogeneity 使三个参数发生同量级标准化位移，
**但分区之间不可排序**，说明 length-weighted proxy 不是 effective coefficient。
③**答 RQ3**：good prediction does not establish parameter identification；参数位移不必然破坏
全网风险格局；operational shortlist 的稳定性取决于所选指标。
④**总体贡献与边界**，收尾句：

> The value of uncertainty-aware calibration therefore lies not only in producing parameter
> intervals, but in distinguishing which conclusions are supported by the observations, which remain
> conditional on modelling assumptions, and which are sufficiently robust to inform operational
> screening.

**不要**：引入新数字；重新解释所有情景；写很长 future work；声称真实管网通用性。

---

### 非编号部分

- **Acknowledgements**（约 40–60 words）
- **Statement on the use of generative AI**（约 60–120 words）——**强制项**。
  课程说明书：*"if you have made use of AI tools in the preparation of your Research Paper (in whole
  or in part), this must be formally acknowledged in a written statement included in your paper"*，
  并要求参照部门 Policy Guidance note。**该 note 尚未取得**，格式待定；
  可声明的事实清单见 §11 第 3 项。
- **References**（Imperial Harvard，不计入字数）
- **Appendices A–H**（见 §8）

## 6. 原稿处理对照表

| 原论文内容 | 处理方式 | 新位置 | 修改原因 | 具体方法 |
|---|---|---|---|---|
| 原标题及 "GLUE uncertainty-aware calibration" 主叙事 | 删除并重写 | Title/Abstract/Intro | GLUE 已非 primary inference | 用推荐标题；Abstract 按三层主线重写 |
| 饮用水余氯、bulk/wall decay 一般背景 | 保留但压缩 | 1.1、2.1 | 背景正确但过长且未服务当前问题 | 只保留与 grouped `k_w`、`k_b` trade-off、uncertainty 有关内容 |
| EPANET/WNTR 模型介绍 | 保留但修改 | 2.1、3.1 | 配置、单位与验证已更新 | 补 mass transfer、internal unit、known-answer、frozen model |
| 三个 old/average/new 分组 | 保留但修改 | 3.1.1–3.1.2 | 不能解释成真实管龄类别 | 明确称 synthetic location-based reaction groups |
| 原 72 h simulation / 24 h warm-up | 删除并替换 | 3.1.3、3.2.1 | 24 h 不满足浓度 cyclostationarity，影响 severity/top nodes | 替换为 168 h / 120 h，正文写有限时域限制 |
| 原 pseudo-random、约 2000 candidates | 删除并替换 | 3.2.3、3.3.1 | 小样本库下 formal ESS 太低 | 8192 Sobol；样本数/ESS/convergence 图表更新 |
| informal GLUE 作为主分析 | 移动并降级 | 2.3.2、3.3.3、4.1 | 未充分利用残差信息且改变结论 | primary 改 censored Gaussian；GLUE 结果显式标 "comparator" |
| `RMSE<0.12` behavioural threshold | 移动 | Supplement S3 | 只属 informal comparator | 正文只留 "threshold 不能修复 score inefficiency" |
| §4.4 "The weighted mean of every group lies close to its true value" | 删除 | 4.1.1 替换 | 均值接近真值部分来自 prior centring | 改为 prior-SD retention + formal/informal 对照 |
| 用均值接近真值证明参数 recovery | 删除并替换 | 4.1.1–4.1.3 | 须考虑 prior、区间、displaced prior、repeated noise | 用五条 identifiability evidence chain |
| deterministic 7×7×7 grid "恢复三个 truth" | 移动并降级 | Supplement S4 / Methods QA | grid 以真值为中心且量化粗 | 只作 implementation check |
| coarse profile/grid intervals | 删除并替换 | 4.1.3 | 对区间低估 15%–39% | 只引 continuous profile endpoints |
| `old ≫ new > average` identifiability gradient | 删除并重写 | 4.1.3、5.1、5.3 | formal baseline 下三参数精度相近 | 改为 practical robustness gradient |
| 旧 noise sensitivity（不同实验设置） | 删除并替换 | 3.5.1、4.2.1 | 与三分区 baseline 不一致 | 用 Step 6 同配置 30-replicate 结果 |
| "需要 σ≤0.05 才能有用" | 删除 | 4.2.1、5.3 | 是 informal score 的 artefact | 改成 σ=0.10 已明显收缩；σ≤0.05 当前 sampling-limited |
| 单一 heterogeneity field 的 structural-bias 结论 | 删除 | 不引为正式结果 | 单场结果在 25 场后符号反转 | 用 homogeneous control + 25-field ensemble |
| 对称异质性 robustness 结果 | 保留但限定 | 4.2.2 | 有多场证据支持 | 限定为 ±20%、本网络、本噪声水平 |
| length-correlated structured heterogeneity | 新增 | 3.5.2、4.2.2、5.3 | precise-but-biased 的主要正结果 | 明确 length-weighted 只是 proxy，并报 average 的 overshoot |
| Fisher/CRLB | 新增 | 3.4.2、4.1.3、4.2 | 原稿缺 a-priori identifiability | Case A/B/C 分层呈现 |
| continuous profile likelihood | 新增 | 3.4.3、4.1.3 | 提供 a-posteriori 证据 | 与 CRLB、ensemble 对照 |
| 100 次 repeated-noise calibration | 新增 | 3.4.3、4.1.3 | 单次噪声无法说明 bias/coverage | compact table / forest plot |
| sensor constant bias | 新增 | 3.5.3、4.2.3 | 系统误差远大于随机不确定性 | 用 posterior SD 标准化，双侧报告 |
| sensor drift | 新增但精简 | 4.2.3 / Supplement | drift 主要由 mean bias 决定 | 正文一句主结论，完整 arms 下沉 |
| zero clipping / censoring | 新增但精简 | 3.3.2、4.2.3 | primary likelihood 必须说明 | 正文约半页，完整比较入附录 |
| 固定 `k_b` 且不分析 trade-off | 删除并替换 | 3.5.4、4.2.4 | `k_b` 误设显著移动 avg/new | 加 Case B Fisher + ±20% 实证 |
| "top risk nodes 对 `k_b` 不敏感" | 删除 | 4.2.4、4.4.2 | 与当前表格及不同指标不一致 | 改成 metric-specific、scale-specific |
| 只用 `P(C<0.2)` 风险图 | 保留但扩展 | 2.4、3.6.2、4.4 | 单一概率混淆持续时间与深度 | 加 `P_min`/`P_bar`/`E[D]`/`E[A]`/min C |
| 把 0.2 mg/L 写成安全或合规阈值 | 修改 | 全文 | 只是代表性运营阈值 | 统一写 "selected representative operational threshold" |
| water age 结果 | 新增但限界 | 4.4.1、5.5 | 提供水力解释 | 只作 descriptive association |
| 仅 LOO monitor validation | 合并并扩展 | 3.6.1、4.3 | LOO 太容易，不能证明参数识别 | 与 LOZO、未监测节点、异质真值合并 |
| 用预测好证明参数正确 | 删除 | 4.3、5.4 | LOZO 已明确反驳 | "prediction ≠ identification" 改为主结论 |
| temperature/ageing/dosing 结果 | 新增但降为应用展示 | 4.4.3、5.5 | 假设较强 | 正文一表一图，完整 register 入 Supplement |
| risk register 的 breach/severity bands | 移动 | Supplement S8 | 项目内定义，缺外部验证 | 正文只说明多指标必要性 |
| 1000× concentration unit correction | 新增但压缩 | 3.2.2、Supplement S2 | 须保证物理解释可信，数值结论不变 | 正文一段透明说明 |
| pattern-aware demand correction | 保留数值，细节移动 | 3.6.2 / Supplement | 影响 demand-weighted summaries | 正文只说明 average expected demand |
| provenance / hash / validator | 新增但移动 | Data & Code Availability / Supplement | 可信度支撑而非科学发现 | 正文方法一句 |
| 原 Conclusion 的 "所有参数接近 truth"/"σ≤0.05"/"risk map robust" | 整体删除并重写 | 6 | 三个结论均已被修正 | 按 RQ1–RQ3 逐段回答 |
| 原稿 59 页、无规范编号、仍有 placeholders | 整体格式重构 | 全文 | 不符合 journal-paper style 与 12 000 words | Heading styles、连续编号、交叉引用、统一 captions |
| 原稿分散的 limitations | 合并 | 5.7 | 主线不清 | 按 synthetic / error process / grouping / horizon-sampling 四类组织 |
| Bayesian hierarchical / MCMC（计划未完成） | 删除或移入 Future Work | 5.8 | 不能把未完成方法写成本文方法 | 只作下一步方向 |
| GLUE 批评相关文献 | 新增并强化 | 1.2、2.3、5.2 | 本研究提供具体定量实例 | 加 Stedinger (2008)、Mantovan & Todini (2006)，准确限定到本实现 |

**已删除的一行**：原方案含一条 "Bristol Water Field Lab / 三个真实 DMA / 真实在线监测数据" 处理项。
`Ruixin_Peng_Draft_FINAL.docx` 中不存在这些内容，该行不适用（见 §0.2 第 1 条）。

---

## 7. 篇幅分配

### 官方计数规则（2026-08-06 确认）

> 计入：**abstract、正文、以及图表 caption**。
> 不计入：**references、以及图表的_内容_本身**。

两个杠杆随之确定：

1. **caption 必须像正文一样预算**——它们计入 12 000。
2. **表格单元格里的文字免费**——凡是能塞进表格的细节都不该写成正文散文。
   Table 3 那些长 caveat 列一个字都不占预算，只有它的 caption 占。

**附录两边都没提。** layout 把 Appendices 与正文并列，暗示不计入，但文件没写死。
**按最保守口径处理：假定 Appendix 的解释性文字计入**，因此附录做成近乎纯表格与图，
每个只留一两句引导语，并在预算里留位。**不要用附录规避字数。**

### 预算表

旧稿在 post-review 新结果加入前已约 11 624 words，所以这是重写而非扩写。

| 部分 | 建议字数 | 说明 |
|---|---:|---|
| Abstract | 230–250 | 五件事 + 四个数字锚点 |
| 1. Introduction | 1 300–1 500 | 含原 Background；每段文献服务于 gap |
| 2. Method and approach | 2 500–2 800 | 只写"如何做"，QA 细节入附录 |
| 3. Results and discussion | 5 400–5 900 | 全文重心，六个小节见下 |
| 4. Conclusions | 400–500 | 四段，按 RQ 回答 |
| Acknowledgements + AI statement | 100–180 | AI 声明为强制项 |
| Figure/Table captions | 450–600 | 7 图 + 4 表 = 11 个 caption |
| Appendix 引导语 | 300–450 | 保守口径下按计入处理 |
| **目标总计** | **约 11 100–11 400** | 留 600–900 words 缓冲 |

> ⚠ **各节上限之和是 12 080，超过目标总计。** 这不是错，但意味着**不能所有节都取上限**——
> 按下限到中位规划，否则会不知不觉超出 12 000。

### §3 内部分配（七个小节，与 §2 一一对应）

| 小节 | 建议字数 | 对应 Method |
|---|---:|---|
| 3.1 Forward baseline and observations | 650–720 | 2.1–2.2 |
| 3.2 Inference formulation | 1 100–1 180 | 2.3–2.4 |
| 3.3 Measurement and nuisance errors | 880–960 | 2.5 |
| 3.4 Structural heterogeneity | 730–800 | 2.6 |
| 3.5 Prediction vs identification | 680–760 | 2.7 |
| 3.6 Operational risk | 900–980 | 2.8 |
| 3.7 Implications, limitations, future work | 520–580 | — |

分项上限之和 5 980,略高于 5 900——**不能所有小节都取上限**。3.6 已从原 1 050–1 200 下调,
因为 §3.1.2 已把时域限制讲完,那边不必重复。

**优先压缩**：EPANET 教科书式介绍；逐 Step 方法重复；每个 sensitivity arm 的完整数字；
单次 preliminary/superseded 实验；unit/debugging 过程；risk register 全部分类规则；
逐节点讨论；全部 monitoring nodes 的完整 bias 表。

**不可压缩**：formal vs informal 核心对照；Fisher/profile/repeated-noise 三角验证；
symmetric vs structured heterogeneity；LOZO 的 parameter–prediction decoupling；
`k_b` 对不同 risk metrics 的影响；limitations 与 claim boundaries。

**不要为规避字数把整段论证硬塞进表格**——表格该放数字与限定，论证仍在正文。

---

## 8. 图表规划

正文总量：**Figures 7 张、Tables 4 张**，其余全部进 Appendix A–H。
11 个 caption 对 450–600 words 预算 ≈ 41–55 words/个，紧但可行。
所有正文图须统一字体、线宽、颜色语义、panel lettering、坐标单位与 caption 风格
（"保留" 指保留数据与图意，不表示原图无需重绘）。每张图都要有一句明确的 takeaway sentence。

### Figure 1 — Controlled study design and evidence chain

**内容**：Panel A —— Net3 拓扑、三分组、六监测点、source/tank、大致流向；
Panel B —— workflow：synthetic truth → noisy/censored observations → inference → identifiability
→ error stress tests → prediction → risk propagation。
**证明**：研究不是普通参数拟合，而是受控地拆解 calibration conclusion 的来源。
**处理**：网络图底图数据可保留，必须重新排版；**图内不得出现 Step 0–15**。

### Figure 2 — Inference-rule dependence

**内容**：每参数一个 panel —— prior、formal censored、formal iid、informal GLUE @0.107/@0.120、
truth line；旁边加 SD-retained bar chart。
**证明**：同一数据因 weighting formulation 不同而得到完全不同的 apparent identifiability。
**来源**：baseline、Step 2、Step 3。
**正文必要性**：**全文最重要的主图。**

### Figure 3 — Triangulated baseline identifiability

**内容**：Forest plot —— formal ensemble interval、continuous profile interval、Fisher interval、
repeated-noise empirical SD、truth。右侧可加 empirical SD / CRLB 与 coverage。
**证明**：正式似然的基线结论并非单一算法的偶然结果，而得到多种诊断的相互支持。

### Figure 4 — Robustness to measurement and model error

**内容**：standardized-effect matrix。
横轴：σ increase、AR(1)、`k_b = −0.4/−0.6`、sensor bias、sensor drift、censoring、
symmetric heterogeneity、structured heterogeneity。
纵轴：old、average、new。
单元格：shift / baseline posterior SD，或 interval widening factor。
**证明**：不同误差来源影响不同；sensor bias、`k_b` 和 structured heterogeneity 比稀少 censoring 更危险。
**注意**：不能把不同物理量直接用未经标准化的绝对差值比较。

> ⚠ **本图有三个必须先解决的设计问题**（详见 §10）：
> 1. **两种单元格语义不能混在一个矩阵里。** σ 和 AR(1) 产生的是**区间加宽**（σ 0.10→0.15 为
>    ×1.41/1.52/1.48；AR(1) ρ=0.4 为 ×1.48/1.49/1.44），其余六列产生的是**位移**。
>    建议拆成 Panel A（widening factors，2 列）与 Panel B（standardised shifts，6 列）。
>    否则这张图恰好犯了它自己的 "注意" 所警告的错误。
> 2. **drift 列的 `new` 单元格没有数据。** `step8d_sensor_drift.json` 只跑了 node 15（old 区）
>    和 node 231（average 区），无 new 区 arm。要么标注 "not run"，要么直接删掉 drift 列
>    ——drift ≈ 0.89–0.99 × mean-equivalent bias，本就与 bias 列高度冗余。
> 3. **必须固定一个标准化口径。** 例如结构化异质性：`bias / own-run SD` = 1.29/2.05/0.86，
>    `bias_net_of_baseline / baseline SD` = 1.55/1.89/1.65。两种算法给出的三组数完全不同，
>    图内必须全程用同一种并在 caption 里写明。

**可填充性已核实**（formal censored，除 drift-new 外全部有数据）：
censoring −0.12/−0.003/+0.009 SD；symmetric het +0.11/+0.02/−0.06 SD；
structured het −1.55/−1.89/−1.65 SD；sensor bias 最大 |shift| 3.87/5.94/4.44 SD；
`k_b ±20%` 0.56–0.66 / 1.41–1.53 / 1.50–1.58 SD。

### Figure 5 — Symmetric versus structured heterogeneity

**内容**：Panel A —— 25 fields structural increment distribution；
Panel B —— single-field result 与 multi-field ensemble 对照；
Panel C —— structured case：**30 次实现的中位数 + 5–95 区间**（主标记），单次抽样（淡，仅示散布）；
Panel D —— fit residual vs parameter bias。
**证明**：单一场、单次抽样都可能支持错误结论；结构化异质性而非异质性本身导致方向性偏差。
**注意**：Panel C 的主标记**必须**是 30 次中位数。用单次抽样作主标记会让 average 看起来越过 proxy，
而在中位数下越过的是 new——见 §2 发现 4 的更正框。

### Figure 6 — Good prediction without parameter identification

**内容**：每个 leave-one-zone-out case 的 parameter posterior / prior / truth、held-out RMSE、coverage。
加 conceptual annotation："coefficient returns to prior"、"prediction remains at noise floor"。
**证明**：Predictive success is not evidence of parameter identifiability.
**定位**：应成为 Discussion 中引用最多的图之一。

### Figure 7 — Risk robustness is metric-specific

**内容**：Panel A —— `P_bar` 与 `E[A]` 的 node ranking / rank change；
Panel B —— 不同 perturbations 的 full-network Spearman 与 top-3/top-6/top-10 Jaccard；
Panel C（可选）—— duration vs deficit 的代表性节点（deep/short 对 shallow/long）。
**证明**：全网稳定、top-k 稳定和 absolute severity 稳定是不同概念；风险指标会改变 shortlist。

### 正文表格

| 表 | 位置 | 内容 | 作用 |
|---|---|---|---|
| **Table 1** — Baseline design and parameter ranges | §2.1.3 | parameter / truth / prior / unit / fixed-inferred / corresponding monitors | 一处交代全部设计常数；表内容免费 |
| **Table 2** — Baseline inference comparison | §3.2.1 | truth / prior SD / 四种 scheme × mean / SD / SD retained / ESS | 支撑 RQ1 |
| **Table 3** — Robustness summary | §3.6.2 | error source / 三参数位移 / risk effect / evidence / caveat，**统一以基线后验 SD 为分母** | 防止 Results 被零散数字淹没；长 caveat 列免费 |
| **Table 4** — Held-out validation | §3.5.2 | LOMO 六行 + LOZO 三行：own-coefficient error / own SD retained / held-out RMSE / coverage | 支撑 RQ3，承载核心 novelty |

### 已砍与已改（2026-08-06）

- **原 Figure 8「情景地图」→ Appendix H**。正文 §3.5.3 只留紧凑 summary 与散文数字
  （21/28/29/31 节点、55.4/64.7/67.8/69.4 L/s、E[A] 0.2216/0.3645/0.5218/0.5790）。
- **原 Table 1「实验设计矩阵」已删**（与 robustness summary 重叠）；
  新的 **Table 1 是 §2.1.2 的 design and parameter ranges**，性质不同，予以保留——
  它把全部设计常数集中在一张免费的表里。
- 因此 `paper_figs.py` 生成的三张表重新编号为 **Table 2 / 3 / 4**。

### 适合正文的结果

formal vs informal baseline；continuous profile + Fisher + repeated noise；
symmetric vs structured heterogeneity；sensor bias 与 `k_b` 的代表性结果；LOZO；
metric-specific risk；compact scenario application。

### 适合 Appendix/Supplement 的结果

full warm-up convergence table；unit-equivalence test；known-answer 详细数据；
Sobol leading-2^k convergence；threshold 0.107/0.110/0.120 全表；displaced-prior 所有方向和阈值；
coarse grid results；25 fields 逐场结果；σ=0.02/0.05 sampling-limited rows；full AR(1) profile grid；
six-monitor 偏差矩阵（**6 节点 × 4 offsets = 24 arms**，非 "two-sign"）；drift 全部 arms；
exact-zero vs censored 全部结果；report timestep sensitivity；full risk register；
severity-band definitions；ageing multiplier sensitivity；full scenario maps；
provenance manifest 和 validator 说明。

### 图表证据链顺序（严格按此出现）

1. **Figure 1** — 研究设计和网络
2. **Figure 2 / Table 2** — 同一数据、不同推断结论
3. **Figure 3** — 正式结论获得多工具验证
4. **Figure 4–5 / Table 3** — 现实误差如何破坏结论
5. **Figure 6 / Table 4** — 参数错误但预测仍好
6. **Figure 7** — 风险排序为何与参数误差解耦
7. **情景（正文散文 + Supplement S8）** — 下游应用示例

这条顺序形成完整论证：先证明有信息 → 再证明原方法没充分提取 → 再证明正式结果不是偶然
→ 再测试它在现实误差下会不会坏 → 最后判断坏掉的参数是否真的影响运营决策。

参见记忆 `thesis-figure-source-mapping.md`：现有 docx 配图来自旧 pipeline，
`Net3/Figures/step*.png` 是对应替换件。

---

## 9. 修改优先级

### P0 — 必须修改，否则论文逻辑或结论不成立

**P0-1 锁定新的核心问题、RQ 和标题.** 使用 RQ1–RQ3；删除以"估计三个参数并画风险图"为核心的旧目标；
场景分析降为 downstream application。

**P0-2 统一 primary inference.** 全文所有 headline parameter、risk 和 scenario 结果必须来自
**censored Gaussian likelihood-weighted ensemble**；informal GLUE 必须始终标为
**comparator / sensitivity analysis**。
需全局搜索并替换：`baseline GLUE`、`GLUE posterior`、作为主结果的 `behavioural ensemble`、
`threshold-based primary result`。

**P0-3 删除已被推翻的结论.** 至少包括：
"weighted mean of every group lies close to truth"；
"average/new cannot be identified by the monitoring array"；
"old ≫ new > average identifiability"；
"σ≤0.05 is required"；
"risk hotspots are unchanged under `k_b`"；
"good held-out prediction validates the coefficients"；
"120 h means full periodic steady state"；
"water age has converged"；
"0.2 mg/L is a safety/compliance threshold"。

**P0-4 用当前正式配置重建所有数字.** 全文只能使用：168 h simulation、120 h warm-up、
8192 Sobol candidates、correct mg/L conversion、scaled quality tolerance、
pattern-aware average expected demand、formal censored primary、current 92-junction risk results。
任何来自 72/24 h、pre-Sobol library、old concentration convention、base-demand-only weighting、
stale cached grid 的数字必须删除或明确标记 superseded，原则上不进入正文。

**P0-5 彻底重写 Results.** 不能在旧 Results 后追加 Step 7–15。必须重组为：
inference-rule dependence / practical robustness / parameter–prediction decoupling / risk propagation。

**P0-6 彻底重写 Discussion 和 Conclusion.** Discussion 围绕 conditional identifiability、
practical robustness、prediction vs parameters、metric-specific decision stability、synthetic limitations；
Conclusion 按 RQ1–RQ3 回答，不再总结脚本或实验步骤。

**P0-7 建立 claim-scope 规则.** 每个重要句子应回答：under what inference rule？
under what model assumptions？under what error structure？on which risk metric？
at what comparison scale？synthetic or externally validated？
尤其对 **robust / identifiable / validated / risk / hotspot** 五个词做全文审计。

**P0-8 重新生成所有主文图表.** 全部使用 current artifacts；不允许从旧 Word 文档直接复制；
统一单位、inference scheme 颜色、三分区颜色、risk map scale；每张图有明确 takeaway sentence。

**P0-9 控制在 12 000 words 内.** 旧稿已接近上限，不能局部修补。执行方式：
先建 11 200-word skeleton → 再把旧稿中仍可用的段落搬入 —— **不是在 11 624 words 后继续增加**。

**P0-10 提交前做三重一致性检查.**
① 数字一致性：正文数字对 artifact；
② 语义一致性：表格和文字是否得出相同结论；
③ scope 一致性：同一结论在 Results / Discussion / Abstract / Conclusion 中是否保持相同限定。

### P1 — 强烈建议，直接影响论文质量

- **P1-1** 构建一张统一的 robustness summary table（= Table 3），防止读者迷失在大量实验中。
- **P1-2** 把 Fisher、profile 和 repeated-noise 真正整合，不要散成三个孤立小节。它们必须共同支撑：
  *baseline identifiability is triangulated rather than inferred from one ensemble.*
- **P1-3** 突出 LOZO 结果——应进入 Abstract、Results、Discussion、Conclusion 四处。
- **P1-4** 加强 GLUE 文献定位：引入统计批评、说明本项目是定量受控例子、
  明确不推广到所有 GLUE applications、区分 behavioural philosophy 与本项目具体 pseudo-likelihood。
- **P1-5** 把 structural-error 结果写成"结构决定偏差"的完整论证
  （symmetric mean-zero → structured correlation → single realisation risk → control subtraction），
  而非一连串 jitter 实验。
- **P1-6** 风险结果必须同时报告值和排名：每个 shortlist 附 risk values、uncertainty、
  metric definition、top-k sensitivity、tie/plateau information。
  **避免把第 5 和第 6 名的微小交换写成重大运营变化。**
- **P1-7** 精简场景部分至 Results 的 15%–20%（约 450–600 words）；risk register、severity bands
  和所有节点表放 Supplement。
- **P1-8** 完善 limitation section——不能只在各小节末尾散落 caveats，必须集中成可审阅的限制体系。

### P2 — 改善表达、结构和完整性

- **P2-1 统一术语**：grouped wall-decay coefficient；censored Gaussian likelihood；
  likelihood-weighted ensemble；informal GLUE behavioural comparator；prior-SD retention；
  practical identifiability；predictive adequacy；operational screening metric；cumulative deficit；
  window-breach probability。
- **P2-2 统一符号和单位**：`k_b` day⁻¹；`k_w` m/day；concentration mg/L；deficit mg/L·h；
  duration h；demand L/s；σ 始终指 one standard deviation。
- **P2-3 规范 journal formatting**：Heading 1/2/3 styles；三级编号一致；Figure/Table 连续编号；
  每张图表正文中先引用后出现；caption 说明数据、统计量、区间和 weighting；
  **不在图标题中写脚本名或 Step 编号**；不使用截图式代码输出。
- **P2-4 压缩重复定义**：`P_min`、`P_bar`、`E[D]`、`E[A]`、SD retained、ESS、censored likelihood
  只在首次出现时完整定义，后文交叉引用。
- **P2-5 Abstract 和 Conclusion 最后写**。正确顺序：确定 claim matrix → 完成正文 Figures/Tables
  → 重写 Results → 重写 Discussion → 压缩 Methods → 最后写 Introduction、Abstract、Conclusion。

---

## 10. 母命题

> In a controlled Net3 chlorine-calibration experiment, the apparent identifiability of grouped
> wall-decay coefficients depended strongly on the inference formulation; formal likelihood-based
> diagnostics supported baseline identification of all three coefficients, but realistic nuisance
> processes weakened that result unevenly, while accurate spatial prediction and broadly stable risk
> patterns could persist even when individual parameters were poorly identified.

所有章节、图表和结论都应服务于这句话，而不是服务于原来的 Step 顺序或旧 GLUE 叙事。

> 措辞微调建议：末句的 "poorly identified" 对 LOZO 结果偏弱。该实验中 old/average 的系数是
> **完全没有被数据更新**（回到先验中点、保留 100% 先验 SD），比 "识别得不好" 更强。
> 可改为 "…even when individual parameters were not identified at all"。

---

## 11. 落笔前的未决问题

1. ~~附录是否计入 12 000 words~~ —— **2026-08-06 已按最保守口径处理**：假定计入，
   附录做成近乎纯表格与图，预算里留 300–450 words 引导语。仍可向导师确认以放宽。
2. ~~章节结构~~ —— **已按官方 layout 重排为四个编号一级标题**（见 §5）。
3. **部门 GenAI Policy Guidance note 尚未取得。** 课程说明书要求"formally acknowledged in a
   written statement included in your paper"，并指向该 note 与图书馆的
   `learning-support/generative-ai-guidance` 页面；两者都不在已读文件里，
   **因此声明的格式与颗粒度未知**。可声明的事实清单（等格式确定后据此撰写）：

   | 参与程度 | 内容 |
   |---|---|
   | AI 主导、人工审定 | 论文框架重构方案；`Net3/paper_figs.py` 全部绘图与制表代码；配色 CVD 校验脚本 |
   | AI 执行、有独立验证 | 数值核对（40+ 项对照 artifact）；逐节点风险指标重算（与 step10 逐位吻合） |
   | AI 发现、改变了结论 | 三次"单次实现被当作重复结果" —— Figure 6 后验宽度画错、Table 3 证据标注错、RESULTS_LOG 总结段与详细节矛盾 |
   | 人工主导 | 全部实验设计与 `step*.py` 计算脚本；所有科学判断与取舍 |
   | 未使用 AI | EPANET/WNTR 仿真本身；artifact 数值的产生 |

   最后一行应在声明中明确写出：**论文中的每一个数字都来自 `baseline_cache/` 的确定性计算，
   不是 AI 生成的。**
4. **`Net3/RESULTS_LOG.md` 的六项语义待修项**（见记忆 `results-log-outstanding-corrections`）
   要不要在写正文前先修。其中 Case C（2.30/1.10 → 2.24/1.09）和
   "eight → nine of ten hot-spot nodes" 两项会直接被正文引用。
5. **提交事务**：CID 与第一导师姓氏（决定文件名
   `ResearchPaper-CID-YourName-SurnameofFirstSupervisor`）；题名页按模板、**不得用 College crest**；
   论文 2026-08-21 12:00 截止，海报 2026-08-28 12:00。
