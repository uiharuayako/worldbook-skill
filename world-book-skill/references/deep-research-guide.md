# Gemini Deep Research 指引

> 本文件规范 world-book-skill 中的 Deep Research 用法。它是可选资料搜集层，不是默认流程。只有用户明确要求使用 Gemini Deep Research / Google AI Studio 深度检索时，才读取本文件并调用对应脚本。

---

## 本文内容

>本文指引如何在 world-book-skill 中使用 Gemini Deep Research 搜集资料。内容包括触发条件、API key 配置、脚本调用、输出物处理、隐私边界和失败回退规则。Deep Research 的职责是搜资料和整理引用，不直接替代角色卡 JSON 生成。

---

## 铁律

1. **仅显式触发** — 用户没有明确要求 Deep Research 时，不要主动调用。
2. **不替代主流程** — Deep Research 输出只是源材料，后续仍要按 `information-extraction-guide.md` / `character-card-guide.md` / `world-book-guide.md` 编写。
3. **未配置不硬跑** — 若用户明确要求 Deep Research 但未配置授权，先说明缺少配置，再由用户决定是否改走普通搜索。
4. **不把个人信息写入仓库** — API key 只放本地 `.env` 或环境变量，绝不写进 tracked 文件。
5. **结果先落盘再使用** — 先产出 `report.md` / `sources.json` / `interaction.json`，再把报告视为源材料继续提取。

---

## 授权方式

只支持一种方式：Google AI Studio API key。

在 `.env` 中填写：

```bash
GEMINI_API_KEY=your_google_ai_studio_api_key
```

---

## 触发场景

以下场景才适合使用：

- 用户明确说要用 Deep Research / Gemini 深度检索 / Google AI Studio 搜资料
- 二创作品资料分散，普通搜索不够稳定
- 需要研究报告和来源引用，后续再写角色卡或世界书

以下场景不建议使用：

- 用户只是让你普通联网搜一下
- 用户给了完整原文，本地提取已经足够
- 只是修改一个已有条目，不需要重新搜集资料

---

## 标准调用

```bash
python scripts/gemini-deep-research.py \
  --env-file .env \
  --input "Research the target work, extract character/worldbuilding facts, and cite sources." \
  --output-dir ./deep-research-output
```

可选参数：

- `--input-file prompt.txt`：从文件读取研究提示词
- `--tool url_context`：当用户给了明确 URL，希望纳入研究上下文时使用
- `--interaction-id ...`：继续轮询已启动的研究任务
- `--no-wait`：仅创建任务并立即返回

---

## 输出物

脚本默认输出到 `deep-research-output/`：

- `interaction.json`：原始 API 返回，便于排错
- `report.md`：整理后的研究报告，可直接作为源材料阅读
- `sources.json`：从返回中提取出的来源和引用

后续处理规则：

1. 先阅读 `report.md`
2. 将角色 / 世界观 / 物品 / 文风信息整理为简短简介 txt
3. 再按 `information-extraction-guide.md` 的提取格式继续工作

---

## 提示词建议

Deep Research 提示词要写成“研究任务”，不是“直接生成角色卡 JSON”。

推荐写法：

- 指明作品名 / 角色名 / 世界观范围
- 指明你要提取的维度：外貌、背景、关系、能力、势力、规则、章节
- 要求保留来源
- 要求区分“原作事实”和“推测”

不推荐写法：

- “直接给我最终角色卡 JSON”
- “自己决定写什么”
- “不要来源”

---

## 回退规则

如果出现以下情况：

- 缺少 API key 配置
- API 返回鉴权错误
- 研究任务超时
- 官方返回无有效内容

处理顺序：

1. 明确告诉用户 Deep Research 没有成功执行
2. 说明失败原因
3. 询问是否改为普通网络搜索或改为用户提供原文

不要假装已经完成深度检索。
