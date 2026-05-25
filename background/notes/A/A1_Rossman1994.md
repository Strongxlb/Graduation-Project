# A1 — Rossman, Clark, Grayman (1994) 讲解笔记

> 配套文件：`[../Literature/literature.md](../Literature/literature.md)` §A1、`[../../README.md](../../README.md)`、`[../../plan1.md](../../plan1.md)`
> PDF 路径：`[../Literature/rossman-et-al-1994-modeling-chlorine-residuals-in-drinking-water-distribution-systems.pdf](../Literature/rossman-et-al-1994-modeling-chlorine-residuals-in-drinking-water-distribution-systems.pdf)`
>
> **本文风格**：故事 + 直觉为主，公式只解释"为什么这么写"。
> **怎么用这份笔记**：
>
> - **§1** 是论文原文 Abstract + 翻译 + **逐句讲解**（想从论文原文入手就读这一节）
> - **§2** 是 TL;DR（想 60 秒看懂全文就读这一节）
> - 想**顺着故事读完整套理解** → 从 §2 一直读到 §8
> - 想**写论文/找数据** → §9（毕设联系）+ §11（公式/数字速查表）

---

## 1. 原文 Abstract + 翻译 + 讲解

### 1.1 原文（PDF p.803）

> A mass transfer-based model is developed for predicting chlorine decay in drinking-water distribution networks. The model considers first-order reactions of chlorine to occur both in the bulk flow and at the pipe wall. The overall rate of the wall reaction is a function of the rate of mass transfer of chlorine to the wall and is therefore dependent on pipe geometry and flow regime. The model can thus explain field observations that show higher chlorine decay rates associated with smaller pipe sizes and higher flow velocities. It has been incorporated into a computer program called EPANET that can perform dynamic water-quality simulations on complex pipe networks. The model is applied to chlorine measurements taken at nine locations over 53 h from a portion of the South Central Connecticut Regional Water Authority's service area. Good agreement with observed chlorine levels is obtained at locations where the hydraulics are well characterized. The model should prove to be a valuable tool for managing chlorine-disinfection practices in drinking-water distribution systems.

### 1.2 中文翻译（直译版，结构对齐原文）

> 本文提出一个**基于质量传递**的模型，用于预测饮用水管网中余氯的衰减。该模型认为氯在**水体流动**和**管壁**两处同时发生一阶反应。管壁反应的总速率取决于氯向管壁的传质速率，因此依赖于**管道几何**与**流态**。这样一来，模型就能解释现场观察到的现象——**管径越小、流速越高，余氯衰减速率越快**。该模型已集成进一个名为 **EPANET** 的计算机程序，可对复杂管网执行动态水质模拟。本研究将模型应用于 South Central Connecticut Regional Water Authority（SCCRWA）部分服务区的余氯实测数据——9 个位置、53 小时连续观测。在**水力条件刻画清楚**的位置，模拟结果与实测氯浓度吻合良好。本模型应能成为饮用水管网中管理氯消毒实践的有效工具。

### 1.3 逐句讲解（把每一句的"潜台词"挖出来）

摘要短短 8 句，但每一句都在做某件具体的事——下面一句一句拆开看。

---

**第 1 句**

> A mass transfer-based model is developed for predicting chlorine decay in drinking-water distribution networks.
>
> 我们做了一个**基于质量传递的**模型，用来预测饮用水管网中的余氯衰减。

**讲解**：

- **"mass transfer-based"** 这个定语是整个摘要里最重要的词。它在说："**我们的模型和别人不一样的地方在于——我们显式把传质这件事建进去了**"。这是论文区别于 Hunt & Kroon（每根管一个 `k_b` 硬拟合）和早期 Wable 等人（只看 bulk）的核心标签。
- **"chlorine decay"**（余氯衰减）是结果指标，不是机理。读者要明白：这套模型不预测细菌、不预测消毒副产物，只预测**氯本身的浓度变化**。
- **"distribution networks"**（分配管网）——不是水厂内部、不是水源水，是**家庭水龙头之前**那段管子。这是论文的边界。

---

**第 2 句**

> The model considers first-order reactions of chlorine to occur both in the bulk flow and at the pipe wall.
>
> 该模型认为氯在水体流动中**和**管壁上**同时**发生一阶反应。

**讲解**：

- **"first-order"**（一阶）是一个**重要简化**：反应速率 ∝ 浓度本身。这意味着如果氯加倍，衰减速率也加倍。**它不是严格成立的**——A2 (Hua 1999) 等后续工作发现真实衰减更接近"快段+慢段"的双指数。但作为工程近似它够用。
- **"both ... and"**——这是论文的"双段模型"主张。**bulk + wall** 这个二分法成为后续二十多年文献的标准结构（包括 EPANET 默认设置）。
- 这一句**没提传质**——传质是下一句的主角，作者刻意把"反应分两处"和"壁反应受传质限制"拆成两步说。

