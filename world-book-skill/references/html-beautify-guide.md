# HTML 前端美化指南

HTML 前端美化通过正则脚本将占位符或标签替换为可视化的 HTML 界面。**仅当用户明确要求时才添加！**

---

## 三种美化模式

| 模式 | 美化对象 | 适用场景 |
|------|----------|----------|
| 模式A：状态栏美化（有MVU） | 仅状态栏面板 | 含完整MVU变量系统的卡 |
| 模式B：状态栏美化（无MVU） | 仅状态栏面板 | 无MVU但需要数值展示 |
| **模式C：全局美化** | **整个消息体 + 状态栏** | **需要全文主题包装的卡** |

### 三种模式的关键差异

| 对比维度 | 模式A（有MVU） | 模式B（无MVU） | 模式C（全局美化） |
|----------|---------------|---------------|------------------|
| 美化范围 | 仅状态栏 | 仅状态栏 | 整个消息体 |
| AI输出包裹 | 无 | 无 | **`<chat>...</chat>`** |
| 数值来源 | MVU变量系统 | AI文本→正则解析 | 同A或B（取决于有无MVU） |
| findRegex | `<StatusPlaceHolderImpl/>` | `/<statusbar>([\s\S]*?)<\/statusbar>/gm` | `/<chat>(.*?)<\/chat>/s` |
| D0格式条目 | 不需要 | 需要（状态栏格式） | **必须**（`<chat>`包裹+状态栏格式） |
| 状态栏兼容 | ✓ | ✓ | ✓（正则顺序：状态栏先→全局后） |
| HTML设计重点 | 状态面板贴合人设 | 状态面板贴合人设 | 整个页面框架贴合世界观 |

---

## 模式A：有 MVU ZOD 时

### 正则配置

```
# 状态栏美化正则
findRegex: <StatusPlaceHolderImpl/>
replaceString: [完整HTML代码，通过JS读取MVU变量]
markdownOnly: true
placement: [2]
runOnEdit: true

# 对AI隐藏状态栏正则
findRegex: <StatusPlaceHolderImpl/>
replaceString: ""
promptOnly: true
placement: [2]
runOnEdit: true
```

### HTML 设计要点

- 通过 `{{format_message_variable::stat_data.变量路径}}` 读取数值
- 或通过 JS 读取 `getvar()` / 全局变量
- 设计必须贴合角色人设和世界观
- 可以设计多页签（tab切换）

### 设计示例（笺上孤鸾风格）

有 MVU 的情况下，HTML 面板从变量系统获取：
- 好感度 → 进度条/数值
- 心情 → 标签/颜色
- 服装 → 列表渲染
- 自定义指标 → 对应 UI 组件

### 外部加载 vs 内联

| 方式 | 优点 | 缺点 |
|------|------|------|
| 内联HTML/CSS | 不依赖外部，离线可用 | 占用角色卡体积 |
| 外部CDN加载 | 不占角色卡体积 | 依赖CDN可用性 |

```js
// 外部加载示例
<script>$('body').load('https://.../index.html')</script>
```

---

## 模式B：无 MVU ZOD 时

### 步骤1：世界书引导条目

创建"状态栏格式规范"条目，引导 AI 每轮输出状态栏：

```
## 内容格式规范
- 每个回复末尾必须输出 <statusbar>...</statusbar>
- 使用以下格式：

<statusbar>
<emotion-list>
[平静25%][烦躁5%][开心50%][喜悦10%]
</emotion-list>
好感度: XX
当前情绪: 描述
身体状态: 描述
<choice>
[选项1描述][选项2描述][选项3描述]
</choice>
</statusbar>
```

- **条目配置**：position=4 (D0), depth=0, constant=true, role=0

### 步骤2：美化正则

```
findRegex: /<statusbar>([\s\S]*?)<\/statusbar>/gm
replaceString: [从$1捕获内容解析各字段的HTML代码]
markdownOnly: true
placement: [1, 2]
runOnEdit: true
```

### 步骤3：隐藏正则

```
findRegex: /<statusbar>[\s\S]*?<\/statusbar>/gm
replaceString: ""
promptOnly: true
placement: [2]
runOnEdit: true
```

### HTML 解析方式

由于没有 MVU 变量，HTML 必须从 AI 输出的文本中解析数据：

