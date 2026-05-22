# D2 — Soares et al. (2016) 精读笔记

> 配套文件：[`../../Literature/literature.md`](../../Literature/literature.md) §D2
> PDF 路径：[`../../Literature/D-测量不确定性 (DPD : colorimetric : 在线传感器)/D2-Avaliacao_de_metodos_para_determinacao_de_cloro_re.pdf`](../../Literature/D-测量不确定性%20(DPD%20:%20colorimetric%20:%20在线传感器)/D2-Avaliacao_de_metodos_para_determinacao_de_cloro_re.pdf)
>
> **来源标签**（2026-05-19，已通读 PDF 12 页；**原文葡萄牙语**，关键数值来自 Resumo/Results/Conclusões）

---

## 0. 元数据

| 字段 | 内容 |
| --- | --- |
| Title (PT) | Avaliação de métodos para determinação de cloro residual livre em águas de abastecimento público |
| Title (EN) | Evaluation of methods for determining free residual chlorine in public water supply |
| Authors | **Samara Silva Soares**, Poliana Nascimento Arruda, Germán Sanz Lobón, **Paulo Sérgio Scalize** |
| Affiliation | Univ. Federal de Goiás, Brazil |
| Journal | *Semina: Ciências Exatas e Tecnológicas* 37(1):119–130 |
| DOI | `10.5433/1679-0375.2016v37n1p119` |
| 语言 | **葡萄牙语**（Abstract 双语） |
| 优先级 | **P0** |
| 状态 | `read` |

---

## 1. Abstract / Resumo（要点）

`[原文]` 比较 **DPD 比色法** 四种组合：**视觉 disk vs 数字 chlorimeter** × **粉剂 (pó) vs 片剂 (pastilha)**。Goiânia 40 个家庭龙头 **grab samples**（2014-07）。同时测 pH、浊度、CE、氟化物、大肠菌群。

**主要发现**：
- **粉剂读数 > 片剂**  
- **视觉 disk > 数字仪**（两种试剂均如此）  
- **浊度** 与 free chlorine（尤其 **数字仪**）显著相关  
- 氟化物与 CE **负相关** ($R=-0.5442$)

---

## 2. 中文摘要

巴西 Goiânia 管网末端 40 点现场比对显示：DPD 方法系统偏差可达 **10.5%–47.3%**（方法组合间）；单样本四方法 CV **8.1%–26.1%**。数字 Hach 仪标称精度 **±0.02 mg/L**，但仍系统低于视觉 Dellab disk。所有样本氯浓度 **0.54–2.0 mg/L**，满足巴西法规 **0.2–2.0 mg/L**。作者认为视觉法 field 更方便但 **精度更低、操作者误差更大**。

---

## 3. 方法与设备

| 项目 | 详情 | 来源 |
| --- | --- | --- |
| 采样 | 40 点，6 区，2014-07-15–31；直接龙头，避家用水箱 | `[原文]` §Metodologia |
| 视觉 | Dellab disk，0–3.5 mg/L | `[原文]` |
| 数字 | Hach portable，528 nm，0–4.5 mg/L，**±0.02 mg/L** | `[原文]` |
| 试剂 | DPD **pó / pastilha** | `[原文]` |
| 标准 | SM **4500-Cl G** (APHA 21st) | `[原文]` |
| 统计 | XLSTAT；boxplot 95% CI；**Spearman** 相关 | `[原文]` |

**法规背景**：巴西 Portaria MS 2914/2011 — 管网 **free chlorine ≥ 0.2 mg/L**，上限 2.0 mg/L `[原文]` Intro — 与项目 0.2 mg/L 工作阈值 **同数量级**（巴西国家法规，非 UK）。

---

## 4. 主要结果

### 4.1 浓度范围与合规

- 检出 **0.54–2.0 mg/L** `[原文]` §Resultados  
- 全部满足 0.2–2.0 mg/L  
- 四方法均值线性关系 **$R^2=0.994$**  

### 4.2 方法间系统偏差（均值差异）

| 比较 | 相对差异 |
| --- | --- |
| Digital-pó vs Disco Visual-pastilha | **10.5%** |
| Digital-pastilha vs Disco Visual-pó | **47.3%** |
| Digital-pó vs Digital-pastilha | 18.8% |
| Disco Visual-pó vs pastilha | 12.2% |

**排序（均值从高到低）**：Visual-pó > Visual-pastilha > Digital-pó > **Digital-pastilha**（最低）`[原文]` Fig. 5。

### 4.3 重复性

- 每样本四方法 CV：**8.1%–26.1%**（剔除一异常 42.8%）`[原文]`

### 4.4 Spearman 相关（Table 1）

- Digital-pó vs Digital-pastilha：**0.9545**  
- Visual-pó vs Digital-pó：**0.8237**  
- **浊度 vs Digital 读数**：0.35–0.41（显著）  
- 浊度 vs Visual：**不显著** `[原文]` — 与 SM 4500-Cl G 浊度干扰一致  
- 氟 vs CE：**-0.5442**

