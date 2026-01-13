def extract_attributes(text: str, intent: str):
    attributes = {"category": None, "activity": None, "feature": None}

   
    if "shoe" in intent:
        attributes["category"] = "shoe"

    
    if "jog" in text or "run" in text:
        attributes["activity"] = "jogging"
    elif "gym" in text:
        attributes["activity"] = "gym"

    
    if "rain" in text or "water" in text:
        attributes["feature"] = "waterproof"

    return attributes