---

**第 3 句（核心 claim）**

> The overall rate of the wall reaction is a function of the rate of mass transfer of chlorine to the wall and is therefore dependent on pipe geometry and flow regime.
>
> 管壁反应的**总速率**取决于氯到管壁的传质速率，因此依赖于**管道几何**和**流态**。

**讲解**：

- 这是整篇论文的**核心 claim**，也是"为什么这模型聪明"的关键。注意作者用的词是 **"overall rate"**——总速率，意指**反应速率 + 传质速率**串联后的等效速率（即 §4.4 的串联电阻类比）。
- **"is therefore dependent on pipe geometry and flow regime"** 是个**因果链**：传质 → 管径/流速依赖。这一步推理是论文得以解释"小管/快流速 → 快衰减"现象的逻辑桥梁。
- 这一句**没出现公式**，但它实际上描述的就是论文 Eq 3 里那个 `(k_w·k_f)/(k_w+k_f)` 项。

---

**第 4 句（卖点 / 解释力）**

> The model can thus explain field observations that show higher chlorine decay rates associated with smaller pipe sizes and higher flow velocities.
>
> 模型由此可以**解释**现场观察到的现象——管径越小、流速越高，氯衰减越快。

**讲解**：

- **"thus"**（由此/因此）紧扣第 3 句——作者在强调：**这不是经验拟合，这是物理推论**。这一句的份量在于 "explain"（解释）而不是 "fit"（拟合）。这是论文区别于 Hunt & Kroon 的关键卖点。
- **"smaller pipe sizes and higher flow velocities"** 不是随便举例——这正是 1980 年代工程师反复观察、却给不出合理解释的两个现象。作者在这里实际上是在说："**你们二十年来困惑的问题，我们解决了**"。
- 写论文时如果需要一句话总结这篇文章的**贡献**，这就是那一句。

---

**第 5 句（工程实现）**

> It has been incorporated into a computer program called EPANET that can perform dynamic water-quality simulations on complex pipe networks.
>
> 该模型已集成进一个叫 **EPANET** 的计算机程序，可以对复杂管网做动态水质仿真。

**讲解**：

- 这是论文从"理论"跨到"工具"的桥梁。**注意时态——"has been incorporated"**（已经集成进去了）。这意味着这篇 1994 年的论文**写作时 EPANET 已经存在**。
- **"dynamic"**（动态）和**"complex pipe networks"**（复杂管网）一起出现很关键：Biswas 1993 那篇也建了模型，但只能算**单根管 + 稳态**。Rossman 这一句在划界——"我们能处理整张管网 + 随时间变化"。
- **对你毕设的直接含义**：你用 WNTR/EPANET 跑 demo 时，**水质引擎里跑的就是这篇论文的方程**。这不是历史文献，是你正在用的工具的源代码描述。

---

**第 6 句（验证数据）**

> The model is applied to chlorine measurements taken at nine locations over 53 h from a portion of the South Central Connecticut Regional Water Authority's service area.
>
> 本研究将模型应用于 SCCRWA 部分服务区的余氯实测数据——9 个位置、53 小时。

**讲解**：

- **"applied to"**（应用于实测数据）——这是在告诉审稿人/读者："**我们不只是纸上谈兵，我们用真实数据验证过**"。这是论文从 model → applied science 的转折。
- **"nine locations over 53 h"** 是个**关键数字**。在 1990 年代初，这种规模的时空连续观测非常稀少。这也是为什么 SCCRWA Cherry Hill 数据集后来成为**经典 benchmark**——同时代很难找到第二份。
- **隐含的限制**：只有一个网络、一段时间。摘要不会说，但你做研究要明白——基于单一案例的结论外推到其他系统**有不确定性**。

---

**第 7 句（关键诚实声明）**

> Good agreement with observed chlorine levels is obtained at locations where the hydraulics are well characterized.
>
> 在**水力条件刻画得清楚**的位置，模拟与实测氯浓度吻合良好。

**讲解**：

- **这一句是整个摘要最重要的"隐藏陷阱"**。作者没说 "good agreement is obtained"，而是加了限定语 **"where the hydraulics are well characterized"**。
- 翻译成大白话：**水力没校准好的地方，水质模型也好不了**。这是水质建模领域的"金科玉律"，也是 1990 年代实践的痛点。
- **对你毕设的直接含义**：
  - 这就是为什么论文用了"先 fluoride 校水力 → 再 chlorine 校水质"的两阶段流程
  - 这也是为什么 Cherry Hill 案例里那些**死端节点（10, 28, 34）拟合差**——它们用水量小、随机性大，水力本身就没校准好
  - 你跑 Net1 demo 时，因为 Net1 是**合成网络**（水力是已知的，无需校准），所以这条限制对你**不适用**。但如果未来要做真实管网，要把这条记在脑子里。
