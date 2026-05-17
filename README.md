# SillyTavern 角色卡/世界书管理助手 — Character & World Book Manager

一句话让 AI 读轻小说/设定集，自动生成结构化世界书 JSON 与角色卡。

**注意：本项目基本由 AI 生成，可能会出现意料之外的问题。作者并不很懂编程，但欢迎提出 issue。**

## 致谢
本项目的角色卡编写方法论和提示词设计大量参考了 [sanmingyue](https://github.com/sanmingyue) 大佬的写卡教程与工作流理念，是本技能写作规范的基石。

## 立场声明
本项目致力服务于开源RolePlay社区，服务于非商业的角色扮演创作。
严禁用于任何收费 AI 平台、商业 API 服务、或盈利性角色卡代写业务。
违反上述条款的使用者，将拒绝提供任何技术支持。

---

## 这是什么

一个 **AI Skill + CLI 工具** 的组合包。给 AI 装上它，SAY：

> "帮我读这本轻小说，把所有角色、世界观做成世界书条目"
> "根据这个设定，帮我写一个带 MVU 状态栏和 HTML 美化的角色卡"
> "为我生成一个有关于赛车的世界书，并提取作者的文风"

AI 就会自动执行任务：
1. **识别** — 自动判断是角色卡需求、世界书需求还是美化需求。
2. **编写** — 遵循“角色卡编写铁律”，支持 XML 包裹 YAML 格式，自动处理禁词扫描。
3. **生成** — 调用 CLI 脚本输出可直接导入 SillyTavern 的世界书或角色卡 JSON。

## 功能一览

| 功能 | 说明 |
|------|------|
| **轻小说→世界书** | 喂文本，AI 自动抽取角色/世界观，生成标准世界书 JSON |
| **高颜值角色卡** | 生成支持MVU ZOD与前端美化的角色卡，含档案、性格、世界观、开场白 |
| **MVU & HTML 美化** | 集成 ZOD 变量系统，支持状态栏渲染与全局正文美化 |
| **CLI 管理工具** | `world-book-create.py` (世界书) / `card-generator.py` (角色卡) |
| **质量自检 (DoubleCheck)** | 内置 20+ 项检查清单，逐字扫描禁词，确保人设不崩且符合规范 |

## 支持场景

| 场景 | 使用的 reference |
|------|-----------------|
| **V3 角色卡制作** | card-writing-guide + card-generator-guide + DoubleCheck 流程 |
| **MVU 变量/美化** | mvu-guide + html-beautify-guide |
| **轻小说/游戏转化** | conversion-guide + 全部 extract-* + 创作 guide |
| **原创世界观/物品** | worldbuilding-guide + extract-item + config-guide |
| **文风/故事提取** | extract-style + extract-story + config-guide |
| **修改/查询已有内容** | query.py + 对应类型的 reference |

---

## 使用方法

把 `world-book-skill/` 文件夹装进你的 AI Agent（如 Codex/Claude 等支持 skill 的终端），AI 就能独立完成：

1. **场景路由**：读取 `references/guide.md` 判断任务类型。
2. **内容创作**：按 `character-guide.md` (世界书) 或 `card-writing-guide.md` (角色卡) 编写。
3. **质量控制**：执行 **DoubleCheck** 扫描禁词与格式。
4. **文件生成**：调用 `scripts/` 下的工具生成最终 JSON。

---

## 目录结构

```
world-book-skill/
├── SKILL.md                     # 技能入口：v3.0 重构，涵盖角色卡与世界书全流程
├── agents/openai.yaml           # 技能注册元数据
├── scripts/
│   ├── world-book-create.py    # 世界书增删改查 CLI
│   ├── card-generator.py       # [新] 角色卡 V3 JSON 生成/解包工具
│   └── query.py                # 世界书轻量查询/导出工具
└── references/
    ├── guide.md                # 场景路由器（AI 第一步读取）
    ├── entry-conventions.md    # 总索引（含 XML 包裹 YAML 铁律）
    ├── card-writing-guide.md   # [新] 角色卡创作规范与禁词自检
    ├── card-generator-guide.md # [新] 角色卡生成器使用手册
    ├── html-beautify-guide.md  # [新] HTML 模式与全局美化指南
    ├── mvu-guide.md            # [新] MVU ZOD 变量系统说明
    ├── character-guide.md      # 世界书角色条目创作铁律
    ├── worldbuilding-guide.md  # 世界观写作 + 压缩 + 嵌套
    ├── config-guide.md         # 世界书配置规则
    ├── position-guide.md       # ST 注入位置参考
    ├── extract-worldbuilding.md # 世界观提取指南
    ├── extract-character.md    # 角色提取指南
    ├── extract-item.md         # 物品/能力/装备提取指南
    ├── extract-story.md        # 故事/章节提取指南
    ├── extract-style.md        # 文风提取指南
    └── conversion-guide.md     # 转化完整工作流
```

## 依赖

- Python 3.8+
- SillyTavern (用于导入生成的 JSON)

---

# 更新日志

## v3.0 — 2026-05-14 (Current)
### 重大功能升级
- **角色卡系统上线**：新增 `card-generator.py`，支持生成/解包高标准 V3 角色卡 JSON。
- **美化支持**：新增 `html-beautify-guide` 与 `mvu-guide`，支持 ZOD 变量状态栏与全局美化布局。
- **质量检查体系**：引入 **DoubleCheck** 质量清单，包含 10+ 项逐字禁词扫描、6 项一致性检查。
- **格式标准演进**：全面转向 **XML 包裹 YAML** 格式，提升 AI 编写的结构化程度。

### 细节优化
- `SKILL.md` 全面重写，增加任务路由逻辑（第零步）。
- 细化了“场景路由器” `guide.md`，明确区分世界书、角色卡、美化任务。
- 更新所有提取指南，适配最新的 YAML 结构化输出。

## v2.1 — 2026-05-09
- `world-book-create.py` 新增 `excludeRecursion` 支持。
- 优化提示词结构，增加世界书禁词防止增殖。

## v2.0 — 2026-04-26
- 新增 `query.py` 查询工具。
- 新增场景路由器 `guide.md` 及 7 个场景提取/转化指南。
- 角色条目格式升级，由单一指南拆分为角色、世界观、配置三个专项指南。

## v1.0 — 2025
- 初始版本发布，支持基础世界书 JSON 生成。
