# app_local.py - Enhanced Local AI with Spiritual Tone (No API Key Required)

import os
from typing import Dict, List
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
import torch
import re
from prompt import (
    CLASSIFICATION_PROMPT, 
    REPLY_GENERATION_PROMPTS, 
    SYSTEM_PROMPT,
    SPIRITUAL_TEMPLATES,
    get_keyword_context,
    get_template_response
)

class LocalSocialMediaAI:
    """
    Local AI system with spiritual/biblical tone using Hugging Face Transformers.
    No API key required - runs completely offline after downloading models.
    """
    
    def __init__(self):
        """Initialize local AI models."""
        print("🤖 Initializing local AI models with spiritual tone...")
        print("This may take a few minutes on first run to download models...")
        
        # Initialize classification model (using zero-shot classification)
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Initialize text generation model
        # Using GPT-2 medium for better quality
        self.generator = pipeline(
            "text-generation",
            model="gpt2-medium",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Categories for classification
        self.categories = ["LEAD", "PRAISE", "SPAM", "QUESTION", "COMPLAINT"]
        
        # Spiritual category descriptions for better classification
        self.category_descriptions = {
            "LEAD": "interested in devotionals spiritual resources or faith content",
            "PRAISE": "positive spiritual feedback testimonial or expressing gratitude to God",
            "SPAM": "irrelevant promotional content or suspicious links",
            "QUESTION": "asking about faith God spirituality or seeking spiritual guidance",
            "COMPLAINT": "spiritual struggles doubts criticism or expressing hurt"
        }
        
        print("✅ Local AI models initialized successfully!")
        print(f"Using device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    
    def classify_comment(self, comment: str) -> str:
        """
        Classify a social media comment using local model with spiritual context.
        """
        try:
            # Use zero-shot classification with spiritual descriptions
            result = self.classifier(
                comment,
                candidate_labels=list(self.category_descriptions.values()),
                hypothesis_template="This comment is about {}."
            )
            
            # Map back to category
            top_label = result['labels'][0]
            for cat, desc in self.category_descriptions.items():
                if desc == top_label:
                    return cat
            
            # Fallback to keyword classification
            return self._spiritual_keyword_classification(comment)
            
        except Exception as e:
            print(f"Error in classification: {str(e)}")
            return self._spiritual_keyword_classification(comment)
    
    def _spiritual_keyword_classification(self, comment: str) -> str:
        """Enhanced keyword classification with spiritual context."""
        comment_lower = comment.lower()
        
        # Spiritual keyword patterns
        patterns = {
            "LEAD": ["devotional", "interested", "get this", "how can i", "want to", "course", "resource"],
            "PRAISE": ["blessed", "grateful", "thank", "moved", "powerful", "tears", "crying", "amazing"],
            "SPAM": ["click here", "free followers", "bit.ly", "check out my", "xxx"],
            "COMPLAINT": ["struggling", "doubt", "fake", "shallow", "disappointed", "silent", "abandoned"],
            "QUESTION": ["?", "how", "what", "why", "is god", "does god", "can god", "where is god"]
        }
        
        # Count matches for each category
        scores = {}
        for category, keywords in patterns.items():
            score = sum(2 if keyword in comment_lower else 0 for keyword in keywords)
            # Boost score for question marks in QUESTION category
            if category == "QUESTION" and "?" in comment:
                score += 3
            scores[category] = score
        
        # Return category with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return "QUESTION"  # Default
    
    def generate_reply(self, comment: str, category: str) -> str:
        """
        Generate a spiritually-toned reply using GPT-2 or templates.
        """
        # First, try template-based response for consistency
        template_response = get_template_response(category, comment)
        
        # For GPT-2, we'll use it to enhance or vary the template slightly
        try:
            # Get the appropriate prompt
            prompt = REPLY_GENERATION_PROMPTS.get(category, REPLY_GENERATION_PROMPTS["QUESTION"])
            formatted_prompt = prompt.format(comment=comment)
            
            # Try GPT-2 generation with spiritual context
            response = self.generator(
                formatted_prompt,
                max_length=len(formatted_prompt.split()) + 40,
                num_return_sequences=1,
                temperature=0.8,
                pad_token_id=50256,
                do_sample=True,
                top_p=0.9
            )
            
            # Extract and clean the generated text
            generated_text = response[0]['generated_text']
            gpt2_reply = self._clean_spiritual_reply(generated_text, formatted_prompt)
            
            # Validate the reply
            if self._is_valid_spiritual_reply(gpt2_reply, category):
                return gpt2_reply
            else:
                # Fall back to template
                return template_response
                
        except Exception as e:
            print(f"Using template response due to: {str(e)}")
            return template_response
    
    def _clean_spiritual_reply(self, generated_text: str, prompt: str) -> str:
        """Clean up GPT-2 output to match spiritual tone."""
        # Remove the prompt
        reply = generated_text.replace(prompt, "").strip()
        
        # Remove any unwanted prefixes
        prefixes_to_remove = [
            "Write a", "Reply:", "Response:", "Answer:", 
            "Customer:", "Business:", "Examples of"
        ]
        for prefix in prefixes_to_remove:
            reply = re.sub(f'^{prefix}.*?:', '', reply, flags=re.IGNORECASE).strip()
        
        # Extract first 2 sentences
        sentences = re.split(r'[.!?]+', reply)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 2:
            reply = f"{sentences[0]}. {sentences[1]}."
        elif len(sentences) == 1:
            reply = f"{sentences[0]}."
        else:
            return ""
        
        # Ensure it doesn't end with incomplete thoughts
        reply = re.sub(r'\s+[A-Z][a-z]*$', '.', reply)
        
        return reply.strip()
    
    def _is_valid_spiritual_reply(self, reply: str, category: str) -> bool:
        """Validate if the reply maintains appropriate spiritual tone."""
        if not reply or len(reply) < 20:
            return False
        
        # Check for inappropriate content
        inappropriate = [
            "click here", "buy now", "limited time", "act now",
            "deal", "discount", "offer expires", "hurry"
        ]
        
        reply_lower = reply.lower()
        if any(phrase in reply_lower for phrase in inappropriate):
            return False
        
        # Ensure spiritual replies don't sound too casual or sales-y
        if category in ["LEAD", "PRAISE", "QUESTION", "COMPLAINT"]:
            # Should have some spiritual/empathetic language
            spiritual_indicators = [
                "grace", "god", "bless", "journey", "heart", "soul",
                "faith", "hope", "peace", "love", "truth", "sacred"
            ]
            has_spiritual_tone = any(word in reply_lower for word in spiritual_indicators)
            
            # Even without explicit spiritual words, check for appropriate tone
            appropriate_phrases = [
                "thank you", "grateful", "appreciate", "understand",
                "hear you", "with you", "for you", "honored"
            ]
            has_appropriate_tone = any(phrase in reply_lower for phrase in appropriate_phrases)
            
            return has_spiritual_tone or has_appropriate_tone
        
        return True
    
    def process_comment(self, comment: str) -> Dict[str, str]:
        """
        Process a comment with spiritual tone: classify and generate reply.
        """
        # Step 1: Classify the comment
        category = self.classify_comment(comment)
        
        # Step 2: Generate a spiritually-toned reply
        reply = self.generate_reply(comment, category)
        
        # Step 3: Add context about the tone
        context = get_keyword_context(comment)
        
        return {
            "comment": comment,
            "category": category,
            "reply": reply,
            "context": context
        }


# Enhanced test function with spiritual examples
def test_local_spiritual_ai():
    """Test the local AI system with spiritual comments."""
    print("🙏 Testing Local AI with Spiritual Tone (No API Key Required)\n")
    
    # Initialize local AI
    ai = LocalSocialMediaAI()
    
    # Test comments from the PDF
    test_comments = [
        # Emotional responses
        "That devotional had me tearing up at my desk... again!",
        "I'm crying. This was so powerful.",
        
        # Seeking/Interest
        "This feels like it was written just for me.",
        "How can I get this devotional?",
        "I want to believe in God again. But I don't know where to start.",
        
        # Questions/Doubts
        "I'm struggling to believe this applies to me.",
        "How do I know this is true for me?",
        "Why is this speaking to me louder than my morning coffee?",
        
        # Complaints/Criticism
        "This is such fake spiritual fluff. Y'all just want attention.",
        "I want to believe this, but it feels like God's silent in my life.",
        
        # Praise
        "This really spoke to me.",
        "Your words always uplift me.",
        "This made me feel seen for the first time in a while."
    ]
    
    print("\n" + "="*60)
    print("TESTING SPIRITUAL COMMENTS")
    print("="*60 + "\n")
    
    for i, comment in enumerate(test_comments, 1):
        print(f"Test {i}:")
        print(f"📝 Comment: {comment}")
        
        # Process comment
        result = ai.process_comment(comment)
        
        print(f"🏷️  Category: {result['category']}")
        print(f"💬 Reply: {result['reply']}")
        print(f"📍 Context: {result['context']}")
        print("-"*60 + "\n")
    
    # Interactive mode
    print("\n🎮 INTERACTIVE MODE - Type 'quit' to exit")
    print("="*60)
    
    while True:
        user_comment = input("\n💭 Enter a spiritual/faith comment to test: ").strip()
        
        if user_comment.lower() == 'quit':
            print("🙏 Blessings on your journey!")  
            break
        
        if user_comment:
            result = ai.process_comment(user_comment)
            print(f"\n🏷️  Category: {result['category']}")
            print(f"💬 Reply: {result['reply']}")
            print(f"📍 Context: {result['context']}")


if __name__ == "__main__":
    test_local_spiritual_ai()