- 写 thesis 的 Methodology 或 Discussion 时，**可以直接引这一句作为"hydraulics-first"工作流的依据**。

---

**第 8 句（应用展望）**

> The model should prove to be a valuable tool for managing chlorine-disinfection practices in drinking-water distribution systems.
>
> 本模型应能成为饮用水管网中管理氯消毒实践的有效工具。

**讲解**：

- 摘要的标准收尾——把工具往**应用价值**上推。注意用词是 **"should prove to be"**（"应能成为"，**未来时 + 推测语气**），不是 "is"（"是"）。这是一种学术上谨慎的措辞——作者在说"我们认为它有用，但能不能成为行业标准，要看后续实践"。
- 事实上，30 年后回看，EPANET 确实成为了行业标准——**这句"should prove to be"的预言完全兑现了**。
- 写 thesis 的 Introduction 时，如果你需要论证"EPANET 是行业标准工具"，可以引这篇 + 引用次数（截至 2026-04 已 386+ 次）作为证据。

---

### 1.4 一段话把整个摘要消化成"我懂了什么"

如果让你用自己的话向同学讲清这个摘要，可以这样讲：

> "1994 年之前大家发现，余氯在管网里掉得比烧杯里快得多，但**说不清原因**——你只能给每根管子调一个 `k` 硬凑。Rossman 这篇论文说：'其实管壁本身也在吃氯，但更关键的是——**氯要先从水里运到管壁才能被吃掉**。所以表面上看是化学反应，其实有一半是物理传质的事'。把这个想法写成方程之后，**小管/快流速衰减快**这个十几年没人解释清楚的现象，自然就出来了。他们把这套模型塞进了一个叫 EPANET 的软件，并用一组真实管网数据（53 小时、9 个点）验证——水力条件清楚的地方拟合很好，水力差的地方拟合也差（这条诚实声明对工程很重要）。三十年后，这篇文章定义了整个领域的标准工具。"

---

## 2. 一分钟看懂这篇论文

**这是什么**：EPANET 水质模块的奠基论文。第一作者 Rossman 就是 EPANET 的作者本人。

**它干了一件事**：用一个**物理上说得通**的模型，解释了 1980–1990 年代工程师反复观察到、但说不清原因的一个现象——

> "为什么同一份水，放在烧杯里慢悠悠地衰减，进了管网就**快好几倍**？而且小管比大管更快、流速大的地方比流速小的地方更快？"

**它的答案分三层**：

1. **bulk reaction**（水体里的反应）——和烧杯里发生的是一回事，速率 = `k_b`
2. **wall reaction**（管壁上的反应）——这是烧杯里**没有**的东西，速率 = `k_w`
3. **传质**（mass transfer）——管壁反应**只能消耗到达管壁的氯**。水中央的氯得先"走"到壁面才能反应，这个"走"的速度 = `k_f`，由流速和管径决定

**为什么这个洞察重要**：第三层是**关键创新**。前人也想过 wall reaction，但要么完全忽略传质（简单粗暴），要么用一根管一个 `k_b` 硬拟合（参数爆炸）。Rossman 把传质这层显式加进来，**全网只需两个参数 `k_b` 和 `k_w`** 就能解释为什么"小管 + 快流速 = 衰减快"。

如果你只能记三件事：

- 余氯衰减是**串联过程**：先传质到壁，再在壁上反应。任意一环慢，整条链就慢。
- 全网两个参数：`**k_b`（水里的）+ `k_w`（管壁的）**。EPANET 里 `bulk_coeff` / `wall_coeff` 就是这俩。
- Rossman 用**试 2 个值看 RMSE** 做校准（确定性、手动 sweep）——**这正是你毕设要补的洞**：他没给 `k_w` 的不确定性。

---

## 3. 故事的起点：1994 年之前大家在为什么发愁

想象你是 1990 年的供水工程师。你要保证管网末端的家庭水龙头流出来的水还有一点余氯（防细菌），所以你在水厂出口投了 1.1 mg/L 的氯。可问题来了：

- **烧杯试验**告诉你：这水放 12 小时也就掉一半，按这速度，远端 8 小时车程的居民家应该还剩 0.7 mg/L 才对。
- **现场实测**告诉你：远端实际只剩 0.2 mg/L，少了一倍多。

**水在管网里被什么东西"额外吃掉"了？**

当时学界的几个回答：


