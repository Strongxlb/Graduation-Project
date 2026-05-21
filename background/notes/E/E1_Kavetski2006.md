# E1 — Kavetski, Kuczera, Franks (2006) Paper 2 精读笔记

> 配套文件：[`../../Literature/literature.md`](../../Literature/literature.md) §E1
> PDF 路径：[`../../Literature/E-不确定性感知校准（Monte Carlo : Bayesian : GLUE）/E1-Kavetski, Kuczera, Franks (2006). Bayesian analysis of input uncertainty in hydrological modeling.pdf`](../../Literature/E-不确定性感知校准（Monte Carlo%20:%20Bayesian%20:%20GLUE）/E1-Kavetski, Kuczera, Franks (2006). Bayesian analysis of input uncertainty in hydrological modeling.pdf)
>
> **注意**：本 PDF 为 **WRR 系列第 2 篇（Application）**；理论见 companion Paper 1 (`10.1029/2005WR004368`)。literature.md 条目标题为系列名，实际阅读文件为 **Paper 2** (`10.1029/2005WR004376`)。
>
> **来源标签**（2026-05-19，已通读 PDF 10 页）

---

## 0. 元数据

| 字段 | 内容 |
| --- | --- |
| Title | Bayesian analysis of input uncertainty in hydrological modeling: **2. Application** |
| Authors | **Dmitri Kavetski**, **George Kuczera**, **Stewart W. Franks** |
| Affiliation | Univ. of Newcastle, Australia（Kavetski 后转 Princeton） |
| Journal | *Water Resources Research* 42, W03408 |
| DOI（本篇） | `10.1029/2005WR004376` |
| DOI（Paper 1 理论） | `10.1029/2005WR004368` |
| 页数 | 10 |
| 优先级 | **P0** |
| 状态 | `read` |

**领域**：降雨径流 / MOPEX 流域 — **非** 供水管网；收录理由为 **输入（forcing）不确定性** 的 Bayesian 处理范式，可类比 **水质校准中的 Cl 观测误差 + 水力 forcing 误差**。

---

## 1. Abstract（原文要点）

`[原文]` **BATEA**（Bayesian Total Error Analysis）同时处理 **输入与输出** 误差，要求模型者 **显式** 假设数据不确定度。两案例（French Broad、Potomac）+VIC 模型：考虑 **降水误差** 后，预测区间与参数后验 **显著变化**。BATEA 在 **严重模型误差**（如省略雪模块）下能力有限 — 需 **正确指定 error model**；计算量大但可用 Newton 型方法。

---

## 2. 中文摘要

传统最小二乘（SLS）把 **观测 forcing（降水）当真值**，会在 forcing 有偏时 **扭曲参数**（Kavetski et al. 2002）。BATEA 引入 **潜变量** $F$ 将观测 forcing 映射为「真值」forcing，并联合估计 $\{Q, F, B_x, B_y\}$。French Broad：storm **multiplier** 高斯模型使 Nash–Sutcliffe 从 ~0.76 升至 **~0.95**，峰值拟合改善。Potomac：省略雪模块时 SLS 崩溃（NSE 0.30），BATEA 仍可达 0.80，但 **不能替代正确模型结构**。完整 VIC+雪模块时 SLS 与 BATEA 参数接近，但 BATEA 预测区间更紧（NSE 0.97）。

---

## 3. BATEA 核心（Paper 1 理论 + 本篇应用）

### 3.1 与 SLS 对比

**SLS**（固定 forcing）：

$$p(Q|\tilde X,\tilde Y) \propto \exp\left(-\frac{1}{2\sigma_y^2}\sum(\tilde y_n - h_n(Q,\tilde X))^2\right)$$

**BATEA**（联合 forcing / 参数 / 误差模型）：

$$p(Q,F,B_x,B_y|\tilde X,\tilde Y) \propto p(\tilde Y|Q,\tilde X,F,B_y)\,p(Q)\,p(F|B_x)\,p(B_x)\,p(B_y)$$

`[原文]` §2.3 — **关键**：$F$ 为 latent true forcing。

### 3.2 Storm multiplier 模型（本篇使用）

每场 storm 降水乘子 $m_i \sim \mathcal{N}(\mu_m, \sigma_m^2)$，$\sigma_m^2$ 用 vague inverse-gamma 先验积分掉 `[原文]` §2.4。

