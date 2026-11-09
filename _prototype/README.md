# 博客首页与历史视觉方向

当前首页使用真正的三维机械手模型、透视相机、轮廓线与真实遮挡。打开 `hands-3d.html`、`hands.html` 或 `hero.html` 可查看同一版本。

- 首屏以“让想法相遇”为主标题，配有简短英文、淡纸纹、细线与少量绿色；没有介绍段落、工程标注或场景控制面板。
- 首页与文章页共用 `assets/css/palette.css`：深绿用于浅色界面的文字和交互，亮绿用于三维局部轮廓与指尖信号。深色模式采用更亮的绿色，纸面底色和正文颜色独立保留。
- 三维机械手仅在食指中末节及腕部使用绿色轮廓，表面仍为纸色；绿色随真实关节和相机移动，保留遮挡关系。
- 桌面页眉显示 AI PRODUCT NOTES，中央为 WHERE IDEAS MEET.；底部 EXPLORE NOTES 跳转到文章目录。手机隐藏页眉英文以保留空间。
- 导航透明叠在首屏上方，三维画布从页面顶部开始，机械手不再被单独的页眉区域截断。导航的空白区域不拦截场景交互。
- 两手缓慢轻触并活动关节，鼠标移动带有轻微相机视差。
- 减少动态效果时停止自动播放；离屏或后台暂停渲染。
- 无 WebGL 时显示同一场景渲染的三维静帧，分别适配桌面、手机与深浅色。

源文件和构建说明在 `three-hands/README.md`。正式资源是 `assets/js/hands-3d.js`、`assets/css/hands-3d.css` 和 `assets/images/hands-3d-*.png`。原始三维资产及许可保留在 `three-hands/vendor/shadow_hand/`，公开许可副本位于 `assets/licenses/`。

首页模板位于 `_layouts/home.html`，文章目录读取 `site.posts`。文章正文与链接保持独立。

`build_hands.py`、`hands.svg`、`hands.template.html` 是旧二维方案；`build_art.py` 与 `engineering.template.html` 是历史装置方案，均不再用于当前首页。`editorial.html` 和 `hero-v1.html` 仅保留作对照。

`review/` 保存实际浏览器截图、动效预览与验证结果。
