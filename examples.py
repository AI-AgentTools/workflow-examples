"""Two copyable workflow adapters. No network calls on import."""
import json, os, urllib.request
from pathlib import Path

def call_actor(slug, field, text, price):
    url = f'https://api.apify.com/v2/acts/creatieve_naald~{slug}/run-sync-get-dataset-items?memory=256&timeout=20&maxTotalChargeUsd={price}'
    request = urllib.request.Request(url, data=json.dumps({field: text}).encode(), headers={'Authorization': 'Bearer '+os.environ['APIFY_TOKEN'], 'Content-Type': 'application/json'}, method='POST')
    # A timeout can mean the job ran. Never automatically start a replacement job.
    with urllib.request.urlopen(request, timeout=35) as response:
        rows = json.load(response)
    if not isinstance(rows,list) or len(rows)!=1 or rows[0].get('schema_version')!='1.0':
        raise ValueError('Unexpected response; inspect existing run before retrying')
    return rows[0]

def contact_rows(envelope):
    """One row/contact, keeping every phone and email in arrays."""
    return [{'name': [x['value'] for x in c['fields']['formatted_names']['items']],
             'phones': [x['value'] for x in c['fields']['phones']['items']],
             'emails': [x['value'] for x in c['fields']['emails']['items']],
             'warnings': c['warnings'], 'original': c} for c in envelope['contacts']]

def telegram_payloads(envelope):
    """Ordered sendMessage body fragments; no bot token/chat ID or sending."""
    messages=envelope['messages']
    if [m['index'] for m in messages]!=list(range(1,len(messages)+1)):
        raise ValueError('Unexpected message order')
    return [{'text': m['text'], 'entities': m['entities']} for m in messages]

# Live VCF workflow (caller supplies token through environment/secret manager):
# result = call_actor('vcard-to-json','vcard_text',Path('contacts.vcf').read_text(encoding='utf-8'),'0.02')
# rows = contact_rows(result)  # map into your destination, after reviewing warnings

# Live Telegram preparation workflow:
# result = call_actor('telegram-message-preparer','markdown',Path('answer.md').read_text(encoding='utf-8'),'0.01')
# payloads = telegram_payloads(result)
# Your sender adds chat_id and posts sequentially to Telegram sendMessage.
# Do not set parse_mode. Handle rate limits/partial delivery in your sender.
