# Git 入门笔记（针对本 repo）

> 面向 Git 新手，目标：能日常安全地把毕设代码、笔记、图、论文稿同步到 GitHub，不丢东西、不污染仓库。
>
> 本 repo 信息：
> - 远端：`https://github.com/Strongxlb/Graduation-Project.git`
> - 主分支：`main`
> - 工作目录：`/Users/prx/Desktop/帝国理工/毕设/codes`

---

## 0. 先有一个心智模型

Git 把你的文件分成 **4 个"地方"**，理解了这 4 个地方，剩下的命令都是在它们之间搬东西：

```
┌─────────────┐  git add   ┌──────────┐  git commit  ┌──────────┐  git push  ┌──────────┐
│ 工作目录    │ ─────────▶ │ 暂存区   │ ───────────▶ │ 本地仓库 │ ─────────▶ │ GitHub   │
│ (Working)   │            │ (Staging)│              │ (Local)  │            │ (Remote) │
└─────────────┘            └──────────┘              └──────────┘            └──────────┘
       ▲                                                                          │
       └──────────────────────── git pull ────────────────────────────────────────┘
```

- **工作目录**：你眼睛看到的文件（你正在编辑的 `plan1.md`）
- **暂存区 (staging / index)**：你"打算提交"的快照，由 `git add` 放进来
- **本地仓库 (.git 目录)**：`git commit` 之后，历史记录就刻在这里了
- **远端 (origin)**：GitHub 上那一份，靠 `git push` / `git pull` 同步

**核心原则**：commit 是本地的，push 才会上传到 GitHub。

---

## 1. 每天最常用的 5 个命令

```bash
git status              # 我现在改了啥？哪些没 add？哪些没 commit？
git add <file>          # 把改动放进暂存区（准备提交）
git commit -m "msg"     # 把暂存区的内容固化成一条历史
git push                # 把本地新 commit 推到 GitHub
git pull                # 把 GitHub 上别人/别设备的更新拉下来
```

90% 的日常工作就是这 5 个。其它命令都是"出问题"或"做骚操作"时才用。

---

## 2. 实战：今天就用本 repo 跑一遍

打开终端，`cd` 到本 repo：

```bash
cd "/Users/prx/Desktop/帝国理工/毕设/codes"
```

### Step 1：看现状

```bash
git status
```

你现在会看到类似这样的输出（这是真实的当前状态）：

```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
        modified:   background/literature.md

Untracked files:
        meetings/2026-05-22.md
```

读懂它：

- `On branch main`：现在在 `main` 分支
- `up to date with 'origin/main'`：本地和远端是齐的（指最近一次 push 之后没新 commit）
- `modified: ...`：这个文件你改了，但还没 `add`
- `Untracked files: ...`：这个文件是新建的，Git 还不认识它

### Step 2：看具体改了什么

```bash
git diff                       # 看所有未 add 的改动
git diff background/literature.md   # 只看某个文件
```

`+` 是新增行，`-` 是删除行。**养成 commit 前 `git diff` 一眼的习惯**，能避免提交废代码。

### Step 3：选择要提交的文件并 add

两种方式：

```bash
git add background/literature.md meetings/2026-05-22.md   # 精确指定
git add .                                                  # 把当前目录下所有改动都 add 进去
```

新手建议**优先用精确指定**，避免不小心把临时文件、调试输出一起提交了。

> 想反悔？`git restore --staged <file>`（把文件从暂存区拿出来，工作目录的改动不丢）

### Step 4：commit

```bash
git commit -m "docs: 增加 5/22 会议记录，更新文献综述"
```

提交后 `git status` 会显示 `Your branch is ahead of 'origin/main' by 1 commit.`，意思是"本地比远端多 1 个 commit"，还没推上去。

### Step 5：push 到 GitHub

```bash
git push
```

完成。打开 GitHub 网页就能看到。

---

## 3. commit message 怎么写（**重点章节**）

