"""Voice activity detection with Silero VAD and proper chunking."""

from typing import Optional
import numpy as np


class SileroVad:
    """Voice activity detection with silero VAD."""

    def __init__(self, threshold: float, trigger_level: int) -> None:
        from pysilero_vad import SileroVoiceActivityDetector

        self.detector = SileroVoiceActivityDetector()
        self.threshold = threshold
        self.trigger_level = trigger_level
        self._activation = 0

        # Internal buffer for samples
        self._buffer = np.zeros(0, dtype=np.int16)

        # Dynamically get the chunk size in **samples**
        self.chunk_samples = self.detector.chunk_samples()

    def __call__(self, audio_bytes: Optional[bytes]) -> bool:
        if audio_bytes is None:
            # Reset everything
            self._activation = 0
            self.detector.reset()
            self._buffer = np.zeros(0, dtype=np.int16)
            return False

        # Convert incoming bytes to int16 samples
        samples = np.frombuffer(audio_bytes, dtype=np.int16)

        # Append to internal buffer
        self._buffer = np.concatenate((self._buffer, samples))

        # Process full chunks
        speech_detected = False
        while len(self._buffer) >= self.chunk_samples:
            # Slice exactly one chunk
            chunk = self._buffer[:self.chunk_samples]
            self._buffer = self._buffer[self.chunk_samples:]

            # Convert chunk back to raw bytes
            chunk_bytes = chunk.tobytes()

            # Pass to Silero detector
            score = self.detector(chunk_bytes)
            if score >= self.threshold:
                self._activation += 1
                if self._activation >= self.trigger_level:
                    self._activation = 0
                    speech_detected = True
            else:
                self._activation = max(0, self._activation - 1)

        return speech_detected
