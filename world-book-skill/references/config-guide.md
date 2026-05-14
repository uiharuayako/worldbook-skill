# 世界书配置规则

内容写得好没用，配置错 = AI 读不到。本章是必读。

### 内容格式

所有世界书条目的内容采用 **XML 包裹 YAML** 格式：

```yaml
<pomelo>
name: 柚子猫
outfit:
  - 上衣: 白色水手服
  - 下装: 黑色百褶裙
</pomelo>
```

不要使用纯XML格式（`<tag>key:value</tag>`），标签独立成行，内容以 YAML 缩进展开。

---

## 一、触发策略：蓝灯 vs 绿灯

### 蓝灯（constant）——始终激活

只要世界书开着，该条目每轮都发给AI。**必须始终存在的信息才蓝灯。**

应该蓝灯的内容：世界观总纲、背景设定、角色速览

### 绿灯（关键词触发）——按需激活

只在最近消息中出现关键词时才发给AI。**扫描深度建议设为2。**

应该绿灯的内容：NPC详情、具体场景、事件、多角色卡的各个角色详细信息

### 单角色卡铁律

**单角色卡的所有条目全部蓝灯。** 无论拆成多少个条目。

条目拆开≠不同角色。同一个角色的基础信息、外貌、性格、背景拆成5个条目，描述的都是同一个人。AI必须同时知道全部信息才能正确扮演。不要把其中一些改成绿灯省token——缺了任何一条，角色就不完整。

### 多角色卡配置

- 角色速览：蓝灯。所有角色的一句话简介放一起
- 各角色详细信息：绿灯。关键词=角色名、昵称、外号

---

## 二、位置（position）

| 内容类型 | 位置 | Flag |
|----------|------|------|
| 世界观总纲/背景/规则/地理 | 0 (↑Char) | `--position 0` |
| 角色详细信息/NPC/场景/物品 | 1 (↓Char) | `--position 1` |
| 文风规则/格式指令 | 2 (↑AT) | `--position 2` |
| 行为纠正/二次解释 | 4 (@D, depth=0) | `--position 4 --depth 0 --role 0` |
| D1+ (@D depth≥1) | **永不使用** | 破坏聊天记录完整性 |

详细位置参考见 `references/position-guide.md`。

---

## 三、顺序（order）

数值越大越靠后。同一位置内的推荐分配：

| 内容 | order |
|------|-------|
| 世界观总纲 | 1 |
| 区域速览/背景设定 | 2-3 |
| 角色速览 | 4 |
| 场景/事件详情 | 50-98 |
| 核心角色详细信息 | 99 |
| NPC | 100 |

单角色卡拆分条目的内部顺序：基础信息10 → 外貌20 → 性格30 → 背景40 → NSFW50

---

## 四、递归设置（双字段，必须同时勾选）

**所有条目必须同时勾选两个递归选项。** 无一例外。

| CLI Flag | JSON 字段 | SillyTavern 术语 | 含义 |
|----------|-----------|------------------|------|
| `--prevent-recursion` | `preventRecursion` | 不可进一步递归 | 本条目**不会触发**其他条目 |
| `--exclude-recursion` | `excludeRecursion` | 无法被其他条目激活 | 本条目**不被**其他条目触发 |

⚠️ `world-book-create.py` 脚本默认两个字段均为 `false`。如果不加 flag，条目就**不会**设置递归防护。创建每条命令时都必须带这两个 flag。

不勾 `preventRecursion` 的后果：条目A内容出现条目B的关键词→B被触发→B的内容触发C→连锁反应→token爆炸。蓝灯和绿灯的配置全部白做。

不勾 `excludeRecursion` 的后果：条目B的关键词出现在条目C的内容中→条目C加载时触发了条目B→B的内容又触发了D→双向递归。特别是蓝灯条目之间互相触发，会导致关键设定条目被意外激活后又被驱逐出上下文。

---

## 五、关键词（keys）格式

