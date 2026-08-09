# Net3 论文公式 · 位置 + LaTeX 对照表

在 Word 里逐条替换成「插入公式」对象：

1. 选中并删掉旧公式（原 `\[...\]` 文字或已转的 Unicode）。
2. 按 `Alt` + `=` 插入空公式。
3. 公式工具栏 →「转换 / Conversions」→ 点 `{}LaTeX`（输入模式设为 LaTeX）。
4. 粘贴下面对应代码块里的 LaTeX，按回车 / 点「Convert → Professional」排版。

> **已是真正公式、不要动**：§3.2「Hydraulic and chlorine transport modelling」里的单位换算/本体系数
> （`k_b = -0.5 day⁻¹`、`time⁻¹`、`m day⁻¹`、`k_{b,s}=k_{b,d}/86400`、`k_{w,s}=k_{w,d}/86400`）
> 之前已经做成 Word 原生公式了。
>
> 兼容性：若 `\begin{cases}` / `\arg\min` / `\mathrm` 在你的 Word 版本不转换，见文末备注。

---

## §3.4 Synthetic wall-decay grouping in Net3

**1. 搜「The imposed first-order wall reaction coefficients were:」→ 其后三条**

```latex
k_{w,\mathrm{old}} = -1.0\ \mathrm{m/day}
```

```latex
k_{w,\mathrm{average}} = -0.1\ \mathrm{m/day}
```

```latex
k_{w,\mathrm{new}} = -0.05\ \mathrm{m/day}
```

**2. 搜「The imposed grouped wall-decay vector can be written as」**

```latex
\theta_{\mathrm{true}} = \left(k_{w,\mathrm{old}},\ k_{w,\mathrm{average}},\ k_{w,\mathrm{new}}\right) = \left(-1.0,\ -0.1,\ -0.05\right)\ \mathrm{m/day}
```

---

## §3.5 Synthetic monitoring observations

**3. 搜「the model-generated true chlorine concentration is denoted as」**（单符号，可留斜体文字）

```latex
C_{\mathrm{true}}(t,n)
```

**4. 搜「The synthetic observed chlorine concentration was defined as」**

```latex
C_{\mathrm{obs}}(t,n) = \mathrm{max}\left(0,\ C_{\mathrm{true}}(t,n) + \epsilon(t,n)\right)
```

**5. 搜「assumes independent Gaussian noise:」**

```latex
\epsilon(t,n) \sim \mathcal{N}(0,\ \sigma^2)
```

**6. 搜「the standard deviation of the observation error was set to」**

```latex
\sigma = 0.1\ \mathrm{mg/L}
```

---

## §3.5.2 Measurement-noise sensitivity check

**7. 搜「using three Gaussian observation-noise levels:」**

```latex
\sigma = 0.02,\ 0.05,\ 0.10\ \mathrm{mg/L}
```

---

## §3.6.1 Parameter vector and objective function

**8. 搜「The parameter vector was defined as」**

```latex
\theta = \left(k_{w,\mathrm{old}},\ k_{w,\mathrm{average}},\ k_{w,\mathrm{new}}\right)
```

**9. 搜「simulated chlorine concentrations at the monitoring nodes:」**（单符号）

```latex
C_{\mathrm{sim}}(t,n;\theta)
```

**10. 搜「compared with the noisy synthetic observations,」**（单符号）

```latex
C_{\mathrm{obs}}(t,n)
```

**11. 搜「the root mean square error, RMSE:」**

```latex
RMSE(\theta) = \sqrt{\frac{1}{N_t N_m} \sum_{t=1}^{N_t} \sum_{n=1}^{N_m} \left[C_{\mathrm{sim}}(t,n;\theta) - C_{\mathrm{obs}}(t,n)\right]^2}
```

---

## §3.6.2 Deterministic grid-search

**12. 搜「evaluated candidate values of the three grouped wall reaction coefficients,」**（同 #8）

```latex
\theta = \left(k_{w,\mathrm{old}},\ k_{w,\mathrm{average}},\ k_{w,\mathrm{new}}\right)
```

**13. 搜「the grid candidate with the minimum RMSE:」**

```latex
\hat{\theta}_{\mathrm{grid}} = \mathrm{argmin}_{\theta_g}\, RMSE(\theta_g)
```

---

## §3.6.3 GLUE

**14. 搜「uniform ranges for the three grouped wall reaction coefficients:」→ 其后三条**

```latex
k_{w,\mathrm{old}} \sim U(-1.5,\ -0.2)
```

```latex
k_{w,\mathrm{average}} \sim U(-0.2,\ -0.04)
```

```latex
k_{w,\mathrm{new}} \sim U(-0.10,\ -0.005)
```

**15. 搜「A total of」**

```latex
N_s = 2000
```

**16. 搜「Each sampled parameter vector was denoted as」**

