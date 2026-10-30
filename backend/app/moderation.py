"""Recovery moderation: CRISIS -> REMOVE -> HOLD -> SOFTEN -> ALLOW (in that order)."""
CRISIS_WORDS = ("kill myself","suicide","overdose","want to die","hurt myself","self-harm","end my life")
REMOVE_WORDS = ("sell drugs","buy drugs","sourcing","score some","threaten you","doxx","minor sex","send money to","gang recruit")
HOLD_WORDS = ("tapering plan","medical advice","legal advice about","war story","glorifying","his address is","her phone is")
SOFTEN_WORDS = ("my full name is","my address is","my case number","ssn","social security")

def moderate(text: str) -> dict:
    low = (text or "").lower()
    if any(w in low for w in CRISIS_WORDS):
        return {"decision":"crisis","rule":"crisis_first","needs_human":True,"urgency":"now","reply":"You are not alone. Please call or text 988, or call 911 if you are in immediate danger. For overdose, call 911 and use naloxone if available."}
    if any(w in low for w in REMOVE_WORDS):
        return {"decision":"remove","rule":"remove_escalate","needs_human":True,"urgency":"high","reply":"This post cannot stay up because it may put people at risk. A member of our team will review it."}
    if any(w in low for w in HOLD_WORDS):
        return {"decision":"hold","rule":"hold_for_review","needs_human":True,"urgency":"normal","reply":"Thanks for sharing. A moderator will take a look before this appears."}
    if any(w in low for w in SOFTEN_WORDS):
        return {"decision":"soften","rule":"soften_personal_info","needs_human":False,"urgency":"low","reply":"Consider removing personal details like names, addresses, or case numbers to protect your privacy."}
    return {"decision":"allow","rule":"allow","needs_human":False,"urgency":"none","reply":""}
