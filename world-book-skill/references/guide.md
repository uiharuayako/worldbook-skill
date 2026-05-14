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

## 第一步：澄清式问询（PromptSmith 原则）

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

**创建后强制创建禁词条目（3 条：叙事禁词 + 比喻禁词 + 描写禁律）。**

**必须执行 DoubleCheck 确认流程。**

---

### 类型 1：原创世界书 / 原创角色卡（世界书部分）

**触发关键词：** 世界书、生成世界书、创建世界书、世界观设定

**需要读取的 reference：**
- `references/character-guide.md`
- `references/worldbuilding-guide.md`
- `references/config-guide.md`
- `references/position-guide.md`
- 如果涉及物品/能力：`references/extract-item.md`

**创建后强制创建禁词条目（3 条：叙事禁词 + 比喻禁词 + 描写禁律）。**

---

### 类型 2：轻小说/游戏/小说 → 转化世界书

**触发关键词：** 轻小说、小说、转角色卡、根据原文、根据小说、转化、提取、原作、游戏、文本转化、原文

**需要读取的 reference：**
- `references/conversion-guide.md`（转化工作流总览）
- `references/extract-worldbuilding.md`（世界观提取）
- `references/extract-character.md`（角色提取）
- `references/extract-item.md`（物品/能力提取）
- `references/extract-story.md`（故事/章节提取）
- `references/character-guide.md`（角色条目写入规范）
- `references/worldbuilding-guide.md`（世界观条目写入规范）
- `references/config-guide.md`（配置规范）
- `references/position-guide.md`
- **不读** `references/extract-style.md`（除非用户明确要求提取文风）

**提取完成后强制创建禁词条目。**

---

### 类型 3：纯世界观/规则设定

**触发关键词：** 世界观、设定集、规则书、魔法体系、修炼体系、势力设定、地理设定、世界规则

**需要读取的 reference：**
- `references/worldbuilding-guide.md`
- `references/config-guide.md`
- `references/position-guide.md`
- 如果涉及物品/能力：`references/extract-item.md`

**创建后强制创建禁词条目。**

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

**文风条目需包含禁词规范。**

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

**修改时检查：禁词条目是否完整？双递归是否全部为 true？**

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

## 决策流程

```
用户输入 → 判断任务类型(角色卡? 世界书? MVU? HTML?)
         → 角色卡: 读取 card-writing-guide.md → DoubleCheck确认 → card-generator.py生成
         → 世界书: 按原有流程 → 总纲先行 → 逐条填充 → 自查
         → 转化:   读取 conversion-guide.md → 提取 → 条目化 → 自查
```

---

## 执行原则

1. **先读 reference，再动手。** 不要凭记忆写，必须读过对应 reference 后才开始写内容。
2. **每个任务类型都必须读 `config-guide.md` 和 `position-guide.md`**——配置错误比内容错误更难排查。
3. **角色卡任务必须读 `card-writing-guide.md`**，并执行 DoubleCheck 确认流程。
4. **转化任务必须先读 `conversion-guide.md`**，它规定了提取→条目创建的整体流程。
5. 对于修改任务，**先用 `query.py --brief` 查看**，再确定改什么。
6. **所有创建任务强制写入禁词条目（3 条）**——叙事禁词 + 比喻禁词 + 描写禁律。
7. **所有条目键不可跳过 `--prevent-recursion --exclude-recursion`**——参照 config-guide.md 第四节。
8. **零度写作、白描原则贯穿始终**——不写意象比喻、不写解释性修饰、不写不存在的事物。
9. **MVU 和 HTML 仅用户明确要求时才启用**——不主动建议，不主动添加。
