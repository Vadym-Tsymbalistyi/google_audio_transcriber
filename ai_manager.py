import logging
import json
import re
from openai import AzureOpenAI
from config import Config


class AIManager:
    def __init__(self):
        self.logger = logging.getLogger("AIManager")
        self.logger.debug("Initializing AIManager")

        self.client = AzureOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_KEY,
            api_version="2024-12-01-preview"
        )
        self.model = Config.CHAT_COMPLETION_NAME
        self.keys = [
            "Початок розмови, представлення",
            "Чи дізнався менеджер кузов автомобіля",
            "Чи дізнався менеджер рік автомобіля",
            "Чи дізнався менеджер пробіг",
            "Пропозиція про комплексну діагностику",
            "Дізнався які роботи робилися раніше",
            "Завершення розмови прощання",
            "Яка робота з топ 100",
            "Чи дотримувався всіх інструкцій з топ 100 робіт Да/Ні",
            "Результат",
            "Коментар"
        ]

    def analyze_transcript(self, transcript_text: str) -> dict:
        self.logger.debug("Preparing prompt for GPT")

        prompt = f"""
Проаналізуй розмову менеджера з клієнтом. Для кожного пункту дай відповідь Так/Ні.
Обов'язково додай короткий коментар, де зазнач:
- де дзвінок з клієнтом не ОК,
- де менеджер відповідав некоректно, грубо або не проконсультував.

Для пункту "Яка робота з топ 100" обери одну або кілька робіт.

Також визнач значення для поля "Результат" — одне зі списку:
["Запис", "Повторна консультація", "Передано іншому філіалу", "Передзвонити", "Інше"]

Виведи **валідний JSON** з подвійними лапками, коментар в один рядок, без переносів.

Ключі JSON повинні бути:
"Початок розмови, представлення", 
"Чи дізнався менеджер кузов автомобіля",
"Чи дізнався менеджер рік автомобіля",
"Чи дізнався менеджер пробіг",
"Пропозиція про комплексну діагностику", 
"Дізнався які роботи робилися раніше",
"Завершення розмови прощання", 
"Яка робота з топ 100",
"Чи дотримувався всіх інструкцій з топ 100 робіт Да/Ні",
"Результат",
"Коментар"

Транскрипт:
{transcript_text}
"""
        try:
            self.logger.debug("Sending request to Azure OpenAI")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            self.logger.debug("Response received from Azure OpenAI")

            gpt_text = response.choices[0].message.content.strip()
            self.logger.debug(f"Raw GPT response: {gpt_text[:200]}...")

            json_match = re.search(r'\{.*\}', gpt_text, re.DOTALL)
            if json_match:
                raw_json = json_match.group().replace("\n", " ").replace("'", '"')
                try:
                    result = json.loads(raw_json)
                    self.logger.debug("JSON parsed successfully")
                except json.JSONDecodeError:
                    self.logger.warning("GPT returned invalid JSON, using defaults")
                    result = {key: "Ні" if key not in ["Коментар", "Результат"] else "" for key in self.keys}
            else:
                self.logger.warning("No JSON found in GPT response, using defaults")
                result = {key: "Ні" if key not in ["Коментар", "Результат"] else "" for key in self.keys}

        except Exception as e:
            self.logger.error("Azure GPT error: %s", e)
            result = {key: "Ні" if key not in ["Коментар", "Результат"] else "" for key in self.keys}

        self.logger.debug("Transcript analysis completed")
        return result
