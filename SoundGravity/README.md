# 🎵 SoundGravity

<p align="center">
  <img src="assets/icon.png" width="128" height="128" alt="SoundGravity Logo">
</p>

<p align="center">
  <b>Утилита для полной кастомизации звуковых уведомлений в Google Antigravity</b><br>
  <i>Не нравится стандартный звук завершения работы или уведомления о вмешательстве? Настрой под себя!</i>
</p>

<p align="center">
  <a href="README.md">Русский</a> •
  <a href="README.en.md">English</a> •
  <a href="README.ua.md">Українська</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Version-1.0.0-8B5CF6?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

## ⚡ О проекте

**SoundGravity** — это компактная и стильная программа с современным тёмным интерфейсом для гибкой замены и настройки звуков в **Google Antigravity**:
1. **Звук завершения задачи** (*Task Completed / Finish sound*)
2. **Звук при необходимости вмешаться** (*User Intervention / Action Needed sound*)

Программа находит установленный `language_server.exe` Antigravity и аккуратно заменяет звуковые дорожки, сохраняя целостность приложения.

---

## ✨ Основные возможности

- 🎧 **Встроенные звуковые пресеты:**
  - **Cyberpunk** — стильный неоновый футуристичный звук
  - **Original** — оригинальные классические звуки Antigravity
  - **Minimal** — короткий, ненавязчивый soft-клип
  - **Retro 8-Bit Arcade** — олдскульный аркадный ретро-звук
- 🎙️ **Встроенный AI-генератор речи (Neural TTS):**
  - Озвучивайте завершение задач любыми фразами! (например, *«Джеминай закончил проект»*)
  - Поддержка языков и голосов:
    - **Украинский (UA):** Остап (`OstapNeural`), Полина (`PolinaNeural`)
    - **Русский (RU):** Дмитрий (`DmitryNeural`), Светлана (`SvetlanaNeural`)
    - **Английский (EN):** Andrew, Ava, Aria, Guy (`Multilingual Neural`)
  - Регулировка скорости речи и громкости прямо в меню генерации.
- 📁 **Свои аудиофайлы:** Загрузка любых пользовательских `.mp3` или `.wav` файлов.
- 🔊 **Индивидуальная регулировка громкости:** Плавные слайдеры громкости (от 0% до 100%) отдельно для каждого звука.
- 🔄 **Авто-патч при обновлениях (Auto-Patch):** При обновлении Antigravity утилита автоматически восстанавливает ваши выбранные звуки.
- 🌐 **Мультиязычный интерфейс:** Мгновенное переключение между **RU**, **UA** и **EN** с плавной анимацией тумблера.
- 📦 **Полный Standalone:** Работает из одного `.exe`, не требует установки Python, библиотек или сторонних зависимостей.

---

## 🚀 Установка и запуск

### Вариант 1: Готовый `.exe` (Рекомендуется)
1. Скачайте свежий релиз `SoundGravity.exe` из раздела [Releases](../../releases).
2. Запустите файл. Установка не требуется!
3. Выберите нужный звук или сгенерируйте свой через TTS, настройте громкость и нажмите «Применить».

### Вариант 2: Запуск из исходного кода

Требуется **Python 3.10+**.

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/SoundGravity.git
   cd SoundGravity
   ```

2. Установите необходимые зависимости:
   ```bash
   pip install pillow edge-tts pywin32
   ```

3. Запустите приложение:
   ```bash
   python src/app.py
   ```

---

## 🛠️ Сборка автономного .exe

Для создания единого переносимого `.exe` используется **PyInstaller**:

```bash
python -m PyInstaller --noconfirm --clean --onefile --windowed `
  --name "SoundGravity" `
  --icon "assets/icon.ico" `
  --add-data "assets;assets" `
  --add-data "presets;presets" `
  --hidden-import "edge_tts" `
  --hidden-import "win32com.client" `
  --hidden-import "PIL" `
  --hidden-import "webbrowser" `
  "src/app.py"
```
Собранный бинарник появится в директории `dist/SoundGravity.exe`.

---

## 📂 Структура проекта

```text
SoundGravity/
├── assets/                  # Иконки, векторная графика и шрифты
│   ├── icon.ico
│   ├── icon.png
│   └── ...
├── presets/                 # Готовые наборы звуков
│   ├── Cyberpunk/
│   ├── Original/
│   ├── Minimal/
│   └── Arcade/
├── src/                     # Исходный код приложения
│   ├── app.py               # Главный GUI на Tkinter / Canvas с векторной отрисовкой
│   ├── patcher.py           # Поиск и патчинг language_server.exe
│   └── watcher.py           # Фоновый мониторинг обновлений Antigravity
├── README.md                # Документация проекта
└── ...
```

---

## 💖 Поддержка автора

Если вам нравится проект и вы хотите поддержать дальнейшую разработку:

- 💬 **DonationAlerts:** [dalink.to/reeshkaii](https://dalink.to/reeshkaii)
- 🤍 **Donatello:** [donatello.to/Reeshkaii](https://donatello.to/Reeshkaii)

---

## 📄 Лицензия

Распространяется под лицензией **MIT**. Подробности в файле `LICENSE`.
