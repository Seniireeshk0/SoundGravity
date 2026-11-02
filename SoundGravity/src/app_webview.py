import os
import sys
import json
import base64
import tkinter as tk
from tkinter import filedialog
import webview

# Import patcher & watcher
from patcher import find_language_server, patch_language_server_exe
from watcher import load_config, save_config, UpdateWatcher

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            p = os.path.join(sys._MEIPASS, relative_path)
            if os.path.exists(p):
                return p
        p = os.path.join(os.path.dirname(sys.executable), relative_path)
        if os.path.exists(p):
            return p
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root_dir, relative_path)

# Prepare embedded font and icon in base64
FONT_TTF_PATH = get_resource_path(os.path.join('assets', 'Unbounded-Variable.ttf'))
with open(FONT_TTF_PATH, 'rb') as f:
    FONT_BASE64 = base64.b64encode(f.read()).decode('ascii')

ICON_PNG_PATH = get_resource_path(os.path.join('assets', 'icon.png'))
with open(ICON_PNG_PATH, 'rb') as f:
    ICON_BASE64 = base64.b64encode(f.read()).decode('ascii')

HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
@font-face {{
  font-family: 'Unbounded';
  src: url('data:font/truetype;charset=utf-8;base64,{FONT_BASE64}') format('truetype');
  font-weight: 100 900;
  font-style: normal;
}}

* {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  user-select: none;
  -webkit-user-select: none;
}}

body, html {{
  width: 506px;
  height: 311px;
  overflow: hidden;
  background-color: #000000;
  font-family: 'Unbounded', sans-serif;
  color: #FFFFFF;
  position: relative;
}}

/* Custom Window Drag Titlebar if frameless, or draggable canvas */
.titlebar {{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 35px;
  -webkit-app-region: drag;
  z-index: 50;
}}

.no-drag {{
  -webkit-app-region: no-drag;
}}

/* Moving Neon Lines Canvas */
#lines-canvas {{
  position: absolute;
  top: 0;
  left: 0;
  width: 506px;
  height: 311px;
  z-index: 1;
  pointer-events: none;
}}

/* Main Title "SoundGravity" */
.main-title {{
  position: absolute;
  left: 15px;
  top: 12px;
  font-size: 20px;
  font-weight: 400;
  line-height: 25px;
  color: #FFFFFF;
  z-index: 10;
  letter-spacing: -0.02em;
}}

/* Subtitle Block */
.subtitle-block {{
  position: absolute;
  left: 16px;
  top: 43px;
  font-size: 16px;
  font-weight: 400;
  line-height: 22px;
  color: #FFFFFF;
  z-index: 10;
  max-width: 374px;
}}

/* Language Switcher Container: x=362, y=13, w=97, h=24, r=12, bg=#131313 */
.lang-container {{
  position: absolute;
  left: 362px;
  top: 13px;
  width: 97px;
  height: 24px;
  background: #131313;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2.5px 3px;
  z-index: 20;
}}

.lang-btn {{
  width: 28px;
  height: 19px;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 400;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  cursor: pointer;
  background: transparent;
  transition: all 0.15s ease;
}}

.lang-btn.active {{
  border: 1px solid #FFFFFF;
  background: #272727;
}}

.lang-btn:hover:not(.active) {{
  background: #1e1e1e;
}}

/* Section 1: Completion Sound */
.label-done {{
  position: absolute;
  left: 15px;
  top: 126px;
  font-size: 14px;
  font-weight: 400;
  line-height: 18px;
  color: #FFFFFF;
  z-index: 10;
}}

.btn-done {{
  position: absolute;
  left: 16px;
  top: 166px;
  width: 104px;
  height: 20px;
  background: #131313;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 400;
  color: #FFFFFF;
  cursor: pointer;
  z-index: 20;
  transition: background 0.15s ease, transform 0.05s ease;
}}

.btn-done:hover, .btn-action:hover {{
  background: #222222;
}}

.btn-done:active, .btn-action:active {{
  transform: scale(0.97);
}}

/* Section 2: Action Required Sound */
.label-action {{
  position: absolute;
  left: 15px;
  top: 194px;
  font-size: 14px;
  font-weight: 400;
  line-height: 18px;
  color: #FFFFFF;
  z-index: 10;
}}