历史是给未来的自己看的。**烂 message 三个月后等于没写**。

一条好的 commit message 应该让人**不打开代码就能猜到这次改了什么、为什么改**。

### 3.1 标准结构

完整版长这样（推荐你日常用**简化版**就够了）：

```
<类型>(<范围>): <一句话主题，≤50 字符，祈使句>
<空行>
<正文：为什么这么改、上下文、权衡>（每行 ≤72 字符）
<空行>
<脚注：关联 issue / 破坏性变更>
```

例子（完整版）：

```
feat(src): add chlorine decay analysis for week-2 demo

WNTR 1.4 supports MSX-style first-order decay. This adds
01_chlorine_decay.py that runs Net3 for 24h and dumps
node-level chlorine concentrations to results/week2_chlorine/.

Used kbulk = -0.5/day from Rossman (2000) as a sanity baseline;
will calibrate with real data in week 4.

Refs: #3
```

**90% 的 commit 用简化版就行**：

```
<类型>(<范围>): <主题>
```

例如：`feat(src): add chlorine decay analysis for week-2 demo` 这一行单独 commit 就够了。

### 3.2 类型（type）—— 让人一眼看出"哪类改动"

| 类型 | 用途 | 例子 |
|------|------|------|
| `feat` | 新功能 / 新脚本 / 新分析 | `feat(src): add chlorine decay simulation on Net3` |
| `fix` | 修 bug / 改错 | `fix(src): correct WNTR demand units (LPS -> CMH)` |
| `docs` | 文档、笔记、README、会议记录 | `docs(meetings): add 5/22 meeting notes` |
| `refactor` | 重构（行为不变，只改结构） | `refactor(src): split simulation runner into module` |
| `data` | 新增/更新数据或网络模型 | `data: add Net3 .inp benchmark` |
| `results` | 新增/更新结果图、报告 | `results: regenerate week1 pressure plots` |
| `thesis` | 论文初稿/章节更新 | `thesis: draft chapter 2 background` |
| `chore` | 杂项（依赖、配置、目录结构） | `chore: bump WNTR to 1.4` |
| `experiment` | 实验性尝试（可能丢弃） | `experiment(src): try GNN on toy network` |
| `style` | 格式化（空格、缩进），不改逻辑 | `style: black format all of src/` |
| `revert` | 撤销之前的 commit | `revert: feat(src): add chlorine decay` |

新手只要会用 `feat` / `fix` / `docs` / `chore` 这四种就能覆盖 80% 的场景。

### 3.3 范围（scope）—— 让人一眼看出"改了哪块"

范围是可选的，但**强烈推荐用**——它能让历史一眼看出影响哪里。

针对你本 repo，推荐这套 scope：

| scope | 对应位置 | 何时用 |
|-------|---------|--------|
| `src` | `src/` 下的脚本 | 改/加分析代码 |
| `data` | `data/` 下的输入 | 改/加输入数据、网络模型 |
| `results` | `results/` | 重新生成结果、改图 |
| `thesis` | `thesis/` | 写论文 |
| `meetings` | `meetings/` | 加/改会议记录 |
| `background` | `background/` | 文献综述、背景资料 |
| `env` | `environment.yml`, `requirements.txt` | 改依赖 |
| `ci` | `.github/`, hook | CI / 自动化（暂未用到） |
| `repo` | `.gitignore`, README | 整体仓库层面 |

不知道用哪个就**省略**，宁可没有也别乱填。

### 3.4 主题行（subject）—— 让人一眼看懂"做了啥"

主题行决定了别人（包括未来的你）在 `git log --oneline` 里能看到什么。**必须经得起扫读**。

**5 条规则**：

1. **≤ 50 字符**（GitHub 列表里超出会被截断）
2. **用祈使句、动词开头**：写"add" / "fix" / "update"，不写"added" / "fixed" / "updated"
   - 想象你在告诉 Git："**做这件事**"