| 谁                    | 怎么说                        | 问题在哪                       |
| -------------------- | -------------------------- | -------------------------- |
| Clark et al. (1993)  | "余氯到处都不一样，确实有这现象"          | **现象描述，没机理**               |
| Wable et al. (1991)  | "管子里掉得比烧杯快，可能是壁的事儿"        | 没有定量模型                     |
| Hunt & Kroon (1991)  | "那我每根管子调一个不同的 `k_b` 总能拟合上" | **几百根管几百个参数**，工程上不可用       |
| Biswas et al. (1993) | "单根管子稳态下，可以同时考虑径向扩散 + 壁反应" | 只能算**一根管子、稳态**，不能算管网、不能算时变 |


Rossman 看到的痛点：缺一个**简洁、物理、能跑整张管网、能跑动态**的工具。这就是这篇论文要干的。

---

## 4. Rossman 的三层洞察（论文的核心思想）

### 4.1 第一层：水体里的反应（bulk）

这层好理解。水里有有机物（NOM）和氨等还原剂，氯会和它们慢慢反应。这就是你**烧杯试验**里测到的那种衰减，是一阶反应：

```
dc/dt = -k_b · c
```

这里 `c` 是水里氯浓度，`k_b` 是 bulk decay rate。**在烧杯里这是唯一发生的事**。

### 4.2 第二层：管壁上的反应（wall）——烧杯里没有

把同样的水灌进一根管子，再来一层反应：**管壁本身（腐蚀产物、生物膜、铁锈）也会消耗氯**。

如果我们假设这个反应也是一阶的，速率应该是：

```
壁面反应速率 = k_w · c_w
```

注意：这里用的是 `c_w`（壁面处氯浓度），**不是 `c`（水中央浓度）**。

> **这一步是论文真正聪明的地方**：很多人会偷懒写成 `k_w · c`，但物理上不对——壁面反应只能吃掉**已经到达壁面的氯**。要是水中央有氯但壁面没有（来不及补充），反应就停了。

### 4.3 第三层：传质（mass transfer）——把氯从水中央"运"到壁面

水流是湍流（一般情况下），主流速度方向沿管轴。**横向**（径向）的氯输运靠湍流扩散 + 分子扩散，通过一层薄薄的**边界层**完成。

这个"运货"的速度由 `k_f` 描述，单位是 m/s（不是 /s！这是一个**通量**速率，不是化学反应速率）：

```
单位时间从主流送到壁的氯量 ∝ k_f · (c - c_w)
```

直觉：

- 如果 `c_w` 接近 `c`（壁面浓度和水中央一样高）→ 没有浓度梯度 → 不传输 → 反应饿死
- 如果 `c_w` 接近 0（壁面把氯吃得很猛）→ 浓度梯度很大 → 拼命传 → 但能不能跟上反应速度，得看 `k_f` 够不够大

### 4.4 串联起来：取小者为瓶颈

这是论文最漂亮的物理直觉。可以用**串联电路**类比：

```
水中央(c)  ──[传质阻力 1/k_f]──  壁面(c_w)  ──[反应阻力 1/k_w]──  消失
```

像两个电阻串联，**总阻力 = 1/k_w + 1/k_f**，所以等效"导通率"是：

```
1 / (1/k_w + 1/k_f) = (k_w · k_f) / (k_w + k_f)
```

这就是论文 Eq 3 里那个看起来有点突兀的 `(k_w·k_f)/(k_w+k_f)` 的来历——**就是两个串联电阻的等效公式**。

物理推论：

- 如果 `k_f` 远大于 `k_w`（传质很快、反应很慢）→ 等效 ≈ `k_w` → **反应限制**，瓶颈在化学
- 如果 `k_f` 远小于 `k_w`（传质很慢、反应很快）→ 等效 ≈ `k_f` → **传质限制**，瓶颈在物理
- 取**较小**的那个为瓶颈，正是串联电路的常识

这一条直觉是后面 §8 解读 Fig 13 的钥匙。

---

## 5. 数学是怎么变美的（不深究推导）

把上面三层串起来，对一段沿轴向流动的水，写下守恒方程（论文 Eq 1）：

```
∂c/∂t = -u·(∂c/∂x) - k_b·c - (k_f/r_h)·(c - c_w)
```

**这里每一项的物理意义**：

- `-u·∂c/∂x`：水流把氯沿管轴带走（对流）
- `-k_b·c`：bulk 反应在吃氯
- `-(k_f/r_h)·(c - c_w)`：往壁面流失的氯，`r_h = d/4` 是水力半径（壁面积/体积的几何因子）

但这里有个新未知数 `c_w`。怎么办？

**关键近似**：假设壁面浓度**准稳态**——壁面被反应吃掉的速度等于传质送来的速度（壁面不积累）：

```
k_f · (c - c_w) = k_w · c_w        ← 这是论文 Eq 2
```

解出 `c_w`，代回去，**消掉 `c_w` 这个变量**，得到论文最重要的 **Eq 3**：