.btn-action {{
  position: absolute;
  left: 16px;
  top: 252px;
  width: 104px;
  height: 20px;
  background: #131313;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 400;
  color: #FFFFFF;
  cursor: pointer;
  z-index: 20;
  transition: background 0.15s ease, transform 0.05s ease;
}}

/* Version Tag: x=459, y=287, size=14 */
.version-tag {{
  position: absolute;
  left: 459px;
  top: 287px;
  font-size: 14px;
  font-weight: 400;
  color: #FFFFFF;
  z-index: 10;
}}

/* Modal / Dropdown Dialog for choosing sound presets */
.modal-overlay {{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: none;
  align-items: center;
  justify-content: center;
}}

.modal-content {{
  width: 320px;
  background: #111113;
  border: 1px solid #28282D;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.8);
}}

.modal-header {{
  font-size: 13px;
  font-weight: 500;
  color: #FFFFFF;
  margin-bottom: 12px;
  text-align: center;
}}

.preset-item {{
  display: flex;
  align-items: center;
  padding: 7px 10px;
  margin-bottom: 5px;
  background: #18181C;
  border-radius: 7px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.15s ease;
}}

.preset-item:hover {{
  background: #24242A;
}}

.preset-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 10px;
}}

.custom-file-btn {{
  margin-top: 10px;
  padding: 8px;
  background: #202026;
  border-radius: 7px;
  text-align: center;
  font-size: 12px;
  cursor: pointer;
  color: #8CFF00;
  transition: background 0.15s;
}}

.custom-file-btn:hover {{
  background: #2A2A34;
}}

/* Toast Notification */
.toast {{
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: #161619;
  border: 1px solid #8CFF00;
  color: #FFFFFF;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 11px;
  z-index: 200;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}}

.toast.show {{
  opacity: 1;
}}
</style>
</head>
<body>

<canvas id="lines-canvas" width="506" height="311"></canvas>

<div class="main-title">SoundGravity</div>

<!-- Language Switcher -->
<div class="lang-container no-drag">
  <div class="lang-btn" id="btn-en" onclick="setLang('EN')">EN</div>
  <div class="lang-btn" id="btn-ua" onclick="setLang('UA')">UA</div>
  <div class="lang-btn" id="btn-ru" onclick="setLang('RU')">RU</div>
</div>

<!-- Subtitle -->
<div class="subtitle-block" id="txt-subtitle">
  Не нравится звук окончания работы<br>Antigravity?<br>Настрой под себя!
</div>

<!-- Section 1: Completion Sound -->
<div class="label-done" id="txt-label-done">
  Звук завершения<br>работы:
</div>
<div class="btn-done no-drag" id="btn-select-done" onclick="openPicker('done')">
  Выбрать
</div>

<!-- Section 2: Action Sound -->
<div class="label-action" id="txt-label-action">
  Звук при<br>необходимости<br>вмешаться:
</div>
<div class="btn-action no-drag" id="btn-select-action" onclick="openPicker('action')">
  Выбрать
</div>

<!-- Version Tag -->
<div class="version-tag">1.0.0</div>

<!-- Preset Selection Modal -->
<div class="modal-overlay" id="modal-overlay" onclick="closeModal(event)">
  <div class="modal-content" onclick="event.stopPropagation()">
    <div class="modal-header" id="modal-title">Выберите звук</div>
    
    <div class="preset-item" onclick="choosePreset('Cyberpunk')">
      <div class="preset-dot" style="background: #9900FF;"></div>
      <span id="txt-preset-cyber">Cyberpunk (Новый)</span>
    </div>

    <div class="preset-item" onclick="choosePreset('Original')">
      <div class="preset-dot" style="background: #555555;"></div>
      <span id="txt-preset-orig">Оригинал (Стандарт)</span>
    </div>

    <div class="preset-item" onclick="choosePreset('Minimal')">
      <div class="preset-dot" style="background: #8CFF00;"></div>
      <span id="txt-preset-mini">Minimal (Короткий)</span>
    </div>

    <div class="preset-item" onclick="choosePreset('Arcade')">
      <div class="preset-dot" style="background: #00CCFF;"></div>
      <span id="txt-preset-arcade">Retro 8-Bit Arcade</span>
    </div>

    <div class="custom-file-btn" onclick="chooseCustomFile()">
      📁 <span id="txt-custom-btn">Выбрать свой файл...</span>
    </div>
  </div>
