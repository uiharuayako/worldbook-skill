# 场景路由器

本文档帮助模型在开始任何工作前，自行判断任务类型，然后读取对应的 reference 文件。**必须在读取本文件后，再根据任务类型读取相应的参考文件，不可跳过。**

---

## 第零步：任务判断逻辑（最优先）

### 核心规则

**先判断用户要的是角色卡还是世界书：**

| 用户表达 | 输出内容 | 触发条件 |
|----------|----------|----------|
| 写卡/角色卡/人物设定/生成角色 | 完整的角色卡 | 自动 |
| 世界书/世界观/设定集 | 世界书条目 | 自动 |
| 完整的卡/全套/整套 | 角色卡+世界书 | 用户明确要求 |
| MVU/ZOD/变量 | 启用MVU | **仅用户明确要求时** |
| 美化/HTML/前端/状态栏 | 启用HTML | **仅用户明确要求时** |

### 铁律

**如果用户没说 MVU 或 HTML，绝对不要主动建议或添加。**

### 确认流程（角色卡任务）

角色卡任务必须执行 DoubleCheck：

1. 输出完整草稿
2. 等待用户确认（说"可以""满意""继续""生成"等）
3. 用户确认后 → 用 card-generator.py 生成 JSON

世界书任务按原有总纲先行流程执行。

---

## 第一步：澄清式问询

不确定任务类型时，**先提问，再动手**。对照以下维度向用户确认：

| 维度 | 问什么 |
|------|--------|
| 任务类型 | 是写角色卡还是世界书？（第一步必须确认） |
| 任务规模 | 几个核心角色？是否多角色卡？条目数预估？ |
| 世界观复杂度 | 真实背景 / 套路世界 / 完全原创？ |
| 素材来源 | 原创构思 / 轻小说原文 / 游戏文本 / 其他？ |
| 输出格式 | 单角色卡还是多角色卡？独立世界书还是嵌入角色卡？ |
| 风格偏好 | 严肃文学 / 轻松日常 / 二次元 / 网络小说 / 白描 / 心理流？ |
| 特殊需求 | 是否需要 NSFW 设定？是否需要文风提取？ |

**多层任务判定原则：** 如果用户输入同时匹配多种类型（如"把这个轻小说转成角色卡"），按**类型 2（转化）**处理，它已包含所有子类型需要的 reference。

如果用户输入不明确，**先询问用户意图**，不猜测。

---

## 任务类型识别

根据用户的输入，判断属于以下哪种任务类型：

### 类型 0：角色卡创建

**触发关键词：** 写卡、角色卡、人物设定、生成角色、创建角色、设计角色

**需要读取的 reference：**
- `references/card-writing-guide.md`（角色卡编写规范）
- `references/character-guide.md`（角色条目结构）
- `references/worldbuilding-guide.md`（世界观编写）
- `references/config-guide.md`（配置规范）
- `references/position-guide.md`
- `references/card-generator-guide.md`（生成工具）

**如果用户要求 MVU：** 额外读取 `references/mvu-guide.md`
**如果用户要求 HTML：** 额外读取 `references/html-beautify-guide.md`

**必须执行 DoubleCheck 确认流程。**

编写完成后，按 `card-writing-guide.md` 第六节禁词清单逐条扫描所有内容，确保无禁词渗入。

---

### 类型 1：原创世界书 / 原创角色卡（世界书部分）

**触发关键词：** 世界书、生成世界书、创建世界书、世界观设定

**需要读取的 reference：**
- `references/character-guide.md`
- `references/worldbuilding-guide.md`
- `references/config-guide.md`
- `references/position-guide.md`
- 如果涉及物品/能力：`references/extract-item.md`

编写完成后，按 `card-writing-guide.md` 第六节禁词清单逐条扫描所有条目内容，确保无禁词渗入。

---

### 类型 2：轻小说/游戏/小说 → 转化世界书/角色卡

**触发关键词：** 轻小说、小说、转角色卡、根据原文、根据小说、转化、提取、原作、游戏、文本转化、原文

