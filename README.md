# Agent Tools — file and message APIs for automated workflows

Free, reusable examples for small AI and automation workflows. We maintain the **paid Apify Actors** linked below. The example code is MIT licensed; running a hosted Actor may incur charges. Check its current price and input limits first.

**Turn awkward files and long messages into structured inputs your next workflow step can use.** Agent Tools provides small, bounded processing APIs on Apify, with reusable Python and n8n examples.

## Files stuck inside winmail.dat?

[Extract the attachments with Winmail.dat Attachment Extractor](https://apify.com/creatieve_naald/winmail-dat-extractor) — **USD 0.03 per successfully extracted input file**, not per attachment. No mailbox login is needed. [Follow the first-run guide](WINMAIL_GUIDE.txt) for supported input, a capped run and verified downloads. If you control the sender, changing Outlook's message format may avoid TNEF altogether.

**Not sure you need hosted extraction?** [Choose whether to ask for a resend, extract locally or automate](https://agent-tools-workflows.creatieve-naald.chatgpt.site/guides/winmail-dat-resend-or-extract/) before starting a run. For a recurring workflow, [read the manifest, verification and retry pattern](https://agent-tools-workflows.creatieve-naald.chatgpt.site/guides/winmail-dat-attachment-workflow/). These Agent Tools notes include free alternatives and disclose our paid tool.

## Find your starting point

| Your workflow gets stuck here | Use this tool | What you get |
| --- | --- | --- |
| An email contains winmail.dat instead of the files your workflow needs | [Winmail.dat Attachment Extractor](https://apify.com/creatieve_naald/winmail-dat-extractor) | Attachment bytes, safe storage keys and a checksum manifest |
| A contact has several phone numbers or email addresses | [VCF to JSON](https://apify.com/creatieve_naald/vcard-to-json) | Structured contact fields without keeping only the first value |
| A generated report is too long for Telegram | [Telegram Message Preparer](https://apify.com/creatieve_naald/telegram-message-preparer) | Ordered text and entity payloads for your sender |
| Your next step needs JPEG instead of an iPhone HEIC image | [HEIC to JPEG](https://apify.com/creatieve_naald/heic-to-jpeg-for-ai) | A resized JPEG from supported single-image HEIC input |
| Subtitle text needs timestamps for search or retrieval | [SRT & VTT to JSON](https://apify.com/creatieve_naald/srt-vtt-to-json) | Cues and timestamped text chunks |
| A long report exceeds Discord message limits | [Discord Message Preparer](https://apify.com/creatieve_naald/discord-message-preparer) | Ordered message payloads, including simple code fences |
| Audio needs splitting before your transcription step | [Audio Chunk Preparer](https://apify.com/creatieve_naald/audio-chunk-preparer) | Timestamped mono WAV parts; transcription stays with your provider |
| XML is too large to pass through a workflow as one JSON object | [XML Record Batcher](https://apify.com/creatieve_naald/xml-record-batcher) | Ordered NDJSON batches of at most 1 MiB, preserving XML structure |

## Explore without starting a paid run

Download this repository using **Code → Download ZIP** and extract it first.

- **Contacts:** inspect [the invented vCard sample](contact-import-sample.vcf) offline: two phone numbers, two email addresses and a grouped `Desk` label. Downloading or reading the file starts no hosted run. Use only a destination test environment if you choose to test an import; the repository does not write to a CRM. [Review the expected checks](VCF_GUIDE.txt).

- **Discord:** run `python3 discord_export_payloads.py discord-sample-dataset.json` to inspect synthetic webhook bodies. This validates output locally; it sends no messages and needs no token.
- **Audio:** run `python prepare_audio.py recording.wav` with your own supported local file to inspect it without uploading. Only the explicit `--submit` route starts hosted processing.
- **HEIC:** follow the [offline JSON preparation recipe](TROUBLESHOOTING.txt). It prepares input without uploading or converting a photo; format and pixel validation still happen in the Actor.
- **XML:** if you already downloaded a result, use [the reader's offline mode](XML_GUIDE.txt). Obtaining a new hosted result is a separate paid step.

Offline preparation does not prove that an eventual hosted run will accept your input. Keep generated files private. When you choose hosted processing, follow the price and run-cap checks below.

## Try one complete processing step

1. Choose the tool above and read its current price, supported input and limits. Use its synthetic example first, not confidential data.
2. Set a maximum run charge in Apify and run the example once. A hosted run can consume credit; these are paid tools.
3. Inspect the successful run's output. Use the matching guide below to connect your own workflow. Message tools prepare payloads; they do not send them. Audio preparation does not transcribe.

**Why use the hosted version?** Avoid installing and maintaining the processing dependency in your workflow environment. Reuse Apify authentication, run history and output storage. If a local library or your automation platform already handles the job, that may be the better choice; the guides explain the supported boundaries.

## Examples and setup

- **Winmail.dat:** [recover attachments in one bounded processing step](WINMAIL_GUIDE.txt); no mailbox connection or file delivery is included.
- **vCard import:** [preserve multiple phones, emails and labels](VCF_GUIDE.txt) with the Python adapter in [examples.py](examples.py). Before CRM writes, use our [mapping, matching and safe-replay checklist](https://agent-tools-workflows.creatieve-naald.chatgpt.site/guides/vcard-import-without-losing-fields/). It includes a free local route and discloses our paid tool.
- **Telegram reports:** [prepare ordered text/entities payloads](TELEGRAM_GUIDE.txt) using Python or the [importable n8n workflow](n8n-telegram.json).
- **Discord reports:** [validate and export ordered webhook bodies](DISCORD_GUIDE.txt), with an [offline adapter](discord_export_payloads.py) and [synthetic sample](discord-sample-dataset.json). No sending or webhook credentials required.
- **Audio preparation:** [upload audio and obtain timestamped WAV parts](AUDIO_GUIDE.txt) with [prepare_audio.py](prepare_audio.py). Local inspection is free; `--submit` explicitly calls the paid Actor.
- **XML batches:** [read and validate an existing result](XML_GUIDE.txt) with [read_xml_batches.py](read_xml_batches.py). No Actor is started by the reader.
- **Subtitle search and summaries:** [keep source timestamps with transcript chunks](SUBTITLE_GUIDE.txt), with a verified synthetic input/output and local UTF-8 input recipe.
- **HEIC input preparation:** [create bounded base64 JSON offline without overwriting an existing file](TROUBLESHOOTING.txt).
- **Troubleshooting:** [HEIC and subtitle input checks](TROUBLESHOOTING.txt).

Download this repository using **Code → Download ZIP**, extract it, and keep the guide and `examples.py` together. For n8n, import `n8n-telegram.json` and configure your own Apify Header Auth credential. The workflow contains synthetic input and no saved credentials. It prepares messages; it does not send them.

[View the Agent Tools portfolio on Apify](https://apify.com/creatieve_naald). Start with one processing step and verify its output before connecting downstream actions.

## What has been tested

The XML reader has 19 local checks, including mocked HTTP cases. Its real authenticated HTTPS path was also tested against one existing two-record synthetic owner run, including manifest and hash validation. This is not a live n8n Cloud test. The audio adapter was checked with a fake SDK; the Actor has separate synthetic cloud acceptance. No transcription provider or end-to-end n8n audio workflow was tested.

The Discord adapter validates the whole batch before emitting NDJSON. Its synthetic sample and malformed cases were checked locally. Actual Discord delivery and visual rendering remain untested.


Python adapters were checked using synthetic fixtures and mocked HTTP. The n8n workflow was imported and executed locally with n8n 2.43.8 and fixture responses, including invalid output and HTTP errors. This is **not a verified live Apify-to-n8n-to-Telegram integration** or an approved n8n template-directory listing.

Keep tokens in environment variables or workflow credentials, never in exported JSON or issues. A timed-out request may already have completed: inspect its existing run before retrying. Messaging delivery, ordering, retries and rate limits belong to your sender.

## Support and license

For a script or guide problem, use the [example problem form](https://github.com/AI-AgentTools/workflow-examples/issues/new?template=example-problem.yml). GitHub sign-in is required. Include the example filename/revision, Python or workflow version, a minimal **invented** input, expected result and redacted actual result. You do not need to start a paid run to report an example problem.

For a failed **hosted Actor run**, open that Actor's listing from the table above and use its **Issues** tab. A successful Actor run followed by a failure in an example script belongs in this repository instead. Actual CRM writes, message delivery and transcription-provider behavior remain the responsibility of your downstream integration.

Issues are public. Remove personal data, API tokens, webhook URLs, signed links and private paths before submitting. Do not attach original contact exports, recordings or source messages. Share only the smallest synthetic reproduction. Custom integrations and bespoke processing are outside scope.

See [LICENSE.txt](LICENSE.txt) and [RIGHTS.txt](RIGHTS.txt). The license covers original examples and explanations only, not third-party software, trademarks or hosted services. Prepared with AI assistance.