```latex
\theta_i = \left(k_{w,\mathrm{old},i},\ k_{w,\mathrm{average},i},\ k_{w,\mathrm{new},i}\right)
```

**17. 搜「reproduced the observations sufficiently well:」**

```latex
RMSE(\theta_i) < 0.12\ \mathrm{mg/L}
```

**18. 搜「The behavioural indicator was defined as」**

```latex
B_i = \begin{cases} 1, & RMSE(\theta_i) < 0.12\ \mathrm{mg/L} \\ 0, & RMSE(\theta_i) \geq 0.12\ \mathrm{mg/L} \end{cases}
```

**19. 搜「an informal Gaussian likelihood was assigned to each sampled parameter vector based on its RMSE:」**

```latex
L_i = \exp\left[-\frac{1}{2}\left(\frac{RMSE(\theta_i)}{\sigma_L}\right)^2\right]
```

**20. 搜「where」（紧接在上面 L_i 之后的那句）**

```latex
\sigma_L = 0.1\ \mathrm{mg/L}
```

**21. 搜「The final GLUE weight for each sampled parameter vector was calculated as」**

```latex
w_i = \frac{L_i B_i}{\sum_{j=1}^{N_s} L_j B_j}
```

**22. 搜「it is a weighted behavioural ensemble:」**

```latex
\left\{\theta_i,\ w_i\right\}_{i=1}^{N_s}
```

---

## § Propagation of GLUE ensemble

**23. 搜「For each behavioural parameter set,」**（同 #16）

```latex
\theta_i = \left(k_{w,\mathrm{old},i},\ k_{w,\mathrm{average},i},\ k_{w,\mathrm{new},i}\right)
```

**24. 搜「a chlorine concentration time series over the post-warm-up period:」**（单符号）

```latex
C_{\mathrm{sim},i}(t,n)
```

**25. 搜「The resulting ensemble,」**

```latex
\left\{C_{\mathrm{sim},1}(t,n),\ C_{\mathrm{sim},2}(t,n),\ \ldots,\ C_{\mathrm{sim},N_b}(t,n)\right\}
```

**26. 搜「the cumulative weight first reached the probability level」**

```latex
Q_p(t,n) = \mathrm{inf}\left\{c:\ \sum_{i:\,C_{\mathrm{sim},i}(t,n)\leq c} w_i \geq p\right\}
```

**27. 搜「the 5th, 50th and 95th weighted quantiles were used:」**

```latex
Q_{0.05}(t,n),\quad Q_{0.50}(t,n),\quad Q_{0.95}(t,n)
```

---

## § Threshold-based low-chlorine risk assessment

**28. 搜「The threshold used in the Net3 synthetic analysis was」**

```latex
C_{\min} = 0.2\ \mathrm{mg/L}
```

**29. 搜「the GLUE propagation stage produced a simulated chlorine concentration」**（单符号）

```latex
C_{\mathrm{sim},i}(t,n)
```

**30. 搜「A below-threshold indicator was defined as」**

```latex
I_i(t,n) = \begin{cases} 1, & C_{\mathrm{sim},i}(t,n) < C_{\min} \\ 0, & C_{\mathrm{sim},i}(t,n) \geq C_{\min} \end{cases}
```

**31. 搜「the weighted below-threshold probability at each node and time step:」**

```latex
P_n(t) = \sum_{i=1}^{N_b} w_i\, I_i(t,n)
```

**32. 搜「averaged over all post-warm-up time steps:」**

```latex
P_n = \frac{1}{N_t} \sum_{t=1}^{N_t} P_n(t)
```

**33. 搜「Equivalently, this can be written as」**

```latex
P_n = \frac{1}{N_t} \sum_{t=1}^{N_t} \sum_{i=1}^{N_b} w_i\, I_i(t,n)
```

---

## 备注（若某条不转换）

- **`\begin{cases}`**（#18 B_i、#30 I_i）：部分 Word 不认。替代：用「括号→分段」模板手搭两行，或写成一行文字：
  - `B_i = 1 if RMSE(θ_i) < 0.12 mg/L; 0 otherwise`
  - `I_i(t,n) = 1 if C_sim,i(t,n) < C_min; 0 otherwise`
- **限算子的空框问题**（重要）：`\max`、`\min`、`\inf`、`\sup`、`\arg\min` 这类"带下限的算子"在 Word 里会多出一个空框 `□`。已改成 `\mathrm{max}`、`\mathrm{inf}`、`\mathrm{argmin}`（当普通函数名，不出空框）。若还有别的，同样用 `\mathrm{...}` 包起来即可。
- **`·`（点）不是错误**：那是 Word「显示空格」的格式标记，按 ¶ 按钮或 `Ctrl`+`Shift`+`8` 关掉即可。
- **`\mathrm{old}`** 等：若不认，换 `\text{old}` 或直接写 `old`。
- 标「单符号」的（#3、9、10、24、29）是单个量，做不做成公式都行，留斜体文字也常见。
