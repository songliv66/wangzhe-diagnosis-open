# 中文字体

文件 `DiagnosisSansSC-Regular.ttf` 为本发行版所附的 OFL 字体衍生版，SHA-256：`b4f4fad746997165bf9c2189f7d52c49aea0645276e654e471d8751d60932d75`。

来源为 [Google Fonts 的 Noto Sans SC](https://github.com/google/fonts/tree/2894aab31764f10f29c421bdfd2340d3b382d384/ofl/notosanssc)，原路径 `ofl/notosanssc/NotoSansSC[wght].ttf`。Copyright 2014-2021 Adobe，Reserved Font Name 为 Source。完整 [SIL OFL 1.1](OFL.txt) 随包保留，字体不适用根目录 MIT。

2026-10-22 的构建变更：使用 FontTools 4.67.0 的 `instantiateVariableFont(font, {'wght': 400}, inplace=False)` 固定常规字重；name 表 1/4/6/16/17 字段分别改为 Diagnosis Sans SC、Diagnosis Sans SC Regular、DiagnosisSansSC-Regular、Diagnosis Sans SC、Regular。未改字形含义。它避免源变量字体默认 Thin 字重导致报告过细。FontTools 仅构建时使用，不是用户运行依赖。

此字体用于 PDF 嵌入与 PNG 光栅化，不加载系统字体或远程 CDN。替换字体前需确认中文覆盖、嵌入权和分发权。
