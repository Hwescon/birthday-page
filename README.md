# 星屑成诗 · 生日快乐

一个单文件（HTML + CSS + JS 全内联）的生日表白页：粒子星河、烟花、手势识别（比 4→3→2→1 再握拳）、愿望蛋糕、照片与文字、内置旋律。

打开即用，不需要构建、不需要装依赖、不需要服务器。

## 直接使用

| 方式 | 做法 |
|---|---|
| 双击打开 | 下载仓库，双击 `index.html`（推荐 Chrome / Edge） |
| 在线看 | https://hwescon.github.io/birthday-page/ |

- 首屏点「开启摄像头」用真实手势互动，点「无摄像头预览」用鼠标/触摸预览。
- 手势识别需要摄像头权限；画面只在本机处理，不上传任何图像。
- 页面数据（改过的文案、导入的音乐、添加的照片）只存在本机浏览器里。

## 浏览器要求

现代 Chrome / Edge / Safari（需 WebGL + ES Module）。手机浏览器同样可用。

联网会被用来加载：

- Three.js r187（jsDelivr，失败自动切 unpkg → esm.sh）
- MediaPipe 手势识别库与模型（jsDelivr / unpkg + Google 官方模型源），只在点「开启摄像头」时才加载

## 和原版「封装版」的差异

原始文件 `生日页面-封装版.html` 原样保留在仓库里，未作任何改动。`index.html` 是在它基础上做的最小修复（脚本见 `tools/patch.py`，幂等，可重跑）：

| 问题 | 原版状态 | 现在 |
|---|---|---|
| 字体 | 7 个 `@font-face` 指向 `dazzling-dodol-e84320.netlify.app`，**全部 404**，回退系统字体 | 改指 fontsource on jsDelivr（Cormorant Garamond / Manrope，均已验证 200 + CORS `*`） |
| 背景音乐 | 8 首 mp3 同在已失效的 netlify 部署上，**全部 404**，设置面板显示「音频加载失败」 | 改为运行时用 WebAudio 数据的纯 JS 合成《生日快乐》旋律（13 秒 WAV，blob 直读），零外部文件、零版权素材；仍可「导入音乐」换成本机 MP3 |
| 手势模型镜像 | 首选 netlify 死链，靠 Google 官方地址兜底（会先白等一次 404） | 删掉死链，直接用 Google 官方模型地址 |
| Three.js | 单源 jsDelivr | 三源自动探测：jsDelivr → unpkg → esm.sh |
| 文案提示 | 「默认是第一首 Happy Birthday to You」 | 同步为内置旋律说明 |

除以上几处，页面结构、样式、动画、交互逻辑一行未动。

## 目录

```
.
├── index.html              # 修好的成品，Pages 首页
├── 生日页面-封装版.html       # 原始文件，字节级未改动，作为原版备份
├── tools/patch.py          # 由原版生成 index.html 的补丁脚本（可复现）
├── .nojekyll               # 跳过 Jekyll
└── README.md
```

`index.html` 与 `生日页面-封装版.html` 的关系：后者是输入，前者是 `python tools/patch.py` 的输出。想验证或重做，直接跑脚本。

## 换成你自己的名字 / 文案

定制内容不在正文里，而在 `<script id="q8">` 里的一段 base64 JSON：

```json
{"name":"星屑成诗","title":"生日快乐","lead":"当指针靠近时，粒子便有了心事。\n请把手交给我，让它替代你看星星。","age":"新的一岁","finale":"生日快乐","note":"愿你如愿，皆成真。"}
```

改法：把 JSON 改好 → base64 编码 → 替换 `<script id="q8" type="application/octet-stream">` 里的那串字符。命令行一行搞定（Python）：

```bash
python -c "import base64,json;print(base64.b64encode(json.dumps({'name':'小美','title':'生日快乐','lead':'','age':'十八岁','finale':'生日快乐','note':'愿你如愿'},ensure_ascii=False).encode()).decode())"
```

页面里「仪式文字」那一栏也能改首屏标题、引导语、年龄、蛋糕文字等内容，改完会存在本机浏览器。

## 部署

GitHub Pages 已开（`main` / `/`）。仓库 Settings → Pages 可改域名或用自定义域。

其它静态托管直接拖这个文件就行：Vercel、Netlify、Cloudflare Pages、任意对象存储 + CDN。