</div>

<div class="toast" id="toast">Звук успешно применен!</div>

<script>
let currentLang = 'RU';
let currentTarget = 'done'; // 'done' or 'action'

const TRANSLATIONS = {{
  RU: {{
    subtitle: "Не нравится звук окончания работы<br>Antigravity?<br>Настрой под себя!",
    done: "Звук завершения<br>работы:",
    action: "Звук при<br>необходимости<br>вмешаться:",
    select: "Выбрать",
    modal_done: "Выбор звука завершения",
    modal_action: "Выбор звука действия",
    p_cyber: "Cyberpunk (Новый)",
    p_orig: "Оригинал (Стандарт)",
    p_mini: "Minimal (Короткий)",
    p_arcade: "Retro 8-Bit Arcade",
    custom: "Выбрать свой файл...",
    applied: "Звук успешно применен!"
  }},
  UA: {{
    subtitle: "Не подобається звук закінчення роботи<br>Antigravity?<br>Налаштуй під себе!",
    done: "Звук завершення<br>роботи:",
    action: "Звук при<br>необхідності<br>втручання:",
    select: "Вибрати",
    modal_done: "Вибір звуку завершення",
    modal_action: "Вибір звуку дії",
    p_cyber: "Cyberpunk (Новий)",
    p_orig: "Оригінал (Стандарт)",
    p_mini: "Minimal (Короткий)",
    p_arcade: "Retro 8-Bit Arcade",
    custom: "Обрати власний файл...",
    applied: "Звук успішно застосовано!"
  }},
  EN: {{
    subtitle: "Don't like the finish sound<br>of Antigravity?<br>Customize it for yourself!",
    done: "Sound for task<br>completion:",
    action: "Sound when<br>action is<br>needed:",
    select: "Select",
    modal_done: "Select Completion Sound",
    modal_action: "Select Action Sound",
    p_cyber: "Cyberpunk (New)",
    p_orig: "Original (Default)",
    p_mini: "Minimal (Short)",
    p_arcade: "Retro 8-Bit Arcade",
    custom: "Choose custom file...",
    applied: "Sound applied successfully!"
  }}
}};

function setLang(lang) {{
  currentLang = lang;
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + lang.toLowerCase()).classList.add('active');

  const t = TRANSLATIONS[lang];
  document.getElementById('txt-subtitle').innerHTML = t.subtitle;
  document.getElementById('txt-label-done').innerHTML = t.done;
  document.getElementById('txt-label-action').innerHTML = t.action;
  document.getElementById('btn-select-done').innerText = t.select;
  document.getElementById('btn-select-action').innerText = t.select;
  document.getElementById('txt-preset-cyber').innerText = t.p_cyber;
  document.getElementById('txt-preset-orig').innerText = t.p_orig;
  document.getElementById('txt-preset-mini').innerText = t.p_mini;
  document.getElementById('txt-preset-arcade').innerText = t.p_arcade;
  document.getElementById('txt-custom-btn').innerText = t.custom;

  if (window.pywebview && window.pywebview.api) {{
    window.pywebview.api.save_language(lang);
  }}
}}

function openPicker(target) {{
  currentTarget = target;
  const t = TRANSLATIONS[currentLang];
  document.getElementById('modal-title').innerText = target === 'done' ? t.modal_done : t.modal_action;
  document.getElementById('modal-overlay').style.display = 'flex';
}}

function closeModal(e) {{
  document.getElementById('modal-overlay').style.display = 'none';
}}

function choosePreset(name) {{
  document.getElementById('modal-overlay').style.display = 'none';
  if (window.pywebview && window.pywebview.api) {{
    window.pywebview.api.apply_preset(name, currentTarget).then(res => {{
      showToast(res || TRANSLATIONS[currentLang].applied);
    }});
  }}
}}

function chooseCustomFile() {{
  document.getElementById('modal-overlay').style.display = 'none';
  if (window.pywebview && window.pywebview.api) {{
    window.pywebview.api.choose_file(currentTarget).then(res => {{
      if (res) showToast(res);
    }});
  }}
}}

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.innerText = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}}

