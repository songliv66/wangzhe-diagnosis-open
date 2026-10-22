# 来源、权利与私有版边界

- 本公开版 v1.0.0 是 2026-10-22 按用户授权独立重写的开源发行版，发布者 songliv66，公开联系 puddingvoid（未指定平台）。根目录 MIT 仅覆盖本次独立编写的代码、说明、问卷及完全合成案例；第三方项按下面各自许可。
- 功能需求来自同一维护者的私有 `wangzhe-diagnosis`。已实时比对默认 main 与个人/归档分支；保留“问卷自述不能冒充录像观察”、三格式交付、独立教练配置的产品边界。原私有包未声明统一开源许可，因此未复制旧渲染器、旧教学材料、个人配置、头像、学生内容或 Git 历史。公开版是新的实现，不能声称与个人版算法、样式或教学内容完全等价。
- 私有版、本机安装与集合副本未被修改。公开仓库不承载私有维护记录、私人来源链接或旧迁移备份。功能来源仅作必要说明，不公开私人分支详情。
- `assets/fonts/DiagnosisSansSC-Regular.ttf`：Google Fonts 官方仓库 `google/fonts` 的 `ofl/notosanssc/NotoSansSC[wght].ttf` 为来源（2026-10-22 下载），使用 FontTools 4.67.0 将 wght 轴实例化为 400，并将字体名称更改为 Diagnosis Sans SC，Copyright 2014-2021 Adobe，按 SIL Open Font License 1.1 分发，完整许可见同目录 `OFL.txt`。字体为常规字重衍生版，已重命名，未把字体重新套 MIT。来源：https://github.com/google/fonts/tree/main/ofl/notosanssc 。PDF 嵌入字体子集由该字体生成。
- ReportLab（BSD）、Pillow（HPND）、pypdf（BSD-3-Clause）和 Poppler（GPL 及其组件许可）作为独立运行依赖，不打包其源码/二进制。各项目的具体版本和许可以安装包为准；调用独立 Poppler 命令不把它复制进发布包。
- 示例 PNG/PDF 均由本次脚本从合成 Markdown 生成，无真人头像、无游戏截图、无第三方诊断图。静态 Demo 使用本地 CSS 与这些产物，不加载外部字体或模型。
- 《王者荣耀》名称用于说明兼容的训练场景；游戏名称及商标归权利人。本项目并非官方产品，不分发游戏资产。一般训练建议不是官方机制文档。