3. **不要句号结尾**
4. **首字母小写**（类型已经标好了，主题里大写浪费空间）
5. **具体到对象**：说"加了什么"而不是"加了一些东西"

**对比**：

| ✗ 烂 | ✓ 好 | 为什么 |
|------|------|--------|
| `update` | `docs(meetings): add 5/22 meeting notes` | 说清楚改了啥 |
| `fix bug` | `fix(src): handle empty result from WNTR EpsSimulator` | 说清楚啥 bug |
| `修改` | `chore(env): pin setuptools<81 to fix WNTR install` | 具体到原因 |
| `加了一些图` | `results: add week1 pressure & flow time series (Net1)` | 加了哪些图、哪个网络 |
| `测试commit` | （这种就别 commit） | 测试用 `git stash` 或本地分支 |

### 3.5 正文（body）—— 解释"为什么"，可选但重要

什么时候**必须**写正文：

- 改动**不是显而易见**的（比如换了算法、改了参数）
- 你做了**权衡**（"为什么不用 A 而用 B"）
- 涉及**踩坑/原因**（"WNTR 1.5 有 bug，所以锁版本"）
- 后人可能会问"这个怎么这么写？"

什么时候**不需要**写正文：

- 主题行已经讲完了（"`docs: fix typo in README`" 不用解释）
- 一行就够的小改动

**怎么用命令行写多行 message**：

```bash
git commit          # 直接回车，会打开编辑器写完整 message
# 或者
git commit -m "feat(src): add chlorine decay analysis" \
           -m "Use Rossman 2000 kbulk = -0.5/day as baseline." \
           -m "Refs: #3"
```

多个 `-m` 会自动用空行分隔成多段。

### 3.6 黄金原则：一个 commit 只做一件事

这是**最重要也最容易忽略**的一条。

**✗ 反面**（一个 commit 装了 3 件事）：

```
feat: add chlorine decay + fix README typo + bump WNTR + reorganize src/
```

未来想撤回某一件，整个 commit 都要回滚。

**✓ 正面**（拆成 3 个 commit）：

```
chore(env): bump WNTR to 1.4
docs(repo): fix typo in README install section
refactor(src): rename simulate.py -> run_hydraulics.py
feat(src): add chlorine decay analysis
```

如果发现自己已经把多件事混在工作目录里了，用：

```bash
git add -p <file>     # 交互式选择哪几行加进暂存区
```

可以把同一个文件里的不同改动**分到不同 commit**里。

### 3.7 中英文怎么选

- **类型 + scope 始终用英文**（这是约定，工具能识别）
- **主题/正文中英文都行**，但**整个 repo 风格保持一致**
- 你 repo 里已经有 `feat: WNTR 1.4 hydraulic + chlorine demo on Net1` 这种英文风格，建议继续

如果想中英文混用，推荐：**类型英文 + 主题中文**

```
feat(src): 增加 Net3 余氯衰减仿真脚本
fix(src): 修正 WNTR 流量单位 LPS->CMH
docs(meetings): 5/22 周会记录
```

### 3.8 模板：直接套用

**最常用的 6 类，直接复制**：

```bash
# 写代码
git commit -m "feat(src): <加了啥，作用是啥>"
git commit -m "fix(src): <修了啥问题>"
git commit -m "refactor(src): <重构了啥，为啥>"

# 写文档/笔记
git commit -m "docs(meetings): add <日期> meeting notes"
git commit -m "docs(repo): update README <哪一节> section"

# 实验结果
git commit -m "results: add <实验名> figures and tables"

# 杂项
git commit -m "chore(env): bump <包名> to <版本>"
git commit -m "chore(repo): update .gitignore for <啥文件>"
```

### 3.9 实战：拿你当前未提交的改动练习

你现在有这些改动：

- `background/literature.md` 被修改了
- `meetings/2026-05-22.md` 是新建的
- `learning/git_learning.md` 是新建的（这份教程）

