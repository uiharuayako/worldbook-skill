# Gemini Deep Research 配置指南

本文档说明如何为 `worldbook-skill` 配置 Gemini API key，并在明确需要时使用 Deep Research 搜集资料。

## 适用范围

- 你想用 Google AI Studio 的 API key 调用 Gemini
- 你想在写角色卡 / 世界书前，先做一轮 Deep Research 资料搜集

Deep Research 是**可选功能**。不配置 API key 也不影响 `worldbook-skill` 的普通写卡、世界书、MVU、HTML 美化流程。

## 第一步：创建 API key

1. 打开 [Google AI Studio](https://aistudio.google.com/)
2. 进入 `Dashboard`
3. 选择一个已有项目，或创建一个新项目
4. 打开 `API Keys`
5. 创建一个新的 Gemini API key

注意：

- Gemini API key 底层会关联一个 Google Cloud 项目
- 很多账号在 AI Studio 中会自动带一个默认项目
- 你不需要把 key 写进仓库文件

## 第二步：本地配置 `.env`

在仓库根目录创建 `.env`：

```bash
cp .env.example .env
```

然后填写 API key：

```env
GEMINI_API_KEY=your_google_ai_studio_api_key
GEMINI_DEEP_RESEARCH_AGENT=deep-research-preview-04-2026
GEMINI_DEEP_RESEARCH_API_REVISION=2026-05-20
GEMINI_DEEP_RESEARCH_POLL_INTERVAL=10
GEMINI_DEEP_RESEARCH_TIMEOUT=1800
GEMINI_DEEP_RESEARCH_OUTPUT_DIR=deep-research-output
```

说明：

- `GEMINI_API_KEY` 只保存在本地 `.env`
- `.env` 已被 `.gitignore` 忽略，不会默认进入 git

## 第三步：先做一个基础连通性测试

如果你只想确认 key 是否可用，可以先跑普通的 `generateContent`：

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H "Content-Type: application/json" \
  -H "X-goog-api-key: $GEMINI_API_KEY" \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
```

如果返回模型回答，说明这个 key 至少具备基础 Gemini API 调用能力。

## 第四步：运行 Deep Research

在仓库根目录执行：

```bash
python world-book-skill/scripts/gemini-deep-research.py \
  --env-file .env \
  --input "Research the target work, extract key character and worldbuilding facts, and include sources." \
  --output-dir ./deep-research-output
```

如果你只想先创建研究任务，不等待完成：

```bash
python world-book-skill/scripts/gemini-deep-research.py \
  --env-file .env \
  --input "Research the target work and include sources." \
  --output-dir ./deep-research-output \
  --no-wait
```

脚本会输出：

- `interaction_id`
- `status`
- `artifacts` 目录

## 第五步：查看产物

默认输出目录里会包含：

- `interaction.json`：原始 API 返回
- `report.md`：整理后的研究报告
- `sources.json`：提取出的来源列表

推荐后续流程：

1. 先阅读 `report.md`
2. 将角色 / 世界观 / 物品 / 文风要点整理为简短摘要
3. 再按 `worldbook-skill` 的既有写卡 / 世界书流程继续处理

## 什么时候会触发 Deep Research

这个 skill 不会默认联网跑 Deep Research。

只有当用户明确提出类似意思时，才应该启用：

- “使用 Deep Research 搜资料”
- “用 Gemini 深度检索整理原作设定”
- “先联网做研究报告，再写卡”

如果用户没有明确要求，就继续使用普通流程，不要自动切换。

## 常见问题

### 1. 必须绑定项目吗？

要。Gemini API key 底层总会关联一个 Google Cloud 项目。  
但你通常只需要在 Google AI Studio 中选项目并创建 key，不一定要自己手动去 Cloud Console 复杂配置。

### 2. Deep Research 和普通 generateContent 有什么区别？

- `generateContent`：适合普通问答、快速试调用
- `Deep Research`：适合显式的资料搜集任务，会返回研究过程对应的 interaction 结果和来源信息

### 3. key 要不要提交到仓库？

不要。  
只保存在本地 `.env`，或通过本地环境变量传入。

### 4. 如果 key 泄露了怎么办？

去 Google AI Studio 立即删除或轮换该 key，然后更新本地 `.env`。