- **英文逗号** `,` 分隔——中文逗号 `，` 和空格直接失效
- 覆盖所有称呼：全名、昵称、外号、职务
- 示例：`--keys "林小雨,小雨,班长"`

角色条目：全名 + 昵称 + 外号
NPC条目：全名 + 昵称 + 外号 + 职务
场景条目：场景名 + 所在区域 + 别称 + 相关动作
势力条目：全名 + 简称 + 所在地名

---

## 六、扫描深度

绿灯条目推荐 `--scan-depth 2`（只看最后一条用户消息和最后一条AI消息）。

---

## 七、常用配置组合

```bash
# 世界观总纲（蓝灯，角色定义前）
--constant --position 0 --order 1 --prevent-recursion --exclude-recursion

# 角色详细信息（蓝灯，角色定义后，单角色卡）
--constant --position 1 --order 99 --prevent-recursion --exclude-recursion

# NPC条目（绿灯，角色定义后，关键词触发）
--keys "角色名,昵称,外号" --position 1 --order 100 --scan-depth 2 --prevent-recursion --exclude-recursion

# 场景条目（绿灯，角色定义后，关键词触发）
--keys "场景名,地点名" --position 1 --order 80 --scan-depth 2 --prevent-recursion --exclude-recursion

# 行为纠正/二次解释（绿灯，D0）
--keys "角色名" --position 4 --depth 0 --role 0 --scan-depth 2 --prevent-recursion --exclude-recursion

# 文风条目（蓝灯，Author's Note前）
--constant --position 2 --order 1 --prevent-recursion --exclude-recursion

# 禁词条目（蓝灯，Author's Note前）
--constant --position 2 --order 1 --prevent-recursion --exclude-recursion
```

---

## 八、创建后必须自查

**所有条目创建完毕后，逐一用以下 checklist 检查，不得跳过。**

用 `python scripts/query.py <世界书路径> --brief` 查看每个条目的 constant 状态。

### 单角色卡（1个核心角色）

| 条目类型 | 蓝灯/绿灯 | 如果写错了 |
|---------|----------|-----------|
| 该角色的所有拆分条目 | **全部蓝灯** | 绿灯→角色不完整，AI猜着演→八股 |
| 世界观/背景 | 蓝灯 | — |
| NPC | 绿灯 | 蓝灯→无关NPC常驻吃token |

**铁律：单角色卡没有例外。** 拆成5个条目=5个蓝灯。拆成10个=10个蓝灯。

### 多角色卡（2+个核心角色）

| 条目类型 | 蓝灯/绿灯 | 如果写错了 |
|---------|----------|-----------|
| 角色速览 | **蓝灯** | 绿灯→AI不知道世界里有谁 |
| 各角色详细信息 | **绿灯** | 蓝灯→所有角色常驻，token爆炸 |
| 世界观/背景 | 蓝灯 | — |
| NPC/场景 | 绿灯 | 蓝灯→常驻吃token |
| 故事章节 | 绿灯 | 蓝灯→20章全常驻=上下文直接被撑爆 |

### 配置检查清单

**用 `python scripts/query.py <世界书路径> --brief` 逐条检查：**

- [ ] 先数清楚几个核心角色（1个=单角色卡，2+个=多角色卡）
- [ ] 单角色卡？→ 所有该角色的条目 `constant=true`
- [ ] 多角色卡？→ 速览 `constant=true`，角色详情 `constant=false` + `keys`
- [ ] 世界观条目全部 `constant=true`
- [ ] NPC/场景/故事章节全部 `constant=false` + `keys`
- [ ] **⚠️ 所有条目 `preventRecursion=true` 且 `excludeRecursion=true`**（脚本默认false，不加flag就不会设！）
- [ ] 关键词用英文逗号分隔，无空格
- [ ] 绿灯条目 `scanDepth=2`
- [ ] 禁词条目已创建（3条：叙事禁词 + 比喻禁词 + 描写禁律，蓝灯 position=2）