**正确做法**：拆成 3 个 commit，每个做一件事：

```bash
git add meetings/2026-05-22.md
git commit -m "docs(meetings): add 5/22 meeting notes"

git add background/literature.md
git commit -m "docs(background): update literature review with <你新加了啥>"

git add learning/git_learning.md
git commit -m "docs(repo): add git learning notes for beginners"

git push
```

未来你 `git log --oneline` 一扫，三件事一清二楚。

### 3.10 反面教材集锦（来自真实项目）

```
update                 # 改了啥？
fix                    # 修了什么？
asdf                   # ……
WIP                    # work in progress 是个借口，本地分支用 stash 就行
测试commit             # 测试不要 push
完善第一版本的readme   # 完善了哪部分？install？usage？
final final v3 真的最终版.docx  # 这是 Git，不要把版本号写进 message
.                      # 见过有人就 commit 一个点
```

### 3.11 进阶：让 git log 更好看

写得好之后，看 log 也会变得享受：

```bash
git log --oneline -10                           # 最近 10 条
git log --oneline --graph --decorate --all      # 带分支图的全景
git log --grep="chlorine"                       # 按 message 关键字搜
git log --author="xlbbbbb"                      # 按作者搜
git log --since="1 week ago" --oneline          # 最近一周
git log -- src/                                 # 只看 src/ 下的历史
```

如果用了 conventional commits，将来还能用 `git-cliff` 或 `standard-version` **自动生成 CHANGELOG**——这是你坚持好习惯的额外奖励。

---

## 4. `.gitignore`：让 Git 假装看不见某些文件

你 repo 里已经有了一份不错的 `.gitignore`，覆盖了：

- Python 缓存 (`__pycache__/`, `*.pyc`)
- 虚拟环境 (`.venv/`)
- macOS 系统文件 (`.DS_Store`)
- 原始/大数据 (`data/raw/`, `*.h5`, `*.parquet`)
- 大模型输出 (`results/raw/`, `*.bin`, `results/*.pkl`)
- EPANET 中间产物 (`*.rpt`, `*.out`, `*.tmp`)
- LaTeX 编译垃圾

### 关键规则

1. `.gitignore` 只对**还没被 Git 跟踪**的文件生效。
   - 如果一个文件已经被 commit 过了，再加进 `.gitignore` 不会让它消失，需要：
     ```bash
     git rm --cached <file>   # 让 Git 不再跟踪它（本地文件还在）
     git commit -m "chore: stop tracking <file>"
     ```
2. 想临时**不忽略**某个被忽略的文件：用 `!` 前缀。
   - 例：`!.env.example` 就是"忽略所有 .env*，但保留 .env.example"
3. **不要忽略源代码**。
4. **大文件原则**：单文件超过 50 MB，先想想"它真的需要进 Git 吗？"。能重新生成的（仿真结果、缓存、PDF 编译产物）就别进 Git。

### 你 repo 当前的小问题

根目录有 `temp.bin`、`temp.inp`、`temp.rpt` 三个文件：

- `*.bin` 和 `*.rpt` 已经在 `.gitignore` 里，会被忽略 ✅
- `temp.inp` 没被忽略，但因为带 `temp.` 前缀，看名字像临时调试产物。如果是的话，建议要么删掉，要么在 `.gitignore` 加一行 `temp.*`

---

## 5. 分支（branch）：什么时候用？

新手很容易过度使用或完全不用分支。对你这种"一个人写毕设"的项目，建议：

### 简单策略（推荐你先用这个）

- **`main` 只放能跑通、能交付的东西**
- 写新东西、做大胆实验时**新开分支**，搞砸了直接删，不污染 main

```bash
git switch -c experiment/gnn-baseline    # 从当前分支新建并切换
# ... 改代码、commit ...
git switch main                          # 回到 main
git merge experiment/gnn-baseline        # 把分支并回 main（如果实验成功）
git branch -d experiment/gnn-baseline    # 删掉这个分支
```

