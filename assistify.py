import json
import os
import tkinter as tk
from datetime import datetime
from tkinter.scrolledtext import ScrolledText
import sv_ttk
from newspaper import Article
from openai import OpenAI, APIError
from openai.types.chat import ChatCompletion
from config import Config, ConfigLoader, UI


class App(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        config = ConfigLoader().get_config()
        config = {k: v for k, v in config.items() if k in Config.__annotations__}
        self.conf = Config(**config)
        self.ui = UI(**ConfigLoader().load_json('ui.json'))

        self.model = 'gpt-3.5-turbo'
        self.input, self.output = '', ''
        self.status = tk.StringVar()
        self.url = tk.StringVar()

        self.title(self.ui.title)
        self.geometry('800x800')
        self.theme = self.conf.theme

        if self.conf.theme:
            sv_ttk.set_theme(self.conf.theme)

        if not self.conf.resizable_window:
            self.resizable(width=False, height=False)

        self.frame_top()
        self.frame_input()
        self.frame_action()
        self.frame_response()
        self.frame_status_bar()
        self.mainloop()

    def frame_top(self) -> None:
        frame_top = tk.Frame(self)
        frame_top.pack(fill=tk.X, **self.ui.paddings)

        selected_model = tk.StringVar()
        models = list(self.conf.models.keys())
        selected_model.set(models[0])
        dropdown_model = tk.OptionMenu(frame_top, selected_model, *models,
                                       command=self.set_model)
        dropdown_model.config(width=self.ui.dropdown_width)
        dropdown_model.pack(side=tk.LEFT, fill=tk.X)

        default_url = self.ui.message_url

        def clean_url(event: tk.Event = None) -> None:
            if self.url.get().strip() == default_url:
                self.url.set('')

        def select_all(widget: tk.Widget, event: tk.Event = None) -> str:
            widget.select_range(0, 'end')
            widget.icursor('end')
            return 'break'

        self.url.set(default_url)
        input_url = tk.Entry(frame_top, textvariable=self.url)
        input_url.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_url.bind('<Key-Return>', self.get_article)
        input_url.bind('<Button-1>', clean_url)
        input_url.bind('<Control-a>', lambda e, w=input_url: select_all(w, e))

        button_fill = tk.Button(
            frame_top,
            text=self.ui.button_load_article,
            width=self.ui.button_width,
            command=self.get_article
        )
        button_fill.pack(side=tk.LEFT, fill=tk.X)

    def frame_input(self) -> None:
        frame_input = tk.Frame(self)
        frame_input.pack(fill=tk.X, **self.ui.paddings)

        default_input = self.ui.message_input
        fault_input = self.ui.error_load_article

        def clean_input(event: tk.Event = None) -> None:
            if self.input_text.get('1.0', tk.END).strip() in (default_input, fault_input):
                self.input_text.delete('1.0', tk.END)

        def select_all(event: tk.Event = None) -> str:
            self.input_text.tag_add(tk.SEL, '1.0', tk.END)
            self.input_text.mark_set(tk.INSERT, '1.0')
            self.input_text.see(tk.INSERT)
            return 'break'

        def delete_last_word(event: tk.Event = None) -> str:
            self.input_text.delete('insert-1c wordstart', 'insert')
            return 'break'

        self.input_text = ScrolledText(frame_input, wrap=tk.WORD, height=10)
        self.input_text.insert('1.0', default_input)
        self.input_text.bind('<Button-1>', clean_input)
        self.input_text.bind('<Control-a>', select_all)
        self.input_text.bind('<Control-Return>', self.call_gpt)
        self.input_text.bind('<Control-BackSpace>', delete_last_word)
        self.input_text.pack(fill=tk.X)

    def frame_action(self) -> None:
        frame_actions = tk.Frame(self)
        frame_actions.pack(fill=tk.X, **self.ui.paddings)

        self.prompt_template = tk.StringVar()
        templates = list(self.conf.templates.keys())
        self.prompt_template.set(templates[0])
        dropdown_prompt = tk.OptionMenu(
            frame_actions,
            self.prompt_template,
            *templates,
            command=self.set_prompt
        )
        dropdown_prompt.pack(side=tk.LEFT, fill=tk.X, expand=True)

        button_generate = tk.Button(
            frame_actions,
            text=self.ui.button_generate,
            width=self.ui.button_width,
            command=self.call_gpt
        )
        button_generate.pack(side=tk.RIGHT, fill=tk.X)

    def frame_response(self) -> None:
        frame_response = tk.Frame(self)
        frame_response.pack(fill=tk.BOTH, expand=True, **self.ui.paddings)

        def select_all(event: tk.Event = None) -> str:
            self.response_text.tag_add(tk.SEL, '1.0', tk.END)
            self.response_text.mark_set(tk.INSERT, '1.0')
            self.response_text.see(tk.INSERT)
            return 'break'

        self.response_text = ScrolledText(frame_response, wrap=tk.WORD, height=14)
        self.response_text.pack(fill=tk.BOTH, expand=True)
        self.response_text.bind('<Control-a>', select_all)

    def frame_status_bar(self) -> None:
        frame_status_bar = tk.Frame(self)
        frame_status_bar.pack(fill=tk.X, **self.ui.paddings)

        self.status.set(self.ui.ready)
        self.status_bar = tk.Label(frame_status_bar, textvariable=self.status)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X)

        button_switch = tk.Button(
            frame_status_bar,
            text=self.ui.button_switch_theme,
            command=self.switch_theme
        )
        button_switch.pack(side=tk.RIGHT, fill=tk.X)

    def set_model(self, model: str) -> str:
        self.model = model
        return model

    def set_prompt(self, prompt: str) -> str:
        return prompt

    def prepare_prompt(self) -> bool:
        prompt_template = self.prompt_template.get()
        prompt_input = self.input_text.get('1.0', tk.END).strip()

        if not prompt_input or prompt_input == self.ui.message_input:
            self.status.set(self.ui.error_no_input)
            return False

        self.input = '\n\n'.join([
            line.strip().format('\n\n' + prompt_input.strip())
            for line in self.conf.templates[prompt_template]
        ])

        return True

    def call_gpt(self, event: tk.Event = None) -> None:
        if not self.prepare_prompt():
            return

        time_start = datetime.now()
        api_key = os.environ.get('OPENAI_API_KEY', self.conf.openai_api_key)

        try:
            self.status.set(f"{self.ui.waiting}")
            self.update_idletasks()
            self.client = OpenAI(api_key=api_key)
            resp = self.client.chat.completions.create(
                messages=[{
                    'role': 'user',
                    'content': self.input,
                }],
                model=self.model,
            )
        except APIError as e:
            print(e.message)
            self.status.set(f"{self.ui.error} {e.body['message'][:85]} ...")
            return

        self.output = resp.choices[0].message.content
        self.response_text.delete('1.0', tk.END)
        self.response_text.insert('1.0', self.output)
        cost = self.get_request_cost(resp)
        duration = (datetime.now() - time_start).seconds
        self.status.set(f"{self.ui.request_completed.format(
            duration, cost, self.conf.currency
        )}")
        self.copy_to_clipboard()
        self.archive_chat()

    def get_request_cost(self, response: ChatCompletion) -> float:
        per_tokens = 1000
        in_cost = self.conf.models[self.model]['input_token_cost']
        out_cost = self.conf.models[self.model]['output_token_cost']
        cost_prompt = response.usage.prompt_tokens / per_tokens * in_cost
        cost_resp = response.usage.completion_tokens / per_tokens * out_cost
        cost = cost_prompt + cost_resp

        if self.conf.currency != 'USD' and self.conf.currency_exchange_rate:
            cost = cost * self.conf.currency_exchange_rate

        cost = round(cost, 3)

        return cost

    def copy_to_clipboard(self) -> None:
        if not self.conf.copy_to_clipboard:
            return

        response = self.response_text.get('1.0', tk.END).strip()

        if not response:
            return

        self.clipboard_clear()
        self.clipboard_append(response)

        copy_msg = self.ui.copied
        sep = self.ui.separator
        current_status = self.status_bar.cget('text')

        if not current_status.endswith(copy_msg):
            self.status.set(f'{current_status} {sep} {copy_msg}')
            self.update_idletasks()

    def get_article(self) -> None:
        url = self.url.get().strip()

        if not url or url == self.ui.message_url:
            self.status.set(self.ui.error_no_url)
            return

        if not url.startswith(('http://', 'https://')):
            self.status.set(self.ui.error_invalid_url)
            return

        article = Article(url)
        article.download()
        article.parse()
        self.input_text.delete('1.0', tk.END)

        if article.text:
            self.input_text.insert('1.0', article.text)
        else:
            self.input_text.insert('1.0', self.ui.error_load_article)

    def archive_chat(self) -> None:
        if not self.conf.archive:
            return

        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        archive_dir = self.conf.archive_path

        if not os.path.isdir(archive_dir):
            os.makedirs(archive_dir)

        file_path = os.path.join(archive_dir, f'{now}.json')
        dump = {
            'model': self.model,
            'input': self.input,
            'output': self.output,
        }
        with open(file_path, 'w') as f:
            json.dump(dump, f, ensure_ascii=False, indent=4)

    def switch_theme(self) -> None:
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        sv_ttk.set_theme(self.theme)


if __name__ == '__main__':
    app = App()
