import edge_tts
import os
import uuid

# Available Uzbek voices in Edge TTS
VOICES = {
    "sardor": {"name": "uz-UZ-SardorNeural", "title": "Sardor (Erkak 👨)"},
    "madina": {"name": "uz-UZ-MadinaNeural", "title": "Madina (Ayol 👩)"}
}

async def generate_speech(text: str, voice_key: str = "sardor") -> str:
    """
    Given text and voice key, generates an MP3 file using edge_tts
    and returns the file path.
    """
    voice_name = VOICES.get(voice_key, VOICES["sardor"])["name"]
    output_file = f"temp_{uuid.uuid4()}.mp3"
    
    try:
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(output_file)
        return output_file
    except Exception as e:
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e
