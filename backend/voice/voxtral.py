import base64
from pathlib import Path
from mistralai.client import Mistral


class GnowmeVoice:
    """
    Voxtral TTS wrapper.
    Always uses the user's cloned voice reference when available.
    Falls back to default voice if no reference has been recorded.
    """

    def __init__(self, api_key: str, ref_path: str):
        self.client   = Mistral(api_key=api_key)
        self.ref_path = ref_path
        # Load reference audio eagerly so we fail fast on bad paths
        self._ref_b64: str | None = self._load_ref(ref_path)

    def _load_ref(self, path: str) -> str | None:
        """Encode WAV to base64. Returns None if file doesn't exist yet."""
        p = Path(path)
        if p.exists() and p.stat().st_size > 0:
            return base64.b64encode(p.read_bytes()).decode()
        return None

    def reload_ref(self, new_path: str | None = None) -> None:
        """Hot-reload after a new voice recording is saved."""
        target = new_path or self.ref_path
        self.ref_path = target
        self._ref_b64 = self._load_ref(target)

    async def speak(self, text: str, style: str = "grounded") -> bytes:
        """
        Generate speech.
        - If user has a cloned voice reference, uses it for every call.
        - Style modulates the internal-voice framing sent to the model.
        """
        styled_input = (
            f"Speak naturally and conversationally in a {style} tone, "
            f"like my own inner voice — calm, clear, unhurried: {text}"
        )

        voice_config: dict = {}
        if self._ref_b64:
            voice_config = {"reference_audio": self._ref_b64}

        response = self.client.audio.speech.complete(
            model="voxtral-mini-tts-2603",
            input=styled_input,
            voice=voice_config if voice_config else "alloy",
        )
        return response.content
