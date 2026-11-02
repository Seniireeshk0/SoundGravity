import os
import sys
import struct
import zlib
import shutil
import time
import subprocess

def find_language_server():
    r"""
    Finds the Antigravity language_server.exe on any Windows machine.
    Checks:
    1. Active running processes (language_server.exe or Antigravity.exe)
    2. Standard Local Programs path for current user
    3. Other possible paths in AppData / Local
    4. All other user directories in C:\Users
    5. Program Files (system-wide installation)
    """
    candidates = []

    # 1. Check running processes first (most accurate for any custom install location)
    try:
        # Check language_server.exe
        cmd = 'powershell -NoProfile -Command "(Get-Process -Name language_server -ErrorAction SilentlyContinue | Select-Object -First 1).Path"'
        out = subprocess.check_output(cmd, shell=True, text=True, timeout=3).strip()
        if out and os.path.exists(out):
            return out
    except:
        pass

    try:
        # Check Antigravity.exe / antigravity.exe
        cmd = 'powershell -NoProfile -Command "(Get-Process -Name antigravity -ErrorAction SilentlyContinue | Select-Object -First 1).Path"'
        out = subprocess.check_output(cmd, shell=True, text=True, timeout=3).strip()
        if out and os.path.exists(out):
            derived = os.path.join(os.path.dirname(out), 'resources', 'bin', 'language_server.exe')
            if os.path.exists(derived):
                return derived
    except:
        pass

    # 2. Standard user paths
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    if local_app_data:
        search_dirs = [
            os.path.join(local_app_data, 'Programs', 'antigravity', 'resources', 'bin', 'language_server.exe'),
            os.path.join(local_app_data, 'Programs', 'Antigravity', 'resources', 'bin', 'language_server.exe'),
            os.path.join(local_app_data, 'antigravity', 'resources', 'bin', 'language_server.exe'),
            os.path.join(local_app_data, 'Antigravity', 'resources', 'bin', 'language_server.exe'),
        ]
        for p in search_dirs:
            if os.path.exists(p):
                return p

    # 3. Check other user profiles in C:\Users
    if os.path.exists('C:\\Users'):
        try:
            for user in os.listdir('C:\\Users'):
                p1 = os.path.join('C:\\Users', user, 'AppData', 'Local', 'Programs', 'antigravity', 'resources', 'bin', 'language_server.exe')
                p2 = os.path.join('C:\\Users', user, 'AppData', 'Local', 'Programs', 'Antigravity', 'resources', 'bin', 'language_server.exe')
                for p in [p1, p2]:
                    if os.path.exists(p):
                        return p
        except:
            pass

    # 4. Program Files fallback
    for pf in [os.environ.get('ProgramFiles', ''), os.environ.get('ProgramFiles(x86)', '')]:
        if pf:
            for folder in ['antigravity', 'Antigravity']:
                p = os.path.join(pf, folder, 'resources', 'bin', 'language_server.exe')
                if os.path.exists(p):
                    return p

    return None