```js
// 从正则捕获组中解析数值
// $1 内容是类似 "好感度: 65\n当前情绪: 愉快"
// 用 JS 字符串处理提取各字段
const content = `$1`;
// 正则匹配各项...
```

---

## 无 MVU 时的开场嵌入

开场和每次回复都必须包含状态栏文本块：

```
开场故事文本...

<statusbar>
<emotion-list>
[平静80%][烦躁0%][开心10%][喜悦10%]
</emotion-list>
好感度: 50
当前情绪: 平静
身体状态: 健康
想法: 等待用户指令
地点: 图书馆
时间: 下午3点
天气: 晴
<choice>
[去吃点东西][继续看书][出去走走]
</choice>
</statusbar>
```

---

## 模式C：全局美化（正文包裹）

全局美化使用 `<chat>` 标签包裹整个消息体，将正文和状态栏共同装入一个贴合角色世界观的HTML主题框架。

### 步骤1：D0 格式保持条目（必须且关键）

**这是全局美化最容易翻车的点。** AI 如果不被明确要求，会忘记包裹 `<chat>` 标签。

在世界书中创建一条 @D depth=0 条目，强制 AI 保持输出格式：

```
内容格式规范:
  包裹标签:
    - 每次回复必须用 <chat>...</chat> 包裹全部正文内容
    - 状态栏 <statusbar>...</statusbar> 必须放在 </chat> 之前（即正文末尾）
    - 不得遗漏 <chat> 开闭标签
    - 不得在 <chat> 标签之外写任何正文内容
  状态栏格式:
    <statusbar>
    <emotion-list>
    [平静25%][烦躁5%][开心50%][喜悦10%]
    </emotion-list>
    好感度: XX
    当前情绪: 描述
    身体状态: 描述
    <choice>
    [选项1][选项2][选项3]
    </choice>
    </statusbar>
  严禁:
    - 不得省略 <chat> 包裹
    - 状态栏不得放在 <chat> 之外
    - 不得改变状态栏标签结构
    - 不得在 </chat> 之后追加任何正文
```

- **条目配置**：position=4 (D0), depth=0, role=0 (system), constant=true, preventRecursion=true, excludeRecursion=true
- **命名建议**：`[D0]内容格式规范`

### 步骤2：正则执行顺序（状态栏先 → 全局后）

**这是全局美化的核心兼容设计。** 正则按数组顺序执行，顺序错则全部失效。

```
正确的正则顺序：
┌─────────────────────────────────────────┐
│ ① 状态栏美化正则（先执行）                │
│    匹配 <statusbar> 或 <StatusPlaceHolderImpl/>   │
│    替换为状态栏HTML                       │
│                                          │
│ ② 全局美化正则（后执行）                  │
│    匹配 <chat>(.*?)</chat>              │
│    $1 已包含渲染后的状态栏HTML             │
│    替换为全局HTML框架                     │
└─────────────────────────────────────────┘
```

**如果顺序颠倒，结果：** 全局美化先执行，`$1` 里的 `<statusbar>` 还是原始标签文本，状态栏美化再执行时标签已经被HTML包裹了，无法匹配。

### 步骤3：全局美化正则

```
# 全局美化正则
findRegex: /<chat>(.*?)<\/chat>/s
replaceString: [完整HTML框架，$1放在内层"纸张"区域]
markdownOnly: true
placement: [2]
runOnEdit: true
```

**`/s` flag（dotAll）必须加**——确保 `.` 能匹配换行符，因为 AI 输出的正文包含多段换行。

### 步骤4：HTML 主题框架模板

全局美化的 HTML 必须分三层设计：

```html
<div style="[外层容器：背景图案+边框+阴影，贴合世界观]">
  
  <!-- 可选：角色插图/装饰元素 -->
  <img src="角色图URL" style="..." />
  
  <!-- 内层"纸张"/"内容区" -->
  <div style="[内层：仿纸背景、内边距、圆角]">
    $1   <!-- 这里是AI输出的全部正文+已渲染的状态栏 -->
  </div>
  
</div>
```

### HTML 设计原则（全局美化专有）

