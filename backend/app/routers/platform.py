"""Platform: read-aloud config, multi-language, music player (sample tracks, off in academy)."""
from fastapi import APIRouter
from ..i18n_data import LANGS_DATA
from ..seed_data import MUSIC_TRACKS
from ._stub import stub_router

router = stub_router("platform", exclude={"read_aloud", "multi_language", "music_player"})

@router.get("/read_aloud")
async def read_aloud():
    return {"enabled": True, "engine": "Web Speech API (speechSynthesis)", "fallback": "Piper TTS", "instruction": "Use the Read aloud button on any card; it uses your device voice."}

@router.get("/multi_language")
async def langs():
    return {"languages": LANGS_DATA, "count": len(LANGS_DATA), "fallback": "en", "rtl": ["ar"]}

@router.get("/music_player/tracks")
async def music_tracks():
    return {"tracks": MUSIC_TRACKS, "off_in_academy": True,
            "note": "Sample tracks only. No third-party streaming accounts. The player is off inside academy and course modules."}
