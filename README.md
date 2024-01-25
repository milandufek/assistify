# 💬 Assistify - ChatGPT assistant

## Description

Assistify is a simple assistant based on [ChatGPT](https://chat.openai.com/). It allows you to create you own templates and use them to chat with the AI. Like create a summary for the article, correct your grammar or other tasks as a helpful assistant.

## Installation

Clone repository and install the requirements.

```bash
git clone git@github.com:milandufek/assistify.git
cd assistify
pip install -r requirements.txt
```

## Usage

Add your API key to `openai_api_key` value in `config.user.json` or set global environment variable `OPENAI_API_KEY`.

```bash
cp config.user.sample.json config.user.json
```

If both set the environment variable takes precedence.

Ensure you have some money on your OpenAI account :).

```bash
python assistify.py
```

## Configurable options

Do not override `config.json` file. Instead, create `config.user.json` file and override only the options you want to change. You can copy the `config.user.sample.json` file and rename it to `config.user.json`.

### Dark/light mode

You can switch between dark and light mode by changing `theme` value (`dark` or `light`) in `config.user.json` file.

### Templates

There are several templates defined in `config.user.json` file. Feel free to add your own to the configuration file. Use `{}` placeholder in template text where you want to insert an user input. It will be replaced with `input` value from UI.

### Currency conversion

You can switch between currencies by changing `currency` and `currency_exchange_rate` value in `config.user.json`. The exchanges rate is always to USD. This is only to display the price in your local currency, not to change the actual charge currency by GPT.

## Archiving

All conversations are archived in `archive` directory by default, change to `false` in `config.user.json` to not archive conversations. The file name is the timestamp of the conversation start. The file contains the conversation in JSON format.

## Copy to clip board

Last response is copied to the clipboard by default, change to `false` in `config.user.json` to not copy the response to the clipboard.

## License

Under the MIT license. See [LICENSE](/LICENSE) file for more details.
