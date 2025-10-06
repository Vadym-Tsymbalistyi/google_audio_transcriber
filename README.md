# Google Audio Transcriber & AI Analyzer

Програма автоматично обробляє аудіофайли: транскрибує розмови менеджерів з клієнтами, аналізує їх за допомогою AI та записує результати у Google Sheets.

## Основні можливості

* **Транскрипція аудіо** — локально через Whisper або інший обраний метод.
* **Аналіз розмов** — Azure OpenAI визначає, чи менеджер дотримувався інструкцій, виявляє проблемні моменти.
* **Інтеграція з Google Drive** — автоматичне копіювання аудіофайлів у робочу папку.
* **Інтеграція з Google Sheets** — збереження транскриптів та результатів аналізу у таблицю.
* **Автоматизація процесу** — обробка всіх нових файлів по черзі та оновлення таблиці.

## Структура проєкту

```
project_root/
├── main_controller.py      # Основна логіка роботи
├── ai_manager.py           # Аналіз транскриптів через AI
├── audio_manager.py        # Робота з локальними аудіофайлами
├── transcriber.py          # Транскрипція аудіо
├── drive_client.py         # Підключення до Google Drive
├── sheet_manager.py        # Робота з Google Sheets
├── mapping.py              # Відповідність колонок Sheet
├── workspace/              # Локальна папка для аудіо та транскриптів
├── requirements.txt        # Залежності Python
├── config.py               # Конфігурація проєкту
└── .env                    # Налаштування (ключі, шляхи)
```

## Встановлення

1. Клонувати репозиторій:

```bash
git clone <repo_url>
cd <repo>
```

2. Створити та активувати віртуальне середовище:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

3. Встановити залежності:

```bash
pip install -r requirements.txt
```

### 4. Додати файли для Google API

Для роботи з Google Drive та Google Sheets необхідно додати два файли:

- `client_secret.json` — OAuth 2.0 Client ID для авторизації користувача.
- `service_account.json` — Service Account для автоматичного доступу до Google API.

Отримати файли можна через [Google Cloud Console](https://console.cloud.google.com/).

5. Налаштувати  `.env`:

```
CREDENTIALS_PATH=service_account.json
CREDENTIALS=test.json
WORKSPACE_FOLDER_ID=your_workspace_folder_id_here
DRIVE_FOLDER_ID=your_drive_folder_id_here
SHEET_TEMPLATE_ID=your_sheet_template_id_here
GOOGLE_SHEET_ID=your_google_sheet_id_here


# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_KEY=your_azure_openai_key_here
CHAT_COMPLETION_NAME=your_model_name_here
```


## Використання


1. Запуск:

```bash
python main.py
```

2. Система автоматично:

   * завантажує файли з Drive;
   * транскрибує аудіо;
   * завантажує файли ,транскрипт, таблицю  на Drive;
   * аналізує через AI;
   * записує результат у Google Sheet.

## Формат таблиці

* Колонка `Дата` містить транскрипт.
* Інші колонки заповнюються за відповідністю `AI_TO_SHEET_MAP`.

##  Розробник

**Автор:** Vadym Tsymbalisyi
**Мова:** Python 3.13
**IDE:** PyCharm
