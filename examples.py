"""Two copyable workflow adapters. No network calls on import."""
import json, os, urllib.request
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from pathlib import Path

class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Keep authenticated Actor requests on their original endpoint."""
    def redirect_request(self, *args, **kwargs):
        return None

def call_actor(slug, field, text, price):
    supported = {'vcard-to-json': 'vcard_text', 'telegram-message-preparer': 'markdown'}
    if slug not in supported or field != supported[slug]:
        raise ValueError('Use a supported Actor and its matching input field')
    try:
        cap = Decimal(str(price))
    except InvalidOperation:
        raise ValueError('Use a positive finite run charge cap') from None
    if not cap.is_finite() or cap <= 0:
        raise ValueError('Use a positive finite run charge cap')
    query = urlencode({'memory': 256, 'timeout': 20, 'maxTotalChargeUsd': str(cap)})
    url = f'https://api.apify.com/v2/acts/creatieve_naald~{slug}/run-sync-get-dataset-items?{query}'
    request = urllib.request.Request(url, data=json.dumps({field: text}).encode(), headers={'Authorization': 'Bearer '+os.environ['APIFY_TOKEN'], 'Content-Type': 'application/json'}, method='POST')
    # A timeout can mean the job ran. Never automatically start a replacement job.
    with urllib.request.build_opener(NoRedirect).open(request, timeout=35) as response:
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