def patch_language_server_exe(exe_path, done_mp3_bytes=None, action_mp3_bytes=None):
    """
    Surgical byte-exact patch of language_server.exe:
    1. Parses PE headers & section table dynamically.
    2. Extracts embedded zip entries.
    3. Replaces antigravityCascadeDone.mp3 and/or antigravityActionRequired.mp3.
    4. Updates or appends aligned .snddata section.
    5. Dynamically searches and updates Go embedded slice pointer (ptr, len, cap).
    6. Safely replaces file on disk and ensures active Antigravity instance reloads it.
    """
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Файл не найден: {exe_path}")

    # Backup original before first modification
    bak_path = exe_path + ".soundgravity.bak"
    if not os.path.exists(bak_path):
        try:
            shutil.copy2(exe_path, bak_path)
        except Exception:
            pass

    with open(exe_path, 'rb') as f:
        exe_bytes = bytearray(f.read())

    # Parse PE headers dynamically
    e_lfanew = struct.unpack_from('<I', exe_bytes, 0x3c)[0]
    num_sections = struct.unpack_from('<H', exe_bytes, e_lfanew + 4 + 2)[0]
    opt_hdr_size = struct.unpack_from('<H', exe_bytes, e_lfanew + 4 + 16)[0]
    sec_table_offset = e_lfanew + 4 + 20 + opt_hdr_size
    image_base = struct.unpack_from('<Q', exe_bytes, e_lfanew + 4 + 20 + 24)[0]

    sections = []
    snd_sec_idx = -1
    for s_i in range(num_sections):
        s_hdr = exe_bytes[sec_table_offset + s_i * 40 : sec_table_offset + (s_i + 1) * 40]
        s_name, cur_vsize, cur_vaddr, cur_rsize, cur_roff, _, _, _, _, _ = struct.unpack('<8sIIIIIIHHI', s_hdr)
        name = s_name.rstrip(b'\x00').decode('latin1', errors='ignore')
        sec = {'index': s_i, 'name': name, 'vsize': cur_vsize, 'vaddr': cur_vaddr, 'rsize': cur_rsize, 'roff': cur_roff}
        sections.append(sec)
        if name == '.snddata':
            snd_sec_idx = s_i

    snd_sec = sections[snd_sec_idx] if snd_sec_idx != -1 else None

    # Locate the original embedded zip in standard sections (skip .snddata if present)
    act_name = b'antigravityActionRequired.mp3'
    pos = 0
    zip_start = None
    orig_zip_len = None
    orig_sec = None

    while True:
        idx = exe_bytes.find(act_name, pos)
        if idx == -1:
            break
        # Ignore occurrences that are inside an existing .snddata section
        if snd_sec and snd_sec['roff'] <= idx < snd_sec['roff'] + snd_sec['rsize']:
            pos = idx + len(act_name)
            continue

        z_candidate = idx - 30
        if z_candidate >= 0 and exe_bytes[z_candidate:z_candidate+4] == b'PK\x03\x04':
            eocd = exe_bytes.find(b'PK\x05\x06', z_candidate)
            if eocd != -1:
                _, _, _, _, _, _, _, comment_len = struct.unpack('<4sHHHHIIH', exe_bytes[eocd:eocd+22])
                zip_start = z_candidate
                orig_zip_len = (eocd + 22 + comment_len) - z_candidate
                for s in sections:
                    if s['name'] != '.snddata' and s['roff'] <= z_candidate < s['roff'] + s['rsize']:
                        orig_sec = s
                        break
                break
        pos = idx + len(act_name)

    if zip_start is None or orig_sec is None:
        raise ValueError("Встроенный архив звуков не найден внутри language_server.exe.")

    eocd_pos = exe_bytes.find(b'PK\x05\x06', zip_start)
    _, _, _, _, total_entries, cd_size, cd_offset, comment_len = struct.unpack('<4sHHHHIIH', exe_bytes[eocd_pos:eocd_pos+22])
    zip_end = eocd_pos + 22 + comment_len
    orig_zip = bytes(exe_bytes[zip_start:zip_end])

    # Parse central directory entries from orig_zip
    offset = cd_offset
    entries = []
    while offset < cd_offset + cd_size:
        hdr = orig_zip[offset:offset+46]
        vmade, vneed, flags, method, mtime, mdate, crc, comp_s, uncomp_s, fn_len, ex_len, cm_len, disk, iattr, eattr, rel_off = struct.unpack('<HHHHHHIIIHHHHHII', hdr[4:])
        fn = orig_zip[offset+46:offset+46+fn_len]
        extra = orig_zip[offset+46+fn_len:offset+46+fn_len+ex_len]
        comment = orig_zip[offset+46+fn_len+ex_len:offset+46+fn_len+ex_len+cm_len]

        loc_hdr = orig_zip[rel_off:rel_off+30]
        _, l_vneed, l_flags, l_method, l_mtime, l_mdate, l_crc, l_comp_s, l_uncomp_s, l_fn_len, l_ex_len = struct.unpack('<4sHHHHHIIIHH', loc_hdr)
        l_extra = orig_zip[rel_off+30+l_fn_len:rel_off+30+l_fn_len+l_ex_len]

        entries.append({
            'fn': fn,
            'vmade': vmade, 'vneed': vneed, 'flags': flags, 'method': method,
            'mtime': mtime, 'mdate': mdate, 'crc': crc,
            'comp_s': comp_s, 'uncomp_s': uncomp_s,
            'extra': extra, 'comment': comment,
            'rel_off': rel_off,
            'l_extra': l_extra,
            'l_flags': l_flags,
            'disk': disk, 'iattr': iattr, 'eattr': eattr
        })
        offset += 46 + fn_len + ex_len + cm_len

    # Reconstruct zip with updated sound files
    payload = bytearray()
    cd = bytearray()
    for e in entries:
        rel = len(payload)
        fn_str = e['fn'].decode('latin1', errors='ignore')

        if fn_str == 'antigravityCascadeDone.mp3' and done_mp3_bytes:
            raw_data = done_mp3_bytes
            c = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15)
            comp_data = c.compress(raw_data) + c.flush()
            crc = zlib.crc32(raw_data) & 0xffffffff
            method = 8
            comp_s = len(comp_data)
            uncomp_s = len(raw_data)
        elif fn_str == 'antigravityActionRequired.mp3' and action_mp3_bytes:
            raw_data = action_mp3_bytes
            c = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15)
            comp_data = c.compress(raw_data) + c.flush()
            crc = zlib.crc32(raw_data) & 0xffffffff
            method = 8
            comp_s = len(comp_data)
            uncomp_s = len(raw_data)
        else:
            data_start = e['rel_off'] + 30 + len(e['fn']) + len(e['l_extra'])
            comp_data = orig_zip[data_start:data_start+e['comp_s']]
            crc = e['crc']
            method = e['method']
            comp_s = e['comp_s']
            uncomp_s = e['uncomp_s']

        l_hdr = struct.pack('<4sHHHHHIIIHH', b'PK\x03\x04', e['vneed'], e['l_flags'], method, e['mtime'], e['mdate'], crc, comp_s, uncomp_s, len(e['fn']), len(e['l_extra']))
        payload.extend(l_hdr)
        payload.extend(e['fn'])
        payload.extend(e['l_extra'])
        payload.extend(comp_data)

        cd_entry = struct.pack('<4sHHHHHHIIIHHHHHII', b'PK\x01\x02', e['vmade'], e['vneed'], e['flags'], method, e['mtime'], e['mdate'], crc, comp_s, uncomp_s, len(e['fn']), len(e['extra']), len(e['comment']), e['disk'], e['iattr'], e['eattr'], rel)
        cd.extend(cd_entry)
        cd.extend(e['fn'])
        cd.extend(e['extra'])
        cd.extend(e['comment'])

    eocd = struct.pack('<4sHHHHIIH', b'PK\x05\x06', 0, 0, len(entries), len(entries), len(cd), len(payload), 0)
    new_zip = bytes(payload + cd + eocd)
    new_zip_len = len(new_zip)

    # Calculate orig_zip_va dynamically
    orig_zip_rva = orig_sec['vaddr'] + (zip_start - orig_sec['roff'])
    orig_zip_va = image_base + orig_zip_rva

    # Search candidates to find the Go embedded slice pointer dynamically
    slice_candidates = []
    if snd_sec:
        slice_candidates.append(('snddata', image_base + snd_sec['vaddr'], snd_sec['vsize']))
    slice_candidates.append(('original', orig_zip_va, orig_zip_len))

    slice_offset = -1
    for tag, ptr_val, exp_len in slice_candidates:
        ptr_bytes = struct.pack('<Q', ptr_val)
        p = 0
        while True:
            idx = exe_bytes.find(ptr_bytes, p)
            if idx == -1:
                break
            if idx + 24 <= len(exe_bytes):
                slen, scap = struct.unpack_from('<QQ', exe_bytes, idx + 8)
                if slen == exp_len or slen == scap:
                    slice_offset = idx
                    break
            p = idx + 1
        if slice_offset != -1:
            break

    if slice_offset == -1:
        raise ValueError("Не удалось динамически определить смещение Go slice в language_server.exe.")

    # PE Section manipulation (.snddata)
    if snd_sec_idx != -1:
        # Update existing .snddata section
        s_hdr = exe_bytes[sec_table_offset + snd_sec_idx * 40 : sec_table_offset + (snd_sec_idx + 1) * 40]
        _, cur_vsize, cur_vaddr, cur_rsize, cur_roff, _, _, _, _, _ = struct.unpack('<8sIIIIIIHHI', s_hdr)

        new_sec_vaddr = cur_vaddr
        new_sec_roff = cur_roff
        new_sec_rsize = (new_zip_len + 0x1ff) & ~0x1ff
        new_sec_vsize = new_zip_len

        padded_zip = new_zip + b'\x00' * (new_sec_rsize - new_zip_len)
        exe_bytes = exe_bytes[:new_sec_roff] + padded_zip

        # Update section header
        new_sec_hdr = struct.pack('<8sIIIIIIHHI', b'.snddata', new_sec_vsize, new_sec_vaddr, new_sec_rsize, new_sec_roff, 0, 0, 0, 0, 0x40000040)
        exe_bytes[sec_table_offset + snd_sec_idx * 40 : sec_table_offset + (snd_sec_idx + 1) * 40] = new_sec_hdr

        new_size_of_image = (new_sec_vaddr + new_sec_vsize + 0xfff) & ~0xfff
        struct.pack_into('<I', exe_bytes, e_lfanew + 4 + 20 + 56, new_size_of_image)
    else:
        # Append new .snddata section after last section
        last_sec_hdr = exe_bytes[sec_table_offset + (num_sections - 1) * 40 : sec_table_offset + num_sections * 40]
        _, r_vsize, r_vaddr, r_rsize, r_roff, _, _, _, _, _ = struct.unpack('<8sIIIIIIHHI', last_sec_hdr)

        new_sec_vaddr = (r_vaddr + r_vsize + 0xfff) & ~0xfff
        new_sec_roff = (r_roff + r_rsize + 0x1ff) & ~0x1ff
        new_sec_rsize = (new_zip_len + 0x1ff) & ~0x1ff
        new_sec_vsize = new_zip_len

        padded_zip = new_zip + b'\x00' * (new_sec_rsize - new_zip_len)
        exe_bytes = exe_bytes[:new_sec_roff] + padded_zip

        # Write new section header
        new_sec_hdr = struct.pack('<8sIIIIIIHHI', b'.snddata', new_sec_vsize, new_sec_vaddr, new_sec_rsize, new_sec_roff, 0, 0, 0, 0, 0x40000040)
        exe_bytes[sec_table_offset + num_sections * 40 : sec_table_offset + (num_sections + 1) * 40] = new_sec_hdr

        # Update number of sections
        struct.pack_into('<H', exe_bytes, e_lfanew + 4 + 2, num_sections + 1)

        # Update SizeOfImage
        new_size_of_image = (new_sec_vaddr + new_sec_vsize + 0xfff) & ~0xfff
        struct.pack_into('<I', exe_bytes, e_lfanew + 4 + 20 + 56, new_size_of_image)

    # Update the Go slice struct: (ptr, len, cap)
    new_zip_va = image_base + new_sec_vaddr
    struct.pack_into('<QQQ', exe_bytes, slice_offset, new_zip_va, new_zip_len, new_zip_len)

    # Write modified executable safely to a temporary file
    temp_target = exe_path + ".soundgravity.tmp"
    with open(temp_target, 'wb') as f:
        f.write(exe_bytes)

    # Safely replace on disk
    replaced = False
    try:
        os.replace(temp_target, exe_path)
        replaced = True
    except PermissionError:
        pass

    if not replaced:
        try:
            old_path = exe_path + f".old_{int(time.time())}"
            os.rename(exe_path, old_path)
            os.rename(temp_target, exe_path)
            replaced = True
        except Exception:
            pass

    # Determine if we are in the active development session (never kill language_server on dev machine!)
    is_dev_machine = (
        os.environ.get('USERNAME', '').lower() == 'arsen' and
        '2b805910-c951-4a8a-91fb-ee4726c81fb1' in os.path.abspath(__file__)
    )

    if not replaced:
        if not is_dev_machine:
            # On user / other PCs, terminate running language_server.exe so file unlocks
            try:
                subprocess.run("taskkill /F /IM language_server.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.3)
                os.replace(temp_target, exe_path)
                replaced = True
            except Exception as e:
                raise PermissionError(f"Не удалось обновить language_server.exe. Закройте Antigravity и повторите попытку: {e}")
        else:
            raise PermissionError("language_server.exe заблокирован процессом Windows.")

    # On remote / other PCs, restart language_server so Antigravity instantly plays the new sounds!
    if not is_dev_machine:
        try:
            subprocess.run("taskkill /F /IM language_server.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # Clean up stale temp files
    try:
        bin_dir = os.path.dirname(exe_path)
        for fn in os.listdir(bin_dir):
            if fn.startswith("language_server.exe.old_") or fn.endswith(".soundgravity.tmp"):
                try:
                    os.remove(os.path.join(bin_dir, fn))
                except:
                    pass
    except Exception:
        pass

    return True

def adjust_wav_volume(wav_bytes, volume_percent):
    import io, wave, struct
    ratio = max(0.0, volume_percent / 100.0)
    with wave.open(io.BytesIO(wav_bytes), "rb") as w:
        params = w.getparams()
        frames = w.readframes(params.nframes)

    if params.sampwidth == 2:
        count = len(frames) // 2
        fmt = f"<{count}h"
        samples = struct.unpack(fmt, frames)
        scaled = [max(-32768, min(32767, int(s * ratio))) for s in samples]
        out_frames = struct.pack(fmt, *scaled)
    else:
        out_frames = frames

    out_io = io.BytesIO()
    with wave.open(out_io, "wb") as w_out:
        w_out.setparams(params)
        w_out.writeframes(out_frames)
    return out_io.getvalue()

def adjust_mp3_volume(mp3_bytes, volume_percent):
    import math
    if volume_percent >= 100:
        return mp3_bytes
    if volume_percent <= 0:
        delta_gain = -255
    else:
        delta_gain = round(13.333 * math.log10(volume_percent / 100.0))

    data = bytearray(mp3_bytes)

    def get_bit(offset):
        return (data[offset // 8] >> (7 - (offset % 8))) & 1

    def read_bits(offset, n):
        v = 0
        for i in range(n):
            v = (v << 1) | get_bit(offset + i)
        return v

    def write_bits(offset, n, val):
        for i in range(n):
            bit = (val >> (n - 1 - i)) & 1
            pos = (offset + i) // 8
            shift = 7 - ((offset + i) % 8)
            mask = ~(1 << shift) & 0xFF
            data[pos] = (data[pos] & mask) | (bit << shift)

    bitrates = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
    samplerates = [44100, 48000, 32000, 0]

    pos = 0
    while pos < len(data) - 4:
        if data[pos] == 0xFF and (data[pos+1] & 0xFE) == 0xFA: # MPEG-1 Layer 3
            protection = data[pos+1] & 1
            br_idx = (data[pos+2] >> 4) & 0xF
            sr_idx = (data[pos+2] >> 2) & 3
            pad = (data[pos+2] >> 1) & 1
            channels = (data[pos+3] >> 6) & 3

            if br_idx in (0, 15) or sr_idx == 3:
                pos += 1
                continue

            br = bitrates[br_idx] * 1000
            sr = samplerates[sr_idx]
            frame_len = (144 * br) // sr + pad
            if frame_len <= 0 or pos + frame_len > len(data):
                pos += 1
                continue

            hdr_len = 4 if protection else 6
            side = (pos + hdr_len) * 8

            if channels == 3: # Mono
                gain_offsets = [side + 14 + 21, side + 14 + 59 + 21]
            else: # Stereo
                gain_offsets = [
                    side + 20 + 21,
                    side + 20 + 59 + 21,
                    side + 20 + 118 + 21,
                    side + 20 + 177 + 21
                ]

            for goff in gain_offsets:
                curr_gg = read_bits(goff, 8)
                if curr_gg > 0:
                    new_gg = max(0, min(255, curr_gg + delta_gain))
                    write_bits(goff, 8, new_gg)

            pos += frame_len
        else:
            pos += 1

    return bytes(data)

def adjust_audio_volume(audio_bytes, volume_percent):
    if volume_percent == 100:
        return audio_bytes
    if audio_bytes.startswith(b"RIFF"):
        return adjust_wav_volume(audio_bytes, volume_percent)
    else:
        return adjust_mp3_volume(audio_bytes, volume_percent)