**外层容器设计：**
- 背景用 CSS 图案叠加——渐变、星尘、网格、纸质纹理、羊皮纸、像素风等
- 边框色彩取自角色主题色（魔法=紫色、侦探=暖棕、科技=冷蓝青色）
- 阴影和圆角营造层次感
- 可加装饰性 SVG 图标（如罗盘、羽毛笔、齿轮、像素心形等）

**内层"纸张"设计：**
- **必须设置 `white-space: pre-wrap`**——AI输出正文含 `\n` 换行，HTML默认会塌缩为空格，不加此属性整段文本挤在一起无法阅读
- 背景色与外层形成对比（外层深色→内层浅色，反之亦然）
- 内边距适当（左右 8-16px，上下 12-20px）
- 可加内阴影模拟嵌入感
- 可加横线纹理模拟笔记本/日记纸

**风格对照表：**

| 世界观类型 | 外层色调 | 内层风格 | 装饰元素 |
|-----------|----------|----------|----------|
| 中世纪奇幻/魔女 | 深紫+金色星尘 | 泛黄羊皮纸 | 罗盘SVG、魔法阵 |
| 现代校园 | 柔和米白+樱花粉 | 干净白纸 | 花瓣、笔记本格线 |
| 赛博朋克/科幻 | 暗蓝+霓虹青 | 半透明暗面板 | 扫描线、数据流 |
| 古风修仙 | 墨绿+金边 | 宣纸纹理 | 印章、水墨笔触 |
| 侦探/悬疑 | 深棕+暖黄 | 档案纸 | 放大镜、指纹、打字机字体 |

### 步骤5：开场白适配

first_mes 和所有 alternate_greetings 必须用 `<chat>` 包裹：

```
<chat>
开场叙述文本...

场景描写、角色动作、对话...

<statusbar>
<emotion-list>
[平静80%][烦躁0%][开心10%][喜悦10%]
</emotion-list>
好感度: 50
当前情绪: 平静
身体状态: 健康
<choice>
[选项1][选项2][选项3]
</choice>
</statusbar>
</chat>
```

### 完整示例（伊蕾娜风格——中世纪魔女旅行日记）

**AI 输出原文：**
```
<chat>
凛冽的山风抽打着悬崖峭壁...

伊蕾娜骑乘扫帚悬停在半空中，灰白色长发在风中翻飞...

"抓紧了。"伊蕾娜的声音平稳，没有回头。

<statusbar>
<emotion-list>
[好奇30%][不耐烦10%][愉悦20%]
</emotion-list>
好感度: 20
当前情绪: 略带抱怨但保持专业
身体状态: 飞行后轻微疲劳
<choice>
[询问她的旅行目的地][感谢救命之恩并自我介绍][保持沉默观察四周]
</choice>
</statusbar>
</chat>
```

**正则替换后的 HTML 结构（精简示意）：**
```
外层div (深紫星尘背景 + 紫色边框 + 阴影)
  ├── 角色插图 <img>
  └── 内层div (仿羊皮纸背景，内阴影)
        └── $1 (正文叙述 + 已渲染的状态栏HTML)
```

---

## 全局美化正则配置模板

### 全局美化（正文包裹）
```json
{
  "scriptName": "全局美化",
  "findRegex": "/<chat>(.*?)<\\/chat>/s",
  "replaceString": "[完整HTML框架，$1在内层区域内]",
  "markdownOnly": true,
  "promptOnly": false,
  "placement": [2],
  "runOnEdit": true,
  "disabled": false
}
```

### 对AI隐藏全局标签（可选）
```json
{
  "scriptName": "[不发送]隐藏全局标签",
  "findRegex": "/<chat>|<\\/chat>/g",
  "replaceString": "",
  "markdownOnly": false,
  "promptOnly": true,
  "placement": [2],
  "runOnEdit": true,
  "disabled": false
}
```

---

## HTML 正则配置模板

### 状态栏美化（有MVU）
```json
{
  "scriptName": "状态栏美化",
  "findRegex": "<StatusPlaceHolderImpl/>",
  "replaceString": "[内联HTML代码或外部加载]",
  "markdownOnly": true,
  "promptOnly": false,
  "placement": [2],
  "runOnEdit": true,
  "disabled": false
}
```

### 状态栏美化（无MVU）
```json
{
  "scriptName": "状态栏美化",
  "findRegex": "/<statusbar>([\\s\\S]*?)<\\/statusbar>/gm",
  "replaceString": "[内联HTML代码，从$1解析数据]",
  "markdownOnly": true,
  "promptOnly": false,
  "placement": [1, 2],
  "runOnEdit": true,
  "disabled": false
}
```

