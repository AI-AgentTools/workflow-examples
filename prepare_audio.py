"""Explicit opt-in paid Actor example. Install apify-client; set APIFY_TOKEN privately."""
import argparse,os,json,base64
from pathlib import Path
from datetime import timedelta

def main():
    p=argparse.ArgumentParser(description='Upload one audio file and call Audio Chunk Preparer. Hosted usage is paid; local inspection is free.')
    p.add_argument('file',type=Path);mode=p.add_mutually_exclusive_group();mode.add_argument('--submit',action='store_true',help='Authorize upload and Actor call capped at USD0.03');mode.add_argument('--console-json',type=Path,help='Write local Console input for files up to 6,000,000 bytes; no network or token');p.add_argument('--output',type=Path,default=Path('audio-manifest.json'));args=p.parse_args()
    if not args.file.is_file() or not 0<args.file.stat().st_size<=64*1024*1024:raise SystemExit('Use a nonempty file no larger than64MiB')
    if args.file.suffix.lower() not in {'.mp3','.wav','.flac','.ogg'}:raise SystemExit('Supported: mp3,wav,flac,ogg')
    if args.console_json:
        with args.file.open('rb') as f: data=f.read(6_000_001)
        if len(data)>6_000_000:raise SystemExit('Console JSON supports at most 6,000,000 bytes; use the signed upload route for larger files')
        # Exclusive create prevents overwriting the source or an existing input file.
        with args.console_json.open('x') as f:json.dump({'audioBase64':base64.b64encode(data).decode('ascii')},f)
        print('Console JSON saved locally. It contains your audio; keep it private. No network call.');return
    if not args.submit:
        print('Local file check passed. No network call. Add --submit to upload and run (USD0.03 event cap).');return
    from apify_client import ApifyClient
    c=ApifyClient(os.environ['APIFY_TOKEN'])
    store=c.key_value_stores().get_or_create() # unnamed source storage, ordinary account retention
    with args.file.open('rb') as f:c.key_value_store(store.id).set_record('source'+args.file.suffix.lower(),f,content_type='application/octet-stream')
    signed=c.key_value_store(store.id).get_record_public_url('source'+args.file.suffix.lower())
    r=c.actor('creatieve_naald/audio-chunk-preparer').call(run_input={'audioFiles':[signed]},max_total_charge_usd=0.03,run_timeout=timedelta(seconds=180),memory_mbytes=1024)
    if not r or str(r.status)!='SUCCEEDED':raise SystemExit('Run failed. Inspect error code in your Apify Console; do not blindly retry.')
    rows=c.dataset(r.default_dataset_id).list_items().items
    if len(rows)!=1:raise SystemExit('Unexpected manifest count')
    args.output.write_text(json.dumps({'sourceStoreId':store.id,'outputStoreId':r.default_key_value_store_id,'manifest':rows[0]},indent=2)+'\n')
    print('Manifest saved. Download each recordKey from outputStoreId with your own authenticated client. Manage source/output retention in your Apify account.')
if __name__=='__main__':main()