```
**∂c/∂t = -u·(∂c/∂x) - k_b·c - (k_w·k_f) / (r_h·(k_w + k_f)) · c**
```

看出来了吗？这就是 §4.4 的串联电阻公式被乘上了几何因子 `1/r_h`，套进一阶衰减项里。

**整段方程可以重写成更熟悉的形式**：

```
∂c/∂t = -u·(∂c/∂x) - K · c,    其中 K = k_b + (k_w·k_f) / (r_h·(k_w + k_f))
```

`K` 就是**等效一阶衰减系数**——这正是 EPANET / WNTR 在水质引擎里实际用的形式。

> 对管网第 i 根管段就给每根管一个 `K_i`，因为 `r_h` 和 `k_f` 跟管径和流速有关（论文 Eq 9–10）。`k_b` 和 `k_w` 全网公用，但 `K_i` 每根管都不一样——**这就是"全网两个参数"的真实含义**。

---

## 6. 为什么"小管 + 快流速 = 衰减快"自然就出来了

这一节是论文最大的"卖点"——之前需要硬拟合的现象，现在从物理推导**自然涌现**。

回看 Eq 3 里的衰减系数：

```
K = k_b + (k_w·k_f) / (r_h·(k_w + k_f))
```

`k_b`、`k_w` 是化学常数，不变。`r_h = d/4` 跟管径直接相关。`k_f` 跟流态相关——通过 **Sherwood 数**（论文 Eq 4–8）：

```
k_f = Sh · (D/d)        ← D 是分子扩散系数（很小的常数），d 是管径

湍流（Re > 2300）：Sh = 0.023 · Re^0.83 · Sc^0.333
层流（Re < 2300）：Sh = 3.65 + (一个跟 d/L、Re、Sc 有关的修正项)

其中 Re = u·d/ν（流速 × 管径 / 运动粘度）
```

**直觉解读**：

- **管径 `d` 变小** → `r_h` 变小（壁面积/体积变大）→ 同样多的水接触更多壁 → 衰减更快 ✓
- **流速 `u` 变大** → `Re` 变大 → 边界层变薄 → `k_f` 变大 → 传质更快 → 衰减更快 ✓
- **管径 `d` 变小**（再来一次）→ `Re` 还在 → `k_f = Sh · D/d` 里分母变小 → `k_f` 也变大 ✓

所以"小管 + 快流速 = 衰减快"**不是经验规律**，是这个模型的**直接预言**。这是论文真正出彩的地方。

---

## 7. 这套模型怎么验证？Cherry Hill 案例

Rossman 团队跑了一个真实管网做对照：康涅狄格州 South Central Connecticut Regional Water Authority 的 **Cherry Hill/Brushy Plains 服务区**（5.2 km²，住宅区）。

### 7.1 数据采集（1991 年 8 月 13–15 日）

- 53 小时连续观测
- 9 个采样点：1 个泵站 + 1 个水塔 + 7 个消火栓
- 总样本：**181 对**（每对 = 余氯浓度 + fluoride 浓度）
- 测量方式（混合）：
  - 泵站 + 水塔用**连续电化学余氯分析仪**（Rosemount 4024）
  - 7 个 hydrant 用 **DPD 比色法**（Hach 46700-05）做手动 grab sample
- 进水维持 **1.1 mg/L**

### 7.2 两阶段校准：先水力、后水质

**这套流程值得抄进你毕设的 Methodology**。

**阶段一：用 fluoride 当 conservative tracer 校准水力**

- fluoride 不反应、不衰减，所以它的浓度变化**完全反映水流路径**
- 8/13 9:00 关掉水厂的 fluoride 投加，看 fluoride 怎么稀释扩散
- 调整节点用水量和管段粗糙度，让模拟 fluoride 序列 ≈ 实测 fluoride 序列
- 这一步搞定**"水从哪儿来、什么时候到、有多少"**

**阶段二：水质校准**

- `k_b = 0.55 /day` **独立**用实验室 beaker test 测出来，**不动**
- `k_w` 在 [0.15, 0.45] m/day 之间**手动 sweep**——只试几个值，看哪个 RMSE 小
- 把模型预测的 chlorine 和 7 个 hydrant 的实测 chlorine 对比

> **注意单位**：`k_b` 是 /day（一阶反应常数），`k_w` 是 **m/day**（传质式通量速率，因为它要乘 `c - c_w` 后再除 `r_h` 才能变成 /day）。**单位不一样是因为物理意义不一样**——这是初学者常踩的坑。

### 7.3 结果


| 校准参数               | RMSE           |
| ------------------ | -------------- |
| `k_w = 0.45 m/day` | **0.186 mg/L** |
| `k_w = 0.15 m/day` | **0.211 mg/L** |


