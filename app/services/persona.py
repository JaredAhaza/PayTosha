def classify_user(data: dict):
    location = data.get("location")
    job_title = data.get("job_title", "").lower()

    if ".edu" in data.get("email", "") or "student" in job_title:
        return {"tier": "Student", "discount": 50}
    elif "founder" in job_title or "ceo" in job_title:
        return {"tier": "Premium", "discount": 0}
    elif location in ["Kenya", "Uganda", "India"]:
        return {"tier": "Fair Plan", "discount": 70}
    else:
        return {"tier": "Standard", "discount": 0}
