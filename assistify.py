import json
import os
import tkinter as tk
from datetime import datetime
from tkinter.scrolledtext import ScrolledText
from newspaper import Article
from openai import OpenAI, APIError
from openai.types.chat import ChatCompletion


class Config:

    def __init__(self, config_path: str) -> None:
        self.config = self.get_config(config_path)

    def get_config(self, config: str = 'config.json') -> dict:
        with open(config) as f:
            config = json.loads(f.read())

        return config


class App(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.work_dir = os.getcwd()
        self.cfg = Config(config_path='config.json').get_config()
        self.paddings = {'padx': 2, 'pady': 2}
        self.button_width = 16
        self.url = None
        self.model = 'gpt-3.5-turbo'
        self.input = ''
        self.output = ''

        # Draw window and widgets
        self.title(self.cfg['ui']['title'])
        self.geometry('800x800')
        # self.resizable(width=False, height=False)
        self.frame_top()
        self.frame_input()
        self.frame_action()
        self.frame_response()
        self.frame_status_bar()
        self.mainloop()

    def get_config(self, config: str) -> dict:
        with open(config) as f:
            config = json.loads(f.read())

        return config

    def frame_top(self) -> None:
        frame_top = tk.Frame(self)
        frame_top.pack(fill=tk.X, **self.paddings)

        selected_model = tk.StringVar()
        models = list(self.cfg['models'].keys())
        selected_model.set(models[0])
        dropdown_model = tk.OptionMenu(frame_top, selected_model, *models,
                                       command=self.set_model)
        dropdown_model.config(width=14)
        dropdown_model.pack(side=tk.LEFT, fill=tk.X)

        default_url = self.cfg['ui']['message_url']

        def clean_url(event) -> None:
            if self.url.get().strip() == default_url:
                input_url.delete(0, tk.END)

        def select_all(event) -> str:
            self.input_url.tag_add(tk.SEL, '1.0', tk.END)
            self.input_url.mark_set(tk.INSERT, '1.0')
            self.input_url.see(tk.INSERT)
            return 'break'

        self.url = tk.StringVar()
        self.url.set(default_url)
        input_url = tk.Entry(frame_top)
        input_url.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_url['textvariable'] = self.url
        input_url.bind('<Key-Return>', self.get_article)
        input_url.bind('<Button-1>', clean_url)
        input_url.bind('<Control-a>', select_all)

        button_fill = tk.Button(frame_top, text=self.cfg['ui']['button_load_article'],
                                width=self.button_width, command=self.get_article)
        button_fill.pack(side=tk.LEFT, fill=tk.X)

    def frame_input(self) -> None:
        frame_input = tk.Frame(self)
        frame_input.pack(fill=tk.X, **self.paddings)

        default_input = self.cfg['ui']['message_input']
        fault_input = self.cfg['ui']['unable_to_load_article']

        def clean_input(event) -> None:
            if self.input_text.get('1.0', tk.END).strip() in (default_input, fault_input):
                self.input_text.delete('1.0', tk.END)

        def select_all(event) -> str:
            self.input_text.tag_add(tk.SEL, '1.0', tk.END)
            self.input_text.mark_set(tk.INSERT, '1.0')
            self.input_text.see(tk.INSERT)
            return 'break'

        def delete_last_word(event) -> str:
            self.input_text.delete('insert-1c wordstart', 'insert')
            return 'break'

        self.input_text = ScrolledText(frame_input, height=10)
        self.input_text.insert('1.0', default_input)
        self.input_text.bind('<Button-1>', clean_input)
        self.input_text.bind('<Control-a>', select_all)
        self.input_text.bind('<Control-Return>', self.call_gpt)
        self.input_text.bind('<Control-BackSpace>', delete_last_word)
        self.input_text.pack(fill=tk.X)

    def frame_action(self) -> None:
        frame_actions = tk.Frame(self)
        frame_actions.pack(fill=tk.X, **self.paddings)

        self.prompt_template = tk.StringVar()
        templates = list(self.cfg['templates'].keys())
        self.prompt_template.set(templates[0])
        dropdown_prompt = tk.OptionMenu(frame_actions, self.prompt_template, *templates,
                                        command=self.set_prompt)
        dropdown_prompt.pack(side=tk.LEFT, fill=tk.X, expand=True)

        button_generate = tk.Button(frame_actions, text=self.cfg['ui']['button_generate'],
                                    width=self.button_width, command=self.call_gpt)
        button_generate.pack(side=tk.RIGHT, fill=tk.X)

    def frame_response(self) -> None:
        frame_response = tk.Frame(self)
        frame_response.pack(fill=tk.BOTH, expand=True, **self.paddings)

        def select_all(event) -> str:
            self.response_text.tag_add(tk.SEL, '1.0', tk.END)
            self.response_text.mark_set(tk.INSERT, '1.0')
            self.response_text.see(tk.INSERT)
            return 'break'

        self.response_text = ScrolledText(frame_response, height=14)
        self.response_text.pack(fill=tk.BOTH, expand=True)
        self.response_text.bind('<Control-a>', select_all)

    def frame_status_bar(self) -> None:
        frame_status_bar = tk.Frame(self)
        frame_status_bar.pack(fill=tk.X, **self.paddings)

        self.status_bar = tk.Label(frame_status_bar, text=self.cfg['ui']['Ready'])
        self.status_bar.pack(side=tk.LEFT, fill=tk.X)

        button_copy = tk.Button(frame_status_bar, text=self.cfg['ui']['button_copy'],
                                width=self.button_width, command=self.copy_to_clipboard)
        button_copy.pack(side=tk.RIGHT, fill=tk.BOTH)

    def set_model(self, model: str) -> str:
        self.model = model
        print(f'The current model is: {model}')
        return model

    def set_prompt(self, prompt) -> str:
        print(f'The current prompt template is: {prompt}')
        return prompt

    def call_gpt(self, event=None) -> None:
        prompt_template = self.prompt_template.get()
        prompt_input = self.input_text.get('1.0', tk.END).strip()
        self.input = '\n\n'.join([
            line.strip().format('\n\n' + prompt_input.strip())
            for line in self.cfg['templates'][prompt_template]
        ])
        print('Calling GPT...')
        print(f'GPT prompt template: {prompt_template}')
        print(f'GPT user input: {prompt_input[:50]} ... {prompt_input[-50:]}')

        api_key = os.environ.get('OPENAI_API_KEY', self.cfg['openai_api_key'])
        self.client = OpenAI(api_key=api_key)

        resp = self.client.chat.completions.create(
            messages=[{
                'role': 'user',
                'content': self.input,
            }],
            model=self.model,
        )

        self.output = resp.choices[0].message.content
        cost = self.get_cost(resp)
        print(f'Response: {self.output[:100]} ...')

        self.archive_response(self.input, cost)

        self.response_text.delete('1.0', tk.END)
        self.response_text.insert('1.0', self.output)
        self.status_bar.config(text=f'{self.cfg['ui']['last_req_cost']}: {cost} {self.cfg['currency']}')

    def get_cost(self, response: ChatCompletion) -> float:
        per_tokens = 1000
        cost_prompt = int(response.usage.prompt_tokens) / per_tokens * \
            float(self.cfg['models'][self.model]['input_token_cost'])
        cost_resp = int(response.usage.completion_tokens) / per_tokens * \
            float(self.cfg['models'][self.model]['output_token_cost'])
        cost = cost_prompt + cost_resp

        if self.cfg['currency'] != 'USD' and self.cfg['currency_exchange_rate']:
            cost = cost * self.cfg['currency_exchange_rate']

        cost = round(cost, 3)

        return cost

    def copy_to_clipboard(self) -> None:
        response = self.response_text.get('1.0', tk.END).strip()

        if not response:
            return

        self.clipboard_clear()
        self.clipboard_append(response)

        copy_msg = self.cfg['ui']['copied']
        sep = self.cfg['ui']['separator']
        current_status = self.status_bar.cget('text')

        if not current_status.endswith(copy_msg):
            self.status_bar.config(text=f'{current_status} {sep} {copy_msg}')

    def get_article(self) -> None:
        article = Article(self.url.get())
        article.download()
        article.parse()
        self.input_text.delete('1.0', tk.END)

        if article.text:
            self.input_text.insert('1.0', article.text)
        else:
            self.input_text.insert('1.0', self.cfg['ui']['unable_to_load_article'])

    def archive_response(self, message: str, cost: float) -> None:
        if self.cfg['archive']:
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            file_path = os.path.join(self.cfg['archive_path'], f'{now}.json')
            dump = {
                'model': self.model,
                'cost': cost,
                'currency': self.cfg['currency'],
                'input': message,
                'output': self.output,
            }
            with open(file_path, 'w') as f:
                json.dump(dump, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    app = App()
