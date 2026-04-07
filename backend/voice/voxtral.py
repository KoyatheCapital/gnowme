import base64
from pathlib import Path
from mistralai import Mistral

class GnowmeVoice:
    def __init__(self, api_key: str, ref_path: str):
        self.client = Mistral(api_key=api_key)
        self.ref_path = ref_path
        self._ref_b64 = None

    def _load_ref(self) -> str:
        if self._ref_b64 is None:
            self._ref_b64 = base64.b64encode(Path(self.ref_path).read_bytes()).decode()
        return self._ref_b64

    async def speak(self, text: str, style: str = "grounded") -> bytes:
        styled = f"Speak naturally in a {style} tone: {text}"
        response = self.client.audio.speech.complete(
            model="voxtral-mini-tts-2603",
            input=styled,
            voice={"reference_audio": self._load_ref()}
        )
        return response.content
