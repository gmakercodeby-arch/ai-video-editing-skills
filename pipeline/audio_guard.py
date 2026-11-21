# -*- coding: utf-8 -*-
"""
audio_guard.py - MANDATORY zero-bypass Hindi TTS guard.  Every script that makes a Short MUST
synthesise narration through GuardedTTS (never call model.generate() directly).

Guarantees per beat (OmniVoice or any TTS passed in as `generate_fn`):
  1. Pre-TTS normalisation (digits / years / acronyms -> Hindi words)  [hindi_normalizer]
  2. Beat length <= 15 words (hard error otherwise - split the sentence)
  3. Whisper `small` (CPU, int8) transcription of the SHIPPED audio, SequenceMatcher
     similarity >= 0.72 AND last word intact AND no abrupt end
  4. On failure: new seed, max 3 retries; best attempt kept; if still < 0.72 -> clean fallback
     (edge-tts hi-IN-MadhurNeural), clearly flagged in audio_report.json.  A gibberish beat is
     NEVER silently mixed.
  5. Mid-word-cut protection: trim threshold -52 dB with 65 ms safety padding at both ends.
  6. Word timestamps -> exact per-word times for caption + clip-cue sync.
"""
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hindi_normalizer import normalize_hindi, word_count, leftover_latin  # noqa: E402

PY = os.environ.get("SHORTS_PY", r"f:\ai video edit\.venv\Scripts\python.exe")
WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whisper_worker.py")

SIM_THRESHOLD = 0.72      # SequenceMatcher ratio, script vs Whisper transcript (phonetic-normalised)
# Calibrated on real data (old Meridian OmniVoice beats vs Tears edge-tts beats): good audio has
# max_gap <= 5 and suffix <= 2; the beats the user flagged as gibberish/cut have max_gap 11-28.
GAP_MAX = 8               # longest run of script characters that Whisper did NOT hear (~2 words)
SUFFIX_MAX = 4            # script characters missing at the very END (cut last word)
MAX_WORDS = 15
MAX_RETRIES = 3           # retries AFTER the first attempt
TRIM_DB = -52.0
PAD_S = 0.065             # 65 ms safety padding at start + end
ABRUPT_END_DB = -40.0     # raw TTS end RMS above this => abrupt cut
OUT_SR = 48000

_DROP = {0x093C, 0x200C, 0x200D, 0x0964, 0x0965}
_MAP = {"ँ": "ं", "ी": "ि", "ू": "ु", "ॉ": "ो", "ऑ": "ओ", "ॅ": "े", "ई": "इ", "ऊ": "उ", "ृ": "ि", "ऱ": "र", "ळ": "ल"}


def phon(s: str) -> str:
    """Phonetic-ish skeleton: digits->words, NFC, nukta/danda/ZWJ dropped, long->short vowels,
    chandrabindu->anusvara, spaces/punctuation removed.  Makes Whisper spelling variance harmless
    while a hallucinated / cut word still scores low."""
    s = unicodedata.normalize("NFC", normalize_hindi(s))
    out = []
    for ch in s:
        if ord(ch) in _DROP:
            continue
        ch = _MAP.get(ch, ch)
        if "\u0900" <= ch <= "\u097F" or ch.isalpha():
            out.append(ch.lower())
    # collapse Whisper repetition-loop hallucinations ("ँँँँँँ...") so they cannot wreck the score
    return re.sub(r"(.)\1{2,}", r"\1", "".join(out))


def similarity(script: str, transcript: str) -> float:
    return difflib.SequenceMatcher(None, phon(script), phon(transcript), autojunk=False).ratio()


def gap_stats(script: str, transcript: str, min_block: int = 3):
    """(max_gap, suffix_unmatched): longest run of script chars Whisper did not hear, and how many
    script chars are missing at the very end (a cut / swallowed last word).  Matching blocks < 3 chars
    are treated as coincidence.  Spelling variance gives tiny gaps; garbled / dropped words give big ones."""
    a, b = phon(script), phon(transcript)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    blocks = [m for m in sm.get_matching_blocks() if m.size >= min_block]
    runs, pos = [], 0
    for m in blocks:
        if m.a > pos:
            runs.append(m.a - pos)
        pos = m.a + m.size
    if pos < len(a):
        runs.append(len(a) - pos)
    return max(runs, default=0), len(a) - pos


