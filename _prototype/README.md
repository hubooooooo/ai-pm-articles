# 博客首页与视觉方向

直接打开 `index.html` 比较两个方案。无需启动服务，页面没有 CDN、字体或 WebGL 依赖。

- `hero.html`：已选择的 A 方向。博客级主题，连续轴测动画，支持拖动、方向键、展开 / 聚合和播放 / 暂停。
- `editorial.html`：编辑手记，大字排版与带批注的纸页。
- `hero-v1.html`：保留的旧版，仅供对照；它仍需要联网加载 three.js。
- `review/`：实际浏览器渲染截图。

修改 `engineering.template.html` 或 `build_art.py` 后，运行 `python3 build_art.py --site` 更新图解、A 预览和站点资源。共享样式位于 `prototype.css`，交互位于 `prototype.js`。

A 已接入 `_layouts/home.html`。正式首页文章目录读取 `site.posts`，不绑定首篇文章。图解的“观察、场景、实践、复盘、判断、写作”是博客的长期主题。

系统启用减少动态效果时默认暂停；离屏或切到后台会暂停帧循环。B 和旧版保留作设计对照。
