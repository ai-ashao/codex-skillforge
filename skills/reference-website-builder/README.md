# Reference Website Builder

这是一个面向 Codex 和其他 Agent Skills 兼容编码工具的**页面级高保真参考重建 Skill**。

它的目标不是自动复制整个网站，而是：

> 输入一个明确页面 URL，分析并高还原其 UI 设计语言、布局、响应式、动画、交互和多层素材组合；随后替换品牌、文案和素材，接入现有项目，最后通过生产发布门禁。

## 默认处理范围

- 只处理用户明确提供的 URL。
- 不自动读取 sitemap。
- 不自动遍历导航并复制其他内页。
- 输入首页 URL 时，只重建首页。
- 输入工具页 URL 时，只重建该工具页。
- 多个页面需要分别提供多个 URL。

## 两阶段素材策略

### 第一阶段：高保真重建

为了保持还原度，可以临时下载原页面的：

- 图片和背景图
- 产品截图
- SVG 和装饰图层
- 视频与 poster
- 移动端独立素材

这些素材必须进入隔离目录：

```text
.reference-assets/<slug>/raw/       # 原始研究档案，不被页面引用
public/__reference__/<slug>/        # 开发阶段临时展示
src/config/reference-assets.ts      # 统一素材映射

docs/reference-build/<slug>/
  design-language.md                 # 观察、原则、目标适配与生产差异化契约
  asset-manifest.json
  asset-provenance.md
  replacement-checklist.md
```

组件不能到处硬编码 `/__reference__/...`，而应通过统一素材映射引用。后面替换图片时，优先只修改映射和 Manifest。

### 第二阶段：生产适配

上线前必须：

- 替换或授权临时素材
- 替换品牌、Logo、favicon 和 OG 图
- 替换竞品文案、评价、声明和法律文本
- 更新 SEO 与多语言内容
- 清理 `public/__reference__/`
- 清除源码中的 `__reference__` 引用
- 将 Manifest 状态全部变为 `approved` 或 `removed`
- 通过生产发布门禁

只要还有临时素材，结果必须标记：

```text
PROTOTYPE_ONLY=true
PRODUCTION_READY=false
Release status: BLOCKED
```

## 主要能力

- 页面级 URL-to-code，不自动扩展为整站克隆
- 高还原页面布局、设计语言和响应式
- 强制生成 `design-language.md`，分离参考观察、可复用原则和目标产品适配
- 检查点击、Hover、键盘、滚动、Sticky、自动播放、拖拽等交互
- 提取 computed style 和多层素材组合
- 现有项目优先，不强制新建 Next.js/Tailwind/shadcn 脚手架
- 保护多语言、登录、积分、支付、API、Analytics、Consent、SEO 和部署配置
- 临时素材隔离、Manifest 和统一素材映射
- 素材替换清单与视觉约束
- 生产发布自动拦截
- Worktree 和多 Agent 可选，不作为硬依赖

## 目录结构

```text
reference-website-builder/
├── SKILL.md
├── README.md
├── AGENTS_SNIPPET.md
├── CODEX_REVIEW_PROMPT.md
├── CHANGELOG.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── references/
│   ├── inspection-guide.md
│   ├── integration-guide.md
│   ├── qa-guide.md
│   ├── rights-and-provenance.md
│   └── temporary-assets-guide.md
├── templates/
│   ├── project-context.md
│   ├── reference-matrix.md
│   ├── page-topology.md
│   ├── behaviors.md
│   ├── original-design-brief.md
│   ├── design-language.md
│   ├── implementation-plan.md
│   ├── component-spec.md
│   ├── asset-manifest.json
│   ├── asset-provenance.md
│   ├── reference-assets.ts
│   ├── replacement-checklist.md
│   └── qa-report.md
├── examples/
│   └── generic-usage.md
└── scripts/
    ├── install.sh
    ├── check-reference-assets.mjs
    └── validate_skill.py
```

## 安装到 Codex

```bash
bash scripts/install.sh
```

安装到项目：

```bash
bash scripts/install.sh --project /path/to/project
```

兼容旧 Codex 目录：

```bash
bash scripts/install.sh --legacy-codex
```

## 验证 Skill

```bash
python3 scripts/validate_skill.py
```

## 生产门禁脚本

将 `scripts/check-reference-assets.mjs` 复制到目标项目的 `scripts/`，然后运行：

```bash
node scripts/check-reference-assets.mjs
```

推荐加入项目：

```json
{
  "scripts": {
    "check:reference-assets": "node scripts/check-reference-assets.mjs",
    "build:production": "npm run check:reference-assets && npm run build"
  }
}
```

## 推荐调用方式

```text
使用 $reference-website-builder 高保真重建以下页面：
REFERENCE_PAGE_URL
网站名称改成 NEW_SITE_NAME

只处理这个 URL，不自动遍历整站。
重点还原 UI 设计语言、页面布局、控件质感、动画、交互、响应式和多层素材组合。
开发阶段允许临时使用原页面素材，但必须统一放入隔离目录并登记 Manifest，组件通过统一素材映射引用。

保留当前项目的框架、路由、多语言、登录、积分、支付、Analytics、SEO 和部署结构。
先完成高保真重建与视觉 QA，再将网站名称、Logo 处理、favicon、metadata 与其他品牌标识替换为新站点名称，并替换或授权素材和文案。上线前运行生产门禁；存在临时素材或目标站身份内容时不得标记为可发布。
```

参考页面 URL 和新站点名称由当前用户请求提供；可复用的 Skill 说明和示例不得内置第三方网站或品牌。

重建、重建并适配、自有迁移模式会在 `docs/reference-build/<slug>/design-language.md` 中持续维护设计规则。它允许本地阶段精确校准，但同时要求生产版本完成 `Production adaptation contract` 和 `Must replace`，防止把竞品身份与标志性表达原样带到上线版本。

## 不适合

- 仿冒登录页或支付页
- 钓鱼、凭证收集或欺诈性品牌冒充
- 自动抓取整个域名
- 绕过登录、付费墙、CAPTCHA 或反爬限制
- 提取后端源码、密钥、私有 API 或用户数据
- 未完成替换或授权就把临时素材直接上线

## 来源与许可

本项目参考了 JCodesMore 的 MIT 开源项目 `ai-website-cloner-template` 的浏览器侦察、组件规格、并行构建和视觉 QA 思路，并针对页面级重建、现有项目接入和临时素材发布门禁进行了重新设计。详见 `THIRD_PARTY_NOTICES.md`。
