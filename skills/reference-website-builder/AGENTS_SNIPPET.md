# AGENTS.md snippet

将下面一段加入项目根目录的 `AGENTS.md`，并按实际安装路径修改文件位置。

```markdown
## Available skills

- reference-website-builder: Reconstruct an explicitly provided web page with high fidelity, including UI design language, responsive layout, animation, interactions, and layered media, then adapt it inside the existing repository. It is page-scoped and must not automatically crawl the whole site. Development-only target assets may be isolated and mapped for fidelity, but production release is blocked until temporary assets, target identity, copy, metadata, and hotlinks are replaced or authorized. Preserve the current stack, routes, i18n, auth, payments, analytics, SEO, and deployment conventions. (file: ~/.agents/skills/reference-website-builder/SKILL.md)
```

项目本地安装时可改为：

```markdown
(file: .agents/skills/reference-website-builder/SKILL.md)
```
