import os
import sys
import math
import json
import ctypes
import re
import asyncio

# Set AppUserModelID so Windows Taskbar associates windows with this app and displays icon.ico instead of feather
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("antigravity.soundgravity.app.1.0")
except Exception:
    pass

import tkinter as tk
from tkinter import filedialog, font as tkFont
from PIL import Image, ImageDraw, ImageFont, ImageTk

# Import patcher & watcher
from patcher import find_language_server, patch_language_server_exe, adjust_audio_volume
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

def load_system_font():
    font_path = get_resource_path(os.path.join('assets', 'Unbounded-Variable.ttf'))
    if os.path.exists(font_path):
        try:
            ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
        except:
            pass

def draw_vector_icon(icon_type, color='#C084FC', size=24, factor=2):
    s = size * factor
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    stroke = max(2, int(3.0 * factor))

    if icon_type in ('lightning', 'cyberpunk'):
        pts = [
            (int(s * 0.58), int(s * 0.04)),
            (int(s * 0.20), int(s * 0.52)),
            (int(s * 0.48), int(s * 0.52)),
            (int(s * 0.38), int(s * 0.96)),
            (int(s * 0.84), int(s * 0.44)),
            (int(s * 0.54), int(s * 0.44))
        ]
        d.polygon(pts, fill=color)

    elif icon_type in ('bell', 'original'):
        d.arc((int(s * 0.40), int(s * 0.05), int(s * 0.60), int(s * 0.23)), start=180, end=0, fill=color, width=max(2, int(2.5 * factor)))
        bell_pts = [
            (int(s * 0.35), int(s * 0.22)),
            (int(s * 0.65), int(s * 0.22)),
            (int(s * 0.74), int(s * 0.62)),
            (int(s * 0.84), int(s * 0.74)),
            (int(s * 0.16), int(s * 0.74)),
            (int(s * 0.26), int(s * 0.62))
        ]
        d.polygon(bell_pts, fill=color)
        d.ellipse((int(s * 0.42), int(s * 0.76), int(s * 0.58), int(s * 0.92)), fill=color)

    elif icon_type in ('waves', 'minimal'):
        bar_w = max(int(2.5 * factor), int(s * 0.13))
        r = bar_w // 2
        cx = s // 2
        d.rounded_rectangle((cx - bar_w // 2, int(s * 0.10), cx + bar_w // 2, int(s * 0.90)), radius=r, fill=color)
        lx = cx - int(s * 0.28)
        d.rounded_rectangle((lx - bar_w // 2, int(s * 0.26), lx + bar_w // 2, int(s * 0.74)), radius=r, fill=color)
        rx = cx + int(s * 0.28)
        d.rounded_rectangle((rx - bar_w // 2, int(s * 0.26), rx + bar_w // 2, int(s * 0.74)), radius=r, fill=color)

    elif icon_type in ('gamepad', 'arcade'):
        body_top = int(s * 0.26)
        body_bot = int(s * 0.74)
        d.rounded_rectangle((int(s * 0.08), body_top, int(s * 0.92), body_bot), radius=int(6 * factor), fill=color)
        dark_col = "#151022"
        cx_l = int(s * 0.32)
        cy = s // 2
        arm = int(s * 0.14)
        thick = max(int(2 * factor), int(s * 0.09))
        d.rectangle((cx_l - arm, cy - thick // 2, cx_l + arm, cy + thick // 2), fill=dark_col)
        d.rectangle((cx_l - thick // 2, cy - arm, cx_l + thick // 2, cy + arm), fill=dark_col)
        cx_r = int(s * 0.68)
        btn_r = int(s * 0.065)
        d.ellipse((cx_r - btn_r, cy - int(s * 0.09) - btn_r, cx_r + btn_r, cy - int(s * 0.09) + btn_r), fill=dark_col)
        d.ellipse((cx_r + int(s * 0.10) - btn_r, cy + int(s * 0.04) - btn_r, cx_r + int(s * 0.10) + btn_r, cy + int(s * 0.04) + btn_r), fill=dark_col)

    elif icon_type == 'mic':
        cw = int(s * 0.50)
        ch = int(s * 0.54)
        cx = (s - cw) // 2
        cy = int(s * 0.04)
        r = cw // 2
        d.rounded_rectangle((cx, cy, cx + cw, cy + ch), radius=r, fill=color)
        arc_pad = int(s * 0.12)
        d.arc((cx - arc_pad, cy + int(ch * 0.20), cx + cw + arc_pad, cy + ch + arc_pad), start=0, end=180, fill=color, width=stroke)
        stem_top = cy + ch + arc_pad
        stem_bot = stem_top + int(s * 0.15)
        d.line(((s // 2, stem_top), (s // 2, stem_bot)), fill=color, width=stroke)
        base_w = int(s * 0.58)
        d.line(((s // 2 - base_w // 2, stem_bot), (s // 2 + base_w // 2, stem_bot)), fill=color, width=stroke)

    elif icon_type == 'folder':
        p = int(s * 0.06)
        tab_w = int(s * 0.44)
        tab_h = int(s * 0.26)
        d.rounded_rectangle((p, p, p + tab_w, p + tab_h), radius=int(4 * factor), fill=color)
        body_top = p + int(s * 0.15)
        d.rounded_rectangle((p, body_top, s - p, s - p), radius=int(5 * factor), fill=color)
        d.line((p + int(5 * factor), body_top + int(6 * factor), s - p - int(5 * factor), body_top + int(6 * factor)), fill='#181424', width=stroke)

    elif icon_type == 'speaker':
        p = int(s * 0.05)
        box_w = int(s * 0.26)
        box_h = int(s * 0.50)
        cy = s // 2
        d.rectangle((p, cy - box_h // 2, p + box_w, cy + box_h // 2), fill=color)
        d.polygon([
            (p + box_w, cy - box_h // 2),
            (int(s * 0.60), int(s * 0.08)),
            (int(s * 0.60), s - int(s * 0.08)),
            (p + box_w, cy + box_h // 2)
        ], fill=color)
        d.arc((int(s * 0.46), int(s * 0.22), int(s * 0.76), s - int(s * 0.22)), start=-60, end=60, fill=color, width=stroke)
        d.arc((int(s * 0.56), int(s * 0.08), s - p, s - int(s * 0.08)), start=-60, end=60, fill=color, width=stroke)

    elif icon_type == 'check':
        p = int(s * 0.08)
        d.line([
            (p, int(s * 0.52)),
            (int(s * 0.38), s - int(s * 0.16)),
            (s - p, int(s * 0.14))
        ], fill=color, width=int(3.2 * factor), joint='curve')

    elif icon_type == 'dot':
        r = s * 0.36
        cx, cy = s / 2, s / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)

    elif icon_type == 'donatello':
        # Vibrant heart with white coin drop slot
        cx = s / 2.0
        top_y = s * 0.16
        bot_y = s * 0.88
        r = s * 0.23
        d.ellipse((cx - 2 * r, top_y, cx, top_y + 2 * r), fill=color)
        d.ellipse((cx, top_y, cx + 2 * r, top_y + 2 * r), fill=color)
        d.polygon([
            (cx - 1.95 * r, top_y + r * 0.95),
            (cx + 1.95 * r, top_y + r * 0.95),
            (cx, bot_y)
        ], fill=color)
        slot_w = int(s * 0.26)
        slot_h = max(2, int(3.5 * factor))
        slot_y = int(top_y + r * 0.65)
        d.rounded_rectangle((cx - slot_w // 2, slot_y, cx + slot_w // 2, slot_y + slot_h), radius=slot_h//2, fill="#FFFFFF")

    elif icon_type == 'donationalerts':
        # Rounded chat bubble with exclamation mark
        bw = int(s * 0.82)
        bh = int(s * 0.66)
        bx = (s - bw) // 2
        by = int(s * 0.10)
        r = int(6.5 * factor)
        d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=r, fill=color)
        tail = [
            (bx + int(bw * 0.18), by + bh - 1),
            (bx + int(bw * 0.42), by + bh - 1),
            (bx + int(bw * 0.08), by + bh + int(s * 0.18))
        ]
        d.polygon(tail, fill=color)
        cx = bx + bw // 2
        top_ex = by + int(bh * 0.18)
        bot_ex = top_ex + int(bh * 0.40)
        ex_w = max(2, int(3.0 * factor))
        d.line([(cx, top_ex), (cx, bot_ex)], fill="#FFFFFF", width=ex_w)
        dot_r = max(2, int(1.8 * factor))
        dot_y = bot_ex + int(bh * 0.22)
        d.ellipse((cx - dot_r, dot_y - dot_r, cx + dot_r, dot_y + dot_r), fill="#FFFFFF")

    return img.resize((size, size), Image.Resampling.LANCZOS)

TRANSLATIONS = {
    "RU": {
        "title": "SoundGravity",
        "header_1": "Не нравится звук окончания работы",
        "header_2": "Antigravity?",
        "header_3": "Настрой под себя!",
        "sound_done": "Звук завершения работы:",
        "sound_action": "Звук при необходимости вмешаться:",
        "btn_select": "Выбрать",
        "popup_title_done": "Выбор звука завершения",
        "popup_title_action": "Выбор звука действия",
        "preset_cyberpunk": "Cyberpunk (Новый)",
        "preset_original": "Оригинал (Стандарт)",
        "preset_minimal": "Minimal (Короткий)",
        "preset_arcade": "Retro 8-Bit Arcade",
        "custom_file": "Выбрать свой файл (.mp3 / .wav)",
        "custom_file_tag": "Свой файл",
        "tts_btn": "Озвучить текст (TTS)",
        "tts_title": "Генерация звука (TTS)",
        "tts_prompt": "Введите текст для озвучивания:",
        "tts_placeholder": "Задача выполнена!",
        "tts_volume_label": "Громкость:",
        "tts_speed_label": "Скорость речи:",
        "tts_voice_label": "Голос / Язык:",
        "tts_voice_auto": "Авто (По тексту)",
        "tts_display_tag": "Озвучка",
        "tts_generate_btn": "▶ Сгенерировать и прослушать",
        "preview_btn": "▶ Прослушать",
        "apply_btn": "Применить",
        "preview_custom_title": "Предпросмотр файла",
        "preview_custom_msg": "Выбран файл:\n{name}\n\nВы можете прослушать его перед установкой:",
        "auto_patch_label": "Авто-обновление звуков при обновлении Antigravity",
        "sound_volume_label": "Громкость:",
        "menu_copy": "Копировать",
        "menu_paste": "Вставить",
        "menu_cut": "Вырезать",
        "menu_select_all": "Выделить всё",
        "success_title": "Успешно!",
        "success_msg": "Звук успешно применен в Antigravity!",
        "error_title": "Ошибка",
        "not_found": "Не удалось обнаружить установленный Antigravity.",
        "file_missing": "Файлы пресета не найдены."
    },
    "UA": {
        "title": "SoundGravity",
        "header_1": "Не подобається звук закінчення роботи",
        "header_2": "Antigravity?",
        "header_3": "Налаштуй під себе!",
        "sound_done": "Звук завершення роботи:",
        "sound_action": "Звук при необхідності втручання:",
        "btn_select": "Вибрати",
        "popup_title_done": "Вибір звуку завершення",
        "popup_title_action": "Вибір звуку дії",
        "preset_cyberpunk": "Cyberpunk (Новий)",
        "preset_original": "Оригінал (Стандарт)",
        "preset_minimal": "Minimal (Короткий)",
        "preset_arcade": "Retro 8-Bit Arcade",
        "custom_file": "Обрати власний файл (.mp3 / .wav)",
        "custom_file_tag": "Власний файл",
        "tts_btn": "Озвучити текст (TTS)",
        "tts_title": "Генерація звуку (TTS)",
        "tts_prompt": "Введіть текст для озвучування:",
        "tts_placeholder": "Завдання виконано!",
        "tts_volume_label": "Гучність:",
        "tts_speed_label": "Швидкість мовлення:",
        "tts_voice_label": "Голос / Мова:",
        "tts_voice_auto": "Авто (За текстом)",
        "tts_display_tag": "Озвучення",
        "tts_generate_btn": "▶ Згенерувати та прослухати",
        "preview_btn": "▶ Прослухати",
        "apply_btn": "Застосувати",
        "preview_custom_title": "Попередній перегляд файлу",
        "preview_custom_msg": "Обрано файл:\n{name}\n\nВи можете прослухати його перед встановленням:",
        "auto_patch_label": "Авто-оновлення звуків після оновлень Antigravity",
        "sound_volume_label": "Гучність:",
        "menu_copy": "Копіювати",
        "menu_paste": "Вставити",
        "menu_cut": "Вирізати",
        "menu_select_all": "Виділити все",
        "success_title": "Успішно!",
        "success_msg": "Звук успішно застосовано в Antigravity!",
        "error_title": "Помилка",
        "not_found": "Не вдалося виявити встановлений Antigravity.",
        "file_missing": "Файли пресету не знайдено."
    },
    "EN": {
        "title": "SoundGravity",
        "header_1": "Don't like the finish sound",
        "header_2": "of Antigravity?",
        "header_3": "Customize it for yourself!",
        "sound_done": "Sound for task completion:",
        "sound_action": "Sound when action is needed:",
        "btn_select": "Select",
        "popup_title_done": "Select Completion Sound",
        "popup_title_action": "Select Action Sound",
        "preset_cyberpunk": "Cyberpunk (New)",
        "preset_original": "Original (Default)",
        "preset_minimal": "Minimal (Short)",
        "preset_arcade": "Retro 8-Bit Arcade",
        "custom_file": "Choose custom file (.mp3 / .wav)",
        "custom_file_tag": "Custom file",
        "tts_btn": "Voice Synthesis (TTS)",
        "tts_title": "Voice Synthesis (TTS)",
        "tts_prompt": "Enter text to speak:",
        "tts_placeholder": "Task completed successfully!",
        "tts_volume_label": "Volume:",
        "tts_speed_label": "Speech rate:",
        "tts_voice_label": "Voice / Language:",
        "tts_voice_auto": "Auto (By text)",
        "tts_display_tag": "Speech",
        "tts_generate_btn": "▶ Generate & Listen",
        "preview_btn": "▶ Preview",
        "apply_btn": "Apply",
        "preview_custom_title": "Custom File Preview",
        "preview_custom_msg": "Selected file:\n{name}\n\nYou can listen to it before installing:",
        "auto_patch_label": "Auto-restore custom sounds after Antigravity updates",
        "sound_volume_label": "Volume:",
        "menu_copy": "Copy",
        "menu_paste": "Paste",
        "menu_cut": "Cut",
        "menu_select_all": "Select All",
        "success_title": "Success!",
        "success_msg": "Sound successfully applied to Antigravity!",
        "error_title": "Error",
        "not_found": "Antigravity installation was not found.",
        "file_missing": "Preset files missing."
    }
}

_rounded_img_cache = {}

def get_rounded_rect_image(w, h, r, fill_color, outline_color=None, outline_width=1):
    cache_key = (w, h, r, fill_color, outline_color, outline_width)
    if cache_key in _rounded_img_cache:
        return _rounded_img_cache[cache_key]

    factor = 2
    img = Image.new('RGBA', (w * factor, h * factor), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if outline_color:
        draw.rounded_rectangle(
            (0, 0, w * factor - 1, h * factor - 1),
            radius=r * factor,
            fill=fill_color,
            outline=outline_color,
            width=outline_width * factor
        )
    else:
        draw.rounded_rectangle(
            (0, 0, w * factor - 1, h * factor - 1),
            radius=r * factor,
            fill=fill_color
        )
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    res = ImageTk.PhotoImage(img)
    _rounded_img_cache[cache_key] = res
    return res

def create_rounded_pill_button(parent, text, width, height, radius, bg_norm, border_norm, bg_hov, border_hov, fg_norm, fg_hov, command, font=("Unbounded", 9, "bold")):
    """Creates a 100% anti-aliased vector rounded pill button with hover transitions."""
    try:
        f = tkFont.Font(font=font)
        text_w = f.measure(text)
        width = max(width, text_w + 48)
    except Exception:
        pass
    img_n = get_rounded_rect_image(width, height, radius, bg_norm, border_norm, 1)
    img_h = get_rounded_rect_image(width, height, radius, bg_hov, border_hov, 1)

    cv = tk.Canvas(parent, width=width, height=height, bg=parent.cget("bg"), highlightthickness=0, bd=0, cursor="hand2")
    bg_it = cv.create_image(0, 0, anchor="nw", image=img_n)
    tx_it = cv.create_text(width // 2, height // 2, anchor="center", text=text, fill=fg_norm, font=font)

    cv._img_n = img_n
    cv._img_h = img_h

    def on_enter(e):
        cv.itemconfig(bg_it, image=img_h)
        cv.itemconfig(tx_it, fill=fg_hov)

    def on_leave(e):
        cv.itemconfig(bg_it, image=img_n)
        cv.itemconfig(tx_it, fill=fg_norm)

    def on_click(e):
        if command:
            command()

    cv.bind("<Enter>", on_enter)
    cv.bind("<Leave>", on_leave)
    cv.bind("<Button-1>", on_click)
    return cv

class ModernCanvasSlider(tk.Canvas):
    """
    Sleek custom-drawn vector slider replacing glitchy Win32 tk.Scale.
    Features:
    - Rounded background track (#1F1B2C)
    - Electric purple fill (#A855F7)
    - White circle thumb with lilac-purple outline (#FFFFFF / #C084FC)
    - Smooth click-to-seek, drag, and release
    - Boundary checking and integer/step snapping
    - Responsive to parent width via <Configure>
    """
    def __init__(self, master, from_=0, to=100, initial=100, on_change=None, height=24, bg="#000000", track_color="#1F1B2C", fill_color="#A855F7", knob_color="#FFFFFF", knob_border="#C084FC", margin_x=30, **kw):
        super().__init__(master, height=height, bg=bg, highlightthickness=0, bd=0, cursor="hand2", **kw)
        self.from_ = float(from_)
        self.to = float(to)
        self.value = float(initial)
        self.on_change = on_change
        self.track_color = track_color
        self.fill_color = fill_color
        self.knob_color = knob_color
        self.knob_border = knob_border
        
        self.margin_x = margin_x
        self.track_y = height // 2
        self.track_w = 200

        self.track_bg = self.create_line(
            self.margin_x, self.track_y, self.margin_x + self.track_w, self.track_y,
            fill=self.track_color, width=6, capstyle="round"
        )
        self.track_fill = self.create_line(
            self.margin_x, self.track_y, self.margin_x, self.track_y,
            fill=self.fill_color, width=6, capstyle="round"
        )
        r = 7
        self.knob = self.create_oval(
            self.margin_x - r, self.track_y - r, self.margin_x + r, self.track_y + r,
            fill=self.knob_color, outline=self.knob_border, width=2
        )

        self._dragging = False
        self.bind("<Configure>", self._on_configure)
        self.bind("<Button-1>", self._on_mouse_down)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<ButtonRelease-1>", self._on_mouse_up)

        self.set(initial, trigger_callback=False)

    def _on_configure(self, event):
        if event.width > 30:
            self.track_w = max(20, event.width - 2 * self.margin_x)
            self.coords(self.track_bg, self.margin_x, self.track_y, self.margin_x + self.track_w, self.track_y)
            self._render()

    def _val_to_x(self, val):
        if self.to == self.from_:
            return self.margin_x
        ratio = (val - self.from_) / (self.to - self.from_)
        ratio = max(0.0, min(1.0, ratio))
        return self.margin_x + (self.track_w * ratio)

    def _x_to_val(self, x):
        if self.track_w <= 0 or self.to == self.from_:
            return self.from_
        ratio = (x - self.margin_x) / self.track_w
        ratio = max(0.0, min(1.0, ratio))
        val = self.from_ + ratio * (self.to - self.from_)
        return round(val)

    def _render(self):
        kx = self._val_to_x(self.value)
        r = 7
        if kx <= self.margin_x + 1:
            self.itemconfigure(self.track_fill, state="hidden")
        else:
            self.itemconfigure(self.track_fill, state="normal")
            self.coords(self.track_fill, self.margin_x, self.track_y, kx, self.track_y)
        self.coords(self.knob, kx - r, self.track_y - r, kx + r, self.track_y + r)

    def _on_mouse_down(self, event):
        self._dragging = True
        self._update_val(event.x)

    def _on_mouse_drag(self, event):
        if self._dragging:
            self._update_val(event.x)

    def _on_mouse_up(self, event):
        if self._dragging:
            self._update_val(event.x)
            self._dragging = False

    def _update_val(self, mouse_x):
        new_val = self._x_to_val(mouse_x)
        if new_val != self.value:
            self.value = new_val
            self._render()
            if self.on_change:
                self.on_change(self.get())

    def get(self):
        return int(round(self.value))

    def set(self, val, trigger_callback=True):
        self.value = max(self.from_, min(self.to, float(val)))
        self._render()
        if trigger_callback and self.on_change:
            self.on_change(self.get())

VOICE_MAP = {
    "auto": "auto",
    "ostap": "uk-UA-OstapNeural",
    "polina": "uk-UA-PolinaNeural",
    "dmitry": "ru-RU-DmitryNeural",
    "svetlana": "ru-RU-SvetlanaNeural",
    "andrew": "en-US-AndrewMultilingualNeural",
    "ava": "en-US-AvaMultilingualNeural",
    "brian": "en-US-BrianMultilingualNeural",
    "emma": "en-US-EmmaMultilingualNeural",
    "guy": "en-US-GuyNeural",
    "aria": "en-US-AriaNeural",
    # Legacy backward compatibility
    "UA": "uk-UA-OstapNeural",
    "RU": "ru-RU-DmitryNeural",
    "EN": "en-US-AndrewMultilingualNeural"
}

def detect_voice_for_text(text, voice_choice="auto"):
    """
    Detects appropriate neural voice for text.
    Intelligently routes Guy / Aria to multilingual counterparts on Cyrillic/Ukrainian text
    so they NEVER fail with 'No audio was received'.
    """
    has_ukr = bool(re.search(r'[іїєґІЇЄҐ]', text))
    has_cyr = bool(re.search(r'[\u0400-\u04FF]', text))

    if voice_choice and voice_choice != "auto":
        v = VOICE_MAP.get(voice_choice, voice_choice)
        # Guy & Aria are English-monolingual in Edge-TTS; route seamlessly to Multilingual equivalents on Cyrillic text
        if has_cyr:
            if v == "en-US-GuyNeural" or voice_choice == "guy":
                return "en-US-BrianMultilingualNeural"
            if v == "en-US-AriaNeural" or voice_choice == "aria":
                return "en-US-EmmaMultilingualNeural"
        # Dmitry & Svetlana cannot pronounce Ukrainian letters [іїєґ]; route to Ostap/Polina
        if has_ukr:
            if v == "ru-RU-DmitryNeural" or voice_choice == "dmitry":
                return "uk-UA-OstapNeural"
            if v == "ru-RU-SvetlanaNeural" or voice_choice == "svetlana":
                return "uk-UA-PolinaNeural"
        if v in VOICE_MAP.values():
            return v

    # Automatic detection with top-tier natural voices
    if has_ukr:
        return "uk-UA-OstapNeural"
    elif has_cyr:
        return "ru-RU-DmitryNeural"
    elif re.search(r'[äöüßÄÖÜ]', text):
        return "de-DE-KatjaNeural"
    elif re.search(r'[éàèùâêîôûëïüÿçÉÀÈÙÂÊÎÔÛËÏÜŸÇ]', text):
        return "fr-FR-DeniseNeural"
    elif re.search(r'[ñáéíóú¿¡]', text):
        return "es-ES-ElviraNeural"
    elif re.search(r'[\u4e00-\u9fff]', text):
        return "zh-CN-XiaoxiaoNeural"
    elif re.search(r'[\u3040-\u30ff]', text):
        return "ja-JP-NanamiNeural"
    elif re.search(r'[\uac00-\ud7af]', text):
        return "ko-KR-SunHiNeural"
    elif re.search(r'[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', text):
        return "pl-PL-ZofiaNeural"
    else:
        return "en-US-AndrewMultilingualNeural"

def synthesize_multilingual_tts(text, out_path, rate=0, volume=100, voice_choice="auto"):
    """
    Synthesizes speech in any language using edge-tts, with fallback to SAPI5.
    rate: -5 to +5
    volume: 0 to 100
    """
    # 1. High-fidelity Neural TTS via edge-tts (supports all languages)
    try:
        import edge_tts
        voice = detect_voice_for_text(text, voice_choice)
        rate_str = f"{rate * 10:+d}%"
        vol_offset = max(-100, min(100, volume - 100))
        vol_str = f"{vol_offset:+d}%"

        async def _save_voice(v):
            c = edge_tts.Communicate(text, v, rate=rate_str, volume=vol_str)
            await c.save(out_path)

        try:
            asyncio.run(_save_voice(voice))
        except Exception:
            # Fallback to universal multilingual models that never fail
            is_male = any(w in voice.lower() for w in ["dmitry", "ostap", "guy", "brian", "andrew"])
            fallback_v = "en-US-AndrewMultilingualNeural" if is_male else "en-US-AvaMultilingualNeural"
            asyncio.run(_save_voice(fallback_v))
            voice = fallback_v

        if os.path.exists(out_path) and os.path.getsize(out_path) > 100:
            return True, voice
    except Exception as e:
        print(f"[SoundGravity TTS] edge-tts error: {e}")

    # 2. Local Offline Fallback: SAPI5
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        filestream = win32com.client.Dispatch("SAPI.SpFileStream")
        has_cyr = bool(re.search(r'[\u0400-\u04FF]', text))
        for v in speaker.GetVoices():
            desc = v.GetDescription().lower()
            if has_cyr and ("russian" in desc or "irina" in desc or "pavel" in desc):
                speaker.Voice = v
                break
            elif not has_cyr and ("english" in desc or "zira" in desc or "david" in desc):
                speaker.Voice = v
                break
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except:
                pass
        filestream.Open(out_path, 3, False)
        speaker.AudioOutputStream = filestream
        speaker.Volume = max(0, min(100, volume))
        speaker.Rate = max(-10, min(10, rate * 2))
        speaker.Speak(text)
        filestream.Close()
        return True, "SAPI"
    except Exception as e:
        return False, str(e)

class SoundGravityCanvasApp(tk.Tk):
    def __init__(self):
        super().__init__()

        load_system_font()

        self.title("SoundGravity")
        win_w, win_h = 760, 520
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(20, (screen_w - win_w) // 2)
        y = max(30, (screen_h - win_h) // 2)
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.minsize(740, 490)
        self.resizable(True, True)
        self.ui_scale = 1.0

        # Pure Black DWM Titlebar
        self._set_pure_black_titlebar()

        # Icons (multi-res square ICO ensures Windows Taskbar uses custom icon instead of feather)
        self.ico_path = get_resource_path(os.path.join('assets', 'icon.ico'))
        self.png_path = get_resource_path(os.path.join('assets', 'icon.png'))
        self._set_icons()

        # Load font & black background image
        self.font_path = get_resource_path(os.path.join('assets', 'Unbounded-Variable.ttf'))
        self.bg_img_path = get_resource_path(os.path.join('assets', 'black_bg.png'))
        if os.path.exists(self.bg_img_path):
            try:
                self._raw_bg_img = Image.open(self.bg_img_path).convert('RGBA')
                self.bg_photo = ImageTk.PhotoImage(self._raw_bg_img)
            except Exception:
                self.bg_photo = ImageTk.PhotoImage(file=self.bg_img_path)
        else:
            self.bg_photo = ImageTk.PhotoImage(file=self.bg_img_path)

        # Pre-render vector UI icons (prominent, crisp subpixel rendering)
        self.speaker_ico_photo = ImageTk.PhotoImage(draw_vector_icon('speaker', color='#C084FC', size=26))
        self.mic_ico_photo = ImageTk.PhotoImage(draw_vector_icon('mic', color='#C084FC', size=26))
        self.folder_ico_photo = ImageTk.PhotoImage(draw_vector_icon('folder', color='#C084FC', size=26))
        self.check_ico_photo = ImageTk.PhotoImage(draw_vector_icon('check', color='#C084FC', size=22))

        # Config
        self.cfg = load_config()
        self.current_lang = self.cfg.get("language", "RU")
        if self.current_lang not in TRANSLATIONS:
            self.current_lang = "RU"
        self.auto_patch_enabled = self.cfg.get("auto_patch_on_update", True)
        self.done_vol = int(self.cfg.get("done_volume", 100))
        self.act_vol = int(self.cfg.get("action_volume", 100))
        self._dragging_slider = None

        # Smooth language switcher sliding state (comfortably visible 108x30)
        self.lang_slots = {"EN": 3.0, "UA": 38.0, "RU": 73.0}
        self.lang_slider_x = float(self.lang_slots.get(self.current_lang, 73.0))
        self.lang_target_x = self.lang_slider_x
        self.is_slider_animating = False

        # Canvas for everything
        self.canvas = tk.Canvas(self, width=win_w, height=win_h, highlightthickness=0, bd=0, bg="#000000")
        self.canvas.pack(fill="both", expand=True)

        # Put 100% black image as canvas background
        self.bg_item = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo, tags="bg_layer")

        # Cache button and toggle images
        self._cached_buttons = {}
        self._cached_lang_bar = None

        # Mouse handling on canvas items
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Pre-render text & buttons
        self._create_ui_elements()
        self._update_ui_layout()

        # Watcher
        self.watcher = UpdateWatcher(on_reapplied_callback=self._on_auto_patched)
        self.watcher.start()

    def _set_pure_black_titlebar(self):
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()
            
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_CAPTION_COLOR = 35
            DWMWA_BORDER_COLOR = 34
            DWMWA_TEXT_COLOR = 36

            true_val = ctypes.c_int(1)
            black_color = ctypes.c_int(0x00000000)
            white_color = ctypes.c_int(0x00FFFFFF)

            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(true_val), ctypes.sizeof(true_val))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(black_color), ctypes.sizeof(black_color))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_BORDER_COLOR, ctypes.byref(black_color), ctypes.sizeof(black_color))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_TEXT_COLOR, ctypes.byref(white_color), ctypes.sizeof(white_color))
        except Exception:
            pass

    def _set_icons(self):
        try:
            if os.path.exists(self.png_path):
                self.tk_icon = ImageTk.PhotoImage(file=self.png_path)
        except Exception:
            self.tk_icon = None
        self._apply_window_icon(self)

    def _apply_window_icon(self, win):
        try:
            if hasattr(self, 'tk_icon') and self.tk_icon:
                win.iconphoto(True, self.tk_icon)
        except Exception:
            pass
        if hasattr(self, 'ico_path') and os.path.exists(self.ico_path):
            try:
                win.iconbitmap(default=self.ico_path)
                win.iconbitmap(self.ico_path)
            except Exception:
                pass
            try:
                win.update_idletasks()
                hwnd = ctypes.windll.user32.GetAncestor(win.winfo_id(), 2)
                if not hwnd:
                    hwnd = ctypes.windll.user32.GetParent(win.winfo_id()) or win.winfo_id()
                user32 = ctypes.windll.user32
                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x00000010
                h_icon_big = user32.LoadImageW(None, self.ico_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
                h_icon_small = user32.LoadImageW(None, self.ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
                WM_SETICON = 0x0080
                user32.SendMessageW(hwnd, WM_SETICON, 0, h_icon_small)
                user32.SendMessageW(hwnd, WM_SETICON, 1, h_icon_big)
                if hasattr(user32, 'SetClassLongPtrW'):
                    user32.SetClassLongPtrW(hwnd, -14, h_icon_big)
                    user32.SetClassLongPtrW(hwnd, -34, h_icon_small)
                else:
                    user32.SetClassLongW(hwnd, -14, h_icon_big)
                    user32.SetClassLongW(hwnd, -34, h_icon_small)
            except Exception:
                pass

    def _create_rounded_button_image(self, text, w, h, r, is_hover=False):
        cache_key = (text, w, h, r, is_hover)
        if cache_key in self._cached_buttons:
            return self._cached_buttons[cache_key]

        factor = 2
        img = Image.new('RGBA', (w * factor, h * factor), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bg = "#2B1A42" if is_hover else "#181422"
        border = "#C084FC" if is_hover else "#35264B"
        border_w = max(1, int(factor * (h / 36.0)))
        draw.rounded_rectangle((0, 0, w * factor - 1, h * factor - 1), radius=r * factor, fill=bg, outline=border, width=border_w)

        font_size = max(10, int(h * 0.32))
        font = ImageFont.truetype(self.font_path, font_size * factor)
        text_col = "#C084FC" if is_hover else "#FFFFFF"
        draw.text((w * factor / 2, h * factor / 2), text, fill=text_col, font=font, anchor="mm")

        img = img.resize((w, h), Image.Resampling.LANCZOS)
        res = ImageTk.PhotoImage(img)
        self._cached_buttons[cache_key] = res
        return res

    def _create_toggle_image(self, is_on, w=48, h=26, r=13):
        factor = 2
        img = Image.new('RGBA', (w * factor, h * factor), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bg_color = "#A855F7" if is_on else "#222222"
        draw.rounded_rectangle((0, 0, w * factor - 1, h * factor - 1), radius=r * factor, fill=bg_color)

        knob_r = max(4 * factor, int((h - 8) // 2 * factor))
        knob_color = "#FFFFFF" if is_on else "#888888"
        knob_x = (w * factor - knob_r * 2 - int(3 * factor)) if is_on else int(3 * factor)
        knob_y = (h * factor - knob_r * 2) // 2
        draw.ellipse((knob_x, knob_y, knob_x + knob_r * 2, knob_y + knob_r * 2), fill=knob_color)
        img = img.resize((w, h), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _create_lang_bar_image(self, w=108, h=30, r=15):
        factor = 2
        img = Image.new('RGBA', (w * factor, h * factor), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((0, 0, w * factor - 1, h * factor - 1), radius=r * factor, fill="#131313")

        btn_w = int((w / 3.0 - 4) * factor)
        btn_h = (h - 6) * factor
        btn_r = int(btn_h / 2)

        # Draw smooth animated sliding highlight pill at float position self.lang_slider_x
        sx = round(self.lang_slider_x * factor)
        draw.rounded_rectangle((sx, 3 * factor, sx + btn_w - 1, (3 * factor) + btn_h - 1), radius=btn_r, fill="#2E1646", outline="#A855F7", width=factor)

        font_size = max(8, int(h * 0.33))
        font = ImageFont.truetype(self.font_path, font_size * factor)
        langs = ["EN", "UA", "RU"]
        slot_step = w / 3.0
        for idx, lang in enumerate(langs):
            x = int((idx * slot_step + (slot_step - (btn_w / factor)) / 2) * factor)
            y = 3 * factor
            bbox = draw.textbbox((0, 0), lang, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = x + (btn_w - tw) / 2 - bbox[0]
            ty = y + (btn_h - th) / 2 - bbox[1]
            col = "#FFFFFF" if lang == self.current_lang else "#777777"
            draw.text((tx, ty), lang, fill=col, font=font)

        img = img.resize((w, h), Image.Resampling.LANCZOS)
        res = ImageTk.PhotoImage(img)
        self._cached_lang_bar = res
        return res

    def _is_sound_tts(self, sound_type):
        name = self.cfg.get(f"{sound_type}_sound_name", "")
        custom_path = self.cfg.get(f"custom_{sound_type}_sound", "")
        if name == "TTS" or (custom_path and "tts_" in custom_path):
            return True
        return False

    def _create_sound_badge_image(self, sound_type, width=230, height=36, radius=12, is_hover=False):
        is_tts = self._is_sound_tts(sound_type)
        icon_type, label, icon_color = self._get_sound_display_info(sound_type, short=True)
        cache_key = ("badge", sound_type, icon_type, label, icon_color, width, height, radius, is_hover, self.current_lang)
        if cache_key in self._cached_buttons:
            return self._cached_buttons[cache_key]

        factor = 2
        img = Image.new('RGBA', (width * factor, height * factor), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bg = "#381B52" if is_hover else ("#28123B" if is_tts else "#181424")
        border = "#C084FC" if is_hover else ("#A855F7" if is_tts else "#332548")
        border_w = max(1, int(factor * (height / 36.0)))
        draw.rounded_rectangle((0, 0, width * factor - 1, height * factor - 1), radius=radius * factor, fill=bg, outline=border, width=border_w)

        ico_size_on_screen = max(20, int(height * 0.58))
        ico_col = "#FFFFFF" if is_hover else icon_color
        ico_img = draw_vector_icon(icon_type, color=ico_col, size=ico_size_on_screen * factor, factor=2)
        iw, ih = ico_img.size

        font_size = max(10, int(height * 0.31))
        font_txt = ImageFont.truetype(self.font_path, font_size * factor)
        tbbox = draw.textbbox((0, 0), label, font=font_txt)
        tw = tbbox[2] - tbbox[0]

        gap = max(8 * factor, int(height * 0.22 * factor))
        total_w = iw + gap + tw
        start_x = max(int(10 * factor), (width * factor - total_w) // 2)

        iy = (height * factor - ih) // 2
        img.paste(ico_img, (start_x, iy), ico_img)

        ty = (height * factor) // 2
        text_col = "#FFFFFF" if is_hover else ("#C084FC" if is_tts else "#E0D0F5")
        draw.text((start_x + iw + gap, ty), label, fill=text_col, font=font_txt, anchor="lm")

        img = img.resize((width, height), Image.Resampling.LANCZOS)
        res = ImageTk.PhotoImage(img)
        self._cached_buttons[cache_key] = res
        return res

    def _create_preview_button_image(self, text, width=126, height=28, radius=8, is_hover=False):
        cache_key = ("prev_btn", text, width, height, radius, is_hover)
        if cache_key in self._cached_buttons:
            return self._cached_buttons[cache_key]
        factor = 2
        img = Image.new('RGBA', (width * factor, height * factor), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bg = "#A855F7" if is_hover else "#231835"
        border = "#C084FC" if is_hover else "#3D2B59"
        draw.rounded_rectangle((0, 0, width * factor - 1, height * factor - 1), radius=radius * factor, fill=bg, outline=border, width=factor)

        font = ImageFont.truetype(self.font_path, int(8.5 * factor))
        col = "#FFFFFF" if is_hover else "#C084FC"
        btn_text = text if "▶" in text else f"▶ {text}"
        draw.text((width * factor / 2, height * factor / 2), btn_text, fill=col, font=font, anchor="mm")

        img = img.resize((width, height), Image.Resampling.LANCZOS)
        res = ImageTk.PhotoImage(img)
        self._cached_buttons[cache_key] = res
        return res

    def _create_donation_button_image(self, service, size=38, radius=11, is_hover=False):
        cache_key = ("don_icon_btn", service, size, radius, is_hover)
        if cache_key in self._cached_buttons:
            return self._cached_buttons[cache_key]

        factor = 2
        s = size * factor
        img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        # Subtle elegant dark glass container
        bg = "#2D1744" if is_hover else "#181224"
        border = "#C084FC" if is_hover else "#322248"
        border_w = max(1, int(1.4 * factor))
        d.rounded_rectangle((0, 0, s - 1, s - 1), radius=radius * factor, fill=bg, outline=border, width=border_w)

        # Crisp white icon with cutout details
        ico_color = "#FFFFFF" if not is_hover else "#F5EEFF"
        pad = int(s * 0.22)
        ico_s = s - 2 * pad

        ico_img = Image.new('RGBA', (ico_s, ico_s), (0, 0, 0, 0))
        idraw = ImageDraw.Draw(ico_img)

        if service == 'donatello':
            cx = ico_s / 2.0
            top_y = ico_s * 0.16
            bot_y = ico_s * 0.88
            r = ico_s * 0.23
            idraw.ellipse((cx - 2 * r, top_y, cx, top_y + 2 * r), fill=ico_color)
            idraw.ellipse((cx, top_y, cx + 2 * r, top_y + 2 * r), fill=ico_color)
            idraw.polygon([
                (cx - 1.95 * r, top_y + r * 0.95),
                (cx + 1.95 * r, top_y + r * 0.95),
                (cx, bot_y)
            ], fill=ico_color)

            # Cutout slot
            mask = Image.new('L', (ico_s, ico_s), 255)
            md = ImageDraw.Draw(mask)
            slot_w = int(ico_s * 0.28)
            slot_h = max(2, int(3.5 * factor))
            slot_y = int(top_y + r * 0.65)
            md.rounded_rectangle((cx - slot_w // 2, slot_y, cx + slot_w // 2, slot_y + slot_h), radius=slot_h//2, fill=0)

            r_ch, g_ch, b_ch, a_ch = ico_img.split()
            from PIL import ImageChops
            a_ch = ImageChops.multiply(a_ch, mask)
            ico_img = Image.merge('RGBA', (r_ch, g_ch, b_ch, a_ch))

        else: # donationalerts
            bw = int(ico_s * 0.84)
            bh = int(ico_s * 0.68)
            bx = (ico_s - bw) // 2
            by = int(ico_s * 0.10)
            r = int(6.5 * factor)
            idraw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=r, fill=ico_color)
            tail = [
                (bx + int(bw * 0.18), by + bh - 1),
                (bx + int(bw * 0.42), by + bh - 1),
                (bx + int(bw * 0.08), by + bh + int(ico_s * 0.18))
            ]
            idraw.polygon(tail, fill=ico_color)

            mask = Image.new('L', (ico_s, ico_s), 255)
            md = ImageDraw.Draw(mask)
            cx = bx + bw // 2
            top_ex = by + int(bh * 0.18)
            bot_ex = top_ex + int(bh * 0.40)
            ex_w = max(2, int(3.2 * factor))
            md.line([(cx, top_ex), (cx, bot_ex)], fill=0, width=ex_w)
            dot_r = max(2, int(1.8 * factor))
            dot_y = bot_ex + int(bh * 0.22)
            md.ellipse((cx - dot_r, dot_y - dot_r, cx + dot_r, dot_y + dot_r), fill=0)

            r_ch, g_ch, b_ch, a_ch = ico_img.split()
            from PIL import ImageChops
            a_ch = ImageChops.multiply(a_ch, mask)
            ico_img = Image.merge('RGBA', (r_ch, g_ch, b_ch, a_ch))

        img.paste(ico_img, (pad, pad), ico_img)
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        res = ImageTk.PhotoImage(img)
        self._cached_buttons[cache_key] = res
        return res

    def _get_sound_display_info(self, sound_type, short=True):
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["RU"])
        name = self.cfg.get(f"{sound_type}_sound_name", "")
        custom_path = self.cfg.get(f"custom_{sound_type}_sound", "")

        # Sanitize / recover if name is missing or corrupted into "action" / "done"
        if not name or name in ["action", "done"]:
            if custom_path:
                norm_p = custom_path.replace('\\', '/')
                if "tts_" in os.path.basename(custom_path):
                    name = "TTS"
                elif "/presets/" in norm_p or "\\presets\\" in custom_path:
                    for p_cand in ["Original", "Cyberpunk", "Minimal", "Arcade"]:
                        if f"/presets/{p_cand}/" in norm_p or f"/presets/{p_cand.lower()}/" in norm_p.lower() or f"\\presets\\{p_cand}\\" in custom_path:
                            name = p_cand
                            break
                    if not name or name in ["action", "done"]:
                        name = "Original" if sound_type == "action" else "Cyberpunk"
                else:
                    cand_base = os.path.splitext(os.path.basename(custom_path))[0]
                    name = cand_base if cand_base not in ["action", "done"] else ("Original" if sound_type == "action" else "Cyberpunk")
            else:
                name = "Original" if sound_type == "action" else "Cyberpunk"
            self.cfg[f"{sound_type}_sound_name"] = name
            save_config(self.cfg)

        if name == "TTS":
            tts_text = self.cfg.get("tts_last_text", t["tts_placeholder"]).strip()
            limit = 18 if short else 26
            if len(tts_text) > limit:
                tts_text = tts_text[:limit - 1] + "..."
            return "mic", f"«{tts_text}»", "#C084FC"

        orig_word = t["preset_original"].split()[0] # "Оригинал" in RU, "Оригінал" in UA, "Original" in EN
        preset_info = {
            "Cyberpunk": ("lightning", "Cyberpunk", "#D946EF"),
            "Original": ("bell", orig_word, "#9E9EAF"),
            "Minimal": ("waves", "Minimal", "#A855F7"),
            "Arcade": ("gamepad", "8-Bit Arcade", "#38BDF8"),
        }

        if name in preset_info:
            icon_type, display, col = preset_info[name]
            return icon_type, display, col

        # Custom file
        tag = t["custom_file_tag"]
        short_name = name[:16] + "..." if len(name) > 18 else name
        return "folder", short_name if short else f"{tag}: {short_name}", "#C084FC"

    def _create_ui_elements(self):
        # 3 panel card backgrounds behind each section
        self.card1_id = self.canvas.create_image(0, 0, anchor="nw", tags=("card_bg",))
        self.card2_id = self.canvas.create_image(0, 0, anchor="nw", tags=("card_bg",))
        self.card3_id = self.canvas.create_image(0, 0, anchor="nw", tags=("card_bg",))

        self.item_title = self.canvas.create_text(
            36, 28, anchor="nw",
            text="SoundGravity",
            font=("Unbounded", 24, "bold"),
            fill="#FFFFFF",
            tags="ui_element"
        )

        self.item_sub1 = self.canvas.create_text(
            36, 82, anchor="nw",
            text="", font=("Unbounded", 11), fill="#FFFFFF", tags="ui_element"
        )
        self.item_sub2 = self.canvas.create_text(
            36, 104, anchor="nw",
            text="", font=("Unbounded", 11), fill="#FFFFFF", tags="ui_element"
        )
        self.item_sub3 = self.canvas.create_text(
            36, 126, anchor="nw",
            text="", font=("Unbounded", 11), fill="#FFFFFF", tags="ui_element"
        )
        self.item_sub = self.item_sub1

        self.item_lbl_done = self.canvas.create_text(
            36, 188, anchor="nw",
            text="",
            font=("Unbounded", 11, "bold"),
            fill="#FFFFFF",
            justify="left",
            tags="ui_element"
        )

        self.btn_done_id = self.canvas.create_image(
            36, 218, anchor="nw",
            tags=("ui_element", "btn_done")
        )

        self.badge_done_id = self.canvas.create_image(
            168, 218, anchor="nw",
            tags=("ui_element", "badge_done")
        )

        self.badge_done_txt = self.canvas.create_text(
            273, 236, anchor="center",
            text="",
            font=("Unbounded", 10, "bold"),
            fill="#C084FC",
            tags=("ui_element", "badge_done_txt")
        )

        # Volume Controls 1 (Vector Speaker Icon + Label + Slider)
        self.item_vol_done_ico = self.canvas.create_image(
            398, 225, anchor="nw", image=self.speaker_ico_photo,
            tags="ui_element"
        )
        self.item_vol_done_lbl = self.canvas.create_text(
            428, 236, anchor="w",
            text=f"{self.done_vol}%",
            font=("Unbounded", 11, "bold"),
            fill="#FFFFFF",
            tags="ui_element"
        )
        self.item_vol_done_bg = self.canvas.create_line(
            485, 236, 700, 236,
            fill="#1F1B2C", width=6, capstyle="round",
            tags=("ui_element", "vol_done_track")
        )
        self.item_vol_done_fill = self.canvas.create_line(
            485, 236, 700, 236,
            fill="#A855F7", width=6, capstyle="round",
            tags=("ui_element", "vol_done_fill")
        )
        self.item_vol_done_knob = self.canvas.create_oval(
            692, 228, 708, 244,
            fill="#FFFFFF", outline="#C084FC", width=2,
            tags=("ui_element", "vol_done_knob")
        )

        self.item_lbl_act = self.canvas.create_text(
            36, 278, anchor="nw",
            text="",
            font=("Unbounded", 11, "bold"),
            fill="#FFFFFF",
            justify="left",
            tags="ui_element"
        )

        self.btn_action_id = self.canvas.create_image(
            36, 308, anchor="nw",
            tags=("ui_element", "btn_action")
        )

        self.badge_act_id = self.canvas.create_image(
            168, 308, anchor="nw",
            tags=("ui_element", "badge_act")
        )

        self.badge_act_txt = self.canvas.create_text(
            273, 326, anchor="center",
            text="",
            font=("Unbounded", 10, "bold"),
            fill="#C084FC",
            tags=("ui_element", "badge_act_txt")
        )

        # Volume Controls 2 (Vector Speaker Icon + Label + Slider)
        self.item_vol_act_ico = self.canvas.create_image(
            398, 315, anchor="nw", image=self.speaker_ico_photo,
            tags="ui_element"
        )
        self.item_vol_act_lbl = self.canvas.create_text(
            428, 326, anchor="w",
            text=f"{self.act_vol}%",
            font=("Unbounded", 11, "bold"),
            fill="#FFFFFF",
            tags="ui_element"
        )
        self.item_vol_act_bg = self.canvas.create_line(
            485, 326, 700, 326,
            fill="#1F1B2C", width=6, capstyle="round",
            tags=("ui_element", "vol_act_track")
        )
        self.item_vol_act_fill = self.canvas.create_line(
            485, 326, 700, 326,
            fill="#A855F7", width=6, capstyle="round",
            tags=("ui_element", "vol_act_fill")
        )
        self.item_vol_act_knob = self.canvas.create_oval(
            692, 318, 708, 334,
            fill="#FFFFFF", outline="#C084FC", width=2,
            tags=("ui_element", "vol_act_knob")
        )

        # Toggle switch row for Auto-Update
        self.toggle_img_id = self.canvas.create_image(
            36, 378, anchor="nw",
            tags=("ui_element", "toggle_btn")
        )

        self.toggle_lbl_id = self.canvas.create_text(
            96, 381, anchor="nw",
            text="",
            font=("Unbounded", 10),
            fill="#DDDDDD",
            justify="left",
            tags=("ui_element", "toggle_lbl")
        )

        self.lang_bar_id = self.canvas.create_image(
            0, 0, anchor="nw",
            tags=("ui_element", "lang_bar")
        )

        # Donation buttons (Donatello & DonationAlerts)
        self.btn_donatello_id = self.canvas.create_image(
            0, 0, anchor="nw",
            tags=("ui_element", "btn_donatello")
        )
        self.btn_da_id = self.canvas.create_image(
            0, 0, anchor="nw",
            tags=("ui_element", "btn_da")
        )

        self.item_don_tooltip = self.canvas.create_text(
            0, 0, anchor="center",
            text="",
            font=("Unbounded", 9),
            fill="#C084FC",
            tags="ui_element"
        )

        self.item_ver = self.canvas.create_text(
            0, 0, anchor="nw",
            text="1.0.0",
            font=("Unbounded", 13),
            fill="#FFFFFF",
            tags="ui_element"
        )

        self.canvas.tag_lower("card_bg")
        self.canvas.tag_lower("bg_layer")
        self.canvas.tag_raise("ui_element", "card_bg")

    def _on_canvas_configure(self, event):
        w = event.width
        h = event.height
        if w < 100 or h < 100:
            return
        if hasattr(self, '_last_canvas_dim') and self._last_canvas_dim == (w, h):
            return
        self._last_canvas_dim = (w, h)
        self._update_ui_layout_to_size(w, h)

    def _update_ui_layout(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            try:
                w = self.winfo_width()
                h = self.winfo_height()
            except Exception:
                pass
        if w < 100 or h < 100:
            w = 740
            h = 480
        self._update_ui_layout_to_size(w, h)

    def _update_ui_layout_to_size(self, win_w, win_h):
        # Dynamic background resize to fill exact window
        try:
            if hasattr(self, '_raw_bg_img') and self._raw_bg_img:
                resized_bg = self._raw_bg_img.resize((win_w, win_h), Image.Resampling.BILINEAR)
                self.bg_photo = ImageTk.PhotoImage(resized_bg)
                self.canvas.itemconfig(self.bg_item, image=self.bg_photo)
                self.canvas.coords(self.bg_item, 0, 0)
        except Exception:
            pass

        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["RU"])

        self.canvas.itemconfig(self.item_sub1, text=t["header_1"])
        self.canvas.itemconfig(self.item_sub2, text=t["header_2"])
        self.canvas.itemconfig(self.item_sub3, text=t["header_3"])
        self.canvas.itemconfig(self.item_lbl_done, text=t["sound_done"])
        self.canvas.itemconfig(self.item_lbl_act, text=t["sound_action"])

        is_large = (win_w >= 880 and win_h >= 540)

        if not is_large:
            # Compact mode (740-879 width, 480-539 height)
            sc = max(0.95, min(win_w / 760.0, win_h / 500.0, 1.25))
            self.ui_scale = sc

            margin_x = max(28, int(36 * sc))
            self.margin_x = margin_x

            # Header typography with generous, un-cramped spacing
            font_title_sz = 22
            font_sub_sz = 10
            self.font_title_sz = font_title_sz
            self.canvas.itemconfig(self.item_title, font=("Unbounded", font_title_sz, "bold"))
            for itm in (self.item_sub1, self.item_sub2, self.item_sub3):
                self.canvas.itemconfig(itm, font=("Unbounded", font_sub_sz))

            title_y = 22
            self.canvas.coords(self.item_title, margin_x, title_y)
            # Unbounded 22pt bold linespace is ~46px
            title_linespace = 46
            gap_title_sub = 14
            self.sub_y = title_y + title_linespace + gap_title_sub

            f_sub = tkFont.Font(font=("Unbounded", font_sub_sz))
            sub_step = f_sub.metrics("linespace") + 4
            self.sub_step = sub_step
            self.canvas.coords(self.item_sub1, margin_x, self.sub_y)
            self.canvas.coords(self.item_sub2, margin_x, self.sub_y + sub_step)
            self.canvas.coords(self.item_sub3, margin_x, self.sub_y + 2 * sub_step)
            sub_total_h = 2 * sub_step + f_sub.metrics("linespace")

            # Language switcher in header right
            lang_w, lang_h, lang_r = 108, 30, 15
            self.lang_w = lang_w
            self.lang_h = lang_h
            self.lang_x = win_w - lang_w - margin_x
            self.lang_y = title_y
            step = lang_w / 3.0
            pad = (step - int(step - 4)) / 2
            self.lang_slots = {"EN": pad, "UA": step + pad, "RU": 2 * step + pad}
            self.lang_slider_x = self.lang_slots.get(self.current_lang, 2 * step + pad)
            self.lang_target_x = self.lang_slider_x
            img_lang = self._create_lang_bar_image(lang_w, lang_h, lang_r)
            self.canvas.itemconfig(self.lang_bar_id, image=img_lang)
            self.canvas.coords(self.lang_bar_id, self.lang_x, self.lang_y)

            # Donation buttons (DonationAlerts & Donatello white icons)
            don_sz = 38
            don_gap = 10
            total_don_w = don_sz * 2 + don_gap
            self.don_sz = don_sz
            self.don_y = self.lang_y + self.lang_h + 10
            self.don1_x = self.lang_x + (self.lang_w - total_don_w) // 2
            self.don2_x = self.don1_x + don_sz + don_gap
            self.don_tooltip_x = self.lang_x + self.lang_w // 2
            self.don_tooltip_y = self.don_y + don_sz + 13

            self.img_da = self._create_donation_button_image("donationalerts", size=don_sz, radius=11, is_hover=False)
            self.img_da_hover = self._create_donation_button_image("donationalerts", size=don_sz, radius=11, is_hover=True)
            self.canvas.itemconfig(self.btn_da_id, image=self.img_da)
            self.canvas.coords(self.btn_da_id, self.don1_x, self.don_y)

            self.img_donatello = self._create_donation_button_image("donatello", size=don_sz, radius=11, is_hover=False)
            self.img_donatello_hover = self._create_donation_button_image("donatello", size=don_sz, radius=11, is_hover=True)
            self.canvas.itemconfig(self.btn_donatello_id, image=self.img_donatello)
            self.canvas.coords(self.btn_donatello_id, self.don2_x, self.don_y)

            self.canvas.coords(self.item_don_tooltip, self.don_tooltip_x, self.don_tooltip_y)
            self.canvas.itemconfig(self.item_don_tooltip, text="", font=("Unbounded", 9))

            # Cards sizing & positions
            card_w = max(660, win_w - 2 * margin_x)
            card_x = margin_x
            self.card_w = card_w
            self.card_x = card_x

            # Subtitle clean padding
            gap_sub_card = 20
            card1_y = self.sub_y + sub_total_h + gap_sub_card
            card1_h = 90
            card_gap = 12
            card2_y = card1_y + card1_h + card_gap
            card2_h = 90
            card3_y = card2_y + card2_h + card_gap
            card3_h = 56

            img_c1 = get_rounded_rect_image(card_w, card1_h, 14, "#151022", "#2B1A3E", 1)
            img_c2 = get_rounded_rect_image(card_w, card2_h, 14, "#151022", "#2B1A3E", 1)
            img_c3 = get_rounded_rect_image(card_w, card3_h, 14, "#151022", "#2B1A3E", 1)
            self.canvas.itemconfig(self.card1_id, image=img_c1, state="normal")
            self.canvas.coords(self.card1_id, card_x, card1_y)
            self.canvas.itemconfig(self.card2_id, image=img_c2, state="normal")
            self.canvas.coords(self.card2_id, card_x, card2_y)
            self.canvas.itemconfig(self.card3_id, image=img_c3, state="normal")
            self.canvas.coords(self.card3_id, card_x, card3_y)
            self._c1_ref = img_c1
            self._c2_ref = img_c2
            self._c3_ref = img_c3

            # Font sizes for labels
            font_lbl_sz = 10
            self.canvas.itemconfig(self.item_lbl_done, font=("Unbounded", font_lbl_sz, "bold"))
            self.canvas.itemconfig(self.item_lbl_act, font=("Unbounded", font_lbl_sz, "bold"))
            self.canvas.itemconfig(self.item_ver, font=("Unbounded", 11))

            self.lbl1_y = card1_y + 13
            self.canvas.coords(self.item_lbl_done, card_x + 16, self.lbl1_y)

            # Buttons & Badges inside cards
            btn_w, btn_h, btn_r = 110, 36, 12
            badge_w, badge_h, badge_r = 230, 36, 12
            self.btn_w = btn_w
            self.btn_h = btn_h
            self.badge_w = badge_w
            self.badge_h = badge_h

            self.btn1_x = card_x + 16
            self.btn1_y = card1_y + 42
            self.badge1_x = self.btn1_x + btn_w + 10

            self.img_btn_done = self._create_rounded_button_image(t["btn_select"], btn_w, btn_h, btn_r, is_hover=False)
            self.img_btn_done_hover = self._create_rounded_button_image(t["btn_select"], btn_w, btn_h, btn_r, is_hover=True)
            self.canvas.itemconfig(self.btn_done_id, image=self.img_btn_done)
            self.canvas.coords(self.btn_done_id, self.btn1_x, self.btn1_y)

            self.img_badge_done = self._create_sound_badge_image("done", badge_w, badge_h, badge_r, is_hover=False)
            self.img_badge_done_hover = self._create_sound_badge_image("done", badge_w, badge_h, badge_r, is_hover=True)
            self.canvas.itemconfig(self.badge_done_id, image=self.img_badge_done)
            self.canvas.coords(self.badge_done_id, self.badge1_x, self.btn1_y)
            self.canvas.itemconfig(self.badge_done_txt, text="")

            # Section 2 inside Card 2
            self.lbl2_y = card2_y + 13
            self.canvas.coords(self.item_lbl_act, card_x + 16, self.lbl2_y)

            self.btn2_x = card_x + 16
            self.btn2_y = card2_y + 42
            self.badge2_x = self.btn2_x + btn_w + 10

            self.img_btn_action = self._create_rounded_button_image(t["btn_select"], btn_w, btn_h, btn_r, is_hover=False)
            self.img_btn_action_hover = self._create_rounded_button_image(t["btn_select"], btn_w, btn_h, btn_r, is_hover=True)
            self.canvas.itemconfig(self.btn_action_id, image=self.img_btn_action)
            self.canvas.coords(self.btn_action_id, self.btn2_x, self.btn2_y)

            self.img_badge_act = self._create_sound_badge_image("action", badge_w, badge_h, badge_r, is_hover=False)
            self.img_badge_act_hover = self._create_sound_badge_image("action", badge_w, badge_h, badge_r, is_hover=True)
            self.canvas.itemconfig(self.badge_act_id, image=self.img_badge_act)
            self.canvas.coords(self.badge_act_id, self.badge2_x, self.btn2_y)
            self.canvas.itemconfig(self.badge_act_txt, text="")

            # Sliders layout inside Card 1 & 2
            ico_sz = 24
            self.speaker_ico_photo = ImageTk.PhotoImage(draw_vector_icon('speaker', color='#C084FC', size=ico_sz))
            self.canvas.itemconfig(self.item_vol_done_ico, image=self.speaker_ico_photo)
            self.canvas.itemconfig(self.item_vol_act_ico, image=self.speaker_ico_photo)

            speaker_x = self.badge1_x + badge_w + 16
            vol_lbl_x = speaker_x + ico_sz + 10
            font_vol_sz = 10
            f_vol = tkFont.Font(font=("Unbounded", font_vol_sz, "bold"))
            vol_txt_w = f_vol.measure("100%")
            self.canvas.itemconfig(self.item_vol_done_lbl, font=("Unbounded", font_vol_sz, "bold"), text=f"{self.done_vol}%")
            self.canvas.itemconfig(self.item_vol_act_lbl, font=("Unbounded", font_vol_sz, "bold"), text=f"{self.act_vol}%")

            gap_after_vol = 18
            track_x1 = vol_lbl_x + vol_txt_w + gap_after_vol
            track_x2 = card_x + card_w - 24
            track_w = max(80, track_x2 - track_x1)
            self.track_x1 = track_x1
            self.track_w = track_w
            knob_r = 7

            # Slider 1
            y_done_center = self.btn1_y + btn_h // 2
            knob1_x = track_x1 + (track_w * self.done_vol / 100.0)
            self.canvas.coords(self.item_vol_done_ico, speaker_x, y_done_center - ico_sz // 2)
            self.canvas.coords(self.item_vol_done_lbl, vol_lbl_x, y_done_center)
            self.canvas.coords(self.item_vol_done_bg, track_x1, y_done_center, track_x2, y_done_center)
            self.canvas.coords(self.item_vol_done_fill, track_x1, y_done_center, knob1_x, y_done_center)
            self.canvas.coords(self.item_vol_done_knob, knob1_x - knob_r, y_done_center - knob_r, knob1_x + knob_r, y_done_center + knob_r)

            # Slider 2
            y_act_center = self.btn2_y + btn_h // 2
            knob2_x = track_x1 + (track_w * self.act_vol / 100.0)
            self.canvas.coords(self.item_vol_act_ico, speaker_x, y_act_center - ico_sz // 2)
            self.canvas.coords(self.item_vol_act_lbl, vol_lbl_x, y_act_center)
            self.canvas.coords(self.item_vol_act_bg, track_x1, y_act_center, track_x2, y_act_center)
            self.canvas.coords(self.item_vol_act_fill, track_x1, y_act_center, knob2_x, y_act_center)
            self.canvas.coords(self.item_vol_act_knob, knob2_x - knob_r, y_act_center - knob_r, knob2_x + knob_r, y_act_center + knob_r)

            # Card 3: Toggle
            self.toggle_x = card_x + 16
            self.toggle_y = card3_y + 15
            toggle_w, toggle_h, toggle_r = 48, 26, 13
            self.toggle_w = toggle_w
            self.toggle_h = toggle_h
            self.img_toggle = self._create_toggle_image(self.auto_patch_enabled, w=toggle_w, h=toggle_h, r=toggle_r)
            self.canvas.itemconfig(self.toggle_img_id, image=self.img_toggle)
            self.canvas.coords(self.toggle_img_id, self.toggle_x, self.toggle_y)

            self.canvas.itemconfig(self.toggle_lbl_id, text=t["auto_patch_label"], font=("Unbounded", 10))
            self.canvas.coords(self.toggle_lbl_id, self.toggle_x + toggle_w + 14, self.toggle_y + 4)

            # Version Tag
            self.canvas.coords(self.item_ver, win_w - 75, win_h - 26)

        else:
            # Fullscreen / Large Window Mode (e.g. 1920x1080)
            sc = max(1.15, min(win_w / 1150.0, win_h / 720.0, 1.5))
            self.ui_scale = sc

            card_w = min(1160, int(win_w * 0.84))
            card_x = (win_w - card_w) // 2
            self.card_w = card_w
            self.card_x = card_x
            self.margin_x = card_x

            # Header scaling
            font_title_sz = max(26, int(32 * sc))
            font_sub_sz = max(12, int(13.5 * sc))
            self.font_title_sz = font_title_sz
            self.canvas.itemconfig(self.item_title, font=("Unbounded", font_title_sz, "bold"))
            for itm in (self.item_sub1, self.item_sub2, self.item_sub3):
                self.canvas.itemconfig(itm, font=("Unbounded", font_sub_sz))

            header_y = max(36, int(win_h * 0.055))
            self.canvas.coords(self.item_title, card_x, header_y)
            title_linespace = int(font_title_sz * 1.5)
            gap_title_sub = max(16, int(18 * sc))
            self.sub_y = header_y + title_linespace + gap_title_sub

            f_sub = tkFont.Font(font=("Unbounded", font_sub_sz))
            sub_step = f_sub.metrics("linespace") + 6
            self.sub_step = sub_step
            self.canvas.coords(self.item_sub1, card_x, self.sub_y)
            self.canvas.coords(self.item_sub2, card_x, self.sub_y + sub_step)
            self.canvas.coords(self.item_sub3, card_x, self.sub_y + 2 * sub_step)
            sub_total_h = 2 * sub_step + f_sub.metrics("linespace")

            # Language switcher in header right
            lang_w = max(120, int(130 * sc))
            lang_h = max(34, int(38 * sc))
            lang_r = int(lang_h / 2)
            self.lang_w = lang_w
            self.lang_h = lang_h
            self.lang_x = card_x + card_w - lang_w
            self.lang_y = header_y
            step = lang_w / 3.0
            pad = (step - int(step - 4)) / 2
            self.lang_slots = {"EN": pad, "UA": step + pad, "RU": 2 * step + pad}
            self.lang_slider_x = self.lang_slots.get(self.current_lang, 2 * step + pad)
            self.lang_target_x = self.lang_slider_x
            img_lang = self._create_lang_bar_image(lang_w, lang_h, lang_r)
            self.canvas.itemconfig(self.lang_bar_id, image=img_lang)
            self.canvas.coords(self.lang_bar_id, self.lang_x, self.lang_y)

            # Donation buttons (DonationAlerts & Donatello white icons)
            don_sz = max(42, int(46 * sc))
            don_gap = max(12, int(14 * sc))
            total_don_w = don_sz * 2 + don_gap
            self.don_sz = don_sz
            self.don_y = self.lang_y + self.lang_h + max(14, int(18 * sc))
            self.don1_x = self.lang_x + (self.lang_w - total_don_w) // 2
            self.don2_x = self.don1_x + don_sz + don_gap
            self.don_tooltip_x = self.lang_x + self.lang_w // 2
            self.don_tooltip_y = self.don_y + don_sz + max(14, int(18 * sc))

            self.img_da = self._create_donation_button_image("donationalerts", size=don_sz, radius=int(don_sz * 0.28), is_hover=False)
            self.img_da_hover = self._create_donation_button_image("donationalerts", size=don_sz, radius=int(don_sz * 0.28), is_hover=True)
            self.canvas.itemconfig(self.btn_da_id, image=self.img_da)
            self.canvas.coords(self.btn_da_id, self.don1_x, self.don_y)

            self.img_donatello = self._create_donation_button_image("donatello", size=don_sz, radius=int(don_sz * 0.28), is_hover=False)
            self.img_donatello_hover = self._create_donation_button_image("donatello", size=don_sz, radius=int(don_sz * 0.28), is_hover=True)
            self.canvas.itemconfig(self.btn_donatello_id, image=self.img_donatello)
            self.canvas.coords(self.btn_donatello_id, self.don2_x, self.don_y)

            self.canvas.coords(self.item_don_tooltip, self.don_tooltip_x, self.don_tooltip_y)
            self.canvas.itemconfig(self.item_don_tooltip, text="", font=("Unbounded", max(10, int(11 * sc))))

            # Vertical space distribution for cards
            gap_sub_card = max(26, int(win_h * 0.04))
            card1_y = self.sub_y + sub_total_h + gap_sub_card
            bottom_margin = max(40, int(win_h * 0.06))
            avail_h = max(380, win_h - card1_y - bottom_margin)

            card1_h = max(125, min(165, int(avail_h * 0.29)))
            card2_h = card1_h
            card3_h = max(68, min(84, int(avail_h * 0.16)))
            card_gap = max(16, min(28, int(avail_h * 0.05)))

            card2_y = card1_y + card1_h + card_gap
            card3_y = card2_y + card2_h + card_gap

            # Render 3 spacious styled cards
            img_c1 = get_rounded_rect_image(card_w, card1_h, 16, "#151022", "#2B1A3E", 1)
            img_c2 = get_rounded_rect_image(card_w, card2_h, 16, "#151022", "#2B1A3E", 1)
            img_c3 = get_rounded_rect_image(card_w, card3_h, 16, "#151022", "#2B1A3E", 1)
            self.canvas.itemconfig(self.card1_id, image=img_c1, state="normal")
            self.canvas.coords(self.card1_id, card_x, card1_y)
            self.canvas.itemconfig(self.card2_id, image=img_c2, state="normal")
            self.canvas.coords(self.card2_id, card_x, card2_y)
            self.canvas.itemconfig(self.card3_id, image=img_c3, state="normal")
            self.canvas.coords(self.card3_id, card_x, card3_y)
            self._c1_ref = img_c1
            self._c2_ref = img_c2
            self._c3_ref = img_c3

            # Font sizes for labels
            font_lbl_sz = max(12, int(13 * sc))
            self.canvas.itemconfig(self.item_lbl_done, font=("Unbounded", font_lbl_sz, "bold"))
            self.canvas.itemconfig(self.item_lbl_act, font=("Unbounded", font_lbl_sz, "bold"))
            self.canvas.itemconfig(self.item_ver, font=("Unbounded", max(11, int(13 * sc))))

            # Card 1 Section Title & Controls
            pad_left = max(24, int(card_w * 0.025))
            pad_right = max(28, int(card_w * 0.03))
            self.lbl1_y = card1_y + int(card1_h * 0.14)
            self.canvas.coords(self.item_lbl_done, card_x + pad_left, self.lbl1_y)

            btn_w = max(130, int(145 * sc))
            btn_h = max(42, int(46 * sc))
            btn_r = int(btn_h * 0.32)
            badge_w = max(300, min(380, int(340 * sc)))
            badge_h = btn_h
            badge_r = btn_r
            self.btn_w = btn_w
            self.btn_h = btn_h
            self.badge_w = badge_w
            self.badge_h = badge_h

            gap_lbl_btn = max(14, int(18 * sc))
            self.btn1_x = card_x + pad_left
            self.btn1_y = self.lbl1_y + font_lbl_sz + gap_lbl_btn
            self.badge1_x = self.btn1_x + btn_w + max(12, int(16 * sc))

            self.img_btn_done = self._create_rounded_button_image(t["btn_select"], btn_w, btn_h, btn_r, is_hover=False)
            self.img_btn_done_hover = self._create_rounded_button_image(t["btn_select"], btn_w, btn_h, btn_r, is_hover=True)
            self.canvas.itemconfig(self.btn_done_id, image=self.img_btn_done)
            self.canvas.coords(self.btn_done_id, self.btn1_x, self.btn1_y)

            self.img_badge_done = self._create_sound_badge_image("done", badge_w, badge_h, badge_r, is_hover=False)
            self.img_badge_done_hover = self._create_sound_badge_image("done", badge_w, badge_h, badge_r, is_hover=True)
            self.canvas.itemconfig(self.badge_done_id, image=self.img_badge_done)
            self.canvas.coords(self.badge_done_id, self.badge1_x, self.btn1_y)
            self.canvas.itemconfig(self.badge_done_txt, text="")

            # Card 2 Section Title & Controls
            self.lbl2_y = card2_y + int(card2_h * 0.14)
            self.canvas.coords(self.item_lbl_act, card_x + pad_left, self.lbl2_y)

            self.btn2_x = card_x + pad_left
            self.btn2_y = self.lbl2_y + font_lbl_sz + gap_lbl_btn
            self.badge2_x = self.btn2_x + btn_w + max(12, int(16 * sc))

            self.img_btn_action = self._create_rounded_button_image(t["btn_select"], btn_w, btn_h, btn_r, is_hover=False)
            self.img_btn_action_hover = self._create_rounded_button_image(t["btn_select"], btn_w, btn_h, btn_r, is_hover=True)
            self.canvas.itemconfig(self.btn_action_id, image=self.img_btn_action)
            self.canvas.coords(self.btn_action_id, self.btn2_x, self.btn2_y)

            self.img_badge_act = self._create_sound_badge_image("action", badge_w, badge_h, badge_r, is_hover=False)
            self.img_badge_act_hover = self._create_sound_badge_image("action", badge_w, badge_h, badge_r, is_hover=True)
            self.canvas.itemconfig(self.badge_act_id, image=self.img_badge_act)
            self.canvas.coords(self.badge_act_id, self.badge2_x, self.btn2_y)
            self.canvas.itemconfig(self.badge_act_txt, text="")

            # Sliders layout inside Card 1 & 2
            ico_sz = max(28, int(32 * sc))
            self.speaker_ico_photo = ImageTk.PhotoImage(draw_vector_icon('speaker', color='#C084FC', size=ico_sz))
            self.canvas.itemconfig(self.item_vol_done_ico, image=self.speaker_ico_photo)
            self.canvas.itemconfig(self.item_vol_act_ico, image=self.speaker_ico_photo)

            font_vol_sz = max(11, int(12.5 * sc))
            f_vol = tkFont.Font(font=("Unbounded", font_vol_sz, "bold"))
            vol_txt_w = f_vol.measure("100%")
            speaker_x = self.badge1_x + badge_w + max(18, int(22 * sc))
            vol_lbl_x = speaker_x + ico_sz + max(10, int(12 * sc))
            self.canvas.itemconfig(self.item_vol_done_lbl, font=("Unbounded", font_vol_sz, "bold"), text=f"{self.done_vol}%")
            self.canvas.itemconfig(self.item_vol_act_lbl, font=("Unbounded", font_vol_sz, "bold"), text=f"{self.act_vol}%")

            gap_after_vol = max(20, int(24 * sc))
            track_x1 = vol_lbl_x + vol_txt_w + gap_after_vol
            track_x2 = card_x + card_w - pad_right
            track_w = max(120, track_x2 - track_x1)
            self.track_x1 = track_x1
            self.track_w = track_w
            knob_r = max(8, int(9 * sc))

            # Slider 1
            y_done_center = self.btn1_y + btn_h // 2
            knob1_x = track_x1 + (track_w * self.done_vol / 100.0)
            self.canvas.coords(self.item_vol_done_ico, speaker_x, y_done_center - ico_sz // 2)
            self.canvas.coords(self.item_vol_done_lbl, vol_lbl_x, y_done_center)
            self.canvas.coords(self.item_vol_done_bg, track_x1, y_done_center, track_x2, y_done_center)
            self.canvas.coords(self.item_vol_done_fill, track_x1, y_done_center, knob1_x, y_done_center)
            self.canvas.coords(self.item_vol_done_knob, knob1_x - knob_r, y_done_center - knob_r, knob1_x + knob_r, y_done_center + knob_r)

            # Slider 2
            y_act_center = self.btn2_y + btn_h // 2
            knob2_x = track_x1 + (track_w * self.act_vol / 100.0)
            self.canvas.coords(self.item_vol_act_ico, speaker_x, y_act_center - ico_sz // 2)
            self.canvas.coords(self.item_vol_act_lbl, vol_lbl_x, y_act_center)
            self.canvas.coords(self.item_vol_act_bg, track_x1, y_act_center, track_x2, y_act_center)
            self.canvas.coords(self.item_vol_act_fill, track_x1, y_act_center, knob2_x, y_act_center)
            self.canvas.coords(self.item_vol_act_knob, knob2_x - knob_r, y_act_center - knob_r, knob2_x + knob_r, y_act_center + knob_r)

            # Card 3: Toggle
            self.toggle_x = card_x + pad_left
            self.toggle_y = card3_y + (card3_h - int(30 * sc)) // 2
            toggle_w, toggle_h, toggle_r = int(54 * sc), int(30 * sc), int(15 * sc)
            self.toggle_w = toggle_w
            self.toggle_h = toggle_h
            self.img_toggle = self._create_toggle_image(self.auto_patch_enabled, w=toggle_w, h=toggle_h, r=toggle_r)
            self.canvas.itemconfig(self.toggle_img_id, image=self.img_toggle)
            self.canvas.coords(self.toggle_img_id, self.toggle_x, self.toggle_y)

            self.canvas.itemconfig(self.toggle_lbl_id, text=t["auto_patch_label"], font=("Unbounded", max(11, int(12 * sc))))
            self.canvas.coords(self.toggle_lbl_id, self.toggle_x + toggle_w + max(14, int(18 * sc)), self.toggle_y + int(toggle_h * 0.18))

            # Version Tag
            self.canvas.coords(self.item_ver, win_w - int(85 * sc), win_h - int(32 * sc))

        # Always re-assert canvas z-orders to prevent items disappearing during resize
        self.canvas.tag_lower("card_bg")
        self.canvas.tag_lower("bg_layer")
        self.canvas.tag_raise("ui_element", "card_bg")

    def _on_canvas_motion(self, event):
        x, y = event.x, event.y
        btn_w = getattr(self, 'btn_w', 120)
        btn_h = getattr(self, 'btn_h', 36)
        badge_w = getattr(self, 'badge_w', 210)
        badge_h = getattr(self, 'badge_h', 36)

        y1 = getattr(self, 'btn1_y', 218)
        y2 = getattr(self, 'btn2_y', 308)
        y1_center = y1 + btn_h // 2
        y2_center = y2 + btn_h // 2
        tx1 = getattr(self, 'track_x1', 485)
        tw = getattr(self, 'track_w', 215)
        lw = getattr(self, 'lang_w', 108)
        lh = getattr(self, 'lang_h', 30)

        # Button 1 hover
        is_btn1 = hasattr(self, 'btn1_x') and self.btn1_x <= x <= self.btn1_x + btn_w and self.btn1_y <= y <= self.btn1_y + btn_h
        # Badge 1 hover
        is_badge1 = hasattr(self, 'badge1_x') and self.badge1_x <= x <= self.badge1_x + badge_w and self.btn1_y <= y <= self.btn1_y + badge_h
        # Button 2 hover
        is_btn2 = hasattr(self, 'btn2_x') and self.btn2_x <= x <= self.btn2_x + btn_w and self.btn2_y <= y <= self.btn2_y + btn_h
        # Badge 2 hover
        is_badge2 = hasattr(self, 'badge2_x') and self.badge2_x <= x <= self.badge2_x + badge_w and self.btn2_y <= y <= self.btn2_y + badge_h

        # Update button 1 & badge 1
        if hasattr(self, 'btn_done_id'):
            self.canvas.itemconfig(self.btn_done_id, image=self.img_btn_done_hover if is_btn1 else self.img_btn_done)
        if hasattr(self, 'badge_done_id'):
            self.canvas.itemconfig(self.badge_done_id, image=self.img_badge_done_hover if is_badge1 else self.img_badge_done)

        # Update button 2 & badge 2
        if hasattr(self, 'btn_action_id'):
            self.canvas.itemconfig(self.btn_action_id, image=self.img_btn_action_hover if is_btn2 else self.img_btn_action)
        if hasattr(self, 'badge_act_id'):
            self.canvas.itemconfig(self.badge_act_id, image=self.img_badge_act_hover if is_badge2 else self.img_badge_act)

        # Donation buttons hover (DonationAlerts & Donatello)
        don_sz = getattr(self, 'don_sz', 38)
        is_da = hasattr(self, 'don1_x') and hasattr(self, 'don_y') and self.don1_x <= x <= self.don1_x + don_sz and self.don_y <= y <= self.don_y + don_sz
        is_donatello = hasattr(self, 'don2_x') and hasattr(self, 'don_y') and self.don2_x <= x <= self.don2_x + don_sz and self.don_y <= y <= self.don_y + don_sz

        if hasattr(self, 'btn_da_id') and hasattr(self, 'img_da'):
            self.canvas.itemconfig(self.btn_da_id, image=self.img_da_hover if is_da else self.img_da)
        if hasattr(self, 'btn_donatello_id') and hasattr(self, 'img_donatello'):
            self.canvas.itemconfig(self.btn_donatello_id, image=self.img_donatello_hover if is_donatello else self.img_donatello)

        if hasattr(self, 'item_don_tooltip'):
            if is_da:
                self.canvas.itemconfig(self.item_don_tooltip, text="DonationAlerts", fill="#FB923C")
            elif is_donatello:
                self.canvas.itemconfig(self.item_don_tooltip, text="Donatello", fill="#F472B6")
            else:
                self.canvas.itemconfig(self.item_don_tooltip, text="")

        if is_btn1 or is_badge1 or is_btn2 or is_badge2 or is_donatello or is_da:
            self.canvas.config(cursor="hand2")
        elif (tx1 - 10 <= x <= tx1 + tw + 10 and abs(y - y1_center) <= 15) or (tx1 - 10 <= x <= tx1 + tw + 10 and abs(y - y2_center) <= 15):
            self.canvas.config(cursor="hand2")
        elif hasattr(self, 'toggle_x') and self.toggle_x <= x <= self.toggle_x + 500 and self.toggle_y <= y <= self.toggle_y + 40:
            self.canvas.config(cursor="hand2")
        elif hasattr(self, 'lang_x') and self.lang_x <= x <= self.lang_x + lw and self.lang_y <= y <= self.lang_y + lh:
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="")

    def _on_canvas_click(self, event):
        x, y = event.x, event.y
        btn_w = getattr(self, 'btn_w', 120)
        btn_h = getattr(self, 'btn_h', 36)
        badge_w = getattr(self, 'badge_w', 210)
        badge_h = getattr(self, 'badge_h', 36)
        tx1 = getattr(self, 'track_x1', 485)
        tw = getattr(self, 'track_w', 215)
        don_sz = getattr(self, 'don_sz', 38)

        # Donation buttons click (DonationAlerts & Donatello)
        if hasattr(self, 'don1_x') and hasattr(self, 'don_y') and self.don1_x <= x <= self.don1_x + don_sz and self.don_y <= y <= self.don_y + don_sz:
            import webbrowser
            webbrowser.open_new_tab("https://dalink.to/reeshkaii")
            return

        if hasattr(self, 'don2_x') and hasattr(self, 'don_y') and self.don2_x <= x <= self.don2_x + don_sz and self.don_y <= y <= self.don_y + don_sz:
            import webbrowser
            webbrowser.open_new_tab("https://donatello.to/Reeshkaii")
            return

        # Check volume slider 1 click
        y1 = getattr(self, 'btn1_y', 218) + btn_h // 2
        if (tx1 - 10) <= x <= (tx1 + tw + 10) and abs(y - y1) <= 18:
            self._dragging_slider = "done"
            self._update_slider_from_mouse("done", x)
            return

        # Check volume slider 2 click
        y2 = getattr(self, 'btn2_y', 308) + btn_h // 2
        if (tx1 - 10) <= x <= (tx1 + tw + 10) and abs(y - y2) <= 18:
            self._dragging_slider = "action"
            self._update_slider_from_mouse("action", x)
            return

        # Button 1 or Badge 1 click
        if (hasattr(self, 'btn1_x') and self.btn1_x <= x <= self.btn1_x + btn_w and self.btn1_y <= y <= self.btn1_y + btn_h) or \
           (hasattr(self, 'badge1_x') and self.badge1_x <= x <= self.badge1_x + badge_w and self.btn1_y <= y <= self.btn1_y + badge_h):
            self.open_sound_menu("done")
            return

        # Button 2 or Badge 2 click
        if (hasattr(self, 'btn2_x') and self.btn2_x <= x <= self.btn2_x + btn_w and self.btn2_y <= y <= self.btn2_y + btn_h) or \
           (hasattr(self, 'badge2_x') and self.badge2_x <= x <= self.badge2_x + badge_w and self.btn2_y <= y <= self.btn2_y + badge_h):
            self.open_sound_menu("action")
            return

        # Toggle Switch click (toggle button or label)
        if hasattr(self, 'toggle_x') and self.toggle_x <= x <= self.toggle_x + 500 and self.toggle_y <= y <= self.toggle_y + 40:
            self.auto_patch_enabled = not self.auto_patch_enabled
            self.cfg["auto_patch_on_update"] = self.auto_patch_enabled
            save_config(self.cfg)
            toggle_w = max(44, int(48 * getattr(self, 'ui_scale', 1.0)))
            toggle_h = max(24, int(26 * getattr(self, 'ui_scale', 1.0)))
            toggle_r = int(toggle_h / 2)
            self.img_toggle = self._create_toggle_image(self.auto_patch_enabled, w=toggle_w, h=toggle_h, r=toggle_r)
            self.canvas.itemconfig(self.toggle_img_id, image=self.img_toggle)
            return

        # Language Bar click
        if hasattr(self, 'lang_x') and hasattr(self, 'lang_w'):
            lw = self.lang_w
            lh = getattr(self, 'lang_h', 30)
            if self.lang_y <= y <= self.lang_y + lh:
                slot_w = lw / 3.0
                if self.lang_x <= x < self.lang_x + slot_w:
                    self.trigger_language_transition("EN")
                elif self.lang_x + slot_w <= x < self.lang_x + 2 * slot_w:
                    self.trigger_language_transition("UA")
                elif self.lang_x + 2 * slot_w <= x <= self.lang_x + lw:
                    self.trigger_language_transition("RU")

    def trigger_language_transition(self, target_lang):
        if target_lang == self.current_lang:
            return
        self.target_lang = target_lang
        self.current_lang = target_lang
        self.cfg["language"] = target_lang
        save_config(self.cfg)

        lw = getattr(self, 'lang_w', 108)
        step = lw / 3.0
        pad = (step - int(step - 4)) / 2
        self.lang_slots = {"EN": pad, "UA": step + pad, "RU": 2 * step + pad}
        self.lang_target_x = float(self.lang_slots.get(target_lang, 2 * step + pad))

        # Smooth animated slider pill transition
        if not self.is_slider_animating:
            self._animate_lang_slider()

        # Update all UI texts and layout immediately in-place with zero coordinate drift
        self._update_ui_layout()

    def _animate_lang_slider(self):
        """Kinetic spring/lerp animation for the language pill slider."""
        self.is_slider_animating = True
        diff = self.lang_target_x - self.lang_slider_x
        lw = getattr(self, 'lang_w', 108)
        lh = getattr(self, 'lang_h', 30)
        lr = int(lh / 2)
        if abs(diff) > 0.5:
            self.lang_slider_x += diff * 0.35 # smooth deceleration curve
            img_lang = self._create_lang_bar_image(lw, lh, lr)
            self.canvas.itemconfig(self.lang_bar_id, image=img_lang)
            self.after(16, self._animate_lang_slider)
        else:
            self.lang_slider_x = self.lang_target_x
            img_lang = self._create_lang_bar_image(lw, lh, lr)
            self.canvas.itemconfig(self.lang_bar_id, image=img_lang)
            self.is_slider_animating = False

    def _animate_lang_fade_out(self, step=0):
        pass

    def _animate_lang_fade_in(self, step=0):
        pass

    def stop_preview(self):
        try:
            ctypes.windll.winmm.mciSendStringW('close sg_audio_prev', None, 0, 0)
        except Exception:
            pass

    def play_preview(self, audio_path, volume=100):
        if not audio_path or not os.path.exists(audio_path):
            return
        try:
            self.stop_preview()
            alias = 'sg_audio_prev'
            buf = ctypes.create_unicode_buffer(500)
            ctypes.windll.kernel32.GetShortPathNameW(audio_path, buf, 500)
            short_p = buf.value or audio_path
            res = ctypes.windll.winmm.mciSendStringW(f'open "{short_p}" type mpegvideo alias {alias}', None, 0, 0)
            if res == 0:
                mci_vol = max(0, min(1000, int(volume * 10)))
                ctypes.windll.winmm.mciSendStringW(f'setaudio {alias} volume to {mci_vol}', None, 0, 0)
                ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, 0)
        except Exception:
            pass

    def _on_canvas_drag(self, event):
        if self._dragging_slider:
            self._update_slider_from_mouse(self._dragging_slider, event.x)

    def _on_canvas_release(self, event):
        if self._dragging_slider:
            st = self._dragging_slider
            self._dragging_slider = None
            self._on_slider_finish(st)

    def _update_slider_from_mouse(self, sound_type, mouse_x):
        track_x1 = getattr(self, 'track_x1', 485)
        track_w = getattr(self, 'track_w', 215)
        btn_h = getattr(self, 'btn_h', 36)
        sc = getattr(self, 'ui_scale', 1.0)
        knob_r = max(7, int(8 * sc))

        pct = max(0, min(100, round((mouse_x - track_x1) / float(track_w) * 100)))
        knob_x = track_x1 + (track_w * pct / 100.0)

        if sound_type == "done":
            self.done_vol = pct
            y = getattr(self, 'btn1_y', 218) + btn_h // 2
            self.canvas.coords(self.item_vol_done_fill, track_x1, y, knob_x, y)
            self.canvas.coords(self.item_vol_done_knob, knob_x - knob_r, y - knob_r, knob_x + knob_r, y + knob_r)
            self.canvas.itemconfig(self.item_vol_done_lbl, text=f"{pct}%")
        else:
            self.act_vol = pct
            y = getattr(self, 'btn2_y', 308) + btn_h // 2
            self.canvas.coords(self.item_vol_act_fill, track_x1, y, knob_x, y)
            self.canvas.coords(self.item_vol_act_knob, knob_x - knob_r, y - knob_r, knob_x + knob_r, y + knob_r)
            self.canvas.itemconfig(self.item_vol_act_lbl, text=f"{pct}%")

        try:
            ctypes.windll.winmm.mciSendStringW(f'setaudio sg_audio_prev volume to {int(pct * 10)}', None, 0, 0)
        except Exception:
            pass

    def _on_slider_finish(self, sound_type):
        pct = self.done_vol if sound_type == "done" else self.act_vol
        self.cfg[f"{sound_type}_volume"] = pct
        save_config(self.cfg)

        snd_path = self.cfg.get(f"custom_{sound_type}_sound", "")
        cur_name = self.cfg.get(f"{sound_type}_sound_name", "")

        # If it's a built-in preset or missing/temp path, resolve from bundled assets
        if cur_name in ["Cyberpunk", "Original", "Minimal", "Arcade"]:
            filename = "done.mp3" if sound_type == "done" else "action.mp3"
            snd_path = get_resource_path(os.path.join('presets', cur_name, filename))
        elif not snd_path or not os.path.exists(snd_path):
            filename = "done.mp3" if sound_type == "done" else "action.mp3"
            default_p = "Cyberpunk" if sound_type == "done" else "Original"
            snd_path = get_resource_path(os.path.join('presets', default_p, filename))

        if os.path.exists(snd_path):
            self.play_preview(snd_path, volume=pct)
            import threading
            threading.Thread(target=self._apply_audio_file, args=(snd_path, sound_type, pct, False), daemon=True).start()

    def open_sound_menu(self, sound_type):
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["RU"])

        popup = tk.Toplevel(self)
        title_text = t["popup_title_done"] if sound_type == "done" else t["popup_title_action"]
        popup.title(title_text)
        popup_w, popup_h = 500, 580
        popup.geometry(f"{popup_w}x{popup_h}")
        popup.resizable(False, False)
        popup.configure(bg="#000000")
        popup.transient(self)
        popup.grab_set()

        popup.protocol("WM_DELETE_WINDOW", lambda: [self.stop_preview(), popup.destroy()])

        try:
            popup.update_idletasks()
            phwnd = ctypes.windll.user32.GetParent(popup.winfo_id())
            if not phwnd:
                phwnd = popup.winfo_id()
            black_c = ctypes.c_int(0x00000000)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(phwnd, 35, ctypes.byref(black_c), ctypes.sizeof(black_c))
        except:
            pass

        self._apply_window_icon(popup)

        popup.update_idletasks()
        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()
        win_x = self.winfo_rootx() + (self.winfo_width() - popup_w) // 2
        win_y = self.winfo_rooty() + (self.winfo_height() - popup_h) // 2
        win_x = max(10, min(win_x, screen_w - popup_w - 20))
        win_y = max(30, min(win_y, screen_h - popup_h - 50))
        popup.geometry(f"{popup_w}x{popup_h}+{win_x}+{win_y}")

        lbl_head = tk.Label(
            popup, text=title_text,
            font=("Unbounded", 12, "bold"),
            fg="#FFFFFF", bg="#000000"
        )
        lbl_head.pack(pady=(16, 4))

        # Volume slider for presets with comfortable 28px inner margin
        current_vol = self.cfg.get(f"{sound_type}_volume", 100)
        vol_frame = tk.Frame(popup, bg="#000000")
        vol_frame.pack(fill="x", padx=26, pady=(2, 10))

        lbl_vol = tk.Label(
            vol_frame,
            text=f"{t['sound_volume_label']} {current_vol}%",
            font=("Unbounded", 10),
            fg="#C084FC", bg="#000000"
        )
        lbl_vol.pack(anchor="center", pady=(0, 4))

        def on_vol_change(v):
            lbl_vol.configure(text=f"{t['sound_volume_label']} {v}%")
            try:
                ctypes.windll.winmm.mciSendStringW(f'setaudio sg_audio_prev volume to {int(v * 10)}', None, 0, 0)
            except:
                pass

        vol_slider = ModernCanvasSlider(
            vol_frame, from_=0, to=100, initial=current_vol,
            fill_color="#A855F7", knob_border="#C084FC", margin_x=16,
            on_change=on_vol_change
        )
        vol_slider.pack(fill="x", pady=(2, 4))

        options = [
            ("Cyberpunk", t["preset_cyberpunk"], "#D946EF", "lightning"),
            ("Original", t["preset_original"], "#9E9EAF", "bell"),
            ("Minimal", t["preset_minimal"], "#A855F7", "waves"),
            ("Arcade", t["preset_arcade"], "#38BDF8", "gamepad"),
        ]

        def on_choose_preset(p_name):
            self.stop_preview()
            popup.destroy()
            v = vol_slider.get()
            self.apply_preset_single(p_name, sound_type, volume=v)
            if sound_type == "done":
                self.done_vol = v
            else:
                self.act_vol = v
            self._cached_buttons.clear()
            self._update_ui_layout()

        def on_choose_custom():
            self.stop_preview()
            popup.destroy()
            self.choose_custom_file(sound_type, initial_volume=vol_slider.get())

        filename = "done.mp3" if sound_type == "done" else "action.mp3"
        cur_name = self.cfg.get(f"{sound_type}_sound_name", "")
        cur_path = self.cfg.get(f"custom_{sound_type}_sound", "")
        if not cur_name or cur_name in ["action", "done"]:
            if cur_path:
                norm_p = cur_path.replace('\\', '/')
                if "tts_" in os.path.basename(cur_path):
                    cur_name = "TTS"
                else:
                    for p_cand in ["Original", "Cyberpunk", "Minimal", "Arcade"]:
                        if f"/presets/{p_cand}/" in norm_p or f"/presets/{p_cand.lower()}/" in norm_p.lower() or f"\\presets\\{p_cand}\\" in cur_path:
                            cur_name = p_cand
                            break
                    if not cur_name or cur_name in ["action", "done"]:
                        cur_name = "Original" if sound_type == "action" else "Cyberpunk"
            else:
                cur_name = "Original" if sound_type == "action" else "Cyberpunk"

        is_custom_active = bool(cur_path and cur_name not in ["Cyberpunk", "Original", "Minimal", "Arcade", "TTS"])
        is_tts_active = (cur_name == "TTS")

        card_w = 460
        row_refs = []

        for p_name, p_label, p_color, p_icon in options:
            p_file = get_resource_path(os.path.join('presets', p_name, filename))
            is_active = (p_name == cur_name and not is_custom_active and not is_tts_active)
            card_h = 48
            card_r = 11

            bg_norm = "#28123B" if is_active else "#151220"
            border_norm = "#A855F7" if is_active else "#282035"
            bg_hov = "#381B52" if is_active else "#221A30"
            border_hov = "#C084FC" if is_active else "#3D2E55"
            txt_col = "#C084FC" if is_active else "#EEEEEE"

            img_norm = get_rounded_rect_image(card_w, card_h, card_r, bg_norm, border_norm, 1)
            img_hov = get_rounded_rect_image(card_w, card_h, card_r, bg_hov, border_hov, 1)
            row_refs.extend([img_norm, img_hov])

            c = tk.Canvas(popup, width=card_w, height=card_h, bg="#000000", highlightthickness=0, cursor="hand2")
            c.pack(pady=3)

            bg_item = c.create_image(0, 0, anchor="nw", image=img_norm)
            
            ico_photo = ImageTk.PhotoImage(draw_vector_icon(p_icon, color=p_color, size=20, factor=2))
            row_refs.append(ico_photo)

            if is_active:
                c.create_image(14, (card_h - 22) // 2, anchor="nw", image=self.check_ico_photo)
                c.create_image(38, (card_h - 20) // 2, anchor="nw", image=ico_photo)
                c.create_text(66, card_h // 2 - 1, anchor="w", text=p_label, fill=txt_col, font=("Unbounded", 10, "bold"))
            else:
                c.create_image(20, (card_h - 20) // 2, anchor="nw", image=ico_photo)
                c.create_text(48, card_h // 2 - 1, anchor="w", text=p_label, fill=txt_col, font=("Unbounded", 10, "normal"))

            # Rounded Play Button with generous padding and embedded vector text
            btn_w, btn_h, btn_r = 132, 28, 8
            btn_x = card_w - btn_w - 14
            btn_y = (card_h - btn_h) // 2

            img_p_norm = self._create_preview_button_image(t["preview_btn"], btn_w, btn_h, btn_r, False)
            img_p_hov = self._create_preview_button_image(t["preview_btn"], btn_w, btn_h, btn_r, True)
            row_refs.extend([img_p_norm, img_p_hov])

            p_btn_bg = c.create_image(btn_x, btn_y, anchor="nw", image=img_p_norm)

            def make_bindings(cv, b_item, p_bg, nm, pf, inorm, ihov, pnorm, phov, bx, by, bw, bh):
                def on_motion(e):
                    if bx <= e.x <= bx + bw and by <= e.y <= by + bh:
                        cv.itemconfig(p_bg, image=phov)
                        cv.itemconfig(b_item, image=inorm)
                    else:
                        cv.itemconfig(p_bg, image=pnorm)
                        cv.itemconfig(b_item, image=ihov)

                def on_leave(e):
                    cv.itemconfig(b_item, image=inorm)
                    cv.itemconfig(p_bg, image=pnorm)

                def on_click(e):
                    if bx <= e.x <= bx + bw and by <= e.y <= by + bh:
                        self.play_preview(pf, volume=vol_slider.get())
                    else:
                        on_choose_preset(nm)

                cv.bind("<Motion>", on_motion)
                cv.bind("<Leave>", on_leave)
                cv.bind("<Button-1>", on_click)

            make_bindings(c, bg_item, p_btn_bg, p_name, p_file, img_norm, img_hov, img_p_norm, img_p_hov, btn_x, btn_y, btn_w, btn_h)

        def on_open_tts():
            self.stop_preview()
            popup.destroy()
            self.open_tts_dialog(sound_type)

        # Local TTS synthesis card with phrase preview
        tts_h = 62
        tts_r = 12
        tts_bg_norm = "#28123B" if is_tts_active else "#161220"
        tts_border_norm = "#A855F7" if is_tts_active else "#282035"
        tts_bg_hov = "#381B52" if is_tts_active else "#221A30"
        tts_border_hov = "#C084FC" if is_tts_active else "#3D2E55"

        img_tts_norm = get_rounded_rect_image(card_w, tts_h, tts_r, tts_bg_norm, tts_border_norm, 1)
        img_tts_hov = get_rounded_rect_image(card_w, tts_h, tts_r, tts_bg_hov, tts_border_hov, 1)
        row_refs.extend([img_tts_norm, img_tts_hov])

        c_tts = tk.Canvas(popup, width=card_w, height=tts_h, bg="#000000", highlightthickness=0, cursor="hand2")
        c_tts.pack(pady=(5, 3))

        tts_bg_item = c_tts.create_image(0, 0, anchor="nw", image=img_tts_norm)

        tts_current_phrase = self.cfg.get("tts_last_text", t["tts_placeholder"]).strip()
        if len(tts_current_phrase) > 28:
            tts_current_phrase = tts_current_phrase[:26] + "..."

        f_tts_title = tkFont.Font(font=("Unbounded", 10, "bold" if is_tts_active else "normal"))
        title_txt = t['tts_btn']
        title_w = f_tts_title.measure(title_txt)

        f_tts_sub = tkFont.Font(font=("Unbounded", 8))
        sub_txt = f"Фраза: «{tts_current_phrase}»"
        sub_w = f_tts_sub.measure(sub_txt)

        mic_w = 26
        gap = 10

        if is_tts_active:
            chk_w = 22
            gap_chk = 8
            total_w1 = chk_w + gap_chk + mic_w + gap + title_w
            start_x1 = (card_w - total_w1) // 2
            c_tts.create_image(start_x1, (tts_h - 22) // 2 - 8, anchor="nw", image=self.check_ico_photo)
            mic_x = start_x1 + chk_w + gap_chk
            c_tts.create_image(mic_x, (tts_h - mic_w) // 2 - 8, anchor="nw", image=self.mic_ico_photo)
            c_tts.create_text(mic_x + mic_w + gap, 21, anchor="w", text=title_txt, fill="#C084FC", font=f_tts_title)

            start_x2 = (card_w - sub_w) // 2
            c_tts.create_text(start_x2, 43, anchor="w", text=sub_txt, fill="#A855F7", font=f_tts_sub)
        else:
            total_w1 = mic_w + gap + title_w
            start_x1 = (card_w - total_w1) // 2
            c_tts.create_image(start_x1, (tts_h - mic_w) // 2 - 8, anchor="nw", image=self.mic_ico_photo)
            c_tts.create_text(start_x1 + mic_w + gap, 21, anchor="w", text=title_txt, fill="#E0D0F5", font=f_tts_title)

            start_x2 = (card_w - sub_w) // 2
            c_tts.create_text(start_x2, 43, anchor="w", text=sub_txt, fill="#9A8CAD", font=f_tts_sub)

        c_tts.bind("<Enter>", lambda e, b=tts_bg_item, h=img_tts_hov: c_tts.itemconfig(b, image=h))
        c_tts.bind("<Leave>", lambda e, b=tts_bg_item, n=img_tts_norm: c_tts.itemconfig(b, image=n))
        c_tts.bind("<Button-1>", lambda e: on_open_tts())

        # Custom file card
        cust_h = 48
        cust_r = 12
        cust_bg_norm = "#28123B" if is_custom_active else "#161220"
        cust_border_norm = "#A855F7" if is_custom_active else "#282035"
        cust_bg_hov = "#381B52" if is_custom_active else "#221A30"
        cust_border_hov = "#C084FC" if is_custom_active else "#3D2E55"

        img_cust_norm = get_rounded_rect_image(card_w, cust_h, cust_r, cust_bg_norm, cust_border_norm, 1)
        img_cust_hov = get_rounded_rect_image(card_w, cust_h, cust_r, cust_bg_hov, cust_border_hov, 1)
        row_refs.extend([img_cust_norm, img_cust_hov])

        c_cust = tk.Canvas(popup, width=card_w, height=cust_h, bg="#000000", highlightthickness=0, cursor="hand2")
        c_cust.pack(pady=(4, 16))

        cust_bg_item = c_cust.create_image(0, 0, anchor="nw", image=img_cust_norm)

        font_cust = ("Unbounded", 10, "bold" if is_custom_active else "normal")
        f_obj = tkFont.Font(font=font_cust)

        if is_custom_active:
            short_cur = cur_name[:18] + "..." if len(cur_name) > 20 else cur_name
            cust_display = f"{t['custom_file_tag']}: {short_cur}"
            text_w = f_obj.measure(cust_display)
            chk_w, fld_w = 22, 26
            gap1, gap2 = 8, 10
            total_w = chk_w + gap1 + fld_w + gap2 + text_w
            start_x = (card_w - total_w) // 2
            chk_x = start_x
            fld_x = chk_x + chk_w + gap1
            txt_x = fld_x + fld_w + gap2

            c_cust.create_image(chk_x, (cust_h - 22) // 2, anchor="nw", image=self.check_ico_photo)
            c_cust.create_image(fld_x, (cust_h - fld_w) // 2, anchor="nw", image=self.folder_ico_photo)
            c_cust.create_text(txt_x, cust_h // 2, anchor="w", text=cust_display, fill="#C084FC", font=font_cust)
        else:
            cust_display = t["custom_file"]
            text_w = f_obj.measure(cust_display)
            fld_w = 26
            gap = 10
            total_w = fld_w + gap + text_w
            start_x = (card_w - total_w) // 2
            fld_x = start_x
            txt_x = fld_x + fld_w + gap

            c_cust.create_image(fld_x, (cust_h - fld_w) // 2, anchor="nw", image=self.folder_ico_photo)
            c_cust.create_text(txt_x, cust_h // 2, anchor="w", text=cust_display, fill="#E0D0F5", font=font_cust)

        c_cust.bind("<Enter>", lambda e, b=cust_bg_item, h=img_cust_hov: c_cust.itemconfig(b, image=h))
        c_cust.bind("<Leave>", lambda e, b=cust_bg_item, n=img_cust_norm: c_cust.itemconfig(b, image=n))
        c_cust.bind("<Button-1>", lambda e: on_choose_custom())

        popup._row_refs = row_refs

    def apply_preset_single(self, preset_name, sound_type, volume=100, show_alert=True):
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["RU"])
        filename = "done.mp3" if sound_type == "done" else "action.mp3"
        preset_file = get_resource_path(os.path.join('presets', preset_name, filename))

        if not os.path.exists(preset_file):
            if show_alert:
                self.show_dark_notification(t["error_title"], f"{t['file_missing']}\n{preset_file}", is_error=True)
            return

        ls_path = find_language_server()
        if not ls_path:
            if show_alert:
                self.show_dark_notification(t["error_title"], t["not_found"], is_error=True)
            return

        try:
            with open(preset_file, 'rb') as f:
                audio_bytes = f.read()

            audio_bytes = adjust_audio_volume(audio_bytes, volume)

            done_bytes = audio_bytes if sound_type == "done" else None
            action_bytes = audio_bytes if sound_type == "action" else None

            if sound_type == "done":
                self.cfg["custom_done_sound"] = preset_file
                self.cfg["done_volume"] = volume
                self.cfg["done_sound_name"] = preset_name
            else:
                self.cfg["custom_action_sound"] = preset_file
                self.cfg["action_volume"] = volume
                self.cfg["action_sound_name"] = preset_name
            save_config(self.cfg)
            self._cached_buttons.clear()

            patch_language_server_exe(ls_path, done_bytes, action_bytes)
            self.after(0, self._update_ui_layout)
            if show_alert:
                self.show_dark_notification(t["success_title"], f"{t['success_msg']}\n[{preset_name}]")
        except Exception as e:
            if show_alert:
                self.show_dark_notification(t["error_title"], str(e), is_error=True)

    def open_tts_dialog(self, sound_type):
        """Multilingual Neural & Offline TTS generator with persisted text, speed, volume, and voice."""
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["RU"])

        diag = tk.Toplevel(self)
        diag.title(t["tts_title"])
        diag_w, diag_h = 580, 610
        diag.geometry(f"{diag_w}x{diag_h}")
        diag.resizable(False, False)
        diag.configure(bg="#000000")
        diag.transient(self)
        diag.grab_set()

        diag.protocol("WM_DELETE_WINDOW", lambda: [self.stop_preview(), diag.destroy()])

        try:
            diag.update_idletasks()
            dhwnd = ctypes.windll.user32.GetParent(diag.winfo_id())
            if not dhwnd:
                dhwnd = diag.winfo_id()
            black_c = ctypes.c_int(0x00000000)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(dhwnd, 35, ctypes.byref(black_c), ctypes.sizeof(black_c))
        except:
            pass

        self._apply_window_icon(diag)

        diag.update_idletasks()
        screen_w = diag.winfo_screenwidth()
        screen_h = diag.winfo_screenheight()
        win_x = self.winfo_rootx() + (self.winfo_width() - diag_w) // 2
        win_y = self.winfo_rooty() + (self.winfo_height() - diag_h) // 2
        win_x = max(10, min(win_x, screen_w - diag_w - 20))
        win_y = max(30, min(win_y, screen_h - diag_h - 50))
        diag.geometry(f"{diag_w}x{diag_h}+{win_x}+{win_y}")

        # Label Prompt
        lbl_p = tk.Label(
            diag, text=t["tts_prompt"],
            font=("Unbounded", 10, "bold"),
            fg="#FFFFFF", bg="#000000"
        )
        lbl_p.pack(pady=(16, 6))

        # Text Entry with beautiful rounded anti-aliased container and focus glow
        saved_text = self.cfg.get("tts_last_text", "")
        if not saved_text:
            saved_text = t["tts_placeholder"]

        entry_w = 520
        entry_h = 44
        entry_r = 12

        img_entry_norm = get_rounded_rect_image(entry_w, entry_h, entry_r, "#151220", "#2E1E45", 1)
        img_entry_focus = get_rounded_rect_image(entry_w, entry_h, entry_r, "#1A1428", "#A855F7", 1)

        entry_canvas = tk.Canvas(diag, width=entry_w, height=entry_h, bg="#000000", highlightthickness=0, bd=0)
        entry_canvas.pack(padx=30, pady=(2, 8))
        entry_bg_id = entry_canvas.create_image(0, 0, anchor="nw", image=img_entry_norm)
        entry_canvas._img_norm = img_entry_norm
        entry_canvas._img_focus = img_entry_focus

        txt_entry = tk.Entry(
            entry_canvas, font=("Unbounded", 10),
            bg="#151220", fg="#FFFFFF",
            insertbackground="#C084FC",
            relief="flat", bd=0, highlightthickness=0
        )
        entry_canvas.create_window(16, entry_h // 2, window=txt_entry, anchor="w", width=entry_w - 32)
        txt_entry.insert(0, saved_text)

        def on_entry_focus_in(e):
            entry_canvas.itemconfig(entry_bg_id, image=img_entry_focus)
            txt_entry.configure(bg="#1A1428")

        def on_entry_focus_out(e):
            entry_canvas.itemconfig(entry_bg_id, image=img_entry_norm)
            txt_entry.configure(bg="#151220")

        txt_entry.bind("<FocusIn>", on_entry_focus_in)
        txt_entry.bind("<FocusOut>", on_entry_focus_out)
        entry_canvas.bind("<Button-1>", lambda e: txt_entry.focus_set())

        # Keyboard shortcuts for Copy, Paste, Cut, Select All (Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A)
        def handle_paste(event=None):
            try:
                clip = diag.clipboard_get()
                if txt_entry.select_present():
                    txt_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
                txt_entry.insert(tk.INSERT, clip)
            except:
                pass
            return "break"

        def handle_copy(event=None):
            try:
                if txt_entry.select_present():
                    text = txt_entry.selection_get()
                    diag.clipboard_clear()
                    diag.clipboard_append(text)
            except:
                pass
            return "break"

        def handle_cut(event=None):
            try:
                if txt_entry.select_present():
                    text = txt_entry.selection_get()
                    diag.clipboard_clear()
                    diag.clipboard_append(text)
                    txt_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except:
                pass
            return "break"

        def handle_select_all(event=None):
            txt_entry.select_range(0, tk.END)
            txt_entry.icursor(tk.END)
            return "break"

        def on_entry_key_press(event):
            if (event.state & 4) or (event.state & 0x20000):
                if event.keycode == 86:
                    return handle_paste(event)
                elif event.keycode == 67:
                    return handle_copy(event)
                elif event.keycode == 88:
                    return handle_cut(event)
                elif event.keycode == 65:
                    return handle_select_all(event)
            return None

        txt_entry.bind("<KeyPress>", on_entry_key_press)
        txt_entry.bind("<Control-v>", handle_paste)
        txt_entry.bind("<Control-V>", handle_paste)
        txt_entry.bind("<Control-c>", handle_copy)
        txt_entry.bind("<Control-C>", handle_copy)
        txt_entry.bind("<Control-x>", handle_cut)
        txt_entry.bind("<Control-X>", handle_cut)
        txt_entry.bind("<Control-a>", handle_select_all)
        txt_entry.bind("<Control-A>", handle_select_all)

        menu = tk.Menu(txt_entry, tearoff=0, bg="#181424", fg="#FFFFFF", activebackground="#2E1646", activeforeground="#C084FC")
        menu.add_command(label=f"{t['menu_copy']} (Ctrl+C)", command=handle_copy)
        menu.add_command(label=f"{t['menu_paste']} (Ctrl+V)", command=handle_paste)
        menu.add_command(label=f"{t['menu_cut']} (Ctrl+X)", command=handle_cut)
        menu.add_separator()
        menu.add_command(label=f"{t['menu_select_all']} (Ctrl+A)", command=handle_select_all)

        def show_context_menu(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        txt_entry.bind("<Button-3>", show_context_menu)

        # Voice / Language selector with 100% vector rounded pills
        voice_frame = tk.Frame(diag, bg="#000000")
        voice_frame.pack(fill="x", padx=30, pady=(2, 6))

        v_lbl = tk.Label(voice_frame, text=t.get("tts_voice_label", "Голос / Озвучка:"), font=("Unbounded", 8), fg="#999999", bg="#000000")
        v_lbl.pack(anchor="w", pady=(0, 4))

        selected_voice = [self.cfg.get("tts_last_voice", "auto")]
        voice_widgets = {}

        voices_row1 = [
            ("auto", t.get("tts_voice_auto", "Авто")),
            ("ostap", "Остап (UA)"),
            ("polina", "Поліна (UA)")
        ]
        voices_row2 = [
            ("dmitry", "Дмитрий (RU)"),
            ("svetlana", "Светлана (RU)"),
            ("andrew", "Andrew (AI)"),
            ("ava", "Ava (AI)")
        ]
        voices_row3 = [
            ("guy", "Guy (EN)"),
            ("aria", "Aria (EN)"),
            ("brian", "Brian (AI)"),
            ("emma", "Emma (AI)")
        ]

        f_pill = tkFont.Font(font=("Unbounded", 8, "bold"))
        pill_h, pill_r = 28, 12

        def update_voice_pills():
            cur = selected_voice[0]
            for v_key, info in voice_widgets.items():
                cv = info["cv"]
                bg_id = info["bg_id"]
                txt_id = info["txt_id"]
                is_sel = (v_key == cur) or (cur in ["UA", "RU", "EN"] and ((cur == "UA" and v_key == "ostap") or (cur == "RU" and v_key == "dmitry") or (cur == "EN" and v_key == "andrew")))
                cv.itemconfig(bg_id, image=info["img_sel"] if is_sel else info["img_norm"])
                cv.itemconfig(txt_id, fill="#FFFFFF" if is_sel else "#9E9EAF")

        def select_voice(v_key):
            selected_voice[0] = v_key
            self.cfg["tts_last_voice"] = v_key
            save_config(self.cfg)
            update_voice_pills()

        for row_voices in [voices_row1, voices_row2, voices_row3]:
            row_box = tk.Frame(voice_frame, bg="#000000")
            row_box.pack(anchor="w", pady=(0, 4))
            for v_key, v_title in row_voices:
                pw = max(52, f_pill.measure(v_title) + 20)
                img_n = get_rounded_rect_image(pw, pill_h, pill_r, "#151220", "#281A3E", 1)
                img_s = get_rounded_rect_image(pw, pill_h, pill_r, "#381B52", "#C084FC", 1)
                img_h = get_rounded_rect_image(pw, pill_h, pill_r, "#241836", "#7C3AED", 1)

                cv = tk.Canvas(row_box, width=pw, height=pill_h, bg="#000000", highlightthickness=0, bd=0, cursor="hand2")
                cv.pack(side="left", padx=(0, 6))

                bg_id = cv.create_image(0, 0, anchor="nw", image=img_n)
                txt_id = cv.create_text(pw // 2, pill_h // 2, text=v_title, font=("Unbounded", 8, "bold"), fill="#9E9EAF")

                voice_widgets[v_key] = {
                    "cv": cv, "bg_id": bg_id, "txt_id": txt_id,
                    "img_norm": img_n, "img_sel": img_s, "img_hov": img_h
                }

                def make_pill_handlers(k=v_key, c=cv, b=bg_id, t_itm=txt_id, inorm=img_n, isel=img_s, ihov=img_h):
                    def on_enter(e):
                        if selected_voice[0] != k:
                            c.itemconfig(b, image=ihov)
                            c.itemconfig(t_itm, fill="#FFFFFF")
                    def on_leave(e):
                        if selected_voice[0] != k:
                            c.itemconfig(b, image=inorm)
                            c.itemconfig(t_itm, fill="#9E9EAF")
                    def on_click(e):
                        select_voice(k)

                    c.bind("<Enter>", on_enter)
                    c.bind("<Leave>", on_leave)
                    c.bind("<Button-1>", on_click)

                make_pill_handlers()

        update_voice_pills()

        # Volume Slider
        saved_vol = int(self.cfg.get("tts_last_volume", 100))
        vol_frame = tk.Frame(diag, bg="#000000")
        vol_frame.pack(fill="x", padx=30, pady=(8, 2))

        vol_lbl = tk.Label(
            vol_frame, text=f"{t['tts_volume_label']} {saved_vol}%",
            font=("Unbounded", 8),
            fg="#C084FC", bg="#000000"
        )
        vol_lbl.pack(anchor="w")

        vol_slider = ModernCanvasSlider(
            vol_frame, from_=0, to=100, initial=saved_vol,
            fill_color="#A855F7", knob_border="#C084FC",
            on_change=lambda v: vol_lbl.configure(text=f"{t['tts_volume_label']} {v}%")
        )
        vol_slider.pack(fill="x", pady=(2, 4))

        # Speed / Rate Slider: -5 to +5
        saved_rate = int(self.cfg.get("tts_last_rate", 0))
        rate_frame = tk.Frame(diag, bg="#000000")
        rate_frame.pack(fill="x", padx=30, pady=(2, 8))

        def format_rate(v):
            if v > 0:
                return f"{t['tts_speed_label']} +{v}"
            return f"{t['tts_speed_label']} {v}"

        rate_lbl = tk.Label(
            rate_frame, text=format_rate(saved_rate),
            font=("Unbounded", 8),
            fg="#C084FC", bg="#000000"
        )
        rate_lbl.pack(anchor="w")

        rate_slider = ModernCanvasSlider(
            rate_frame, from_=-5, to=5, initial=saved_rate,
            fill_color="#A855F7", knob_border="#C084FC",
            on_change=lambda v: rate_lbl.configure(text=format_rate(v))
        )
        rate_slider.pack(fill="x", pady=(2, 4))

        # Output audio path
        temp_dir = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'SoundGravity')
        os.makedirs(temp_dir, exist_ok=True)
        gen_audio = os.path.join(temp_dir, f"tts_{sound_type}.mp3")

        def synthesize_tts():
            phrase = txt_entry.get().strip() or t["tts_placeholder"]
            vol = vol_slider.get()
            rate = rate_slider.get()
            voice_choice = selected_voice[0]

            self.cfg["tts_last_text"] = phrase
            self.cfg["tts_last_volume"] = vol
            self.cfg["tts_last_rate"] = rate
            self.cfg["tts_last_voice"] = voice_choice
            save_config(self.cfg)

            success, engine_info = synthesize_multilingual_tts(
                phrase, gen_audio, rate=rate, volume=vol, voice_choice=voice_choice
            )
            if not success or not os.path.exists(gen_audio):
                self.show_dark_notification(t["error_title"], str(engine_info), is_error=True)
                return False
            return True

        action_box = tk.Frame(diag, bg="#000000")
        action_box.pack(pady=(10, 16))

        def on_tts_preview():
            self.stop_preview()
            if synthesize_tts():
                self.play_preview(gen_audio, volume=vol_slider.get())

        btn_prev = create_rounded_pill_button(
            action_box, t["tts_generate_btn"],
            width=335, height=38, radius=12,
            bg_norm="#26163B", border_norm="#3D255A",
            bg_hov="#381B52", border_hov="#C084FC",
            fg_norm="#C084FC", fg_hov="#FFFFFF",
            command=on_tts_preview,
            font=("Unbounded", 8, "bold")
        )
        btn_prev.pack(side="left", padx=8)

        def on_tts_apply():
            if not os.path.exists(gen_audio):
                if not synthesize_tts():
                    return
            else:
                current_phrase = txt_entry.get().strip() or t["tts_placeholder"]
                if current_phrase != self.cfg.get("tts_last_text"):
                    if not synthesize_tts():
                        return

            v = vol_slider.get()
            self.stop_preview()
            diag.destroy()

            self.cfg[f"{sound_type}_sound_name"] = "TTS"
            if sound_type == "done":
                self.done_vol = v
            else:
                self.act_vol = v
            save_config(self.cfg)

            self._apply_audio_file(gen_audio, sound_type, volume=v)
            self._update_ui_layout()

        btn_app = create_rounded_pill_button(
            action_box, t["apply_btn"],
            width=135, height=38, radius=12,
            bg_norm="#A855F7", border_norm="#C084FC",
            bg_hov="#C084FC", border_hov="#E0D0F5",
            fg_norm="#FFFFFF", fg_hov="#000000",
            command=on_tts_apply,
            font=("Unbounded", 9, "bold")
        )
        btn_app.pack(side="left", padx=8)

    def choose_custom_file(self, sound_type, initial_volume=None):
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["RU"])
        fpath = filedialog.askopenfilename(
            title=t["btn_select"],
            filetypes=[("Audio Files (*.mp3;*.wav)", "*.mp3;*.wav"), ("MP3 Files", "*.mp3"), ("WAV Files", "*.wav"), ("All Files", "*.*")]
        )
        if not fpath:
            return

        # Open Custom Sound Preview & Confirmation Dialog before installing
        self.show_custom_preview_dialog(fpath, sound_type, initial_volume=initial_volume)

    def show_custom_preview_dialog(self, fpath, sound_type, initial_volume=None):
        """Shows modal to listen to user's selected file before applying."""
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["RU"])
        fname = os.path.basename(fpath)

        diag = tk.Toplevel(self)
        diag.title(t["preview_custom_title"])
        diag_w, diag_h = 420, 270
        diag.geometry(f"{diag_w}x{diag_h}")
        diag.resizable(False, False)
        diag.configure(bg="#000000")
        diag.transient(self)
        diag.grab_set()

        diag.protocol("WM_DELETE_WINDOW", lambda: [self.stop_preview(), diag.destroy()])

        try:
            diag.update_idletasks()
            dhwnd = ctypes.windll.user32.GetParent(diag.winfo_id())
            if not dhwnd:
                dhwnd = diag.winfo_id()
            black_c = ctypes.c_int(0x00000000)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(dhwnd, 35, ctypes.byref(black_c), ctypes.sizeof(black_c))
        except:
            pass

        self._apply_window_icon(diag)

        diag.update_idletasks()
        screen_w = diag.winfo_screenwidth()
        screen_h = diag.winfo_screenheight()
        win_x = self.winfo_rootx() + (self.winfo_width() - diag_w) // 2
        win_y = self.winfo_rooty() + (self.winfo_height() - diag_h) // 2
        win_x = max(10, min(win_x, screen_w - diag_w - 20))
        win_y = max(30, min(win_y, screen_h - diag_h - 50))
        diag.geometry(f"{diag_w}x{diag_h}+{win_x}+{win_y}")

        msg_text = t["preview_custom_msg"].format(name=fname)
        lbl = tk.Label(
            diag, text=msg_text,
            font=("Unbounded", 9),
            fg="#FFFFFF", bg="#000000",
            justify="center", wraplength=400
        )
        lbl.pack(pady=(16, 6))

        # Volume Slider
        current_vol = initial_volume if initial_volume is not None else self.cfg.get(f"{sound_type}_volume", 100)
        vol_frame = tk.Frame(diag, bg="#000000")
        vol_frame.pack(fill="x", padx=32, pady=(2, 8))

        lbl_vol = tk.Label(
            vol_frame,
            text=f"{t['sound_volume_label']} {current_vol}%",
            font=("Unbounded", 9),
            fg="#C084FC", bg="#000000"
        )
        lbl_vol.pack(anchor="w")

        def on_custom_vol_change(v):
            lbl_vol.configure(text=f"{t['sound_volume_label']} {v}%")
            try:
                ctypes.windll.winmm.mciSendStringW(f'setaudio sg_audio_prev volume to {int(v * 10)}', None, 0, 0)
            except:
                pass

        vol_slider = ModernCanvasSlider(
            vol_frame, from_=0, to=100, initial=current_vol,
            fill_color="#A855F7", knob_border="#C084FC",
            on_change=on_custom_vol_change
        )
        vol_slider.pack(fill="x", pady=(4, 6))

        btn_box = tk.Frame(diag, bg="#000000")
        btn_box.pack(pady=10)

        # 1. Preview button
        btn_play = create_rounded_pill_button(
            btn_box, t["preview_btn"],
            width=140, height=34, radius=12,
            bg_norm="#26163B", border_norm="#3D255A",
            bg_hov="#381B52", border_hov="#C084FC",
            fg_norm="#C084FC", fg_hov="#FFFFFF",
            command=lambda: self.play_preview(fpath, volume=vol_slider.get())
        )
        btn_play.pack(side="left", padx=10)

        # 2. Apply button
        def on_confirm_apply():
            v = vol_slider.get()
            self.stop_preview()
            diag.destroy()
            fname_base = os.path.splitext(os.path.basename(fpath))[0]
            if sound_type == "done":
                self.cfg["done_sound_name"] = fname_base
                self.done_vol = v
            else:
                self.cfg["action_sound_name"] = fname_base
                self.act_vol = v
            save_config(self.cfg)
            self._apply_audio_file(fpath, sound_type, volume=v)
            self._update_ui_layout()

        btn_apply = create_rounded_pill_button(
            btn_box, t["apply_btn"],
            width=140, height=34, radius=12,
            bg_norm="#A855F7", border_norm="#C084FC",
            bg_hov="#C084FC", border_hov="#E0D0F5",
            fg_norm="#000000", fg_hov="#000000",
            command=on_confirm_apply
        )
        btn_apply.pack(side="left", padx=10)

    def _apply_audio_file(self, fpath, sound_type, volume=100, show_alert=True):
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["RU"])
        ls_path = find_language_server()
        if not ls_path:
            if show_alert:
                self.show_dark_notification(t["error_title"], t["not_found"], is_error=True)
            return

        try:
            with open(fpath, 'rb') as f:
                audio_bytes = f.read()

            audio_bytes = adjust_audio_volume(audio_bytes, volume)

            done_bytes = audio_bytes if sound_type == "done" else None
            action_bytes = audio_bytes if sound_type == "action" else None

            # Detect if file belongs to a preset
            norm_path = fpath.replace('\\', '/')
            detected_preset = None
            for p_cand in ["Original", "Cyberpunk", "Minimal", "Arcade"]:
                if f"/presets/{p_cand}/" in norm_path or f"/presets/{p_cand}\\" in norm_path or f"\\presets\\{p_cand}\\" in fpath:
                    detected_preset = p_cand
                    break

            if sound_type == "done":
                self.cfg["custom_done_sound"] = fpath
                self.cfg["done_volume"] = volume
                if "tts_" in os.path.basename(fpath):
                    self.cfg["done_sound_name"] = "TTS"
                elif detected_preset:
                    self.cfg["done_sound_name"] = detected_preset
                else:
                    cur_cur = self.cfg.get("done_sound_name", "")
                    if cur_cur and cur_cur not in ["done", "action"]:
                        pass
                    else:
                        base = os.path.splitext(os.path.basename(fpath))[0]
                        self.cfg["done_sound_name"] = base if base not in ["done", "action"] else "Cyberpunk"
            else:
                self.cfg["custom_action_sound"] = fpath
                self.cfg["action_volume"] = volume
                if "tts_" in os.path.basename(fpath):
                    self.cfg["action_sound_name"] = "TTS"
                elif detected_preset:
                    self.cfg["action_sound_name"] = detected_preset
                else:
                    cur_cur = self.cfg.get("action_sound_name", "")
                    if cur_cur and cur_cur not in ["done", "action"]:
                        pass
                    else:
                        base = os.path.splitext(os.path.basename(fpath))[0]
                        self.cfg["action_sound_name"] = base if base not in ["done", "action"] else "Original"

            save_config(self.cfg)
            self._cached_buttons.clear()
            patch_language_server_exe(ls_path, done_bytes, action_bytes)
            self.after(0, self._update_ui_layout)
            if show_alert:
                self.show_dark_notification(t["success_title"], t["success_msg"])
        except Exception as e:
            if show_alert:
                self.show_dark_notification(t["error_title"], str(e), is_error=True)

    def _create_phosphor_icon(self, is_error=False, size=38):
        """Draws clean Phosphor Icons checkmark or X."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        scale = size / 256.0
        if is_error:
            color = '#FF4444'
            stroke_w = max(2, round(22 * scale))
            draw.line([(48 * scale, 48 * scale), (208 * scale, 208 * scale)], fill=color, width=stroke_w)
            draw.line([(208 * scale, 48 * scale), (48 * scale, 208 * scale)], fill=color, width=stroke_w)
        else:
            # Official Phosphor Check icon geometry (curved joint, round ends)
            color = '#A855F7'
            stroke_w = max(2, round(24 * scale))
            pts = [
                (40 * scale, 128 * scale),
                (96 * scale, 184 * scale),
                (216 * scale, 64 * scale)
            ]
            draw.line(pts, fill=color, width=stroke_w, joint='curve')
        return ImageTk.PhotoImage(img)

    def show_dark_notification(self, title, message, is_error=False):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("380x150")
        dialog.resizable(False, False)
        dialog.configure(bg="#000000")
        dialog.transient(self)
        dialog.grab_set()

        try:
            dialog.update_idletasks()
            dhwnd = ctypes.windll.user32.GetParent(dialog.winfo_id())
            if not dhwnd:
                dhwnd = dialog.winfo_id()
            black_c = ctypes.c_int(0x00000000)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(dhwnd, 35, ctypes.byref(black_c), ctypes.sizeof(black_c))
        except:
            pass

        self._apply_window_icon(dialog)

        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")

        # Phosphor icon image
        dialog._icon_photo = self._create_phosphor_icon(is_error=is_error, size=38)
        lbl_icon = tk.Label(
            dialog, image=dialog._icon_photo,
            bg="#000000"
        )
        lbl_icon.place(x=20, y=26)

        lbl_msg = tk.Label(
            dialog, text=message,
            font=("Unbounded", 10),
            fg="#E0E0E0", bg="#000000",
            justify="left", wraplength=270
        )
        lbl_msg.place(x=68, y=28)

        btn_ok = create_rounded_pill_button(
            dialog, "OK",
            width=80, height=30, radius=12,
            bg_norm="#A855F7", border_norm="#C084FC",
            bg_hov="#C084FC", border_hov="#E0D0F5",
            fg_norm="#000000", fg_hov="#000000",
            command=dialog.destroy
        )
        btn_ok.place(x=276, y=102)

    def _on_auto_patched(self):
        print("[SoundGravity] Sounds were automatically reapplied after Antigravity update.")

if __name__ == "__main__":
    app = SoundGravityCanvasApp()
    app.mainloop()
