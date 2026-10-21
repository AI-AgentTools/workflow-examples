"""Validate an exported Actor dataset and emit ordered webhook bodies as NDJSON.

Offline only: no network, credentials or message sending. Validates the complete
batch before writing anything, so malformed later messages cannot yield a partial
send queue. Use a single Actor run's JSON dataset export, not a combined dataset.
"""
import json
import sys
from pathlib import Path


def payloads(data):
    if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], dict):
        raise ValueError('Expected one dataset item from one successful run')
    item = data[0]
    messages = item.get('messages')
    if not isinstance(messages, list) or not 1 <= len(messages) <= 50:
        raise ValueError('Expected 1 to 50 messages')
    if type(item.get('messageCount')) is not int or item['messageCount'] != len(messages):
        raise ValueError('Message count mismatch')
    result = []
    for index, message in enumerate(messages):
        if (not isinstance(message, dict) or type(message.get('index')) is not int
                or message['index'] != index):
            raise ValueError('Messages must have consecutive indexes in order')
        body = message.get('payload')
        if not isinstance(body, dict) or set(body) != {'content', 'allowed_mentions'}:
            raise ValueError('Unexpected payload fields')
        content = body['content']
        if not isinstance(content, str) or not content.strip():
            raise ValueError('Empty or invalid content')
        if len(content.encode('utf-16-le')) // 2 > 2000:
            raise ValueError('Content exceeds conservative Discord limit')
        policy = body['allowed_mentions']
        if (not isinstance(policy, dict) or set(policy) != {'parse', 'replied_user'}
                or policy['parse'] != [] or policy['replied_user'] is not False):
            raise ValueError('Mention protection is missing or changed')
        result.append(body)
    return result


def main():
    if len(sys.argv) != 2:
        raise ValueError('Usage: python3 export_payloads.py dataset.json')
    source = Path(sys.argv[1])
    if source.stat().st_size > 2_000_000:
        raise ValueError('Dataset export is larger than this example supports')
    queue = payloads(json.loads(source.read_text(encoding='utf-8')))
    output = '\n'.join(json.dumps(p, ensure_ascii=False) for p in queue)
    sys.stdout.write(output + '\n')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, UnicodeError) as error:
        # Do not echo source text or full paths into workflow logs.
        print('Invalid dataset or unreadable input; no payloads exported.', file=sys.stderr)
        sys.exit(1)
