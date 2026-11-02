# 🎵 SoundGravity

<p align="center">
  <b>A comprehensive audio customization utility for Google Antigravity</b><br>
  <i>Don't like the default completion chime or action notification? Customize it your way!</i>
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

## ⚡ Overview

**SoundGravity** is a sleek, modern desktop utility featuring a dark cyberpunk UI designed to effortlessly replace and fine-tune notification sounds in **Google Antigravity**:
1. **Task Completion Sound** (*when Antigravity finishes generating / executing*)
2. **Action Required Sound** (*when user intervention or approval is required*)

It seamlessly discovers your installed Antigravity `language_server.exe` and patches the audio tracks safely while preserving the application's integrity.

---

## ✨ Features

- 🎧 **Built-in Sound Presets:**
  - **Cyberpunk** — Futuristic neon synth vibe
  - **Original** — Default classic Antigravity sounds
  - **Minimal** — Short, unobtrusive, clean notification
  - **Retro 8-Bit Arcade** — Nostalgic arcade game chiptune sound
- 🎙️ **Built-in AI Voice Generation (Neural Edge TTS):**
  - Synthesize custom completion phrases (e.g. *"Task completed, ready for review"* or *"Gemini has finished your project"*)
  - High-quality natural neural voices:
    - **English (EN):** Andrew, Ava, Aria, Guy (`Multilingual Neural`)
    - **Ukrainian (UA):** Ostap (`OstapNeural`), Polina (`PolinaNeural`)
    - **Russian (RU):** Dmitry (`DmitryNeural`), Svetlana (`SvetlanaNeural`)
  - Real-time rate and volume sliders with instant audio preview.
- 📁 **Custom Audio Files:** Choose any `.mp3` or `.wav` file directly from your local storage.
- 🔊 **Individual Volume Control:** Independent smooth volume tracks (0% to 100%) for both completion and action sounds.
- 🔄 **Auto-Patch on Updates:** Automatically re-applies your selected audio setup when Google Antigravity updates.
- 🌐 **Trilingual Interface:** Instant seamless switching between **EN**, **UA**, and **RU** with animated pill slider.
- 📦 **100% Standalone Portable:** Single `.exe` binary without requiring Python, compilers, or external dependencies.

---

## 🚀 Installation & Usage

### Option 1: Standalone `.exe` (Recommended)
1. Download the latest `SoundGravity.exe` from [Releases](../../releases).
2. Run the executable directly. No setup or installer required!
3. Pick your desired sound or generate speech with TTS, adjust volume, and click "Apply".

### Option 2: Running from Source

Requires **Python 3.10+**.

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/SoundGravity.git
   cd SoundGravity
   ```

2. Install dependencies:
   ```bash
   pip install pillow edge-tts pywin32
   ```

3. Launch the application:
   ```bash
   python src/app.py
   ```

---

## 🛠️ Building Standalone Exe

To compile into a standalone single-file binary with **PyInstaller**:

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
The resulting executable will be available at `dist/SoundGravity.exe`.

---

## 📂 Project Structure

```text
SoundGravity/
├── assets/                  # App icon, vector graphics, and fonts
│   ├── icon.ico
│   ├── icon.png
│   └── ...
├── presets/                 # Built-in sound packs
│   ├── Cyberpunk/
│   ├── Original/
│   ├── Minimal/
│   └── Arcade/
├── src/                     # Source files
│   ├── app.py               # Main GUI (Tkinter Canvas with custom vector drawing)
│   ├── patcher.py           # Discovery and binary audio patching logic
│   └── watcher.py           # Background update monitoring service
├── README.md                # Russian documentation
├── README.ua.md             # Ukrainian documentation
├── README.en.md             # English documentation
└── LICENSE                  # MIT License
```

---

## 💖 Support the Developer

If you find SoundGravity helpful and want to support ongoing development:

- 💬 **DonationAlerts:** [dalink.to/reeshkaii](https://dalink.to/reeshkaii)
- 🤍 **Donatello:** [donatello.to/Reeshkaii](https://donatello.to/Reeshkaii)

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
