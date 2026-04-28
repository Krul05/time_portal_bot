import os
import re
import json
import difflib
import requests

class Checker:
    def normalize_string(self, text):

        text = str(text).lower().strip()
        text = text.replace("ё", "е")

        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)

        text = re.sub(r"\s+", " ", text).strip()

        return text


    def simple_answer_check(self, user_answer, correct_answer):
        user_norm = self.normalize_string(user_answer)
        correct_norm = self.normalize_string(correct_answer)

        if user_norm == correct_norm:
            return True

        comparability = difflib.SequenceMatcher(None, user_norm, correct_norm).ratio()
        if comparability >= 0.9:
            return True

        return False


    def ai_answer_check(self, question, user_answer, correct_answer):
        github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            return False

        prompt = f"""
            Ты проверяешь ответ пользователя в историческом квесте.
            
            Вопрос:
            {question}
            
            Правильный ответ:
            {correct_answer}
            
            Ответ пользователя:
            {user_answer}
            
            Считай ответ правильным, если это тот же человек, объект, событие, место или дата,
            включая другое написание, синоним, прозвище, титул или вариант с ё/е.
            
            Считай ответ неправильным, если ответ слишком общий или относится к другому объекту, событию.
            
            Верни только JSON:
            {{"is_correct": true или false}}
        """

        response = requests.post(
            "https://models.github.ai/inference/chat/completions",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={
                "model": os.getenv("AI_MODEL", "openai/gpt-4.1"),
                "messages": [
                    {"role": "system", "content": "Ты строгий проверяющий ответов для образовательного квеста."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
            },
            timeout=20,
        )

        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]

        try:
            data = json.loads(content)
            return bool(data.get("is_correct", False))
        except Exception:
            return False


    def is_answer_correct(self, question, user_answer, correct_answer):
        if self.simple_answer_check(user_answer, correct_answer):
            return True

        return self.ai_answer_check(question, user_answer, correct_answer)