---

## 4. 案例结果摘要

### 4.1 French Broad River（VIC + 雪）

| 方法 | 校准期 NSE（约） | 要点 |
| --- | --- | --- |
| SLS | 0.76–0.74 | 峰值系统性偏低；预测区间不合理 |
| **BATEA** | **~0.95** | 修正降水；$T_{melt}$ 等更合理 |

300 d vs 600 d 数据：SLS 参数 **不稳定**（$k_b$ 触上界）；BATEA 后验更紧 `[原文]` §4.1–4.2。

### 4.2 Potomac（故意省略雪模块 = 模型误差）

| 配置 | SLS NSE | BATEA NSE |
| --- | --- | --- |
| VIC **无** 雪 | 0.30 | **0.80** |
| VIC **有** 雪 | 0.85 | **0.97** |

`[原文]` §5：**BATEA 不能替代正确结构**；无雪时 multiplier 吸收部分误差，但 Potomac 降水误差 **非高斯 multiplier 形**。

---

## 5. 结论（作者，§6）

1. 降水 modest 修正 → **显著** 改变 hydrograph 与参数。  
2. BATEA 潜力取决于 **error model 是否合理**（timing error 不能用 multiplier）。  
3. 须同时检查 **forcing 与 response** 拟合，不可假设 input exact。  
4. 未来需 **更 realistic 的 model error** 进入目标函数。  

**BATEA 益处方向**：参数区域化、时变稳定性、模型评估、敏感性、数据质量监测 `[原文]` §6 [47]–[53]。

---

## 6. 迁移到本项目的映射

| 水文 BATEA | 余氯 WNTR 校准（类比） |
| --- | --- |
| 降水 $\tilde X$ | 水力 demand / 源氯浓度 / 水龄 forcing |
| 流量 $\tilde Y$ | **节点 free Cl grab samples** |
| Storm multiplier | 分区/时段 **bulk 或 wall 乘子** 或 **源氯 bias** `[推断]` |
| Output noise $B_y$ | **DPD 观测误差** (D2: $\sigma\approx0.02$ + bias) |
| 模型结构误差 | EPANET 一阶 decay 简化 vs 真实二阶/wall 零阶 (A2/A4) |
| SLS 固定 forcing | **仅调 $k_b,k_w$ 且把 Cl_obs 当无噪** — 本项目要避免 |

**与 C2 关系**：C2 对 **参数** 做 MCS；E1 对 **输入数据** 做 Bayesian — 本项目 ideally **两者叠加** `[推断]`。

**与 E3/E4**：literature 中 E3 Vrugt GLUE、E4 Huang Bayesian WDS — E1 提供 **total error / input uncertainty** 哲学基础。

---

## 7. 批判性阅读

**优点**：开创性；显式 latent forcing；posterior predictive check；诚实讨论 model error。  
**局限**：
- **水文** 案例，无 EPANET  
- Multiplier 仅修正 **storm depth**，不修正 timing  
- 计算成本高（数百 storm 维）  
- 模型错误时 multiplier 可能 **补偿过度**  

---

## 8. 待办

- [ ] 读 Paper 1 (`004368`) 完整推导  
- [ ] 读 E4 Kang / Huang WDS Bayesian 看管网实现  
- [ ] 在 thesis Method 写「Inspired by BATEA, we treat Cl observations and…」  

---

## 9. 引用

> Kavetski D, Kuczera G, Franks SW. Bayesian analysis of input uncertainty in hydrological modeling: 2. Application. *Water Resour Res*. 2006;42:W03408. doi:10.1029/2005WR004376

```bibtex
@article{Kavetski2006BATEA2,
  author  = {Kavetski, Dmitri and Kuczera, George and Franks, Stewart W.},
  title   = {Bayesian analysis of input uncertainty in hydrological modeling: 2. Application},
  journal = {Water Resources Research},
  volume  = {42},
  pages   = {W03408},
  year    = {2006},
  doi     = {10.1029/2005WR004376}
}
```

---

## 13. 修正记录

| # | 说明 |
| --- | --- |
| 1 | literature §E1 DOI 指向 **Paper 1** (`004368`)；已下载 PDF 为 **Paper 2** (`004376`) — 建议 literature 补注或拆条 |
| 2 | 系列共 3+ 篇（2006a/b/c calibration revisited）— 本笔记仅 Application 篇 |
