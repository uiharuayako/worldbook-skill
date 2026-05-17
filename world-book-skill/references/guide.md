# 场景路由器

> 本文档帮助模型在开始工作前自行判断任务类型，然后读取对应的 reference 文件。必须在读取本文件后再根据任务类型读取对应参考文件，不可跳过。

---

## 第零步：核心判断

先判断用户是**原创**还是**二创**：

| 维度 | 原创 | 二创 |
|------|------|------|
| 素材来源 | 无原文，靠交互式提问搜集 | 轻小说/游戏解包/网络搜索 |
| 入口 | 类型 1 / 3 | 类型 2（先提取再分流） |
| 建议模式 | Plan 模式 | 直接执行 |

---

## 任务类型识别

### 类型 1：原创角色卡

触发关键词：写卡、角色卡、人物设定、生成角色、创建角色、设计角色

需要读取的 reference：
- `references/character-card-guide.md` — 角色卡编写（世界书条目 + 开场白）
- `references/character-guide.md` — 角色条目结构模板
- `references/world-building-guide.md` — 世界观设计
- `references/world-book-guide.md` — 世界书条目化
- `references/config-guide.md` — 配置规则
- `references/position-guide.md` — 注入位置
- `references/card-generator-guide.md` — 脚本使用指引

如用户要求 MVU → 追加读取 `references/mvu-guide.md`
如用户要求 EJS → 追加读取 `references/ejs-guide.md`（EJS 依赖 MVU，需先确认 MVU）
如用户要求 HTML 美化 → 追加读取 `references/html-beautify-guide.md`
如用户明确要求 Deep Research 搜资料 → 追加读取 `references/deep-research-guide.md`

完成后 → 禁词扫描 → 读 `references/writing-optimization-guide.md`

---

### 类型 2：二创提取 → 角色卡 / 世界书

触发关键词：轻小说、小说、转角色卡、根据原文、根据小说、转化、提取、原作、游戏、文本转化、原文、网络搜索

需要读取的 reference：
- 若用户明确要求 Gemini Deep Research / Google AI Studio 深度检索：
  - `references/deep-research-guide.md` — 深度检索授权与调用方式（先读）
- `references/information-extraction-guide.md` — 信息提取流程（必读，第一步）
- 提取完成后按产出分流：
  - 有角色人设 → 追加读 `references/character-card-guide.md` + `references/character-guide.md`
  - 有世界观信息 → 追加读 `references/world-building-guide.md` + `references/world-book-guide.md`
  - 有物品/能力 → 追加读 `references/world-book-guide.md`（物品条目规范）
- `references/config-guide.md`
- `references/position-guide.md`

完成后 → 禁词扫描 → 读 `references/writing-optimization-guide.md`

---

### 类型 3：纯世界观设计 + 世界书

触发关键词：世界观、设定集、规则书、魔法体系、修炼体系、势力设定、地理设定、世界规则

需要读取的 reference：
- `references/world-building-guide.md` — 世界观设计（先做概念层）
- `references/world-book-guide.md` — 世界书条目化（再做落地层）
- `references/config-guide.md`
- `references/position-guide.md`
- `references/card-generator-guide.md` — 脚本使用指引

---

### 类型 4：物品 / 能力 / 装备

触发关键词：武器、道具、装备、技能、能力、功法、魔法、物品、神器、防具、消耗品

需要读取的 reference：
- `references/world-book-guide.md` — 物品条目编写规范
- `references/world-building-guide.md` — 物品挂靠的世界观背景
- `references/config-guide.md`
- `references/position-guide.md`
- `references/card-generator-guide.md` — 脚本使用指引

---

### 类型 5：文风提取 / 文风设定

触发关键词：文风、写作风格、文笔、笔风、语言风格、模仿写作

需要读取的 reference：
- `references/information-extraction-guide.md` — 从原文提取文风特征
- `references/writing-optimization-guide.md` — 禁词扫描
- `references/config-guide.md`
- `references/position-guide.md`
- `references/card-generator-guide.md`

提取后输出为世界书条目，挂绿灯触发。
如用户明确要求 Deep Research 搜资料 → 追加读取 `references/deep-research-guide.md`