把它当成"沙盒"。失败了：

```bash
git switch main
git branch -D experiment/gnn-baseline    # 强删，所有未合并的提交都没了
```

### 命名建议

- `feat/xxx`：新功能
- `experiment/xxx`：实验性的、可能丢弃的
- `fix/xxx`：修 bug
- `docs/xxx`：纯文档/笔记更新

---

## 6. 与 GitHub 同步：push / pull / fetch

### 单机使用（你现在的场景）

```bash
git push          # 把本地 commit 推上去
git pull          # 把远端的拉下来（pull = fetch + merge）
```

### 在两台机器/换电脑工作时

**离开前**：

```bash
git status        # 确认没有未提交的改动
git push          # 推上去
```

**回来后**（在新机器）：

```bash
git pull          # 先拉最新的
# 然后再开始改
```

**最常见的新手翻车**：忘记 `pull` 就开始改，导致冲突。养成"开干前先 pull"的肌肉记忆。

---

## 7. 撤销 / 反悔（救命用）

### 还没 add：想丢弃工作目录的改动

```bash
git restore <file>          # 把这个文件恢复到上次 commit 的样子
git restore .               # 全部恢复（小心！未保存的改动会丢）
```

### 已经 add 了：想从暂存区拿出来

```bash
git restore --staged <file>     # 文件改动还在，只是不在"准备提交"里了
```

### 已经 commit 了，但还没 push：想改最近一次的 commit

```bash
git commit --amend -m "新的 message"     # 改 message
git add <file> && git commit --amend --no-edit   # 把漏掉的文件加进上一个 commit
```

> **铁律**：`--amend` 只在**没 push** 的 commit 上用。push 出去再 amend，会让远端历史和本地不一致。

### 已经 push 了：想"撤销"一个 commit

不要用 `reset` 改历史，用 `revert`：

```bash
git revert <commit-hash>     # 生成一个"反向 commit"来抵消它，历史不会被改写
git push
```

### 看历史

```bash
git log --oneline             # 简洁版
git log --oneline --graph     # 带分支图
git log -p <file>             # 看某个文件的完整修改史
```

---

## 8. 研究项目特别注意事项

你这是个**毕设研究项目**，跟普通软件项目有些不同：

### ✗ 不要 commit 的东西

- **原始数据集**（GB 级别的）→ 让别人下载，或用云盘
- **仿真大输出**（`.h5`, `.bin`, `.pkl`）→ 能复跑就别存
- **训练好的模型权重**（如果很大）→ 用 Git LFS 或网盘
- **个人会议录音、私人笔记**
- **API key / 密码** → 用 `.env` 文件并加进 `.gitignore`

### ✓ 应该 commit 的东西

- 所有**源代码** (`src/`)
- **配置文件**（`environment.yml`, `requirements.txt`）
- **小的样例数据**（用于 demo / 单元测试）
- **文档、笔记、计划**（`README.md`, `plan1.md`, `meetings/`）
- **关键图表的生成脚本**（图本身可选）
- `.inp` 网络模型文件（EPANET，通常很小）

### 大文件不小心 commit 了怎么办？

**关键**：别只删文件然后 commit，那样历史里还在。

简单情况（还没 push）：

```bash
git reset --soft HEAD~1     # 撤销最近一次 commit，文件回到暂存区
git restore --staged <bigfile>
echo "<bigfile>" >> .gitignore
git add .gitignore
git commit -m "chore: ignore large file"
```

已经 push 了，需要把历史清理干净 → 用 `git filter-repo`（比较进阶，需要时查文档）。

---

## 9. 一次完整的"日常工作流"模板

把它存进肌肉记忆：