**需要读取的 reference：**
- `references/conversion-guide.md`（转化工作流总览）
- `references/extract-worldbuilding-guide.md`（世界观提取）
- `references/extract-character.md`（角色提取）
- `references/extract-item.md`（物品/能力提取）
- `references/extract-story.md`（故事/章节提取）
- `references/character-guide.md`（角色条目写入规范）
- `references/worldbuilding-guide.md`（世界观条目写入规范）
- `references/config-guide.md`（配置规范）
- `references/card-writing-guide.md`（角色卡编写教程）
- `references/position-guide.md`
- **不读** `references/extract-style.md`（除非用户明确要求提取文风）

提取完成后，按 `card-writing-guide.md` 第六节禁词清单逐条扫描所有条目内容。

**转化→角色卡时**：转化流程产出的世界书条目嵌入角色卡，角色卡 description + 开场白按 `card-writing-guide.md` 额外撰写。转化产生的 outline.txt 同时服务于世界书条目和角色卡内容。

---

### 类型 3：纯世界观/规则设定

**触发关键词：** 世界观、设定集、规则书、魔法体系、修炼体系、势力设定、地理设定、世界规则

**需要读取的 reference：**
- `references/worldbuilding-guide.md`
- `references/config-guide.md`
- `references/position-guide.md`
- 如果涉及物品/能力：`references/extract-item.md`

编写完成后，按 `card-writing-guide.md` 第六节禁词清单逐条扫描内容。

---

### 类型 4：物品/能力/装备设定

**触发关键词：** 武器、道具、装备、技能、能力、功法、魔法、物品、神器、防具、消耗品

**需要读取的 reference：**
- `references/extract-item.md`
- `references/worldbuilding-guide.md`（物品需要挂靠世界观）
- `references/config-guide.md`
- `references/position-guide.md`

---

### 类型 5：文风提取/文风设定

**触发关键词：** 文风、写作风格、文笔、笔风、语言风格、模仿写作

**需要读取的 reference：**
- `references/extract-style.md`
- `references/config-guide.md`
- `references/position-guide.md`

文风条目需遵循零度写作原则，不含禁词。

---

### 类型 6：故事/章节提取

**触发关键词：** 故事线、章节、总结故事、提取章节、剧情提取、每章总结

**需要读取的 reference：**
- `references/extract-story.md`
- `references/config-guide.md`
- `references/position-guide.md`

---

### 类型 7：修改已有世界书

**触发关键词：** 修改、更新、编辑、添加条目、删除条目、调整

**需要读取的 reference：**
- 先用 `python scripts/query.py <世界书路径>` 查看现有条目
- 根据要修改的内容类型，读取对应的 reference（参考类型 1-6）
- `references/config-guide.md`

**修改时检查：双递归是否全部为 true？内容是否无禁词渗入？**

---

### 类型 8：MVU ZOD 变量系统

**触发关键词：** MVU、ZOD、变量、变量系统、数值系统、好感度系统

**需要读取的 reference：**
- `references/mvu-guide.md`
- `references/config-guide.md`
- `references/position-guide.md`

---

### 类型 9：HTML 前端美化

**触发关键词：** 美化、HTML、前端、状态栏、界面、UI

**需要读取的 reference：**
- `references/html-beautify-guide.md`
- `references/config-guide.md`
- `references/position-guide.md`

---

## 世界书创建流程

当任务类型为需要创建世界书条目时，按以下流程执行。

### 一、思维链分析

```
思维链:
  需求拆解:
    - 显性需求: ${用户提出的}
    - 隐性需求: ${未明说但需补全的}
    - 冲突判断: ${是否有矛盾？}
  规模规划:
    - 条目总数预估
    - 核心角色数
    - 卡片类型: 单角色卡 / 多角色卡
  配置规划:
    - 单卡: 所有角色条目蓝灯 constant=true
    - 多卡: 角色速览蓝灯 + 各角色详情绿灯
    - 世界观: 蓝灯 position=0
    - NPC/场景: 绿灯 position=1 scanDepth=2
  条目规划表:
    | # | 类型 | comment | position | constant | keys | order |
    |---|------|---------|----------|----------|------|-------|
    | 1 | 世界观总纲 | xxx总纲 | 0 | true | — | 1 |
    | 2 | 角色速览 | xxx速览 | 1 | true/false | — | 4 |
    | 3 | 人物设定 | <角色名> | 1 | true/false | 角色名 | 10 |
    | 4 | 性格 | <角色名>_personality | 1 | true/false | — | 30 |
    | 5 | 人物设定 | <角色名2> | 1 | true/false | 角色名2 | 11 |
    | 6 | 性格 | <角色名2>_personality | 1 | true/false | — | 31 |
    | ... | ... | ... | ... | ... | ... | ... |

  铁律: 多卡时每人2条 = 人物设定 + 性格

  禁词红线: 所有条目内容必须通过禁词扫描（叙事禁词/比喻禁词/描写禁律）。详见 card-writing-guide.md 六
```