// Initialize Canvas Animation
const canvas = document.getElementById('lines-canvas');
const ctx = canvas.getContext('2d');
let t = 0;

function drawLines() {{
  ctx.clearRect(0, 0, 506, 311);
  t += 0.03;

  // Purple Line: #9900FF
  // Base: (506, 2) down to (344, 311)
  const px1 = 506;
  const py1 = 2 + 15 * Math.sin(t * 0.9);
  const px2 = 344 + 25 * Math.cos(t * 0.7);
  const py2 = 311;

  ctx.beginPath();
  ctx.moveTo(px1, py1);
  ctx.lineTo(px2, py2);
  ctx.strokeStyle = '#9900FF';
  ctx.lineWidth = 1.8;
  ctx.stroke();

  // Green Line: #8CFF00
  // Base: (506, 273) to (254, 174)
  const gx1 = 506;
  const gy1 = 273 + 12 * Math.cos(t * 1.1);
  const gx2 = 254 + 20 * Math.sin(t * 0.8);
  const gy2 = 174 + 15 * Math.cos(t * 0.6);

  ctx.beginPath();
  ctx.moveTo(gx1, gy1);
  ctx.lineTo(gx2, gy2);
  ctx.strokeStyle = '#8CFF00';
  ctx.lineWidth = 1.8;
  ctx.stroke();

  requestAnimationFrame(drawLines);
}}

drawLines();
setLang('RU');
</script>
</body>
</html>
"""

class Api:
    def __init__(self, watcher):
        self.watcher = watcher
        self.cfg = load_config()

    def save_language(self, lang):
        self.cfg["language"] = lang
        save_config(self.cfg)

    def apply_preset(self, preset_name, sound_type):
        filename = "done.mp3" if sound_type == "done" else "action.mp3"
        preset_file = get_resource_path(os.path.join('presets', preset_name, filename))

        if not os.path.exists(preset_file):
            return "Ошибка: файл пресета не найден"

        ls_path = find_language_server()
        if not ls_path:
            return "Ошибка: Antigravity не обнаружен"

        try:
            with open(preset_file, 'rb') as f:
                audio_bytes = f.read()

            done_bytes = audio_bytes if sound_type == "done" else None
            action_bytes = audio_bytes if sound_type == "action" else None

            if sound_type == "done":
                self.cfg["custom_done_sound"] = preset_file
            else:
                self.cfg["custom_action_sound"] = preset_file
            save_config(self.cfg)

            patch_language_server_exe(ls_path, done_bytes, action_bytes)
            return f"Применено: {preset_name}"
        except Exception as e:
            return f"Ошибка: {e}"

    def choose_file(self, sound_type):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        fpath = filedialog.askopenfilename(
            title="Выберите звуковой файл",
            filetypes=[("Audio Files (*.mp3;*.wav)", "*.mp3;*.wav"), ("MP3 Files", "*.mp3"), ("WAV Files", "*.wav"), ("All Files", "*.*")]
        )
        root.destroy()

        if not fpath:
            return ""

        ls_path = find_language_server()
        if not ls_path:
            return "Ошибка: Antigravity не обнаружен"

        try:
            with open(fpath, 'rb') as f:
                audio_bytes = f.read()

            done_bytes = audio_bytes if sound_type == "done" else None
            action_bytes = audio_bytes if sound_type == "action" else None

            if sound_type == "done":
                self.cfg["custom_done_sound"] = fpath
            else:
                self.cfg["custom_action_sound"] = fpath
            save_config(self.cfg)

            patch_language_server_exe(ls_path, done_bytes, action_bytes)
            return "Файл успешно применен!"
        except Exception as e:
            return f"Ошибка: {e}"

def main():
    watcher = UpdateWatcher()
    watcher.start()

    api = Api(watcher)
    window = webview.create_window(
        title='SoundGravity',
        html=HTML_TEMPLATE,
        js_api=api,
        width=506,
        height=311,
        resizable=False,
        background_color='#000000',
        text_select=False
    )
    webview.start(debug=False)

if __name__ == '__main__':
    main()