class WhisperClient:
    def __init__(self, log_path=None):
        env = os.environ.copy()
        for k in ("HF_HOME", "HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE"):
            env.pop(k, None)
        env["PYTHONIOENCODING"] = "utf-8"
        self._log = open(log_path or os.devnull, "wb")
        self.p = subprocess.Popen([PY, WORKER], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=self._log, env=env, text=True, encoding="utf-8", bufsize=1)
        if self._read() != "READY":
            raise RuntimeError("Whisper worker failed to start")

    def _read(self):
        while True:
            line = self.p.stdout.readline()
            if line == "":
                raise RuntimeError("Whisper worker died")
            if line.startswith("@@"):
                return line[2:].strip()

    def transcribe(self, wav_path):
        self.p.stdin.write(json.dumps({"wav": wav_path}) + "\n")
        self.p.stdin.flush()
        out = json.loads(self._read())
        if not out.get("ok"):
            raise RuntimeError(out.get("err"))
        return out

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=10)
        except Exception:  # noqa: BLE001
            self.p.kill()


def check_wav(client: WhisperClient, wav_path: str, script_text: str):
    """Standalone mandatory check usable by ANY script: returns the full QA record."""
    text = normalize_hindi(script_text)
    r = client.transcribe(wav_path)
    sim = similarity(text, r["text"])
    mg, suf = gap_stats(text, r["text"])
    return {"similarity": round(sim, 4), "max_gap": mg, "suffix_unmatched": suf,
            "gap_ok": mg <= GAP_MAX, "tail_ok": suf <= SUFFIX_MAX,
            "transcript": r["text"], "words": r["words"]}


def end_rms_db(arr, sr, ms=25):
    n = max(1, int(sr * ms / 1000))
    seg = np.asarray(arr[-n:], dtype=np.float64)
    return float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9))


