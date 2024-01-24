# 💬 Assistify - Chat GPT assistant

## Installation

Clone repository and install the requirements.

```bash
git clone git@github.com:milandufek/assistify.git
cd assistify
pip install -r requirements.txt
```

## Usage

Add your API key to `openai_api_key` value in `config.json` or set global environment variable `OPENAI_API_KEY`.

If both set the environment variable takes precedence.

Ensure you have some money on your OpenAI account :).

```bash
python assistify.py
```

## Configurable options

### Dark/light mode

You can switch between dark and light mode by changing `theme` value (`dark` or `light`) in `config.json` file.

### Currency conversion

You can switch between currencies by changing `currency` and `currency_exchange_rate` value in `config.json` file.

### Templates

There are several templates defined in `config.json` file. Feel free to add your own to the configuration file. Use `{}` placeholder in template text where you want to insert an user input. It will be replaced with `input` value from UI.