**拟合好的点**：3, 6, 11, 19, 25（这些点水力刻画清晰）
**拟合差的点**：10, 28, 34（位于人口稀疏的死端，需水量估不准 → 阶段一就没校准好 → 阶段二也好不了）

**这是论文里一个重要的诚实声明**："水力差则水质差"——给你一个直接的教训。

---

## 8. 论文最深的洞察：瓶颈到底在哪？

如果上面是"用这模型能算啥"，那这一节是"这模型告诉你**世界长什么样**"。

### 8.1 反应贡献分解（Fig 14）

Rossman 把整个 Cherry Hill 系统失去的氯按来源分了三份：


| 损失来源     | `k_w = 0.45 m/day` | `k_w = 0.15 m/day` |
| -------- | ------------------ | ------------------ |
| **管壁反应** | **67%**            | 48%                |
| 水体反应     | 12%                | 19%                |
| 水塔（储存损失） | 21%                | 33%                |


**第一个发现**：不管 `k_w` 取高还是低，**管壁占了一半以上的失氯量**。

**工程含义**：在这套管网里——

- 改水塔操作（缩短停留时间）的收益有限（最多 21–33%）
- 真正能立竿见影的是**清管 / 换管**（占 48–67% 的源头）

这条结论比"我能算出余氯"重要得多——**模型把工程优先级翻了过来**。

### 8.2 反应限制 vs 传质限制（Fig 13）

回到 §4.4 的串联类比。论文画了一张图：**等效衰减系数 vs 流速**。

- `k_w = 0.15`（反应很慢）：曲线随流速基本平的——传质再快也没用，因为壁反应自己跟不上。→ **反应限制**
- `k_w = 0.45`（反应较快）：曲线随流速明显上升——加快流速 → 加快传质 → 加快总衰减。→ **传质限制**

**直觉**：低 `k_w` 时管壁这一段是"慢车道"，传质再快也只能等它；高 `k_w` 时管壁可以吃得很猛，但要看你能不能把氯送过去。

**这个发现告诉你**：同样一根管，反应是化学的事，传质是流体力学的事——**你想干预哪边，先要知道当前瓶颈在哪边**。

---

## 9. 跟你毕设的关系（重点章节）

这篇论文不是历史文献——它就是你毕设代码里跑的那个引擎。

### 9.1 你的代码哪里用到了它


| 你的代码/工件                                 | Rossman 1994 对应                                                                                    |
| --------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `src/01_demo_wntr.py` 里 `bulk_coeff` 参数 | `k_b`（Eq 3 第二项）                                                                                    |
| `src/01_demo_wntr.py` 里 `wall_coeff` 参数 | `k_w`（Eq 3 第三项的 `k_w`）                                                                             |
| EPANET 水质引擎跑的算法                         | **DVEM**（Discrete Volume Element Method）；详见 Rossman 1994 PDF p.808 / Rossman, Boulos & Altman 1993 |
| Net1 demo 计算出的节点余氯曲线                    | Eq 3 + DVEM 的直接结果                                                                                  |


**这意味着**：你之前跑 demo 时调 `wall_coeff` 看到的余氯下降，物理上就是论文 Eq 3 在跑。**你不是在用一个不透明的工具——你在用 Rossman 这篇文章本身**。

### 9.2 这篇论文的"洞"，正是你毕设要补的


| Rossman 1994 的做法                                                       | 你的毕设要补什么                                                |
| ---------------------------------------------------------------------- | ------------------------------------------------------- |
| 手动 sweep `k_w` ∈ [0.15, 0.45]，只试 2 个值，看 RMSE                           | 用 **Monte Carlo / Bayesian** 给 `k_w` 一个**后验分布**，不是一个点估计 |
| RMSE 报了，但**没考虑测量误差**（DPD 自己就有 6–38% 的不确定度，见 D5 Guigues 2022）           | 把测量误差作为先验输入，让校准结果带不确定性                                  |
| 单一 `k_b`、`k_w` 应用于全网                                                   | 分管材/管龄/管径段，呼应 A4 Hallam 2002 的实测 `k_w` 分布               |
| **没有可识别性分析** —— 0.186 vs 0.211 mg/L 差异**可能在噪声水平之下**，但 1994 paper 没说这件事 | T4 之前用 SALib (Morris/Sobol) 先做参数敏感性/可识别性                |
| 单一案例（Cherry Hill）                                                      | 你打算跑 Net1 + Net3（+ BWSN 如能拿到）                           |


**T5 章节的核心 motivation 一句话讲**：

> Rossman 1994 给出了**模型**，但把校准当成"找一组使 RMSE 最小的参数"。在嘈杂的现实数据里，这种"最佳值"很可能不显著优于一个**区间**——而这个区间会让"管壁占 67%"这条工程结论的不确定性翻出来。这正是本项目要做的事。

