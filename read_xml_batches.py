"""Read an existing XML Record Batcher result; never starts an Actor.

Local: python read_xml_batches.py --directory downloaded-result > records.ndjson
Cloud: APIFY_TOKEN=... python read_xml_batches.py --run-id RUN_ID > records.ndjson
All batches are verified on temporary disk before any records reach stdout.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.request

MIB = 1024 * 1024
ACTOR_ID = 'iLm02Ogdc0Gqe0ByV'


class InvalidResult(ValueError):
    pass


def positive(value, limit):
    if type(value) is not int or not 1 <= value <= limit:
        raise InvalidResult('Invalid count or size')
    return value


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or manifest.get('schemaVersion') != 1:
        raise InvalidResult('Unsupported manifest')
    positive(manifest.get('records'), 100000)
    positive(manifest.get('outputBytes'), 220 * MIB)
    parts = manifest.get('batches')
    if not isinstance(parts, list) or not 1 <= len(parts) <= 1000:
        raise InvalidResult('Invalid batch list')
    keys = set()
    for part in parts:
        if not isinstance(part, dict):
            raise InvalidResult('Invalid batch')
        key = part.get('recordKey')
        if not isinstance(key, str) or not re.fullmatch(r'batch-\d{4}\.ndjson', key) or key in keys:
            raise InvalidResult('Invalid or repeated batch key')
        keys.add(key)
        positive(part.get('bytes'), MIB)
        positive(part.get('records'), 100000)
        if not isinstance(part.get('sha256'), str) or not re.fullmatch('[a-f0-9]{64}', part['sha256']):
            raise InvalidResult('Invalid digest')
    if sum(p['bytes'] for p in parts) != manifest['outputBytes'] or sum(p['records'] for p in parts) != manifest['records']:
        raise InvalidResult('Manifest totals disagree')
    return parts


def stage(manifest, fetch, destination):
    parts = validate_manifest(manifest)
    expected_index = 1
    for part in parts:
        raw = fetch(part['recordKey'])
        if not isinstance(raw, bytes) or len(raw) != part['bytes'] or hashlib.sha256(raw).hexdigest() != part['sha256']:
            raise InvalidResult('Batch size or digest mismatch')
        if not raw.endswith(b'\n'):
            raise InvalidResult('Batch must end with a newline')
        rows = raw.splitlines()
        if len(rows) != part['records']:
            raise InvalidResult('Batch count mismatch')
        for line in rows:
            row = json.loads(line)
            if not isinstance(row, dict) or type(row.get('index')) is not int or row['index'] != expected_index or not isinstance(row.get('element'), dict):
                raise InvalidResult('Record order or envelope mismatch')
            expected_index += 1
        destination.write(raw)
    return expected_index - 1


def bounded_read(stream):
    raw = stream.read(MIB + 1)
    if len(raw) > MIB:
        raise InvalidResult('Record exceeds 1 MiB')
    return raw


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def get_json_bytes(path, token):
    # path is assembled only from validated Apify IDs and manifest record keys.
    request = urllib.request.Request('https://api.apify.com/v2/' + path,
                                     headers={'Authorization': 'Bearer ' + token})
    with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
        return bounded_read(response)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--directory', type=Path)
    group.add_argument('--run-id')
    args = parser.parse_args(argv)
    if args.directory:
        def fetch(key):
            with (args.directory / key).open('rb') as stream:
                return bounded_read(stream)
        manifest = json.loads(fetch('manifest.json'))
    else:
        if not re.fullmatch('[A-Za-z0-9]{17}', args.run_id):
            raise InvalidResult('Invalid run ID')
        token = os.environ.get('APIFY_TOKEN')
        if not token:
            raise InvalidResult('Set APIFY_TOKEN in your environment')
        run = json.loads(get_json_bytes('actor-runs/' + args.run_id, token))['data']
        if run.get('status') != 'SUCCEEDED' or run.get('actId') != ACTOR_ID:
            raise InvalidResult('Use a successful XML Record Batcher run')
        store_id = run.get('defaultKeyValueStoreId', '')
        if not re.fullmatch('[A-Za-z0-9]{17}', store_id):
            raise InvalidResult('Invalid result store')
        def fetch(key):
            return get_json_bytes('key-value-stores/' + store_id + '/records/' + key, token)
        manifest = json.loads(fetch('OUTPUT'))
    # Disk staging prevents malformed later batches producing partial stdout.
    # Up to 220 MiB temporary disk; process memory holds one batch at a time.
    with tempfile.TemporaryFile() as staged:
        count = stage(manifest, fetch, staged)
        staged.seek(0)
        shutil.copyfileobj(staged, sys.stdout.buffer, length=65536)
    print(f'Validated {count} records; no Actor started.', file=sys.stderr)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Network errors may contain sensitive request context. Do not echo them.
        print('Could not validate result. Check run status, access, retention and manifest integrity.', file=sys.stderr)
        sys.exit(1)
