"""Speak the scripts in Sai's own voice with AI4Bharat IndicF5 (MIT license).

IndicF5 is a Telugu-capable voice-cloning text-to-speech model. It needs:
  * a short reference clip of the voice + the exact words spoken in it
      content/voice/reference.wav.gpg  (encrypted, unlocked with the VOICE_KEY secret)
      content/voice/reference.txt
  * a Hugging Face token (HF_TOKEN secret) from an account that accepted the
    model's terms at https://huggingface.co/ai4bharat/IndicF5

The reference stays encrypted in the repo so nobody can copy the voice from GitHub.
"""
import os
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
_MODEL = None


def available():
    ref = os.environ.get("SIPP_VOICE_REF")
    return bool(ref and Path(ref).exists() and os.environ.get("HF_TOKEN"))


def _model():
    global _MODEL
    if _MODEL is None:
        from transformers import AutoModel
        print("  loading IndicF5 (first run downloads ~1.4 GB, then it's cached)…")
        _MODEL = AutoModel.from_pretrained("ai4bharat/IndicF5", trust_remote_code=True,
                                           token=os.environ.get("HF_TOKEN"),
                                           low_cpu_mem_usage=False)  # load real weights, not empty "meta" ones
    return _MODEL


def synth_all(texts, folder):
    """Returns one .wav per text, spoken in the cloned voice."""
    import soundfile as sf

    ref_audio = os.environ["SIPP_VOICE_REF"]
    ref_text = (REPO / "content" / "voice" / "reference.txt").read_text(encoding="utf-8").strip()
    model = _model()
    paths = []
    for i, text in enumerate(texts):
        audio = model(text, ref_audio_path=ref_audio, ref_text=ref_text)
        audio = np.asarray(audio)
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        p = Path(folder) / f"voice_{i}.wav"
        sf.write(str(p), audio.astype(np.float32), samplerate=24000)
        print(f"  cloned voice {i + 1}/{len(texts)}: {len(audio) / 24000:.1f}s")
        paths.append(p)
    return paths
