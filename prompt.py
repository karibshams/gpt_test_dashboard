# prompt.py - AI Instructions with Biblical/Spiritual Tone for GPT-2

# Tone Guidelines - Simplified for GPT-2
TONE_GUIDE = """
Biblical and empathetic, showing grace and humility. Never preachy or judgmental.
Point to God, not self. Use gentle humor when appropriate.
"""

CLASSIFICATION_PROMPT = """
Classify this spiritual/faith comment into ONE category:

1. LEAD - Interest in devotionals, courses, spiritual resources
2. PRAISE - Positive spiritual feedback, testimonials, gratitude
3. SPAM - Irrelevant links, off-topic promotion
4. QUESTION - Questions about faith, God, spirituality
5. COMPLAINT - Doubts, struggles, criticism of faith

Comment: {comment}

Category:"""

# GPT-2 friendly prompts with examples built-in
REPLY_GENERATION_PROMPTS = {
    "LEAD": """
Someone interested in spiritual content commented: "{comment}"

Examples of good responses:
- "We'd love for you to walk with us through it. Here's the link to get started."
- "That desire is a whisper from God's heart to yours. The next step doesn't require perfection."

Write a warm spiritual reply (2 sentences):""",
    
    "PRAISE": """
Someone shared positive spiritual feedback: "{comment}"

Examples of good responses:
- "We're so grateful it resonated with you. May it continue to lead you deeper into His truth."
- "Your words are a gift. May every encouragement point you back to the One who uplifts us all."

Write a humble, grateful reply (2 sentences):""",
    
    "SPAM": """
Spam comment received: "{comment}"

Example response:
- "We genuinely hope you find peace wherever your journey leads."

Write a brief, gracious reply (1 sentence):""",
    
    "QUESTION": """
Someone asked about faith/spirituality: "{comment}"

Examples of good responses:
- "Great question. Our foundation is deeply spiritual - this truth isn't just motivational, it's transformative."
- "You're not alone in wondering that. The invitation of grace includes you, even when you doubt."

Write a thoughtful spiritual reply (2 sentences):""",
    
    "COMPLAINT": """
Someone struggling with faith commented: "{comment}"

Examples of good responses:
- "That silence can feel so loud. But even there, you're not abandoned - sometimes stillness is where He whispers."
- "You don't have to pretend here. God meets us in honesty, not perfection."

Write an empathetic spiritual reply (2 sentences):"""
}

# System prompt optimized for GPT-2
SYSTEM_PROMPT = """
You are a compassionate spiritual content creator. Write with biblical grace and humility.
Never be preachy. Point to God's love."""

# Template responses for GPT-2 fallback with spiritual tone
SPIRITUAL_TEMPLATES = {
    "LEAD": {
        "devotional": [
            "We'd love for you to walk with us through this journey. Check your DM for the devotional link - may it meet you right where you are.",
            "Your interest is a beautiful thing. We'll send you the details - this invitation to deeper truth is always open.",
            "So glad this resonated with you. The devotional link is coming your way - may each word point you to His grace."
        ],
        "general": [
            "That pull you feel? It's real. We'll DM you the next steps - no perfection required, just an open heart.",
            "We're honored by your interest. Details coming to your inbox - may this be the beginning of something beautiful.",
            "Your curiosity is sacred ground. Check your messages for more - He's already preparing the way."
        ]
    },
    "PRAISE": {
        "emotional": [
            "Tears are sacred, especially when truth touches something deep. We're honored this moved you.",
            "We take no responsibility for tear-streaked spreadsheets, but we're grateful it met you where you needed it.",
            "Your words are a gift. May this truth continue to echo in the spaces that need it most."
        ],
        "general": [
            "We're so grateful it resonated with you. May it lead you deeper into the truth of who you are in Him.",
            "Thank you for sharing this. It's a joy to know these words found their way to your heart.",
            "Your encouragement means everything. May every blessing point you back to the Source of all good things."
        ]
    },
    "QUESTION": {
        "doubt": [
            "You're not alone in wondering that. The invitation of grace is personal, and yes, it includes you.",
            "That's a brave question to ask. Faith isn't about having all the answers - it's about trusting the One who does.",
            "Your honesty is refreshing. Let's explore this together - check your DM for a deeper conversation."
        ],
        "seeking": [
            "Beautiful question. Our foundation is deeply spiritual - this isn't just motivation, it's transformation.",
            "Thank you for asking. The short answer is yes, but the full story is even better - DMing you now.",
            "Great question. Truth often stirs curiosity first - let's continue this conversation privately."
        ]
    },
    "COMPLAINT": {
        "hurt": [
            "You don't have to pretend here. God meets us in our honesty, not our perfection.",
            "That pain is real, and so is His presence in it. We're here to hold space for your journey.",
            "Your struggle matters. Sometimes the wilderness is where the deepest healing begins."
        ],
        "criticism": [
            "We hear your concern. Our aim is to honor Scripture while making space for grace and growth.",
            "Thank you for your honesty. We understand this may not resonate with everyone, and that's okay.",
            "We appreciate you sharing your perspective. May you find the peace you're looking for."
        ]
    },
    "SPAM": {
        "default": [
            "We hope you find what you're searching for. Blessings on your journey.",
            "Thank you for stopping by. May grace meet you wherever you are.",
            "Peace to you, friend. Our door is always open for genuine connection."
        ]
    }
}

