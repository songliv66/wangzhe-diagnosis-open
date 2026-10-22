# 已有玩家：把辅助游走从结果复盘改为信息复盘

本例所有资料为合成。

1. 复制 [提示词](prompt.txt)，把 [原始答卷](input.json) 交给模型。
2. 对照 [核查与追问示范](clarification.md)，注意真实模型可提出不同但合理的问题。
3. [预写诊断](report.md) 是本项目作者模拟的答复；脚本不会从答卷自动生成这段分析。
4. [实际排版成果](output/) 包含 MD、可选择文字的 PDF、2160 像素 PNG 和指纹。

可单例运行（在仓库根，输出目录须不存在）：

```bash
python3 scripts/render_report.py examples/02-bottleneck/report.md --output-dir outputs/02-bottleneck --profile config/coach.example.json --order-id 02-bottleneck
```
