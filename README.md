# Agent Tools workflow examples

Free, reusable examples for small AI and automation workflows. We maintain the **paid Apify Actors** linked below. The example code is MIT licensed; running a hosted Actor may incur charges. Check its current price and input limits first.

## Start here

- **vCard import:** [preserve multiple phones, emails and labels](VCF_GUIDE.txt) with the Python adapter in [examples.py](examples.py).
- **Telegram reports:** [prepare ordered text/entities payloads](TELEGRAM_GUIDE.txt) using Python or the [importable n8n workflow](n8n-telegram.json).
- **Troubleshooting:** [HEIC and subtitle input checks](TROUBLESHOOTING.txt).

Download this repository using **Code → Download ZIP**, extract it, and keep the guide and `examples.py` together. For n8n, import `n8n-telegram.json` and configure your own Apify Header Auth credential. The workflow contains synthetic input and no saved credentials. It prepares messages; it does not send them.

## Choose a hosted tool

| Task | Tool |
| --- | --- |
| Preserve repeated contact fields in structured JSON | [VCF to JSON](https://apify.com/creatieve_naald/vcard-to-json) |
| Prepare Markdown as ordered Telegram payloads | [Telegram Message Preparer](https://apify.com/creatieve_naald/telegram-message-preparer) |
| Convert supported single-image HEIC to bounded JPEG | [HEIC to JPEG for AI](https://apify.com/creatieve_naald/heic-to-jpeg-for-ai) |
| Extract subtitle cues and timestamped chunks | [SRT & VTT to JSON](https://apify.com/creatieve_naald/srt-vtt-to-json) |
| Split long text and simple code fences for Discord | [Discord Message Preparer](https://apify.com/creatieve_naald/discord-message-preparer) |

[Agent Tools on Apify](https://apify.com/creatieve_naald). Free local libraries are alternatives when you prefer to maintain your own integration.

## What has been tested

Python adapters were checked using synthetic fixtures and mocked HTTP. The n8n workflow was imported and executed locally with n8n 2.43.8 and fixture responses, including invalid output and HTTP errors. This is **not a verified live Apify-to-n8n-to-Telegram integration** or an approved n8n template-directory listing.

Keep tokens in environment variables or workflow credentials, never in exported JSON or issues. A timed-out request may already have completed: inspect its existing run before retrying. Messaging delivery, ordering, retries and rate limits belong to your sender.

## Support and license

Report example problems here with synthetic reproductions. Report hosted Actor problems on its Apify Issues tab. Remove personal data, API tokens and signed links. Custom integrations and bespoke processing are outside scope.

See [LICENSE.txt](LICENSE.txt) and [RIGHTS.txt](RIGHTS.txt). The license covers original examples and explanations only, not third-party software, trademarks or hosted services. Prepared with AI assistance.
