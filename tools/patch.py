# -*- coding: utf-8 -*-
"""修复封装版生日页的死链：字体 CDN + 内置音乐 + 手势模型。
原始文件不动，输出到 index.html。"""
import base64
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "生日页面-封装版.html"
OUT = REPO / "index.html"

html = SRC.read_text(encoding="utf-8")
orig_len = len(html)

# ---------- 1. 字体：netlify 死链 -> fontsource on jsDelivr ----------
FONT_MAP = {
    "https://dazzling-dodol-e84320.netlify.app/fonts/cormorant-500.woff2":
        "https://cdn.jsdelivr.net/npm/@fontsource/cormorant-garamond@5.0.13/files/cormorant-garamond-latin-500-normal.woff2",
    "https://dazzling-dodol-e84320.netlify.app/fonts/cormorant-600.woff2":
        "https://cdn.jsdelivr.net/npm/@fontsource/cormorant-garamond@5.0.13/files/cormorant-garamond-latin-600-normal.woff2",
    "https://dazzling-dodol-e84320.netlify.app/fonts/cormorant-600-italic.woff2":
        "https://cdn.jsdelivr.net/npm/@fontsource/cormorant-garamond@5.0.13/files/cormorant-garamond-latin-600-italic.woff2",
    "https://dazzling-dodol-e84320.netlify.app/fonts/manrope-400.woff2":
        "https://cdn.jsdelivr.net/npm/@fontsource/manrope@5.0.19/files/manrope-latin-400-normal.woff2",
    "https://dazzling-dodol-e84320.netlify.app/fonts/manrope-500.woff2":
        "https://cdn.jsdelivr.net/npm/@fontsource/manrope@5.0.19/files/manrope-latin-500-normal.woff2",
    "https://dazzling-dodol-e84320.netlify.app/fonts/manrope-600.woff2":
        "https://cdn.jsdelivr.net/npm/@fontsource/manrope@5.0.19/files/manrope-latin-600-normal.woff2",
    "https://dazzling-dodol-e84320.netlify.app/fonts/manrope-700.woff2":
        "https://cdn.jsdelivr.net/npm/@fontsource/manrope@5.0.19/files/manrope-latin-700-normal.woff2",
}
font_hits = 0
for old, new in FONT_MAP.items():
    if old not in html:
        print(f"[WARN] font url not found: {old}")
        continue
    font_hits += html.count(old)
    html = html.replace(old, new)

# three.js 增加 unpkg 兜底
OLD_AUDIO = ' src="https://dazzling-dodol-e84320.netlify.app/audio/happy-birthday.mp3"'
if OLD_AUDIO in html:
    html = html.replace(OLD_AUDIO, "", 1)
    print("[OK] bgm <audio>: dropped dead preload src")
else:
    print("[WARN] bgm audio tag src not found")

TEXT_MAP = {
    '<small id="musicStatus">Happy Birthday to You</small>':
        '<small id="musicStatus">生日快乐 · 内置旋律</small>',
    '默认是第一首 Happy Birthday to You；第一次握拳时响起。':
        '默认播放内置合成的《生日快乐》旋律（离线生成，不依赖任何音频文件）；第一次握拳时响起。',
}
for old, new in TEXT_MAP.items():
    if old in html:
        html = html.replace(old, new, 1)
        print(f"[OK] hint text updated: {old[:28]}...")
    else:
        print(f"[WARN] hint text not found: {old[:28]}...")

# 曲目下拉的静态选项同步成内置单曲（运行时本来也会重建）
html, n = re.subn(
    r'<select id="musicTrackSelect">.*?</select>',
    '<select id="musicTrackSelect"><option value="happy-birthday">生日快乐 · 内置旋律（离线可用）</option></select>',
    html,
    count=1,
    flags=re.S,
)
print(f"[OK] music select options reset ({n})")

OLD_THREE = "const three='https://cdn.jsdelivr.net/npm/three@0.187.0/build/three.module.js';"
NEW_THREE = """const threeCandidates=[
 'https://cdn.jsdelivr.net/npm/three@0.187.0/build/three.module.js',
 'https://unpkg.com/three@0.187.0/build/three.module.js',
 'https://esm.sh/three@0.187.0'
];
let three=threeCandidates[0];
for(const candidate of threeCandidates){
 try{ await import(candidate); three=candidate; break; }catch{ /* try next mirror */ }
}"""
if OLD_THREE not in html:
    print("[WARN] three.js loader line not found, skipped mirror fallback")
else:
    html = html.replace(OLD_THREE, NEW_THREE, 1)

# ---------- 2. 解包 q7 ----------
m = re.search(r'(<script id="q7" type="application/octet-stream">)([\s\S]*?)(</script>)', html)
if not m:
    sys.exit("q7 script block not found")
q7_b64 = m.group(2).strip()
modules = json.loads(base64.b64decode(q7_b64).decode("utf-8"))
print(f"[OK] unpacked {len(modules)} modules")