```bash
# 1. 开工前：拉最新
cd "/Users/prx/Desktop/帝国理工/毕设/codes"
git pull

# 2. 干活
# ... 改代码、写笔记、跑实验、生成图 ...

# 3. 看自己改了啥
git status
git diff

# 4. 挑出要提交的（不要无脑 git add .）
git add src/02_chlorine_decay.py
git add results/week2_chlorine/01_chlorine_map.png
git add meetings/2026-05-22.md

# 5. 提交
git commit -m "feat: add chlorine decay analysis for week 2 meeting"

# 6. 上传
git push
```

---

## 10. 常用命令速查表

| 场景 | 命令 |
|------|------|
| 看状态 | `git status` |
| 看改动 | `git diff` / `git diff --staged` |
| 加到暂存区 | `git add <file>` / `git add .` |
| 从暂存区拿出来 | `git restore --staged <file>` |
| 丢弃工作区改动 | `git restore <file>` |
| 提交 | `git commit -m "msg"` |
| 改上次提交 | `git commit --amend` |
| 看历史 | `git log --oneline --graph` |
| 看某行是谁/哪个 commit 改的 | `git blame <file>` |
| 推送 | `git push` |
| 拉取 | `git pull` |
| 新建+切换分支 | `git switch -c <name>` |
| 切换分支 | `git switch <name>` |
| 合并分支 | `git merge <name>` |
| 删分支 | `git branch -d <name>` |
| 撤销已 push 的 commit | `git revert <hash>` |
| 暂存当前改动（不提交） | `git stash` / `git stash pop` |

---

## 11. 推荐配置（一次性，做了就忘）

```bash
# 全局身份（你已经设过就跳过）
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 让中文文件名正常显示（macOS 上很重要！）
git config --global core.quotepath false

# 默认 push 当前分支
git config --global push.default current

# 让 pull 用 rebase（历史更干净，进阶可选）
# git config --global pull.rebase true

# 好用的别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.lg "log --oneline --graph --decorate --all"
```

之后 `git st` 就等于 `git status`，`git lg` 看分支图。

---

## 12. 进阶学习路线

按这个顺序，每周一个：

1. **能跑 5 个基础命令**（你应该已经会了）
2. **理解 `.gitignore`**，能自己加规则
3. **会用分支**做实验
4. **会写有信息量的 commit message**
5. **会用 `git diff` / `git log`** 复盘自己的工作
6. **遇到冲突会解决**（合并时出现 `<<<<<<<` 的情况）
7. **会用 `git stash`** 临时收起改动
8. **了解 `git rebase`**（进阶，可选，**已 push 的不要 rebase**）
9. **了解 Git LFS** 或网盘策略，管理大文件

---

## 13. 卡住的时候

- 命令记不住：`git <命令> --help`，或直接 Google "git 怎么 XXX"
- 不知道现在啥状态：`git status` 永远是答案
- 怕搞砸：所有"破坏性"命令（`reset --hard`, `branch -D`, `push --force`）操作前先 `git status` 看清楚，再做
- 真搞砸了：`git reflog` 能看到你所有的历史操作，几乎所有"误删 commit"都能从这里救回来

---

## 14. 给本 repo 的具体建议

基于现在的状态，建议你：

1. **现在就练一遍**：把 `background/literature.md` 的修改和 `meetings/2026-05-22.md` 提交上去，按第 2 节的步骤走。
2. **每次 meeting 后**：commit 一次会议记录，message 用 `docs: 5/22 meeting notes`。
3. **每跑通一个新实验**：commit 源代码 + 关键产物（小图、小表），message 用 `feat: ...` 或 `experiment: ...`。
4. **决定 `temp.inp` 的去留**：要么 `git rm temp.inp` 删掉，要么改名成正式 demo（如 `data/examples/net1_demo.inp`）。
5. **每周末**：`git log --oneline` 回顾一下这周做了啥，顺便检查 message 写得够不够好。

---

> 这份笔记可以反复回来查。Git 不是一次学完的，是**用着用着就会了**。先把第 1、2、9 节用熟，其它的等真遇到再查。