---

## 5. 结论（作者）

1. 粉剂 > 片剂；视觉 > 数字。  
2. 浊度干扰数字 DPD。  
3. 视觉更适合现场，但 **精度低、操作者依赖强**。  
4. 建议进一步研究以 **精确加氯、避免浪费**。  

---

## 6. 与本项目的关系

| 环节 | 可写入 thesis 的要点 |
| --- | --- |
| **观测误差模型** | grab sample DPD 可设 $\sigma \approx 0.02$ mg/L（仪器规格）+ **系统偏差项**（方法选择） |
| **似然函数** | 不同设备/试剂 → **非 Gaussian 或 biased likelihood**；Bayesian 中可用 **measurement model** 层 |
| **CV 8–26%** | 相对误差在水厂典型氯水平（~1 mg/L）下约 **0.08–0.26 mg/L** — 与 `<0.2` 阈值判别相关 |
| **浊度协变量** | 若现场有浊度数据，可加入 **heteroscedastic** 噪声模型 `[推断]` |
| **非 UK 数据** | 巴西热带管网；Imperial UK 现场需 D3/D4 补充 |

### 可参考要点（写论文 / 做实验时可直接引用）

1. **T5 似然函数**：观测模型 $C_{obs} \sim \mathcal{N}(C_{true}, \sigma^2)$，**$\sigma = 0.02$ mg/L**（Hach 规格）— Methodology 直接写入参数表。
2. **系统偏差项**：视觉 disk **高于** 数字仪；粉剂 **高于** 片剂 — 合成数据或 Bayesian 中可加 **method-specific bias**（如 +5% / +15%）。
3. **数值引用**：方法间均值差 **10.5%–47.3%**；单样本四方法 CV **8.1%–26.1%** — Discussion 解释「校准 RMSE<0.05 仍可能 **掩盖方法偏差**」。
4. **低浓度区**：样本 0.54–2.0 mg/L；在 **0.2 mg/L 附近** 相对误差更大 — 支持对 `<0.2` 概率分析用 **更宽** 观测噪声。
5. **浊度协变量**：数字 DPD 与浊度显著相关 — 若有浊度数据，Methodology 可写 **heteroscedastic** $\sigma(turbidity)$。
6. **法规对照**：巴西 **0.2–2.0 mg/L** 与 WHO/UK 同量级 — Introduction 可辅助说明 **0.2 mg/L 国际常见**，但 UK 引 F1。
7. **Limitation 句**：「D2 为巴西现场 DPD；UK amperometric 见 D3/D4」— 避免过度外推。

---

## 7. 批判性阅读

**优点**：四方法全交叉、现场真实龙头、并行水质参数、定量 Spearman。  
**局限**：
- 无 **Bland–Altman** / 配对 t 检验细节（仅 % 差异）  
- 40 点、单城市、夏季单窗口  
- 未报告 **重复测量同一样本** 的 pure replicate SD  
- 葡萄牙语 — 方法细节需对照 SM 4500-Cl G  
- **无在线 amperometric** — D4/D5 补  

---

## 8. 待办

- [ ] 将 ±0.02 mg/L 与 10–47% 系统差写入 `plan1.md` observation model 草稿  
- [ ] 对照 Wilde (1991) DPD vs amperometric（文中引述）  
- [ ] 读 D3 (Aisopou & Stoianov 2024) Imperial 在线 vs DPD  

---

## 9. 引用

> Soares SS, Arruda PN, Lobón GS, Scalize PS. Avaliação de métodos para determinação de cloro residual livre em águas de abastecimento público [Evaluation of methods for determining free residual chlorine in public water supply]. *Semina Ciênc Exatas Tecnol*. 2016;37(1):119–130. doi:10.5433/1679-0375.2016v37n1p119

```bibtex
@article{Soares2016DPD,
  author  = {Soares, Samara Silva and Arruda, Poliana Nascimento and Lob{\'o}n, Germ{\'a}n Sanz and Scalize, Paulo S{\'e}rgio},
  title   = {Avalia{\c{c}}{\~a}o de m{\'e}todos para determina{\c{c}}{\~a}o de cloro residual livre em {\'a}guas de abastecimento p{\'u}blico},
  journal = {Semina: Ci{\^e}ncias Exatas e Tecnol{\'o}gicas},
  volume  = {37},
  number  = {1},
  pages   = {119--130},
  year    = {2016},
  doi     = {10.5433/1679-0375.2016v37n1p119},
  note    = {English abstract: Evaluation of methods for determining free residual chlorine in public water supply}
}
```

---

## 13. 修正记录

| # | 说明 |
| --- | --- |
| 1 | literature 已含 PT 标题 + EN 方括号译名 — 与 CrossRef 一致 |
| 2 | 文件名 `D2-Avaliacao_de_metodos...` 与 citation 一致 |