# ---------- 3. 内置音乐：8 首 CDN mp3 -> 离线合成生日快乐旋律 ----------
music = modules["music.js"]
GEN = r"""const MUSIC_BOX_RATE = 22050;
const MUSIC_BOX_BEAT = 0.46;
const MUSIC_BOX_PITCH = {
  G4: 392.0, A4: 440.0, B4: 493.88, C5: 523.25,
  D5: 587.33, E5: 659.25, F5: 698.46, G5: 783.99
};
const MUSIC_BOX_SCORE = [
  ['G4', 0.5], ['G4', 0.5], ['A4', 1], ['G4', 1], ['C5', 1], ['B4', 2],
  ['G4', 0.5], ['G4', 0.5], ['A4', 1], ['G4', 1], ['D5', 1], ['C5', 2],
  ['G4', 0.5], ['G4', 0.5], ['G5', 1], ['E5', 1], ['C5', 1], ['B4', 1], ['A4', 2],
  ['F5', 0.5], ['F5', 0.5], ['E5', 1], ['C5', 1], ['D5', 1], ['C5', 2]
];

/**
 * Renders the birthday melody into a mono 16-bit WAV in memory, so the page
 * keeps its soundtrack with no network at all and no third-party audio files.
 */
function createBuiltinMusicUrl() {
  try {
    const rate = MUSIC_BOX_RATE;
    const beat = MUSIC_BOX_BEAT;
    const totalBeats = MUSIC_BOX_SCORE.reduce((sum, note) => sum + note[1], 0);
    const length = Math.ceil((totalBeats * beat + 1.6) * rate);
    const samples = new Float32Array(length);
    let cursor = 0.12;
    for (const [name, beats] of MUSIC_BOX_SCORE) {
      const frequency = MUSIC_BOX_PITCH[name];
      if (!frequency) continue;
      const duration = beats * beat;
      const start = Math.floor(cursor * rate);
      const count = Math.floor(duration * rate * 1.7);
      for (let i = 0; i < count; i += 1) {
        const index = start + i;
        if (index >= length) break;
        const time = i / rate;
        const attack = 1 - Math.exp(-time * 260);
        const decay = Math.exp(-time * 3.1);
        const wave =
          Math.sin(2 * Math.PI * frequency * time) * 0.62 +
          Math.sin(2 * Math.PI * frequency * 2 * time) * 0.20 +
          Math.sin(2 * Math.PI * frequency * 3 * time) * 0.09 +
          Math.sin(2 * Math.PI * frequency * 4.02 * time) * 0.04;
        samples[index] += wave * attack * decay * 0.46;
      }
      cursor += duration;
    }
    const tail = Math.floor(0.4 * rate);
    for (let i = 0; i < tail && i < length; i += 1) {
      samples[length - 1 - i] *= i / tail;
    }
    const buffer = new ArrayBuffer(44 + length * 2);
    const view = new DataView(buffer);
    const writeAscii = (offset, text) => {
      for (let i = 0; i < text.length; i += 1) view.setUint8(offset + i, text.charCodeAt(i));
    };
    writeAscii(0, 'RIFF');
    view.setUint32(4, 36 + length * 2, true);
    writeAscii(8, 'WAVE');
    writeAscii(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, rate, true);
    view.setUint32(28, rate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeAscii(36, 'data');
    view.setUint32(40, length * 2, true);
    let offset = 44;
    for (let i = 0; i < length; i += 1) {
      const value = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, value < 0 ? value * 0x8000 : value * 0x7fff, true);
      offset += 2;
    }
    return URL.createObjectURL(new Blob([buffer], { type: 'audio/wav' }));
  } catch {
    return '';
  }
}

export const BUILT_IN_TRACKS = [
  { id: 'happy-birthday', name: '生日快乐 · 内置旋律（离线可用）', src: '' }
];"""

new_music, n = re.subn(
    r"export const BUILT_IN_TRACKS = \[[\s\S]*?\];", GEN, music, count=1)
if n != 1:
    sys.exit("BUILT_IN_TRACKS block not found in music.js")
print(f"[OK] music.js: replaced {music.count('.mp3')} remote tracks")

OLD_SOURCE_FOR = """  _sourceFor(track) {
    if (!track) return '';
    return track.kind === 'custom' ? this.customUrl : track.src;
  }"""
NEW_SOURCE_FOR = """  _sourceFor(track) {
    if (!track) return '';
    if (track.kind === 'custom') return this.customUrl;
    if (!this.builtinUrl) this.builtinUrl = createBuiltinMusicUrl();
    return this.builtinUrl;
  }"""
if OLD_SOURCE_FOR not in new_music:
    sys.exit("_sourceFor not found in music.js")
new_music = new_music.replace(OLD_SOURCE_FOR, NEW_SOURCE_FOR, 1)
modules["music.js"] = new_music

# ---------- 4. 手势模型：去掉死链，保留 Google 官方地址 ----------
hands = modules["hands.js"]
dead = re.compile(r"[ \t]*'https://dazzling-dodol-e84320\.netlify\.app/vendor/models/hand_landmarker\.task',[ \t]*\r?\n")
hands, n = dead.subn("", hands)
print(f"[OK] hands.js: dropped {n} dead model mirror(s)")
modules["hands.js"] = hands

# ---------- 5. 重新打包 ----------
payload = json.dumps(modules, ensure_ascii=True, separators=(",", ":"))
new_b64 = base64.b64encode(payload.encode("utf-8")).decode("ascii")
html = html[:m.start(2)] + new_b64 + html[m.end(2):]

OUT.write_text(html, encoding="utf-8", newline="\n")
print(f"[DONE] {OUT.name}: {orig_len} -> {len(html)} chars")
print(f"       残留 netlify 引用: {html.count('dazzling-dodol-e84320')}")
