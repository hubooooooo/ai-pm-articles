# 博客首页与历史视觉方向

当前首页改为左右两只线稿机械手，在中央轻触。直接打开 `hands.html` 或 `hero.html` 查看，无需服务或外部依赖。

- 中央仅保留“让想法相遇”，没有工程标注、介绍段落或图解控制面板。
- 两手自动缓慢靠近、触碰、回弹。支持系统减少动态效果；离屏和后台暂停。
- 运行 `python3 build_hands.py` 更新 SVG、预览与 `_includes/home-hands.html`。
- 正式资源为 `assets/css/home-hands.css` 和 `assets/js/home-hands.js`。

历史方案保留作对照：

- `engineering.template.html`：此前的精密装置方案。
- `editorial.html`：编辑手记，大字排版与带批注的纸页。
- `hero-v1.html`：保留的旧版，仅供对照；它仍需要联网加载 three.js。
- `review/`：实际浏览器渲染截图。

历史装置方案的源文件为 `engineering.template.html`、`build_art.py`、`prototype.css` 和 `prototype.js`，不再用于当前首页。

首页位于 `_layouts/home.html`，文章目录继续读取 `site.posts`，不绑定首篇文章。

系统启用减少动态效果时显示静态触碰姿态；离屏或切到后台会暂停动画。B 和旧版保留作设计对照。
