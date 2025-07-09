# app_local.py - Local AI Testing with GPT-2 (No API Key Required)

import os
from typing import Dict, List
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
import torch
import re
from prompt import (
    CLASSIFICATION_PROMPT, 
    REPLY_GENERATION_PROMPTS, 
    SYSTEM_PROMPT
)

class LocalSocialMediaAI:
    """
    Local AI system using Hugging Face Transformers.
    No API key required - runs completely offline after downloading models.
    """
    
    def __init__(self):
        """Initialize local AI models."""
        print("🤖 Initializing local AI models...")
        print("This may take a few minutes on first run to download models...")
        
        # Initialize classification model (using zero-shot classification)
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Initialize text generation model
        self.generator = pipeline(
            "text-generation",
            model="gpt2-medium",  # You can use "gpt2" for smaller/faster model
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Categories for classification
        self.categories = ["LEAD", "PRAISE", "SPAM", "QUESTION", "COMPLAINT"]
        
        # Category descriptions for better classification
        self.category_descriptions = {
            "LEAD": "interested in buying or purchasing products or services",
            "PRAISE": "positive feedback compliments or happy customer",
            "SPAM": "irrelevant promotional content or suspicious links",
            "QUESTION": "asking questions or seeking information",
            "COMPLAINT": "negative feedback problems or dissatisfaction"
        }
        
        print("✅ Local AI models initialized successfully!")
        print(f"Using device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    
    def classify_comment(self, comment: str) -> str:
        """
        Classify a social media comment using local model.
        
        Args:
            comment: The social media comment to classify
            
        Returns:
            Category: LEAD, PRAISE, SPAM, QUESTION, or COMPLAINT
        """
        try:
            # Use zero-shot classification with detailed labels
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
            
            # Fallback classification based on keywords
            return self._keyword_classification(comment)
            
        except Exception as e:
            print(f"Error in classification: {str(e)}")
            return self._keyword_classification(comment)
    
    def _keyword_classification(self, comment: str) -> str:
        """Fallback keyword-based classification."""
        comment_lower = comment.lower()
        
        # Keyword patterns for each category
        patterns = {
            "LEAD": ["interested", "buy", "purchase", "order", "price", "cost", "how much"],
            "PRAISE": ["love", "great", "amazing", "best", "excellent", "wonderful", "thank"],
            "SPAM": ["click here", "free", "win", "prize", "xxx", "bit.ly", "check out my"],
            "COMPLAINT": ["terrible", "worst", "disappointed", "problem", "issue", "broken", "never"],
            "QUESTION": ["?", "how", "what", "when", "where", "why", "can you", "do you"]
        }
        
        # Count matches for each category
        scores = {}
        for category, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in comment_lower)
            scores[category] = score
        
        # Return category with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return "QUESTION"  # Default
    
    def generate_reply(self, comment: str, category: str) -> str:
        """
        Generate a reply using local GPT-2 model.
        
        Args:
            comment: The original comment
            category: The classified category
            
        Returns:
            Generated reply text
        """
        try:
            # Create a simplified prompt for GPT-2
            prompt_templates = {
                "LEAD": f"Customer: {comment}\nBusiness reply to interested customer: Thank you for your interest!",
                "PRAISE": f"Customer: {comment}\nBusiness reply to happy customer: We appreciate your kind words",
                "SPAM": f"Comment: {comment}\nProfessional reply: Thank you for your comment.",
                "QUESTION": f"Customer question: {comment}\nHelpful business reply: Thanks for asking!",
                "COMPLAINT": f"Customer complaint: {comment}\nEmpathetic business reply: We're sorry to hear"
            }
            
            prompt = prompt_templates.get(category, prompt_templates["QUESTION"])
            
            # Generate response
            response = self.generator(
                prompt,
                max_length=len(prompt.split()) + 30,
                num_return_sequences=1,
                temperature=0.7,
                pad_token_id=50256,
                do_sample=True,
                top_p=0.9
            )
            
            # Extract the generated part
            generated_text = response[0]['generated_text']
            
            # Clean up the response
            reply = self._clean_generated_reply(generated_text, prompt)
            
            # If reply is too short or weird, use template
            if len(reply) < 10 or not reply.strip():
                return self._get_template_reply(category, comment)
            
            return reply
            
        except Exception as e:
            print(f"Error in reply generation: {str(e)}")
            return self._get_template_reply(category, comment)
    
    def _clean_generated_reply(self, generated_text: str, prompt: str) -> str:
        """Clean up the generated reply."""
        # Remove the prompt from the generated text
        reply = generated_text.replace(prompt, "").strip()
        
        # Remove any "Customer:" or "Business:" prefixes that might appear
        reply = re.sub(r'^(Customer:|Business:|Reply:|Business reply:)', '', reply, flags=re.IGNORECASE).strip()
        
        # Take only the first 1-2 sentences
        sentences = re.split(r'[.!?]+', reply)
        if sentences:
            reply = '. '.join(sentences[:2]).strip()
            if reply and not reply.endswith('.'):
                reply += '.'
        
        return reply
    
    def _get_template_reply(self, category: str, comment: str) -> str:
        """Get template-based reply for consistent results."""
        templates = {
            "LEAD": [
                "Thank you for your interest! We'd love to help you. Please send us a direct message for more details.",
                "We're excited about your interest! Check your DM for exclusive information.",
                "Thanks for reaching out! We'll send you all the details via direct message."
            ],
            "PRAISE": [
                "Thank you so much for your kind words! Your support means everything to us.",
                "We're thrilled to hear you're happy! Thank you for being an amazing customer.",
                "Your feedback made our day! We appreciate your support."
            ],
            "SPAM": [
                "Thank you for your comment. Feel free to reach out if you have questions about our services.",
                "We appreciate your engagement. Let us know if you need any assistance.",
                "Thanks for stopping by. We're here if you need help."
            ],
            "QUESTION": [
                "Great question! Please send us a direct message and we'll provide all the details.",
                "Thanks for asking! We'll DM you with the information you need.",
                "Happy to help! Check your messages for a detailed response."
            ],
            "COMPLAINT": [
                "We're truly sorry about your experience. Please DM us immediately so we can make this right.",
                "We apologize for the inconvenience. Let's resolve this - please check your direct messages.",
                "Your experience matters to us. We've sent you a DM to address this issue right away."
            ]
        }
        
        # Get replies for category
        replies = templates.get(category, templates["QUESTION"])
        
        # Simple selection based on comment length (to add variety)
        index = len(comment) % len(replies)
        return replies[index]
    
    def process_comment(self, comment: str) -> Dict[str, str]:
        """
        Process a comment: classify it and generate an appropriate reply.
        
        Args:
            comment: The social media comment to process
            
        Returns:
            Dictionary with 'category' and 'reply' keys
        """
        # Step 1: Classify the comment
        category = self.classify_comment(comment)
        
        # Step 2: Generate a reply
        reply = self.generate_reply(comment, category)
        
        return {
            "comment": comment,
            "category": category,
            "reply": reply
        }


# Test function
def test_local_ai():
    """Test the local AI system."""
    print("🧪 Testing Local AI System (No API Key Required)\n")
    
    # Initialize local AI
    ai = LocalSocialMediaAI()
    
    # Test comments
    test_comments = [
        "I'm interested in your product! How can I order?",
        "This is the best service ever! Love it!",
        "What are your business hours?",
        "My order hasn't arrived yet and it's been 2 weeks!",
        "Click here for free followers >>> spam.com",
        "Your product quality is amazing, keep up the great work!",
        "Is this available in size XL?",
        "Terrible experience, very disappointed with the service"
    ]
    
    print("\n" + "="*60)
    print("TESTING COMMENTS")
    print("="*60 + "\n")
    
    for i, comment in enumerate(test_comments, 1):
        print(f"Test {i}:")
        print(f"📝 Comment: {comment}")
        
        # Process comment
        result = ai.process_comment(comment)
        
        print(f"🏷️  Category: {result['category']}")
        print(f"💬 Reply: {result['reply']}")
        print("-"*60 + "\n")
    
    # Interactive mode
    print("\n🎮 INTERACTIVE MODE - Type 'quit' to exit")
    print("="*60)
    
    while True:
        user_comment = input("\nEnter a comment to test: ").strip()
        
        if user_comment.lower() == 'quit':
            print("👋 Goodbye!")
            break
        
        if user_comment:
            result = ai.process_comment(user_comment)
            print(f"\n🏷️  Category: {result['category']}")
            print(f"💬 Reply: {result['reply']}")


if __name__ == "__main__":
    test_local_ai()