### 9.3 写论文时怎么用


| 章节                              | 怎么引用                                                                                          |
| ------------------------------- | --------------------------------------------------------------------------------------------- |
| **Background / Methodology**    | Eq 3 + DVEM 即 EPANET / WNTR 水质引擎的物理基础；引 Rossman 1994 一篇就够                                     |
| **T4 baseline**                 | 复刻"瓶试定 `k_b` + 现场扫 `k_w`"两阶段流程，Brushy Plains 的 `k_w` ∈ [0.15, 0.45]、RMSE ≈ 0.19 是你的**文献对照区间** |
| **Discussion (Fig 14 同款图)**     | 仿 Fig 14 做"bulk / wall / tank"占比图，对比 Net1 demo 在不同 `k_w` 下的占比变化                               |
| **Discussion (局限)**             | "Hydraulics first, water quality second" → Net1 没有 tracer 数据所以不能严格水力校准，这是 demo 的局限            |
| **Introduction (research gap)** | "现有校准框架（Rossman 1994 范式）把校准当确定性问题，不显式处理测量误差和参数不确定性" → 引出你的 Bayesian/MCS 方法                    |


---

## 10. 写论文 + 思考题

### 10.1 三个值得写进 thesis 的关键引用点

1. **物理模型来源**：Rossman et al. 1994 是 EPANET 水质模块的奠基论文，Eq 3 是 `wall_coeff` / `bulk_coeff` 物理含义的来源。
2. **方法论范式**：两阶段校准（fluoride 先校水力 → chlorine 再校水质）是行业标准做法，可在 Methodology 直接引用。
3. **研究 gap 切入点**：1994 paper 的 `k_w` 用了确定性手动 sweep，无可识别性分析、无测量误差、无后验分布——本项目用 MCS/Bayesian 补这条。

### 10.2 想想看（开放问题）

1. **Net1 demo 能不能复现 Fig 13？** Net1 管径 6–18 in 和 Cherry Hill 8/12 in 同量级，开 wall decay、扫 `k_w` ∈ [0.15, 0.45] 应能看到从反应限制到传质限制的过渡。可作为 Week 3 baseline 的一组实验。
2. **测量误差能不能掩盖校准差异？** D5 (Guigues 2022) 给出 DPD 的相对不确定度 6–38%。Rossman 报的 RMSE 差 0.186 vs 0.211 = 0.025 mg/L，相对于 0.5–1 mg/L 量级的浓度大约 3–5%——**很可能在测量噪声之下**。这意味着 1994 paper 无法基于数据"显著拒绝"任一 `k_w`。**这就是 T5 的核心动机**。
3. **wall 67% 这条工程结论有多稳？** 如果用 MC 在 `k_w` ∈ [0.15, 0.45] 均匀采样 1000 次，wall 占比的 90% CI 可能横跨 48–67%。这区间是否会改变"先做管道清洗"的优先级？这可以是一组实验。
4. **Cherry Hill 的 `.inp` 文件能不能拿到？** 这是本领域罕见有完整 53h × 9 点实测的网络，能复刻它做不确定性校准的对照实验会很有价值。可能要邮件问 SCCRWA 或导师。

---

## 11. 速查表（公式 + 数据 + 符号）

> 想看故事跳到 §2；这里是公式表 + 数据点速查。

### 11.1 三个最重要的方程

**等效衰减系数**（论文 Eq 3，写成熟悉的形式）：

```
∂c/∂t = -u·(∂c/∂x) - K · c

其中 K = k_b + (k_w · k_f) / (r_h · (k_w + k_f))
```

**Sherwood 数关联**（论文 Eq 4–8）：

```
k_f = Sh · (D/d)

湍流（Re > 2300）： Sh = 0.023 · Re^0.83 · Sc^0.333
层流（Re < 2300）： Sh = 3.65 + (0.0668·(d/L)·(Re·Sc)) / (1 + 0.04·[(d/L)·(Re·Sc)]^(2/3))

Re = u·d/ν,    Sc = ν/D
```

**水力半径**：满管圆管时 `r_h = d/4`（论文 p.804）。

### 11.2 Cherry Hill 案例关键数字


