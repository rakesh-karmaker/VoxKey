import numpy as np


def compute_audio_level(chunk) -> float:
    if chunk is None or len(chunk) == 0:
        return 0.0

    data = np.asarray(chunk, dtype=np.float32)
    rms = float(np.sqrt(np.mean(np.square(data))))
    peak = float(np.max(np.abs(data)))

    level = (rms * 0.65) + (peak * 0.35)
    return max(0.0, min(1.0, level * 32.0))
