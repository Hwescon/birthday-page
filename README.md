# 星屑成诗 · 生日快乐

一个单文件（HTML + CSS + JS 全内联）的生日表白页面。打开即用，无需构建、无需依赖。

## 预览

- 入口文件：`index.html`（GitHub Pages 默认首页）
- 原始文件：`生日页面-封装版.html`（内容与 `index.html` 完全一致，保留原名便于归档）

## 本地运行

直接双击 `index.html`，或起一个静态服务器：

```bash
python -m http.server 8080
# 浏览器打开 http://127.0.0.1:8080
```

## 部署到 GitHub Pages

1. 仓库 Settings → Pages
2. Source 选择 `Deploy from a branch`
3. Branch 选 `main`，目录选 `/ (root)`
4. 保存后访问 `https://<你的用户名>.github.io/<仓库名>/`

`.nojekyll` 已放置，用于跳过 Jekyll 处理，保证静态资源按原样发布。

## 目录结构

```
.
├── index.html            # 页面入口
├── 生日页面-封装版.html     # 原始文件（同内容）
├── .nojekyll             # 跳过 Jekyll
└── README.md
```

## 说明

- 字体通过 CDN（woff2）加载，离线环境下会回退到系统字体，动画与布局不受影响。
- 页面为自包含单文件，适合直接分享，也适合挂到任意静态托管（Vercel / Netlify / Cloudflare Pages）。
