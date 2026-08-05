# Codex Skillforge

[English](README.md) | 简体中文

[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ai-ashao/codex-skillforge?style=flat-square)](https://github.com/ai-ashao/codex-skillforge/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/ai-ashao/codex-skillforge?style=flat-square)](https://github.com/ai-ashao/codex-skillforge/forks)
[![Last commit](https://img.shields.io/github/last-commit/ai-ashao/codex-skillforge?style=flat-square)](https://github.com/ai-ashao/codex-skillforge/commits/main)

这是一个持续维护的自定义 Codex skills 集合，用于评估和改进小型 Web 产品。每个 skill 都是自包含的：`SKILL.md` 说明适用场景和工作流，配套的参考资料、脚本与样例让结论可复查、可复现。

## 已收录 skills

| Skill | 适用场景 | 确定性支持 |
|---|---|---|
| [`site-opportunity-scorecard`](skills/site-opportunity-scorecard/) | 判断一个 SEO 关键词簇或产品功能应成为独立网站、现有站专区、单一页面，还是暂缓/放弃。 | 加权机会分和拆站风险分、双语报告模板、报告结构校验。 |
| [`website-audit-scorecard`](skills/website-audit-scorecard/) | 对已上线的网站或 Web 产品评估产品质量、UX、信任、SEO、技术可靠性和变现准备度。 | 证据加权的覆盖率与置信度、关键 gate、样例 fixture 与回归测试。 |
| [`web-asset-pipeline`](skills/web-asset-pipeline/) | 将 AI、素材库、设计导出或截图中的视觉素材转为可上线的网站资源。 | 非破坏性素材审计、素材权利记录模板、格式与框架接入指南、回归测试。 |
| [`competitive-ui-reverse-engineering`](skills/competitive-ui-reverse-engineering/) | 将竞品页面参考和截图转为有差异化的页面方案。 | 证据分层的 UI 拆解、原创性边界、复用分析模板与素材流水线交接。 |
| [`technical-seo-audit`](skills/technical-seo-audit/) | 审计多语言公开 URL 的技术 SEO 信号，不把通用阈值误判为缺陷。 | 统一 Markdown/JSON 报告、有边界的 SSRF 防护、交付与索引信号、robots/sitemap、JSON-LD、hreflang 与 30+ 项回归测试。 |

这些是决策框架，并非 Google、Lighthouse、WCAG 或 AdSense 的官方评分体系。评分必须附带当前证据和覆盖范围说明。

## 安装 skill

克隆本仓库，再将需要的单个 skill 复制到 Codex 的用户级 skill 目录：

```bash
git clone https://github.com/ai-ashao/codex-skillforge.git
mkdir -p ~/.codex/skills
cp -R codex-skillforge/skills/site-opportunity-scorecard ~/.codex/skills/
```

将 `site-opportunity-scorecard` 替换为所需 skill，例如 `website-audit-scorecard`、`technical-seo-audit`、`web-asset-pipeline` 或 `competitive-ui-reverse-engineering`。安装后开启新的 Codex 对话；若未立即显示，再重启 Codex。

## 使用

通过名称调用 skill，并给出评估目标与约束：

```text
Use $site-opportunity-scorecard to decide whether a Markdown-to-image workflow
should be an independent site or a section of an existing converter site.
```

```text
Use $website-audit-scorecard to audit https://example.com as a release gate.
```

```text
Use $web-asset-pipeline to audit, optimize, and integrate the visual assets for this website.
```

```text
Use $competitive-ui-reverse-engineering to analyze these competitor references and create a differentiated implementation plan.
```

```text
Use $technical-seo-audit to run a technical SEO audit for this URL and state the evidence limits.
```

在依赖任何评估结论前，请先阅读对应 skill 的 `SKILL.md`，了解所需证据、报告格式和边界。

## 仓库结构

```text
skills/
  <skill-name>/
    SKILL.md        # 调用规则与工作流
    references/     # 评分规则、证据规则与报告模板
    scripts/        # 确定性辅助脚本
    assets/         # 样例输入与预期结果
    tests/          # 含可执行逻辑时的回归测试
```

## 发布前验证

运行与修改内容最相关的校验：

```bash
python3 -B -m unittest discover -s skills/website-audit-scorecard/tests -v
python3 -B skills/site-opportunity-scorecard/scripts/calculate_score.py \
  skills/site-opportunity-scorecard/assets/assessment-input-template.json
python3 -B -m unittest discover -s skills/web-asset-pipeline/tests -v
python3 -B -m unittest discover -s skills/technical-seo-audit/tests -v
```

对于机会评分报告，可校验其结构与语言配置：

```bash
python3 -B skills/site-opportunity-scorecard/scripts/validate_report.py \
  --lang auto path/to/report.md
```

## 维护约定

- 保持评分规则、计算器、模板和样例同步更新。
- 明确区分实测证据、用户提供的第三方指标和模型推断。
- 每次修复计算器问题时，都应补充回归测试。
- 不要在此仓库提交凭据、生产数据、浏览器配置文件或用户导出数据。
