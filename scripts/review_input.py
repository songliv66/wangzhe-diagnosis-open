#!/usr/bin/env python3
"""Offline, deliberately limited questionnaire validation. Does not diagnose play."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

FIELDS = {'nickname', 'peak_rank', 'peak_score', 'roles', 'heroes', 'learn_heroes',
          'goal', 'problems', 'practice_time', 'prior_methods', 'video', 'extra'}
CORE = ['roles', 'goal', 'problems', 'practice_time']


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'重复 JSON 键: {key}')
        result[key] = value
    return result


def load_json(path):
    path = Path(path)
    if path.stat().st_size > 200_000:
        raise ValueError('JSON 文件超过 200 KB')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f'非法数值: {value}')))


def review(data):
    if not isinstance(data, dict) or set(data) - {'case_id', 'answers', 'synthetic'}:
        raise ValueError('顶层仅支持 case_id、answers、synthetic')
    if not isinstance(data.get('case_id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', data['case_id']):
        raise ValueError('case_id 需为 1-64 个英文字母、数字、下划线或短横线')
    if 'synthetic' in data and not isinstance(data['synthetic'], bool):
        raise ValueError('synthetic 必须为布尔值')
    answers = data.get('answers')
    if not isinstance(answers, dict) or not answers or set(answers) - FIELDS:
        raise ValueError('answers 需为非空对象，且只含输入契约允许的字段')
    normalized = {}
    for key, value in answers.items():
        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise ValueError(f'{key} 的列表项必须为字符串')
            value = '；'.join(value)
        if not isinstance(value, str) or len(value) > 8000:
            raise ValueError(f'{key} 必须为不超过 8000 字符的文本或文本列表')
        normalized[key] = value.strip()
    if sum(map(len, normalized.values())) > 30000:
        raise ValueError('问卷文本超过 30000 字符')
    unknown = {'', '不清楚', '未知', '未填', '无答案'}
    missing = [key for key in CORE if normalized.get(key, '') in unknown]
    conflicts = []
    time = normalized.get('practice_time', '')
    if re.search(r'(?:每天|每日)\s*0\s*分', time) and re.search(r'每周\s*(?:[1-9]\d*)\s*(?:小时|h)', time, re.I):
        conflicts.append('练习时间同时写每日 0 分钟与每周非零小时，需确认口径')
    if re.search(r'(?:一把|一次|从未).*没(?:玩|打)过', normalized.get('extra', '')) and normalized.get('peak_rank', '') not in unknown:
        conflicts.append('额外说明与最高段位可能不一致，需确认是历史还是当前情况')
    return {'case_id': data['case_id'], 'status': 'needs_clarification' if missing or conflicts else 'ready_for_model',
            'missing_core_fields': missing, 'conflicts': conflicts,
            'evidence_scope': '仅问卷自述；检查器未读取录像，也不验证答卷真实性',
            'limitations': '自动冲突检查仅覆盖输入契约列出的明确模式，人工仍需核查'}


def review_files(paths):
    seen_ids, seen_content, results = set(), set(), []
    for path in paths:
        data = load_json(path)
        result = review(data)
        digest = hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if result['case_id'] in seen_ids or digest in seen_content:
            raise ValueError(f'重复订单或文件: {result["case_id"]}')
        seen_ids.add(result['case_id']); seen_content.add(digest)
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', nargs='+')
    args = parser.parse_args()
    try:
        print(json.dumps(review_files(args.inputs), ensure_ascii=False, indent=2))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f'输入检查失败: {exc}\n')


if __name__ == '__main__':
    main()
