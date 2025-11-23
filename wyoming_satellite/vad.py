"""Voice activity detection with Silero VAD and internal buffering."""
from typing import Optional
import numpy as np


class SileroVad:
    """Voice activity detection with Silero VAD."""

    def __init__(self, threshold: float, trigger_level: int) -> None:
        from pysilero_vad import SileroVoiceActivityDetector

        self.detector = SileroVoiceActivityDetector()
        self.threshold = threshold
        self.trigger_level = trigger_level
        self._activation = 0

        # Internal buffer to accumulate audio until we have a full chunk
        self._buffer = np.zeros(0, dtype=np.int16)

        # Silero expects chunks of 320 samples (20 ms at 16 kHz)
        self.chunk_size = 320

    def __call__(self, audio_bytes: Optional[bytes]) -> bool:
        if audio_bytes is None:
            # Reset state
            self._activation = 0
            self.detector.reset()
            self._buffer = np.zeros(0, dtype=np.int16)
            return False

        # Convert incoming bytes to int16 samples
        samples = np.frombuffer(audio_bytes, dtype=np.int16)

        # Append to internal buffer
        self._buffer = np.concatenate((self._buffer, samples))

        # Process all full chunks
        speech_detected = False
        while len(self._buffer) >= self.chunk_size:
            chunk = self._buffer[:self.chunk_size]
            self._buffer = self._buffer[self.chunk_size:]

            # Convert back to bytes for Silero
            chunk_bytes = chunk.tobytes()
            if self.detector(chunk_bytes) >= self.threshold:
                self._activation += 1
                if self._activation >= self.trigger_level:
                    self._activation = 0
                    speech_detected = True
            else:
                self._activation = max(0, self._activation - 1)

        return speech_detected
