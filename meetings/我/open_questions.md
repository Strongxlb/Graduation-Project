# 待导师确认事项 - Open Questions

> 配套文件：[`../../README.md`](../../README.md)、[`../../plan1.md`](../../plan1.md)、本周会议稿 [`2026-06-02.md`](2026-06-02.md)
> 维护规则：
> - 进会议前先看一遍本表，挑出本周需要导师拍板的项目。
> - 每条都要带「我的初步建议」，不要只带问题。
> - 状态字段：`open`（待讨论）、`pending`（导师承诺回复中）、`decided`（已定）。
> - 决议后：把结论搬到 §2，并在 README / plan 中同步引用。
>
> **2026-05-25 更新**：导师邮件锁定范围（3-DMA + 10 monitors + first-order + ensemble-based；排除水力校准 / MSX / 运营优化），并已回答原 Q1/Q4/Q5（见 §2）。本表据此重排，剩余 P0/P1 决策见 §1。

---

## 1. 当前未决事项（按优先级排序）

| # | 问题 | 我的初步建议 | 决策影响 | 优先级 | 状态 |
| - | --- | --- | --- | --- | --- |
| Q1a | 10 个监测点数据的格式 / 频率 / 时间跨度？何时交付？（`.inp` / CSV / SCADA dump） | 优先 ≥4 周连续 hourly；CSV 或 SCADA dump 均可；拿到后立即切换主案例 | 决定 T3 数据管线工作量与 Methodology 写法 | P0 | open |
| Q2 | Bristol 3-DMA `.inp` 在哪？管材 / 管径 / 管龄信息齐全度？ | 若管材/管龄缺失，用 Hallam 2002 + Maleki 2023 范围作 informative prior | 决定能否做"分管材 / 分管龄 `k_w`"细化 | P0 | open |
| Q3 | `k_b` 是否跨 3 个 DMA 共享（同一水源）？还是各自估？ | 同一水源 ⇒ **pooled `k_b`（4 参数而非 6）**；用 A3/A6 + 烧瓶值作先验并冻结 | 影响参数维度与可识别性 | P0 | open |
| Q4 | "ensemble-based method" 的具体口径：GLUE / ensemble Kalman / approximate Bayesian？ | **Plan A = GLUE（E6）** 作 robust baseline → **Plan B = Bayesian hierarchical partial pooling（E7）** | 决定 Week 8–9 主算法 | P0 | open |
| Q5 | WP1–WP5 正式结构？（已知 WP5 = hierarchical Bayesian） | 推测：WP1=Lit+Model setup, WP2=Baseline calib, WP3=Uncertainty, WP4=Cross-DMA, WP5=Bayesian | 影响进度报告对齐口径 | P1 | open |
| Q6 | 阈值是否锁定 `0.2 mg/L`？ | 主图用 `0.2 mg/L`（**F2 WHO** 末端 ≥0.2；**F1 UK SI 2016/614** 作消毒法规背景），附录做 `0.1 / 0.3` 敏感性 | 影响所有「阈值概率」结果图与 Discussion | P0 | open |
| Q7 | 测量误差模型：用 DPD（D2）还是在线传感器（D3）的不确定度？分布形式？ | 入口 = 在线传感器 ~5%；下游 grab = DPD ±0.02 mg/L（~15% 相对）；进 likelihood | 决定 MC 采样器与似然函数形式 | P0 | open |
| Q8 | AI 工具使用披露口径：论文附录是否写明 prompt 与用途？ | 按 CEE / Imperial「Use of generative AI tools」模板加一节 Acknowledgement | 论文格式与学术诚信风险 | P1 | open |
| Q9 | 结果图 / poster 是否需中英双语？ | 论文与 poster 全英文；仓库内部文档可保留中文 | 影响图表导出量 | P2 | open |
| Q10 | 是否做 sensor placement 优化？ | 不作为主线；Discussion 点一笔作未来工作 | 影响 scope 是否扩张 | P2 | open |

---

## 2. 已确认事项（决议归档）

> 当某条 Q 讨论结束，把「问题 + 决议 + 决议日期」搬到这里，并在 §1 删除该行。

| # | 问题 | 决议 | 决议日期 | 备注 |
| - | --- | --- | --- | --- |
| Q1 | 真实管网数据是否可获取？ | **有。** Bristol Water Field Lab 3 DMA + 10 chlorine monitors；论文主案例以真实数据为准 | 2026-05-25（邮件） | 交接细节待定 → 见 §1 Q1a / Q2 |
| Q4(旧) | 校准方法路线偏好？ | **ensemble-based**：GLUE 优先 → Bayesian / hierarchical 进阶 | 2026-05-25（邮件） | 具体口径细化 → 见 §1 Q4 |
| Q5(旧) | 论文使用的网络规模？ | **Bristol 3-DMA 实际管网**（非合成 Net1/Net3；Net3 仅练手/方法对照） | 2026-05-25（邮件） | — |
| 范围 | 项目 scope | first-order kinetics；**排除** hydraulic calibration / MSX / 运营优化 | 2026-05-25（邮件） | 见 README §5 |

---

## 3. 给导师的问题清单（2026-06-02 会议直接念）

> 已被邮件回答的（真实数据、ensemble+Bayesian 方向、3-DMA）不再问；按会议语序整理本周必问 6 条。

1. **数据交接（Q1a / Q2）**：10 监测点数据的格式/频率/时间跨度、何时交付？`.inp` 在哪、管材/管龄齐全度？（缺管材信息我打算用 Hallam/Maleki 范围作先验。）
2. **`k_b` 共享（Q3）**：3 个 DMA 同一水源 → 我倾向用一个共享 `k_b`（4 参数），并用烧瓶/文献先验冻结，只标 `k_w`。您是否同意？
3. **"ensemble-based" 口径（Q4）**：我计划 GLUE 作 baseline、Bayesian hierarchical 作进阶。您心目中的 ensemble 是这个意思吗？
4. **WP 结构（Q5）**：WP1–WP5 的正式划分是什么？（我先按 Lit/Baseline/Uncertainty/Cross-DMA/Bayesian 推测对齐。）
5. **阈值（Q6）**：论文是否锁 `0.2 mg/L`（F2 WHO 依据）？我会补 `0.1/0.3` 敏感性。
6. **误差模型（Q7）**：入口用在线传感器 ~5%、下游 grab 用 DPD ±0.02 mg/L 进 likelihood，是否合理？

---

## 4. 行动项 (Action items)

> 每次会议结束 5 分钟内填写，避免遗忘。

| # | 行动项 | 负责人 | 截止 | 状态 |
| - | --- | --- | --- | --- |
| A1 | 记录导师对 §3 六项的决议 → 本表 §2 | 我 | 2026-06-02 | open |
| A2 | 确认 `.inp` + 数据交接方式与时间 | 我 / 导师 | 2026-06-06 | open |
| A3 | `git push` 同步本地 commits | 我 | 2026-06-03 | open |