def prepare_audio(arr, sr_in):
    """Peak-normalise, trim at -52 dB with 65 ms real/zero padding, 4 ms edge fades, resample to 48 kHz."""
    arr = np.asarray(arr, dtype=np.float32).squeeze()
    arr = arr / (np.max(np.abs(arr)) + 1e-8) * 0.85
    end_db = end_rms_db(arr, sr_in)
    frame = max(1, int(0.010 * sr_in))
    n = len(arr) // frame
    rms = np.sqrt(np.mean(arr[: n * frame].reshape(n, frame) ** 2, axis=1))
    voiced = np.where(20 * np.log10(rms + 1e-9) > TRIM_DB)[0]
    if len(voiced) == 0:
        raise RuntimeError("TTS returned silence")
    first, last = voiced[0] * frame, (voiced[-1] + 1) * frame
    pad = int(PAD_S * sr_in)
    s, e = max(0, first - pad), min(len(arr), last + pad)
    seg = arr[s:e].copy()
    if first - s < pad:
        seg = np.concatenate([np.zeros(pad - (first - s), dtype=np.float32), seg])
    if e - last < pad:
        seg = np.concatenate([seg, np.zeros(pad - (e - last), dtype=np.float32)])
    f = int(0.004 * sr_in)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-f:] *= np.linspace(1, 0, f)
    from math import gcd
    g = gcd(OUT_SR, sr_in)
    seg48 = resample_poly(seg, OUT_SR // g, sr_in // g)
    return (np.clip(seg48, -1, 1) * 32767).astype(np.int16), end_db


def script_word_times(text, whisper_words, dur):
    """Start time (s, relative to beat wav) of every script word via monotonic fuzzy alignment with
    Whisper word timestamps; unmatched words are interpolated; falls back to char-proportional."""
    sw = text.split()
    n = len(sw)
    prop = []
    total = sum(len(phon(w)) or 1 for w in sw)
    acc = 0
    for w in sw:
        prop.append(dur * acc / total)
        acc += len(phon(w)) or 1
    ww = [(phon(w["w"]), w["s"]) for w in whisper_words if phon(w["w"])]
    m = len(ww)
    if m == 0:
        return prop
    GAP = 0.55
    INF = 1e9
    D = [[INF] * (m + 1) for _ in range(n + 1)]
    B = [[None] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            best, bk = INF, None
            if i > 0 and j > 0:
                c = 1 - difflib.SequenceMatcher(None, phon(sw[i - 1]), ww[j - 1][0]).ratio()
                if D[i - 1][j - 1] + c < best:
                    best, bk = D[i - 1][j - 1] + c, "d"
            if i > 0 and D[i - 1][j] + GAP < best:
                best, bk = D[i - 1][j] + GAP, "u"
            if j > 0 and D[i][j - 1] + GAP < best:
                best, bk = D[i][j - 1] + GAP, "l"
            D[i][j], B[i][j] = best, bk
    times = [None] * n
    i, j = n, m
    while i > 0 or j > 0:
        bk = B[i][j]
        if bk == "d":
            c = 1 - difflib.SequenceMatcher(None, phon(sw[i - 1]), ww[j - 1][0]).ratio()
            if c < 0.55:
                times[i - 1] = ww[j - 1][1]
            i, j = i - 1, j - 1
        elif bk == "u":
            i -= 1
        else:
            j -= 1
    known = [(k, t) for k, t in enumerate(times) if t is not None]
    if len(known) < max(2, n // 3):
        return prop
    out = []
    for k in range(n):
        if times[k] is not None:
            out.append(times[k])
            continue
        lo = max([(a, t) for a, t in known if a < k], default=None, key=lambda x: x[0])
        hi = min([(a, t) for a, t in known if a > k], default=None, key=lambda x: x[0])
        if lo and hi:
            out.append(lo[1] + (hi[1] - lo[1]) * (k - lo[0]) / (hi[0] - lo[0]))
        elif lo:
            out.append(min(dur, lo[1] + (dur - lo[1]) * (k - lo[0]) / max(1, n - lo[0])))
        else:
            out.append(hi[1] * k / hi[0])
    for k in range(1, n):
        out[k] = max(out[k], out[k - 1] + 0.02)
    return out


def edge_tts_fallback(text, work_dir, tag):
    """Clean fallback voice (flagged in report). Returns (float32 array, 24000)."""
    mp3 = os.path.join(work_dir, f"fallback_{tag}.mp3")
    wav = os.path.join(work_dir, f"fallback_{tag}.wav")
    subprocess.run([PY, "-m", "edge_tts", "--voice", "hi-IN-MadhurNeural", "--rate", "+10%",
                    "--text", text, "--write-media", mp3], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-i", mp3, "-ac", "1", "-ar", "24000", wav], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sr, d = wavfile.read(wav)
    return d.astype(np.float32) / 32768.0, sr


class GuardedTTS:
    def __init__(self, generate_fn, work_dir, sr_in=24000, tag="omnivoice", base_seed=100,
                 threshold=SIM_THRESHOLD, max_retries=MAX_RETRIES, use_fallback=True):
        """generate_fn(text:str, seed:int) -> mono float array at sr_in."""
        self.gen, self.dir, self.sr_in, self.tag = generate_fn, work_dir, sr_in, tag
        self.base_seed, self.thr, self.max_retries, self.use_fallback = base_seed, threshold, max_retries, use_fallback
        os.makedirs(work_dir, exist_ok=True)
        self.client = WhisperClient(os.path.join(work_dir, "whisper_worker.log"))
        self.results = []

    def close(self):
        self.client.close()

    @staticmethod
    def _score(rec):
        return rec["similarity"] + (0.1 if rec["tail_ok"] else 0) + (0.1 if rec["gap_ok"] else 0) - (0.1 if rec["abrupt_end"] else 0)

    def _attempt(self, beat_id, text, seed, attempt, key, arr_sr=None):
        arr, sr_in = arr_sr if arr_sr else (self.gen(text, seed), self.sr_in)
        pcm, end_db = prepare_audio(arr, sr_in)
        path = os.path.join(self.dir, f"beat_{beat_id:02d}_{key}_a{attempt}.wav")
        wavfile.write(path, OUT_SR, pcm)
        chk = check_wav(self.client, path, text)
        rec = {"attempt": attempt, "seed": seed, "wav": path, "dur": round(len(pcm) / OUT_SR, 3),
               "end_rms_db": round(end_db, 1), "abrupt_end": end_db > ABRUPT_END_DB, **chk}
        rec["ok"] = rec["similarity"] >= self.thr and rec["tail_ok"] and rec["gap_ok"] and not rec["abrupt_end"]
        return rec

    def synth_beat(self, beat_id, script_text):
        text = normalize_hindi(script_text)
        n = word_count(text)
        if n > MAX_WORDS:
            raise ValueError(f"Beat {beat_id} has {n} words (> {MAX_WORDS}). Split the sentence - long beats make OmniVoice hallucinate.")
        lat = leftover_latin(text)
        if lat:
            print(f"   [warn] beat {beat_id}: Latin words left for TTS: {lat}", flush=True)
        key = hashlib.md5(f"{text}|{self.tag}".encode("utf-8")).hexdigest()[:8]
        final = os.path.join(self.dir, f"beat_{beat_id:02d}_{key}.wav")
        meta = final[:-4] + ".json"
        if os.path.exists(final) and os.path.exists(meta):
            res = json.load(open(meta, encoding="utf-8"))
            if res["status"] in ("PASS", "FALLBACK_PASS"):
                self.results.append(res)
                print(f"   Beat {beat_id:02d}: cached {res['status']} sim={res['similarity']}", flush=True)
                return res
        attempts, best = [], None
        for a in range(self.max_retries + 1):
            rec = self._attempt(beat_id, text, self.base_seed + beat_id * 17 + a * 101, a, key)
            attempts.append(rec)
            print(f"   Beat {beat_id:02d} attempt {a}: sim={rec['similarity']:.3f} gap={rec['max_gap']} suffix={rec['suffix_unmatched']} abrupt={rec['abrupt_end']} -> {'OK' if rec['ok'] else 'RETRY'}", flush=True)
            if best is None or self._score(rec) > self._score(best):
                best = rec
            if rec["ok"]:
                break
        engine, status = self.tag, "PASS" if best["ok"] else "FAILED_QA"
        if not best["ok"] and self.use_fallback:
            arr, sr = edge_tts_fallback(text, self.dir, f"{beat_id:02d}_{key}")
            fb = self._attempt(beat_id, text, -1, 99, key, (arr, sr))
            attempts.append(fb)
            print(f"   Beat {beat_id:02d} FALLBACK edge-tts: sim={fb['similarity']:.3f} gap={fb['max_gap']} suffix={fb['suffix_unmatched']}", flush=True)
            if fb["ok"] or self._score(fb) > self._score(best):
                best, engine = fb, "edge-tts-fallback"
                status = "FALLBACK_PASS" if fb["ok"] else "FAILED_QA"
        wt = script_word_times(text, best["words"], best["dur"])
        import shutil
        shutil.copyfile(best["wav"], final)
        res = {"id": beat_id, "text": text, "status": status, "engine": engine, "wav": final,
               "dur": best["dur"], "similarity": best["similarity"], "tail_ok": best["tail_ok"],
               "gap_ok": best["gap_ok"], "max_gap": best["max_gap"], "suffix_unmatched": best["suffix_unmatched"],
               "abrupt_end": best["abrupt_end"], "transcript": best["transcript"],
               "words": best["words"], "word_times": [round(x, 3) for x in wt], "script_words": text.split(),
               "attempts": [{k: a[k] for k in ("attempt", "seed", "similarity", "max_gap", "suffix_unmatched", "tail_ok", "gap_ok", "abrupt_end", "ok")} for a in attempts]}
        json.dump(res, open(meta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        self.results.append(res)
        return res

    def write_report(self, path):
        sims = [r["similarity"] for r in self.results]
        rep = {"threshold": self.thr, "min_similarity": min(sims) if sims else None,
               "n_beats": len(self.results),
               "n_failed": sum(r["status"] == "FAILED_QA" for r in self.results),
               "n_fallback": sum(r["engine"] == "edge-tts-fallback" for r in self.results),
               "beats": [{k: r[k] for k in ("id", "text", "status", "engine", "similarity", "max_gap", "suffix_unmatched", "gap_ok", "tail_ok", "abrupt_end", "transcript", "attempts")} for r in self.results]}
        json.dump(rep, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return rep


if __name__ == "__main__":
    # python audio_guard.py "<wav>" "<script text>"   -> mandatory standalone check
    c = WhisperClient()
    r = check_wav(c, sys.argv[1], sys.argv[2])
    r.pop("words")
    print(json.dumps(r, ensure_ascii=False, indent=1))
    c.close()