| 项                | 值                                          |
| ---------------- | ------------------------------------------ |
| 网络               | Cherry Hill/Brushy Plains, SCCRWA, 康涅狄格州   |
| 服务区              | 5.2 km²（住宅）                                |
| 平均用水             | 20.2 L/s                                   |
| 干管管径             | 8 in (20.3 cm) 与 12 in (30.5 cm)           |
| 采样               | 1991-08-13 至 08-15，53 h，9 点，**181 对**      |
| 进水氯              | 1.1 mg/L                                   |
| `k_b`            | **0.55 /day**（lab beaker test，**独立测，不调**）  |
| `k_w` 试值         | **0.15、0.45 m/day**                        |
| RMSE             | 0.186（`k_w=0.45`） / 0.211（`k_w=0.15`） mg/L |
| 反应贡献（`k_w=0.45`） | wall **67%** / bulk 12% / tank 21%         |
| 反应贡献（`k_w=0.15`） | wall 48% / bulk 19% / tank 33%             |
| 拟合好的点            | 3, 6, 11, 19, 25                           |
| 拟合差的点            | 10, 28, 34（死端，水力校准本身差）                     |


### 11.3 符号速查（论文 Appendix II）


| 符号    | 含义                 | 单位                 |
| ----- | ------------------ | ------------------ |
| `c`   | bulk 余氯浓度          | mg/L               |
| `c_w` | 壁面余氯浓度             | mg/L               |
| `k_b` | bulk 一阶反应常数        | **1/day**          |
| `k_w` | 壁面一阶反应常数           | **m/day** ⚠️ 单位不同！ |
| `k_f` | 传质系数               | m/s                |
| `K`   | 等效一阶衰减常数           | 1/day              |
| `r_h` | 水力半径 = d/4         | m                  |
| `d`   | 管径                 | m                  |
| `u`   | 流速                 | m/s                |
| `Re`  | Reynolds 数 = u·d/ν | 无量纲                |
| `Sc`  | Schmidt 数 = ν/D    | 无量纲                |
| `Sh`  | Sherwood 数         | 无量纲                |
| `D`   | 分子扩散系数             | m²/s               |
| `ν`   | 运动粘度               | m²/s               |


---

## 12. 元数据（已验证）


| 字段          | 内容                                                                 |
| ----------- | ------------------------------------------------------------------ |
| Title       | Modeling Chlorine Residuals in Drinking-Water Distribution Systems |
| Authors     | **Lewis A. Rossman**, Robert M. Clark, Walter M. Grayman           |
| Affiliation | US EPA Risk Reduction Engineering Lab, Cincinnati；Grayman 为咨询工程师   |
| Journal     | *Journal of Environmental Engineering* (ASCE)                      |
| 提交 / 出版     | Submitted 1993-04-15；published Vol 120, No. 4, **1994-07/08**      |
| 页码          | 803–820（18 页）                                                      |
| DOI         | `10.1061/(ASCE)0733-9372(1994)120:4(803)`                          |
| Paper No.   | 5922                                                               |
| 被引数         | 386 (CrossRef) / 494 (OpenAlex)（截至 2026-04）                        |
| 优先级         | **P0**（literature.md §A1）                                          |
| 状态          | `read`（PDF 已通读）                                                    |


**为什么是 P0**：第一作者 Rossman 就是 EPANET 的作者本人，本文是 **EPANET water quality module** 的奠基论文。文中明确提到该模型已集成进 "a computer program called EPANET"（p.69）。

---

## 13. 引用模板

**Vancouver 风格**：

> Rossman LA, Clark RM, Grayman WM. Modeling chlorine residuals in drinking-water distribution systems. *J Environ Eng*. 1994;120(4):803–820. doi:10.1061/(ASCE)0733-9372(1994)120:4(803)

**Harvard 风格**：

> Rossman, L.A., Clark, R.M. and Grayman, W.M. (1994) 'Modeling chlorine residuals in drinking-water distribution systems', *Journal of Environmental Engineering*, 120(4), pp. 803–820. doi: 10.1061/(ASCE)0733-9372(1994)120:4(803).

**BibTeX**（可写入 `../../thesis/refs.bib`）：

```bibtex
@article{Rossman1994ChlorineResiduals,
  author    = {Rossman, Lewis A. and Clark, Robert M. and Grayman, Walter M.},
  title     = {Modeling Chlorine Residuals in Drinking-Water Distribution Systems},
  journal   = {Journal of Environmental Engineering},
  volume    = {120},
  number    = {4},
  pages     = {803--820},
  year      = {1994},
  doi       = {10.1061/(ASCE)0733-9372(1994)120:4(803)},
  publisher = {American Society of Civil Engineers}
}
```

---

## 14. 我下一步可以做的事

- 找 Cherry Hill 网络的 `.inp`（若公开），用本项目框架复刻该案例做不确定性校准对照
- 通读 Rossman, Boulos, Altman 1993（DVEM 原文），必要时在 Methodology 简述 DVEM
- 通读 EPANET 2.2 Manual（B2），核对现行 implementation 是否仍是 DVEM
- 通读 Hallam et al. 2002（A4），对照 SCCRWA 推出的 `k_w` ≈ 0.15–0.45 m/day 是否在该论文实测分布内

