import os
import re

from openai import OpenAI


class Chatbot:
    def __init__(self, max_history=6):

        self.client = OpenAI(
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:8000/v1"),
            api_key=os.getenv("LLM_API_KEY", "not needed"),
            timeout=60,  # seconds, so the Streamlit page can't hang forever
        )
        self.model = os.getenv("LLM_MODEL", "Qwen/Qwen3.5-0.8B")
        self.history = []
        self.max_history = max_history
        self.system_prompt = (
            "You are a friendly voice assistant. "
            "Answer the user's actual question in 1-3 short sentences. "
            "Use the earlier conversation to remember facts the user told you, "
            "such as their name. Do not greet the user again after the first message. "
            "Do not use markdown, lists or emojis, because your answer will be read aloud."
        )

    def build_messages(self, user_input):
        messages = [{"role": "system", "content": self.system_prompt}]
        for turn in self.history[-self.max_history:]:      # rolling window
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["bot"]})
        messages.append({"role": "user", "content": user_input})
        return messages

    def chat(self, user_input):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.build_messages(user_input),
                max_tokens=200,
                temperature=0.7,
                extra_body={"chat_template_kwargs": {"enable_thinking": False}},
            )
            bot_reply = response.choices[0].message.content or ""
        except Exception as e:
            return f"[Error: {e}]"

        bot_reply = re.sub(r"<think>.*?</think>", "", bot_reply, flags=re.DOTALL)
        bot_reply = re.sub(r"[*#`_>]", "", bot_reply).strip()

        if not bot_reply:
            return "[No response — try rephrasing]"

        self.history.append({"user": user_input, "bot": bot_reply})
        return bot_reply

    def clear_history(self):
        self.history = []

    def chat_from_file(self, filepath="user_sound.txt"):
        if not os.path.isfile(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            user_input = f.read().strip()

        if not user_input:
            return None

        return self.chat(user_input)