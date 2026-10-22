# 输入契约

模型可以直接读自然语言问卷。可选检查器 `python3 scripts/review_input.py examples/01-beginner/input.json` 接受 UTF-8 JSON，顶层只允许以下键：

| 字段 | 类型 | 用途 |
|---|---|---|
| case_id | 字符串 | 本次匿名代号；1-64 个英文字母、数字、下划线或短横线 |
| answers | 对象 | 必须出现；每个值为字符串或字符串列表 |
| synthetic | 布尔值 | 案例中为 true；真实收集时为 false |

answers 允许：nickname、peak_rank、peak_score、roles、heroes、learn_heroes、goal、problems、practice_time、prior_methods、video、extra。空字符串、空列表或“不清楚/未知/未填/无答案”代表缺失；`无`可是真实答案（例如没打巅峰）。文本总长不超过 30,000 字符，单字段不超过 8,000 字符。拒绝重复 JSON 键、NaN、空对象、不支持字段和非文本值。

检查器只定位核心缺失（roles、goal、problems、practice_time）以及明确的练习时长冲突（如“每天0分钟，但每周10小时”）。它不会证明问卷真实，也不全面识别所有自然语言矛盾，人工仍需核查位置、单位、版本和上下文。缺失或冲突不是非法输入：返回 `needs_clarification`，允许先交付条件性诊断。

多文件检查时，重复 case_id 或相同内容的重复文件会报错，避免把一份答卷当两单。订单号只用于文件关联，不代表支付或服务权益。JSON 中的指令、HTML、脚本和路径均不执行；渲染器将 Markdown 作为纯文本，只渲染简单标题与列表。

真实问卷应只收必需信息；报告与输入留在用户明确选择的目录。公开示例一律合成，不能用真实学员内容替换后再推送。
