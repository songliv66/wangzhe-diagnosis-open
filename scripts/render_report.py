#!/usr/bin/env python3
"""Render authored Markdown into a selectable Chinese PDF and its 2160 px PNG.
No model, network access, diagnostic inference, or existing-output replacement.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT = ROOT / 'assets/fonts/DiagnosisSansSC-Regular.ttf'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get_dependencies():
    try:
        import reportlab
        import PIL
        import pypdf
        return reportlab, PIL, pypdf
    except ImportError as exc:
        raise ValueError(f'缺少 Python 依赖 {exc.name}；请在虚拟环境安装 requirements.txt') from exc


def load_profile(path):
    if path is None:
        return {'coach_name': '', 'contact': '', 'avatar': None, 'output_dir': None, 'teaching_sources': []}
    from review_input import load_json
    profile = load_json(path)
    keys = {'coach_name', 'contact', 'avatar', 'output_dir', 'teaching_sources'}
    if not isinstance(profile, dict) or set(profile) - keys:
        raise ValueError('配置包含不支持的字段')
    for key, limit in [('coach_name', 80), ('contact', 120)]:
        if not isinstance(profile.get(key, ''), str) or len(profile.get(key, '')) > limit:
            raise ValueError(f'配置 {key} 类型或长度错误')
    if profile.get('output_dir') is not None and not isinstance(profile['output_dir'], str):
        raise ValueError('output_dir 需为字符串或 null')
    sources = profile.get('teaching_sources', [])
    if not isinstance(sources, list) or not all(isinstance(s, str) and len(s) < 4000 for s in sources):
        raise ValueError('teaching_sources 必须为文本列表')
    avatar = profile.get('avatar')
    if avatar is not None:
        if not isinstance(avatar, str) or '://' in avatar:
            raise ValueError('头像必须为本地 PNG/JPG 路径')
        avatar = Path(path).resolve().parent / avatar
        if not avatar.is_file() or avatar.stat().st_size > 5_000_000:
            raise ValueError('头像缺失或超过 5 MB')
        from PIL import Image
        with Image.open(avatar) as image:
            if image.format not in {'PNG', 'JPEG'} or image.width * image.height > 20_000_000:
                raise ValueError('头像需为不超过 2000 万像素的 PNG/JPG')
            image.verify()
        profile['avatar'] = str(avatar)
    return profile


def markdown_blocks(text):
    """Supported Markdown is intentionally small; all remaining markup is literal."""
    result, paragraph = [], []
    def flush():
        if paragraph:
            result.append(('body', '\n'.join(paragraph)))
            paragraph.clear()
    for line in text.splitlines():
        if not line.strip():
            flush()
        elif line.startswith('# '):
            flush(); result.append(('title', line[2:].strip()))
        elif line.startswith('## '):
            flush(); result.append(('section', line[3:].strip()))
        elif line.startswith('### '):
            flush(); result.append(('sub', line[4:].strip()))
        elif line.startswith('- '):
            flush(); result.append(('bullet', '• ' + line[2:].strip()))
        else:
            paragraph.append(line.strip())
    flush()
    return result


def ensure_coverage(font, text):
    from reportlab.pdfbase.ttfonts import TTFont
    try:
        registered = TTFont('DiagnosisSC', str(font))
    except Exception as exc:
        raise ValueError(f'字体无法加载（需要 TrueType 轮廓）: {font.name}') from exc
    absent = sorted({char for char in text if not char.isspace() and ord(char) not in registered.face.charToGlyph})
    if absent:
        raise ValueError('字体缺少字符: ' + ''.join(absent[:30]))
    from reportlab.pdfbase import pdfmetrics
    pdfmetrics.registerFont(registered)


def create_pdf(text, profile, font, destination, order_id):
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor
    width, margin, leading = 720, 50, 23
    contact = profile.get('contact', '')
    coach = profile.get('coach_name', '')
    footer = ' · '.join(value for value in [coach, contact] if value)
    ensure_coverage(font, text + footer + '王者问卷诊断 · ' + order_id + '•')
    styles = {
        'title': ParagraphStyle('title', fontName='DiagnosisSC', fontSize=25, leading=36, textColor=HexColor('#12352f'), wordWrap='CJK'),
        'section': ParagraphStyle('section', fontName='DiagnosisSC', fontSize=17, leading=27, textColor=HexColor('#126f60'), wordWrap='CJK'),
        'sub': ParagraphStyle('sub', fontName='DiagnosisSC', fontSize=14, leading=24, textColor=HexColor('#12352f'), wordWrap='CJK'),
        'body': ParagraphStyle('body', fontName='DiagnosisSC', fontSize=12.3, leading=leading, textColor=HexColor('#263c39'), wordWrap='CJK'),
        'bullet': ParagraphStyle('bullet', fontName='DiagnosisSC', fontSize=12.3, leading=leading, leftIndent=10, textColor=HexColor('#263c39'), wordWrap='CJK')}
    flowables = []
    content_height = 0
    for kind, value in markdown_blocks(text):
        paragraph = Paragraph(escape(value).replace('\n', '<br/>'), styles[kind])
        _, h = paragraph.wrap(width - 2 * margin, 14000)
        gap = {'title': 26, 'section': 17, 'sub': 10, 'body': 12, 'bullet': 8}[kind]
        flowables.append((paragraph, h, gap))
        content_height += h + gap
    footer_x = margin + 56 if profile.get('avatar') else margin
    footer_paragraph = Paragraph(escape(footer), styles['body']) if footer else None
    footer_height = footer_paragraph.wrap(width - footer_x - margin, 1000)[1] if footer_paragraph else 0
    height = max(720, content_height + 190 + max(footer_height, 48 if profile.get('avatar') else 0))
    if height > 14000:
        raise ValueError('报告过长，需拆分为多个报告后导出')
    canvas = Canvas(str(destination), pagesize=(width, height), pageCompression=1)
    canvas.setTitle('王者问卷诊断 - ' + order_id)
    canvas.setAuthor(coach)
    canvas.setFillColor(HexColor('#f4f7f4')); canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(HexColor('#ffffff')); canvas.roundRect(25, 25, width - 50, height - 50, 14, fill=1, stroke=0)
    canvas.setFillColor(HexColor('#157c67')); canvas.rect(50, height - 48, 62, 4, fill=1, stroke=0)
    canvas.setFont('DiagnosisSC', 9); canvas.setFillColor(HexColor('#56726c'))
    canvas.drawString(margin, height - 69, '王者问卷诊断 · ' + order_id)
    y = height - 95
    for paragraph, h, gap in flowables:
        paragraph.drawOn(canvas, margin, y - h)
        y -= h + gap
    canvas.setStrokeColor(HexColor('#dce8e2')); canvas.line(margin, y - 8, width - margin, y - 8)
    y -= 38
    if profile.get('avatar'):
        from reportlab.lib.utils import ImageReader
        canvas.drawImage(ImageReader(profile['avatar']), margin, y - 26, width=42, height=42, preserveAspectRatio=True, mask='auto')
        footer_x = margin + 56
    else:
        footer_x = margin
    if footer:
        footer_paragraph.drawOn(canvas, footer_x, y - footer_height + 12)
    canvas.save()


def render(source, output_dir=None, profile_path=None, order_id='anonymous', font=None, pdftoppm=None):
    reportlab, PIL, pypdf = get_dependencies()
    from PIL import Image
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', order_id):
        raise ValueError('order-id 仅允许 1-64 位英文字母、数字、下划线、短横线')
    source = Path(source)
    if source.suffix.lower() != '.md' or not source.is_file() or source.stat().st_size > 200_000:
        raise ValueError('输入必须为不超过 200 KB 的 Markdown 文件')
    text = source.read_text(encoding='utf-8')
    if not text.strip() or len(text) > 30000 or any(ord(c) < 32 and c not in '\n\r\t' for c in text):
        raise ValueError('报告需为 1-30000 字符，不含不支持的控制字符')
    profile = load_profile(profile_path)
    chosen_dir = output_dir or profile.get('output_dir')
    if not chosen_dir:
        raise ValueError('请通过 --output-dir 或配置选择新的输出目录')
    output = Path(chosen_dir)
    if output.exists():
        raise ValueError('输出目录已存在；为保护已有文件，请选择新目录')
    font = Path(font) if font else DEFAULT_FONT
    if not font.is_file():
        raise ValueError('中文字体缺失；请恢复 assets/fonts 或用 --font 指定获授权字体')
    renderer = str(pdftoppm) if pdftoppm else shutil.which('pdftoppm')
    if not renderer or not Path(renderer).is_file():
        raise ValueError('缺少 pdftoppm；安装 Poppler，或使用 --pdftoppm 指定路径')
    # Preflight before creating outputs. Temporary artifacts are removed on any failure.
    version = subprocess.run([renderer, '-v'], capture_output=True, text=True, timeout=15)
    if version.returncode:
        raise ValueError('pdftoppm 无法执行')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.diagnosis-stage-', dir=output.parent) as temp:
        stage = Path(temp)
        (stage / 'report.md').write_text(text, encoding='utf-8')
        create_pdf(text, profile, font, stage / 'report.pdf', order_id)
        subprocess.run([renderer, '-f', '1', '-singlefile', '-scale-to-x', '2160', '-scale-to-y', '-1', '-png',
                        str(stage / 'report.pdf'), str(stage / 'report')], check=True, capture_output=True, timeout=120)
        pdf_text = ''.join(page.extract_text() or '' for page in pypdf.PdfReader(stage / 'report.pdf').pages)
        normalized = lambda value: ''.join(value.split()).replace('•', '')
        expected = normalized(''.join(value for _, value in markdown_blocks(text)))
        if expected not in normalized(pdf_text):
            raise ValueError('PDF 文字提取未完整覆盖正文，未交付输出')
        with Image.open(stage / 'report.png') as image:
            if image.width != 2160 or image.height < 2160:
                raise ValueError('PNG 尺寸异常')
            dimensions = [image.width, image.height]
        manifest = {
            'format_version': 1, 'order_id': order_id, 'created_utc': datetime.now(timezone.utc).isoformat(),
            'source_sha256': sha(source), 'profile_sha256': sha(profile_path) if profile_path else None,
            'font_sha256': sha(font), 'png_size': dimensions, 'pdf_text_coverage': True,
            'diagnosis_origin': '模型或教练预先撰写；本工具仅排版，不自动诊断',
            'versions': {'python': sys.version.split()[0], 'reportlab': reportlab.Version,
                         'pillow': PIL.__version__, 'pypdf': pypdf.__version__},
            'files': {name: {'bytes': (stage / name).stat().st_size, 'sha256': sha(stage / name)}
                      for name in ['report.md', 'report.pdf', 'report.png']}}
        (stage / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        # Claim destination exclusively; even a concurrent creator is never overwritten.
        os.mkdir(output)
        try:
            for item in stage.iterdir():
                with item.open('rb') as source_stream, (output / item.name).open('xb') as destination:
                    shutil.copyfileobj(source_stream, destination)
        except BaseException:
            shutil.rmtree(output)
            raise
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('markdown')
    parser.add_argument('--output-dir')
    parser.add_argument('--profile')
    parser.add_argument('--order-id', default='anonymous')
    parser.add_argument('--font')
    parser.add_argument('--pdftoppm')
    args = parser.parse_args()
    try:
        manifest = render(args.markdown, args.output_dir, args.profile, args.order_id, args.font, args.pdftoppm)
        print(json.dumps({'output_dir': args.output_dir, 'png_size': manifest['png_size'], 'pdf_text_coverage': True}, ensure_ascii=False))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f'导出失败: {exc}\n')


if __name__ == '__main__':
    main()
