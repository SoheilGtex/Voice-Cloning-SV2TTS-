import numpy as np
from voice_cloner.watermark import embed_watermark, detect_watermark

def test_watermark_signal():
    x = np.random.randn(16000).astype("float32") * 0.05
    y = embed_watermark(x, key="k123", tag="t")
    s = detect_watermark(y, key="k123", tag="t")
    assert s > 0.01  # weak but positive correlation