### 二、撰写 outline.txt

```
总纲:
[一句话定义这个世界/角色/故事]

人物总纲:
- 角色名: 身份/定位/一句话速览
- ...

条目规划:
| # | 类型 | comment | position | constant | keys | order |
|---|------|---------|----------|----------|------|-------|
| 1 | 世界观总纲 | xxx | 0 | true | — | 1 |
| 2 | 人物设定 | <角色名> | 1 | true/false | 角色名 | 10 |
| 3 | 性格 | <角色名>_personality | 1 | true/false | — | 30 |
| 4 | 人物设定 | <角色名2> | 1 | true/false | 角色名2 | 11 |
| 5 | 性格 | <角色名2>_personality | 1 | true/false | — | 31 |
| ... | ... | ... | ... | ... | ... | ... |
```

多卡铁律：每人2条 = 人物设定 + 性格。人物设定模板见 `character-guide.md` 一，性格模板见 `character-guide.md` 四。

禁词：所有条目编写完成后，必须逐条扫描禁词清单。此清单绝不以任何形式写入世界书条目内容。

### 三、写入条目

1. **先写世界观总纲**（position=0, constant, order=1）— 确认无误后再展开
2. **写入物总纲/速览** — 蓝绿灯按卡片类型配置
3. **逐条填充详情条目** — 按条目规划表顺序写入。**多卡时每个角色必须拥有独立的 人物设定条目 + 性格条目**（N个角色 = 2N条），每写完一条用 `query.py --brief` 确认配置
4. **终检**：
   - 蓝绿灯分配正确（`query.py --brief`）
   - 所有条目 `preventRecursion=true` 且 `excludeRecursion=true`
   - 按 `card-writing-guide.md` 第六节禁词清单逐条扫描所有条目内容——无禁词渗入

### 四、🚫 禁词自查（强制——写完所有条目后必须执行）

禁词清单（`card-writing-guide.md` 第六节）是**编写者的自查工具**。写完所有世界书条目内容后，逐条对照扫描。此清单绝不以任何形式写入世界书条目。

---

## 决策流程

```
用户输入 → 判断任务类型(角色卡? 世界书? 转化? MVU? HTML?)
         → 角色卡: 读取 card-writing-guide.md → 写 outline → 写内容 → DoubleCheck → card-generator.py
         → 世界书: 总纲先行 → 逐条填充 → 自查
         → 转化:   读取 conversion-guide.md → 提取 → 写 outline.txt → 条目化（世界书）→ 角色卡内容（如需）→ 自查
```

角色卡和转化任务都必须先写 outline（角色卡: SKILL.md A.3; 转化: conversion-guide.md 第二步）。

---

## 执行原则

1. **先读 reference，再动手。** 不要凭记忆写，必须读过对应 reference 后才开始写内容。
2. **每个任务类型都必须读 `config-guide.md` 和 `position-guide.md`**——配置错误比内容错误更难排查。
3. **角色卡任务必须读 `card-writing-guide.md`**，并执行 DoubleCheck 确认流程。
4. **转化任务必须先读 `conversion-guide.md`**，它规定了提取→条目创建的整体流程。
5. 对于修改任务，**先用 `query.py --brief` 查看**，再确定改什么。
6. **写完所有条目后，按 `card-writing-guide.md` 第六节禁词清单逐条扫描**——确保无禁词渗入世界书内容。
7. **所有条目键不可跳过 `--prevent-recursion --exclude-recursion`**——参照 config-guide.md 第四节。
8. **零度写作、白描原则贯穿始终**——不写意象比喻、不写解释性修饰、不写不存在的事物。
9. **MVU 和 HTML 仅用户明确要求时才启用**——不主动建议，不主动添加。
