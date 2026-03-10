# 技能名称 (Skill Name)
WordPressTechPublisher (WordPress 科技图文自动发布专家)

## 📝 技能描述 (Description)
接收原始 Markdown 文章内容，自动调用 `baoyu-article-illustrator` (Gemini Banana 模型) 生成高质量 PNG 科技感配图，将文本转化为符合现代 Web UX 规范的 WordPress Gutenberg HTML 块，并通过 XML-RPC 自动发布至 WordPress 博客。

---

## 📥 输入参数 (Input Parameters)
在调用此技能时，必须提供以下 JSON 格式的参数：

```json
{
 "type": "object",
 "properties": {
 "title": {
 "type": "string",
 "description": "文章的标题，需具备科技感和吸引力"
 },
 "content_markdown": {
 "type": "string",
 "description": "需要发布的正文核心内容，支持原始 Markdown 格式"
 },
 "wp_endpoint": {
 "type": "string",
 "description": "WordPress XML-RPC 端点地址",
 "default": "https://dvspace5.wordpress.com/xmlrpc.php"
 },
 "wp_credentials": {
 "type": "object",
 "description": "WordPress 账号信息 (建议通过环境变量/Secret注入)",
 "properties": {
 "username": { "type": "string" },
 "password": { "type": "string", "description": "WordPress 应用程序密码" }
 },
 "required": ["username", "password"]
 }
 },
 "required": ["title", "content_markdown", "wp_credentials"]
}
```

## 📤 输出格式 (Output Format)
技能执行完成后，应返回以下 JSON 结构：

```json
{
 "type": "object",
 "properties": {
 "success": { "type": "boolean" },
 "post_id": { "type": "integer", "description": "WordPress 返回的文章 ID" },
 "post_url": { "type": "string", "description": "拼接后的文章链接，格式为 /?p=XXX" },
 "display_message": { "type": "string", "description": "面向用户展示的最终成功提示语" }
 }
}
```

## 🧠 执行逻辑与工作流 (Execution Workflow)
Agent/OpenClaw 在执行此技能时，必须严格按以下 4 个阶段运行：

### 阶段 1：规划与生成图像 (从技能库调度)
1. 分析 `content_markdown` 内容，提取 3 个视觉核心概念。
2. 调用技能：`baoyu-article-illustrator`。
3. **文生图模型约束**: 必须使用 Gemini Banana。
4. **生成需求**: 生成 3 张无损 PNG 格式图像：
 - `Cover_Image.png`: 专业封面图（浅色调、极简主义、现代科技感）。
 - `Concept_Image.png`: 概念解释图（插入正文中段，展现架构、数据流或技术概念）。
 - `Vision_Image.png`: 总结愿景图（插入文章末尾，传达积极的科技落地视觉）。

### 阶段 2：媒体库原生上传 (XML-RPC Media Upload)
1. 建立 XML-RPC 连接 (`wp_endpoint`)。
2. **⚠️ 技术要点** (Python 实现参考)：
 - **SSL 环境**: 在 macOS 或部分 Linux 环境下，需通过以下代码规避证书验证错误：
 ```python
 import ssl
 ssl._create_default_https_context = ssl._create_unverified_context
 ```
 - **二进制传输**: 调用 `wp.uploadFile` 时，必须使用 `xmlrpc_client.Binary` 封装图片内容，确保 PNG 无损传输。
3. 调用 `wp.uploadFile` 将 3 张 PNG 图片上传，记录返回的 `attachment_id` 和 url。

### 阶段 3：现代 Web 可视化排版 (Markdown -> Gutenberg blocks)
将原始的 `content_markdown` 转化为对浏览器友好的 WordPress 原生 HTML。 **排版约束与规范**：

- **段落**: 使用简短段落增加呼吸感。
- **标题**: 必须使用 `class="wp-block-heading"` 以匹配现代 WordPress 主题样式。
- **图片块**: 必须使用 `<!-- wp:image -->` 等块注释嵌入图片，以支持自适应显示。
- **请严格遵循以下 HTML 模板合并图文**：

```html
<!-- wp:image {"id":{{Cover_Image_ID}},"sizeSlug":"large","className":"is-style-rounded"} -->
<figure class="wp-block-image size-large is-style-rounded">
 <img src="{{Cover_Image_URL}}" alt="专业科技封面图" class="wp-image-{{Cover_Image_ID}}"/>
</figure>
<!-- /wp:image -->

<!-- wp:paragraph {"dropCap":true} -->
<p>{{引言与摘要部分...}}</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">🚀 {{核心章节标题}}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{{正文内容...}}</p>
<!-- /wp:paragraph -->

<!-- wp:image {"align":"center","id":{{Concept_Image_ID}},"sizeSlug":"large"} -->
<figure class="wp-block-image aligncenter size-large">
 <img src="{{Concept_Image_URL}}" alt="技术架构演示" class="wp-image-{{Concept_Image_ID}}"/>
 <figcaption class="wp-element-caption">图解：{{概念说明}}</figcaption>
</figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>{{后续内容与总结...}}</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":{{Vision_Image_ID}},"sizeSlug":"large"} -->
<figure class="wp-block-image size-large">
 <img src="{{Vision_Image_URL}}" alt="未来愿景" class="wp-image-{{Vision_Image_ID}}"/>
</figure>
<!-- /wp:image -->
```

### 阶段 4：XML-RPC 发布与结果反馈
1. 调用 `wp.newPost` 接口。
2. 将 `Cover_Image_ID` 传入 `post_thumbnail`（设置为特色图像/Featured Image）。
3. 将阶段 3 生成的 HTML 传入 `post_content`。
4. 状态设为 `publish`，并获取返回的 `post_id`。

## ⚠️ 最终标准输出规范 (Display Message Template)
执行完成后，Agent 必须将 `display_message` 的内容严格按照以下格式输出给用户：

```markdown
Baoyu Illustrator 技能集成已成功验证！当前 Pipeline 已实现：
✅ 调用 Gemini banana 模型生成三类专业图像 (PNG无损格式)
✅ 自动处理 XML-RPC 媒体上传 (已包含 SSL/Binary 补丁)
✅ 创建包含 Gutenberg 块标准的图文内容 (Web 响应式排版)
✅ 成功设置文章特色图像 (浅色科技风格)

发布成功后，博文地址为：https://dvspace5.wordpress.com/?p={post_id}
```
(注：执行器需将上述的 {post_id} 替换为阶段4中实际获取的文章数字ID)