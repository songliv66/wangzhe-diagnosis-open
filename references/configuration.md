# 教练配置与输出

复制 `config/coach.example.json` 到个人文件（建议仓库外），按需修改：

| 键 | 默认 | 说明 |
|---|---|---|
| coach_name | 空 | 报告页脚署名；最多 80 字符 |
| contact | 空 | 联系文本；最多 120 字符，不预设平台 |
| avatar | null | 自有或有权使用的本地 PNG/JPG 文件，最多 5 MB；不接受 URL |
| output_dir | null | 可选输出目录；命令行 `--output-dir` 优先 |
| teaching_sources | [] | 有权使用的资料说明；每项为字符串，供模型读取，不自动拼进学生报告 |

命令行头像路径相对配置文件所在目录；设置 null 时不留空头像框。签名与联系可以同时为空。输出目录相对当前工作目录。CLI 不替你读取本机 Skill 配置，不改安装目录。

`--font PATH` 可换字体，但必须有 TrueType 轮廓且包含报告全部字符，并自行确认嵌入与分发权。默认随包 Diagnosis Sans SC（基于 Noto Sans SC）的 OFL 许可允许使用、嵌入与分发；没有字体时报错，不悄悄用缺字字体。运行依赖 ReportLab、Pillow、pypdf 和外部 `pdftoppm`。macOS 可通过 `brew install poppler`，Ubuntu/Debian 可通过 `sudo apt-get install poppler-utils` 安装；Python 建议 3.10-3.13 虚拟环境。

`--pdftoppm /path/to/pdftoppm` 可指定渲染器。缺 Poppler 时会在创建目录前失败；原始 MD 保持原样。缺依赖同样会报出模块名；运行 `python3 -m pip install -r requirements.txt` 安装到当前虚拟环境。
