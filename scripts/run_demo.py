#!/usr/bin/env python3
"""Regenerate all synthetic demo reports. Authored case text is not model output."""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
from render_report import ROOT, render
from review_input import review_files


def run(output, pdftoppm=None):
    target = Path(output)
    if target.exists():
        raise ValueError('Demo 输出目录已存在；请选择新目录，原文件不会覆盖')
    cases = sorted(path.parent for path in (ROOT / 'examples').glob('*/input.json'))
    reviews = review_files([path / 'input.json' for path in cases])
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.demo-stage-', dir=target.parent) as temp:
        stage = Path(temp)
        for path, review in zip(cases, reviews):
            folder = stage / path.name
            render(path / 'report.md', folder, ROOT / 'config/coach.example.json', path.name, pdftoppm=pdftoppm)
            (folder / 'input-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (stage / 'DEMO-NOTICE.txt').write_text('所有输入为合成；诊断为预写模拟答复；本次实际执行输入检查与三格式排版，无模型和网络调用。\n', encoding='utf-8')
        os.mkdir(target)
        try:
            for item in stage.iterdir():
                if item.is_dir():
                    shutil.copytree(item, target / item.name)
                else:
                    shutil.copyfile(item, target / item.name)
        except BaseException:
            shutil.rmtree(target)
            raise
    return len(cases)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--pdftoppm')
    args = parser.parse_args()
    try:
        print(f'完成 {run(args.output_dir, args.pdftoppm)} 个合成案例；输出: {args.output_dir}')
    except (OSError, ValueError) as exc:
        parser.exit(2, f'Demo 失败: {exc}\n')
