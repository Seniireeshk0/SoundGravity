import os
import sys
import time
import json
import threading
import subprocess
from patcher import find_language_server, patch_language_server_exe, adjust_audio_volume

CONFIG_DIR = os.path.join(os.environ.get('APPDATA', ''), 'SoundGravity')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def load_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    cfg = {
        "language": "RU",
        "custom_done_sound": "",
        "custom_action_sound": "",
        "done_sound_name": "Cyberpunk",
        "action_sound_name": "Original",
        "auto_patch_on_update": True,
        "last_known_hash": "",
        "done_volume": 100,
        "action_volume": 100
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                cfg.update(loaded)
        except:
            pass

    # Sanitize legacy corrupted names
    modified = False
    if cfg.get("done_sound_name") in ["done", ""]:
        cfg["done_sound_name"] = "Cyberpunk"
        modified = True
    if cfg.get("action_sound_name") in ["action", ""]:
        cfg["action_sound_name"] = "Original"
        modified = True

    if modified:
        try:
            save_config(cfg)
        except Exception:
            pass

    return cfg

def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def get_file_quick_hash(path):
    if not os.path.exists(path):
        return ""
    stat = os.stat(path)
    return f"{stat.st_size}_{stat.st_mtime}"

class UpdateWatcher:
    """
    Watches language_server.exe for updates (size/mtime change).
    When Antigravity updates, it automatically reapplies the custom sounds.
    """
    def __init__(self, on_reapplied_callback=None):
        self.running = False
        self.thread = None
        self.callback = on_reapplied_callback

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _watch_loop(self):
        while self.running:
            time.sleep(4.0)
            cfg = load_config()
            if not cfg.get("auto_patch_on_update", True):
                continue

            ls_path = find_language_server()
            if not ls_path or not os.path.exists(ls_path):
                continue

            # Check if language_server.exe is unpatched (missing .snddata)
            try:
                with open(ls_path, 'rb') as f:
                    data = f.read(2048) # headers
                    has_snddata = b'.snddata' in data
                
                if not has_snddata:
                    # Antigravity was updated by its updater! Reapply custom sounds!
                    done_vol = cfg.get("done_volume", 100)
                    act_vol = cfg.get("action_volume", 100)
                    done_name = cfg.get("done_sound_name", "Cyberpunk")
                    act_name = cfg.get("action_sound_name", "Original")

                    done_snd = cfg.get("custom_done_sound", "")
                    if done_name in ["Cyberpunk", "Original", "Minimal", "Arcade"] or not os.path.exists(done_snd):
                        done_snd = get_resource_path(os.path.join('presets', done_name if done_name in ["Cyberpunk", "Original", "Minimal", "Arcade"] else "Cyberpunk", 'done.mp3'))

                    act_snd = cfg.get("custom_action_sound", "")
                    if act_name in ["Cyberpunk", "Original", "Minimal", "Arcade"] or not os.path.exists(act_snd):
                        act_snd = get_resource_path(os.path.join('presets', act_name if act_name in ["Cyberpunk", "Original", "Minimal", "Arcade"] else "Original", 'action.mp3'))

                    done_bytes = None
                    if done_snd and os.path.exists(done_snd):
                        with open(done_snd, 'rb') as f:
                            done_bytes = adjust_audio_volume(f.read(), done_vol)

                    act_bytes = None
                    if act_snd and os.path.exists(act_snd):
                        with open(act_snd, 'rb') as f:
                            act_bytes = adjust_audio_volume(f.read(), act_vol)

                    patch_language_server_exe(ls_path, done_bytes, act_bytes)
                    print(f"[SoundGravity] Auto-reapplied sounds after Antigravity update on: {ls_path}")
                    if self.callback:
                        self.callback()
            except Exception as e:
                pass
