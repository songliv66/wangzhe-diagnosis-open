#!/usr/bin/env python3
"""Verify exported files and optionally detect a changed Markdown source."""
import argparse
import json
from pathlib import Path
from render_report import sha


def check(directory, source=None):
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    if set(manifest['files']) != {'report.md', 'report.pdf', 'report.png'}:
        raise ValueError('manifest 的文件清单不受支持')
    for name, expected in manifest['files'].items():
        path = directory/name
        if sha(path) != expected['sha256'] or path.stat().st_size != expected['bytes']:
            raise ValueError(f'文件已变化或损坏: {name}')
    if source and sha(source) != manifest['source_sha256']:
        raise ValueError('原始 Markdown 已改变；旧产物已不对应当前正文，请导出到新目录')
    from PIL import Image
    from pypdf import PdfReader
    with Image.open(directory/'report.png') as image:
        if list(image.size) != manifest['png_size'] or image.width != 2160:
            raise ValueError('PNG 尺寸不符')
    if not ''.join(page.extract_text() or '' for page in PdfReader(directory/'report.pdf').pages).strip():
        raise ValueError('PDF 无可提取文字')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory'); parser.add_argument('--source')
    args = parser.parse_args()
    try:
        check(args.directory, args.source)
        print('文件哈希、大小、PNG 尺寸及 PDF 文字检查通过；不替代视觉与教学审核。')
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f'校验失败: {exc}\n')
