# 🎵 SoundGravity

<p align="center">
  <b>Утиліта для повної кастомізації звукових сповіщень у Google Antigravity</b><br>
  <i>Не подобається стандартний звук закінчення роботи чи сповіщення про необхідність втручання? Налаштуй під себе!</i>
</p>

<p align="center">
  <a href="README.ru.md">Русский</a> •
  <a href="README.md">English</a> •
  <a href="README.ua.md">Українська</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Version-1.0.0-8B5CF6?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

## ⚡ Про проєкт

**SoundGravity** — це компактна та зручна програма із сучасним темним інтерфейсом для гнучкої заміни й налаштування звуків у **Google Antigravity**:
1. **Звук завершення задачі** (*Task Completed / Finish sound*)
2. **Звук при необхідності втручання** (*User Intervention / Action Needed sound*)

Програма автоматично знаходить встановлений `language_server.exe` Antigravity та акуратно замінює звукові доріжки, не порушуючи стабільність середовища.

---

## ✨ Основні можливості

- 🎧 **Вбудовані пресети звуків:**
  - **Cyberpunk** — стильний неоновий футуристичний звук
  - **Original** — класичні стандартні звуки Antigravity
  - **Minimal** — короткий ненав'язливий м'який кліп
  - **Retro 8-Bit Arcade** — олдскульний ретро-звук гральних автоматів
- 🎙️ **Вбудований AI-генератор мовлення (Neural TTS):**
  - Озвучуйте завершення завдань будь-якими власними фразами (наприклад, *«Джемінаoffice/Джемінай закінчив роботу над проєктом»*)
  - Підтримка мов та природних нейронних голосів:
    - **Українська (UA):** Остап (`OstapNeural`), Поліна (`PolinaNeural`)
    - **Русский (RU):** Дмитро (`DmitryNeural`), Світлана (`SvetlanaNeural`)
    - **English (EN):** Andrew, Ava, Aria, Guy (`Multilingual Neural`)
  - Регулювання швидкості та гучності перед генерацією з миттєвим прослуховуванням.
- 📁 **Власні аудіофайли:** Вибір будь-яких файлів `.mp3` або `.wav` з вашого диска.
- 🔊 **Індивідуальне налаштування гучності:** Плавні слайдери (від 0% до 100%) окремо для кожного типу сповіщення.
- 🔄 **Авто-оновлення звуків (Auto-Patch):** Під час оновлень Antigravity програма автоматично повторно застосовує ваші звуки у фоновому режимі.
- 🌐 **Мультимовний інтерфейс:** Швидке перемикання між **UA**, **EN** та **RU** з плавною анімацією.
- 📦 **Повний Standalone:** Працює безпосередньо з одного `.exe`, не вимагає встановлення Python чи сторонніх пакетів.

---

## 🚀 Встановлення та запуск

### Спосіб 1: Готовий файл `.exe` (Рекомендовано)
1. Завантажте актуальний реліз `SoundGravity.exe` з розділу [Releases](../../releases).
2. Запустіть файл — програма одразу готова до роботи без інсталяції.
3. Оберіть звук або згенеруйте новий через TTS, налаштуйте гучність і натисніть «Застосувати».

### Спосіб 2: Запуск із вихідного коду

Необхідний встановлений **Python 3.10+**.

1. Клонуйте репозиторій:
   ```bash
   git clone https://github.com/your-username/SoundGravity.git
   cd SoundGravity
   ```

2. Встановіть необхідні модулі:
   ```bash
   pip install pillow edge-tts pywin32
   ```

3. Запустіть програму:
   ```bash
   python src/app.py
   ```

---

## 🛠️ Збірка власного .exe

Для створення повністю автономного `.exe` використовується **PyInstaller**:

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
Готовий файл буде створено в папці `dist/SoundGravity.exe`.

---

## 📂 Структура проєкту

```text
SoundGravity/
├── assets/                  # Іконки, векторні елементи та шрифти
│   ├── icon.ico
│   ├── icon.png
│   └── ...
├── presets/                 # Вбудовані набори аудіо
│   ├── Cyberpunk/
│   ├── Original/
│   ├── Minimal/
│   └── Arcade/
├── src/                     # Вихідний код програми
│   ├── app.py               # Основний GUI (Tkinter / Canvas із власною векторною графікою)
│   ├── patcher.py           # Пошук та патчинг language_server.exe
│   └── watcher.py           # Моніторинг оновлень середовища
├── README.md                # Документація (Русский)
├── README.ua.md             # Документація (Українська)
├── README.en.md             # Документація (English)
└── LICENSE                  # Ліцензія MIT
```

---

## 💖 Підтримка розробника

Якщо проєкт став вам у пригоді й ви бажаєте підтримати його розвиток:

- 💬 **DonationAlerts:** [dalink.to/reeshkaii](https://dalink.to/reeshkaii)
- 🤍 **Donatello:** [donatello.to/Reeshkaii](https://donatello.to/Reeshkaii)

---

## 📄 Ліцензія

Проєкт розповсюджується під ліцензією **MIT**. Подробиці у файлі `LICENSE`.