---

### 类型 6：故事 / 章节提取

触发关键词：故事线、章节、总结故事、提取章节、剧情提取、每章总结

需要读取的 reference：
- `references/information-extraction-guide.md` — 标注章节行号、重要章节
- `references/world-book-guide.md` — 故事/章节条目格式与配置
- `references/config-guide.md`
- `references/position-guide.md`
- `references/card-generator-guide.md`

每章一条世界书条目，绿灯关键词触发，scanDepth=2。写入前必须复读对应章节原文。
如用户明确要求 Deep Research 搜资料 → 追加读取 `references/deep-research-guide.md`

---

### 类型 7：修改已有世界书

触发关键词：修改、更新、编辑、添加条目、删除条目、调整

需要读取的 reference：
- 先用 `python scripts/query.py <世界书路径> --brief` 查看现有条目
- 根据要修改的内容类型，读取对应的 reference（参考类型 1-4）
- `references/config-guide.md`

---

### 类型 8：MVU ZOD 变量系统

触发关键词：MVU、ZOD、变量、好感度系统、数值系统

需要读取的 reference：
- `references/mvu-guide.md`
- `references/config-guide.md`
- `references/position-guide.md`

---

### 类型 9：EJS 动态内容

触发关键词：EJS、动态内容、多阶段、调色盘、条件控制

需要读取的 reference：
- `references/ejs-guide.md`
- `references/mvu-guide.md` — EJS 必须有 MVU 才能用
- `references/config-guide.md`
- `references/position-guide.md`

---

### 类型 10：HTML 前端美化

触发关键词：美化、HTML、前端、状态栏、界面、UI、开场选择器

需要读取的 reference：
- `references/html-beautify-guide.md`
- 如涉及 MVU 状态栏 → 追加读 `references/mvu-guide.md`

---

### 类型 11：禁词扫描 / 写作优化

触发关键词：自查、检查禁词、扫描、写作优化、润色

需要读取的 reference：
- `references/writing-optimization-guide.md`

---

### 类型 12：Gemini Deep Research 资料搜集

触发关键词：deep research、Deep Research、Gemini 深度检索、Google AI Studio 搜索、深度研究、联网研究报告

需要读取的 reference：
- `references/deep-research-guide.md`
- 后续再按输出内容分流到类型 1-6

铁律：
1. 仅在用户明确要求时启用
2. 未配置授权时，不要假装已经执行
3. 研究结果只是源材料，不直接替代角色卡 JSON 生成

---

## 决策流程

```
用户输入 → 判断原创/二创
  ├─ 原创 → 角色卡？ → 类型1 → character-card-guide.md → 禁词扫描
  │        世界书？ → 类型3 → world-building-guide.md → world-book-guide.md
  │        文风？   → 类型5 → information-extraction-guide.md
  │        章节？   → 类型6 → information-extraction-guide.md → world-book-guide.md
  │
  └─ 二创 → 类型2 → information-extraction-guide.md
            → 若明确要求 Deep Research → deep-research-guide.md
            → 提取产出分流：
              ├─ 角色人设 → character-card-guide.md
              ├─ 世界观 → world-building-guide.md → world-book-guide.md
              ├─ 物品 → world-book-guide.md
              ├─ 文风 → 世界书条目
              └─ 章节 → world-book-guide.md
            → 禁词扫描 → writing-optimization-guide.md
```

---

## 执行原则

1. 先读 reference，再动手。不凭记忆写
2. 每个任务类型必须读 `config-guide.md`、`position-guide.md` 和 `card-generator-guide.md`
3. 二创任务必须先读 `information-extraction-guide.md`
4. 修改任务先用 `query.py --brief` 查看，再确定改什么
5. 所有产出物在完成后必须读 `writing-optimization-guide.md` 做禁词扫描
6. MVU/EJS/HTML 仅用户明确要求时启用，不主动建议
7. EJS 依赖 MVU，用户要 EJS 时必须先确认 MVU 已启用
8. Deep Research 仅用户明确要求时启用，不主动替换普通搜索流程
