# MVU ZOD 变量系统指南

MVU (MagVarUpdate) 是 SillyTavern 的变量管理系统。**仅当用户明确要求时才添加！**

---

## 前置条件

使用 MVU ZOD 需要安装以下插件：
1. **酒馆助手** (JS-Slash-Runner)
2. **提示词模板** (ST-Prompt-Template)

---

## MVU 两种风格

| 对比维度 | MVU zod（推荐） | MVU beta（旧版） |
|----------|----------------|-------------------|
| 初始化 | YAML 格式 | JSON 格式 |
| 更新命令 | JSON Patch (RFC 6902) | `_.add()` / `_.set()` |
| 变量路径 | `/角色名/好感度` | `stat_data.角色名.好感度[0]` |
| 读取方式 | `{{format_message_variable::stat_data}}` | `getvar("stat_data.角色名.好感度[0]")` |
| Schema | Zod Schema + `registerMvuSchema` | 无 |

**推荐默认使用 MVU zod 风格。** 两种风格不兼容，选定后所有配置必须统一。

---

## MVU 系统组件清单（5类9项）

完整的 MVU 系统需要以下全部组件：

### 1. 酒馆助手脚本（2个）

#### MVU 核心脚本
```js
// content
import 'https://testingcf.jsdelivr.net/gh/MagicalAstrogy/MagVarUpdate/artifact/bundle.js';

// 按钮
重新处理变量(可见)、重新读取初始变量(可见)、清除旧楼层变量(隐藏)、
快照楼层(隐藏)、重演楼层(隐藏)、重试额外模型解析(隐藏)
```

#### Zod Schema 脚本
```js
import { registerMvuSchema } from 'https://testingcf.jsdelivr.net/gh/StageDog/tavern_resource/dist/util/mvu_zod.js';

export const Schema = z.object({
  角色名: z.object({
    好感度: z.coerce.number()
      .describe('0-100，好感度指标')
      .transform(v => _.clamp(v, 0, 100))
      .prefault(20),
    心情: z.string()
      .describe('当前心情状态')
      .prefault('平静'),
  }),
});

$(() => {
  registerMvuSchema(Schema);
});
```

### 2. 世界书条目（4个）

#### [initvar] 变量初始化条目
- **状态**: enabled=false（禁用！）
- **position**: after_char (1), constant=true
- **内容**: YAML 格式初始值

```yaml
角色名:
  好感度: 20
  心情: 平静
  着装:
    上装: 白色衬衫
    下装: 黑色长裤
```

#### 变量列表条目
- **状态**: enabled=true, constant=true
- **position**: at_depth (4), depth=0

```
---
<status_current_variable>
{{format_message_variable::stat_data}}
</status_current_variable>
```

#### [mvu_update] 变量更新规则条目
- **状态**: enabled=true, constant=true
- **position**: after_char (1)

```yaml
---
变量更新规则:
  角色名:
    好感度:
      type: number
      range: 0~100
      check:
        - 根据互动质量调整 ±(3~6)
        - 每轮对话自然衰减 -1~-2
    心情:
      type: string
      check:
        - 根据对话内容推断并更新
```

#### [mvu_update] 变量输出格式条目
- **状态**: enabled=true, constant=true
- **position**: at_depth (4), depth=0

```
---
变量输出格式:
  rule:
    - 你必须在回复末尾输出变量更新分析
    - 使用 JSON Patch 格式描述变化
    - 不需要变化时省略对应字段
  format: |-
    <UpdateVariable>
    <Analysis>简要分析变化原因</Analysis>
    <JSONPatch>[{"op":"replace","path":"/角色名/好感度","value":25},{"op":"replace","path":"/角色名/心情","value":"开心"}]</JSONPatch>
    </UpdateVariable>
```

### 3. 正则脚本（3个必需 + 可选）

#### [不发送] 去除变量更新（隐藏）
- **用途**: 对AI隐藏旧消息中的变量更新
- **findRegex**: `/<UpdateVariable>[\s\S]*?<\/UpdateVariable>/gm`
- **replaceString**: `""`
- **promptOnly**: true, **minDepth**: 4
- **placement**: [2]

#### [美化] 完整变量更新
- **用途**: 用户可见的折叠面板
- **findRegex**: `/<update(?:variable)?>\s*(.*)\s*<\/update(?:variable)?>/gsi`
- **replaceString**: `<details><summary>变量更新情况</summary>$1</details>`
- **markdownOnly**: true
- **placement**: [2]

#### [美化] 变量更新中（不完整标签）
- **用途**: AI可能只输出开始标签
- **findRegex**: `/<update(?:variable)?>(?!.*<\/update(?:variable)?>)\s*(.*)\s*$/gsi`
- **replaceString**: `<details><summary>变量更新中{{random::.::..::...}}</summary>$1</details>`
- **markdownOnly**: true
- **placement**: [2]

#### 可选：[不发送] 对AI隐藏状态栏
- **findRegex**: `<StatusPlaceHolderImpl/>`
- **replaceString**: `""`
- **promptOnly**: true
- **runOnEdit**: true
- **placement**: [2]

#### 可选：[不发送] 仅格式思维链
- **findRegex**: `/<Analysis>[\s\S]+?<\/Analysis>/gm`
- **replaceString**: `""`
- **promptOnly**: true
- **runOnEdit**: true
- **placement**: [2]

---

## 开场白中的 initvar 嵌入

不同可选开场可以设置不同的变量初始值：

```
开场文本...

<UpdateVariable>
<initvar>
角色名:
  好感度: 30
  心情: 好奇
</initvar>
</UpdateVariable>

开场续...

<StatusPlaceHolderImpl/>
```

规则：
- 开场中有 `<initvar>` → 使用开场中的值
- 开场中无 `<initvar>` → 使用世界书中禁用的 `[initvar]` 条目(保底)

---

## 变量路径别名

在 Zod Schema 中可为路径定义别名，简化更新格式：

```js
export const Schema = z.object({
  角色名: z.object({
    好感度: z.coerce.number().alias('aff').prefault(20),
    心情: z.string().alias('mood').prefault('平静'),
  }),
});
```

输出格式中可提示AI使用别名：
- `{ "op": "replace", "path": "/角色名/好感度", "value": 25 }`
- 或 `{ "op": "replace", "path": "/aff", "value": 25 }`（使用别名）

---

## MVU 自查清单

- [ ] 用户明确要求了 MVU？
- [ ] MVU 核心脚本已添加
- [ ] Zod Schema 脚本已添加
- [ ] [initvar] 条目已创建（disabled=true）
- [ ] 变量列表条目已创建（@D depth=0）
- [ ] 更新规则条目已创建
- [ ] 输出格式条目已创建（@D depth=0）
- [ ] 去除变量更新正则已创建（minDepth=4, promptOnly）
- [ ] 变量更新美化正则已创建（markdownOnly）
- [ ] 变量更新中正则已创建（不完整标签）
- [ ] 所有条目 preventRecursion=true
- [ ] 所有条目 excludeRecursion=true
- [ ] 风格统一（全部使用 MVU zod 或全部 MVU beta）
- [ ] 每个可选开场含不含 initvar 已确认
