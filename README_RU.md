# Telegram Mini App: Подготовка к ЕГЭ

## Что внутри
- `index.html` — исходное приложение, подготовленное для запуска в Telegram Web Apps.
- `bot.py` — пример Telegram-бота с кнопкой открытия Mini App.
- `requirements.txt` — зависимости бота.

## 1. Разместить Mini App в интернете
Telegram Mini App должен открываться по публичному HTTPS-адресу. Сам файл на телефоне или ссылка `sandbox:` не подойдут.

Простой вариант — GitHub Pages:
1. Создай репозиторий на GitHub.
2. Загрузи `index.html` в корень репозитория.
3. Открой Settings → Pages.
4. Выбери Deploy from a branch, ветку `main`, папку `/ (root)`.
5. Дождись публикации. Получится адрес вида `https://USERNAME.github.io/REPOSITORY/`.

## 2. Создать бота
1. Открой в Telegram @BotFather.
2. Отправь `/newbot` и пройди создание бота.
3. Сохрани токен бота у себя. Не отправляй его в чат и никому не публикуй.

## 3. Запустить пример бота
Нужен компьютер или сервер с Python 3.10+:
```bash
pip install -r requirements.txt
```
Linux/macOS:
```bash
export BOT_TOKEN="ТОКЕН_ОТ_BOTFATHER"
export WEBAPP_URL="https://USERNAME.github.io/REPOSITORY/"
python bot.py
```
Windows PowerShell:
```powershell
$env:BOT_TOKEN="ТОКЕН_ОТ_BOTFATHER"
$env:WEBAPP_URL="https://USERNAME.github.io/REPOSITORY/"
python bot.py
```
После запуска открой бота и отправь `/start`. Появится кнопка запуска Mini App.

## Важно
- Для постоянной работы бота процесс `bot.py` должен работать на сервере. Для теста можно запустить его на компьютере.
- Если хочешь запускать Mini App через кнопку меню профиля бота, настрой Menu Button через @BotFather (`/setmenubutton`) и укажи тот же публичный HTTPS URL.
- Данные прогресса в исходном приложении сохраняются локально в браузере Telegram. Они привязаны к этому приложению/устройству; для синхронизации между устройствами понадобится backend и Telegram user identity.
- Не публикуй токен бота в GitHub или в HTML.
