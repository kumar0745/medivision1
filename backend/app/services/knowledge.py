# Small, curated educational snippets for retrieval-grounded demo answers.
# These are general wellness references, not clinical protocols.
KNOWLEDGE = [
    {"title":"When to seek urgent care", "source":"NHS - When to call 999", "url":"https://www.nhs.uk/nhs-services/urgent-and-emergency-care-services/when-to-call-999/", "text":"Seek emergency help for life-threatening symptoms such as severe difficulty breathing, suspected heart attack or stroke, severe bleeding, unconsciousness, or a seizure that does not stop. Do not wait for an online assistant when symptoms may be urgent."},
    {"title":"Physical activity basics", "source":"WHO - Physical activity", "url":"https://www.who.int/news-room/fact-sheets/detail/physical-activity", "text":"Regular physical activity supports physical and mental health. Adults should aim for regular moderate activity according to their abilities. Start gradually, adapt activity to health status, and seek professional advice if exercise causes concerning symptoms."},
    {"title":"Stress management", "source":"WHO - Doing What Matters in Times of Stress", "url":"https://www.who.int/publications/i/item/9789240003927", "text":"Grounding, noticing thoughts, making room for difficult feelings, and acting on personal values are practical stress-management skills. Short daily practice can help build habits; seek qualified support when distress is persistent or overwhelming."},
    {"title":"Healthy sleep", "source":"CDC - About Sleep", "url":"https://www.cdc.gov/sleep/about/index.html", "text":"Healthy sleep supports overall health. Consistent sleep schedules and a calming bedtime routine can help. Sleep needs vary by age and individual; persistent sleep problems should be discussed with a healthcare professional."},
    {"title":"Menstrual health", "source":"NHS - Periods", "url":"https://www.nhs.uk/conditions/periods/", "text":"Menstrual cycles vary between people. Tracking period dates and symptoms can help notice patterns. Severe pain, very heavy bleeding, missed periods, or significant changes should be discussed with a healthcare professional."},
    {"title":"PCOS awareness", "source":"NHS - Polycystic ovary syndrome", "url":"https://www.nhs.uk/conditions/polycystic-ovary-syndrome-pcos/", "text":"PCOS can involve irregular periods, excess androgen symptoms and polycystic ovaries, but symptoms vary. No single symptom or questionnaire confirms PCOS. A clinician evaluates symptoms and may arrange tests."},
    {"title":"Skin changes", "source":"NHS - Moles", "url":"https://www.nhs.uk/conditions/moles/", "text":"A new or changing mole, change in size, shape or colour, itching, bleeding, or an unusual skin lesion should be assessed by a healthcare professional. An online image review cannot rule out skin cancer."},
]

def retrieve(query: str, limit: int = 3):
    terms = {w.lower().strip(".,!?") for w in query.split() if len(w) > 3}
    ranked = []
    for item in KNOWLEDGE:
        hay = (item["title"] + " " + item["text"]).lower()
        score = sum(1 for term in terms if term in hay)
        if score:
            ranked.append((score, item))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in ranked[:limit]]