# Keywords for better classification and response selection
SPIRITUAL_KEYWORDS = {
    "emotional": ["crying", "tears", "moved", "touched", "felt", "heart", "soul"],
    "seeking": ["searching", "looking", "want to believe", "help me", "show me", "curious"],
    "doubt": ["struggling", "doubt", "hard to believe", "questioning", "wondering", "confused"],
    "praise": ["blessed", "grateful", "amazing", "powerful", "beautiful", "thank you"],
    "hurt": ["broken", "lost", "alone", "abandoned", "failed", "messed up", "tired"],
    "devotional": ["devotional", "study", "course", "program", "resource", "material"]
}

def get_keyword_context(comment: str) -> str:
    """
    Analyze comment for spiritual context keywords.
    Returns the most relevant context for template selection.
    """
    comment_lower = comment.lower()
    
    # Check each keyword category
    scores = {}
    for context, keywords in SPIRITUAL_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in comment_lower)
        if score > 0:
            scores[context] = score
    
    # Return context with highest score, or 'general' as default
    if scores:
        return max(scores, key=scores.get)
    return "general"

def get_template_response(category: str, comment: str) -> str:
    """
    Get an appropriate template response based on category and context.
    """
    context = get_keyword_context(comment)
    
    # Get templates for this category
    category_templates = SPIRITUAL_TEMPLATES.get(category, SPIRITUAL_TEMPLATES["SPAM"])
    
    # Try to get context-specific templates first
    if context in category_templates:
        templates = category_templates[context]
    elif "general" in category_templates:
        templates = category_templates["general"]
    else:
        templates = category_templates.get("default", ["Thank you for reaching out. Blessings to you."])
    
    # Select template based on comment length for variety
    index = len(comment) % len(templates)
    return templates[index]

# Example responses from the PDF for reference
PDF_EXAMPLES = {
    "tear_response": "We take no responsibility for tear-streaked spreadsheets, but we're grateful it met you right where you needed it.",
    "coffee_response": "The Holy Spirit moves in mysterious ways… but a strong second place goes to caffeine.",
    "targeted_response": "We've filed that under 'divinely targeted content.' So glad it found its way to you!",
    "doubt_response": "You're not alone in feeling that. But the invitation remains: His love meets you right where you are, even in the doubt.",
    "struggle_response": "That silence can feel so loud. But even there, you're not abandoned. Sometimes the stillness is where He whispers the loudest.",
    "criticism_response": "We understand this may not resonate with everyone, and that's okay. We genuinely hope you find peace wherever your journey leads.",
    "seeking_response": "You've already started right here, in that sentence. The return journey begins with honesty, not certainty."
}