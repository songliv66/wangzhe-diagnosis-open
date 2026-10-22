# v1.0.0 本机验收 · 2026-10-22

## 实际完成

- macOS、Python 3.12；ReportLab 4.4.9、Pillow 12.3.0、pypdf 6.10.0；Poppler `pdftoppm` 真实光栅化。
- 运行 `python3 -m unittest discover -s tests -v`，13 项全部通过，0 跳过。覆盖核心缺失与时间冲突、非法类型/字段/长度、重复 JSON 键与重复订单、问卷指令只作为文本、已有目录与重复运行不覆盖、依赖/字体/渲染器缺失、字体缺字、远程头像拒绝、本地可选合成头像与长署名/联系、文件损坏及原 Markdown 修改后的失效提示。
- 真实导出三份示例；不是只检查脚本存在。三份 PDF 都有可提取的完整正文；同源 PNG 尺寸分别为 2160×3633、2160×3666、2160×3522。MD 与作者正文一致，manifest 的大小和 SHA-256 再次核对通过。
- 查看三份完整 PNG，正文、标题、列表和页脚无缺字、重叠或裁切；另查看有效长度上限内的长署名/联系与可选合成头像输出，页脚留在画布内。字体为常规 400 字重，非变量字体默认 Thin。
- 本机浏览器实际打开静态 Demo，检查首屏和报告预览，点击展开合成问卷；入口和 28 个页面资源/链接的本地部分均可定位。README 中附真实浏览器截图。没有模型请求、表单收集或外部字体加载。
- Skill 创建器 `quick_validate.py` 通过；待公开文本的内部绝对路径、凭证模式扫描没有命中，包内不含旧 .git、个人配置或真实学生资料。

## 这些结果的范围

诊断正文和追问对话为作者预写的合成模拟答复；本次脚本运行证明机械核查与排版功能，不证明某个模型的诊断准确率或实际教学效果。独立试用与公开部署、远端提交、Release ZIP 的验证由发布阶段另行记录，不能从本机结果推定。

Windows 未实测。测试与视觉检查不覆盖每一种字体、超长内容和配置组合，也不验证问卷真实性或当前游戏机制。13 项是行为风险测试数量，不是学生样本数。

## 自行复验

先安装 README 中的 Python 依赖与 Poppler，然后运行：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/run_demo.py --output-dir outputs/demo-verification
python3 scripts/check_output.py outputs/demo-verification/01-beginner --source examples/01-beginner/report.md
```

输出目录必须尚不存在。发布包中的生成结果可直接浏览；复跑会生成新的指纹与时间记录。CI 文件仅是手动启用示例，本机通过不等于 GitHub Actions 已通过。
