# 💬 Assistify - Chat GPT assistant

## Installation

Clone repository and install requirements.

```bash
git clone git@github.com:milandufek/assistify.git
cd assistify
pip install -r requirements.txt
```

Add your API key to `openai_api_key` value in `config.json` or set global environment variable `OPENAI_API_KEY`.

If both set environment variable takes precedence.

Ensure you have money on your OpenAI account :)

## Usage

```bash
python assistify.py
```

## Templates
There are several templates defined in `config.json` file. Feel free to add your own to the configuration file. Use `{}` placeholder in template text where you want to insert an user input. It will be replaced with `input` value from UI.