### 状态栏隐藏（通用）
```json
{
  "scriptName": "[不发送]界面占位符",
  "findRegex": "占位符或标签",
  "replaceString": "",
  "markdownOnly": false,
  "promptOnly": true,
  "placement": [2],
  "runOnEdit": true,
  "disabled": false
}
```

---

## HTML前端的六条铁律

1. **HTML必须贴合角色世界观和人设设计。** 禁止通用模板。一个古代修仙角色的全局框架和现代侦探的风格应该完全不同。
2. **有MVU时数字从变量读取，无MVU时从文本解析。** 两种方式的正则和HTML结构完全不同，不可混淆。
3. **必须有配对的隐藏正则。** AI不应该看到HTML代码或状态栏原始文本。
4. **用户不要求，绝不主动建议添加。** 这是最容易被忽视的规则。
5. **全局美化必须配合 D0 格式保持条目。** 没有 D0 条目，AI 会忘记 `<chat>` 包裹，全局美化正则完全失效。
6. **正则顺序：状态栏美化在前，全局美化在后。** 顺序错 = 状态栏无法渲染 = 全局框架内出现原始标签文本。

---

## 设计范例

### 范例1：笺上孤鸾（MVU+双页签面板）

- **风格匹配**：角色是阿尔茨海默病患者+研究员
- **设计**：笔记本记录页签(格子纸、YAML、怀旧色) + 实验室研究页签(深色科技风)
- **正则**：`<StatusPlaceHolderImpl/>`，数值全从MVU读取

### 范例2：普拉娜（无MVU+毛玻璃面板）

- **风格匹配**：AI少女，现代科技+柔软感
- **设计**：毛玻璃效果、浮动动画、背景轮播
- **正则**：`/<statusbar>([\s\S]*?)<\/statusbar>/gm`，从文本解析

### 范例3：色情侦探（MVU+外部CDN）

- **风格匹配**：侦探事务所、案件调查
- **设计**：外部HTML加载(不占角色卡体积)
- **正则**：`<StatusPlaceHolderImpl/>` + 多个`<AbilitiesGeneration>`/`<EventGeneration>`功能面板

### 范例4：伊蕾娜（全局美化+状态栏，模式C）

- **风格匹配**：中世纪魔女旅行日记
- **设计**：外层深紫魔纹背景+星尘+魔法阵图案；内层仿羊皮纸内容区；角色插图+罗盘SVG装饰
- **正则**：`/<chat>(.*?)<\/chat>/s` 全局美化 + `/<日记内容>...<\/日记内容>/s` 状态栏
- **正则顺序**：旅行日志(状态栏)正则在前(①) → 全局美化正则在后(②)
- **D0条目**：要求AI永久输出并保持 `<chat>` 包裹格式

---

## 自查清单

- [ ] 用户明确要求了HTML美化？
- [ ] 已判断美化模式（A/B/C）？
- [ ] 模式A：正则匹配 `<StatusPlaceHolderImpl/>`（单占位符）
- [ ] 模式B：正则匹配 `<tag>...</tag>`（配对标签+捕获组）
- [ ] **模式C：D0格式保持条目已创建（position=4, depth=0, role=0）**
- [ ] **模式C：正则顺序正确（状态栏美化在前① → 全局美化在后②）**
- [ ] **模式C：开场白/可选开场均包裹在 `<chat>` 中**
- [ ] **模式C：`/<chat>(.*?)<\/chat>/s` 正则已含 `/s` flag**
- [ ] 世界书引导条目已创建（模式B和C均需要）
- [ ] 美化正则已创建（markdownOnly=true）
- [ ] 隐藏正则已创建（promptOnly=true）
- [ ] HTML设计贴合角色人设和世界观
- [ ] 无MVU时，开场含状态栏文本块
- [ ] 无MVU时，`alternate_greetings` 中状态栏值各不相同
- [ ] **模式C：全局美化HTML的三层结构清晰（外层容器，可选装饰，内层纸张区）**
- [ ] **模式C：内层内容区 `$1` 所在 div 设置了 `white-space: pre-wrap`（否则换行失效）**
