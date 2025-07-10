Social Media AI Dashboard (Local Version)
This project provides a local AI-powered dashboard to manage social media engagement using AI. It processes social media comments, classifies them, and generates automated replies based on predefined categories (Lead, Praise, Spam, Question, Complaint). The AI works offline using Hugging Face's GPT-2 and BART models.

Features
Comment Classification: Classify comments into five categories (LEAD, PRAISE, SPAM, QUESTION, COMPLAINT) using a zero-shot classification model.

Automated Replies: Generate AI-based replies tailored to the comment category.

Local AI Mode: Runs the models locally without requiring an API key (using Hugging Face’s transformers library).

Interactive Dashboard: A user-friendly dashboard built using Streamlit where you can test AI responses in real-time.

Optional GHL Integration: Connect and integrate with GoHighLevel (GHL) for CRM functionalities (optional).

Requirements
Python 3.8 or higher

transformers (for Hugging Face models)

torch (for PyTorch-based models)

streamlit (for the dashboard)

requests (for GHL integration)

.env file for environment variables like API keys

Installation
Clone the repository:

bash
Copy
git clone https://github.com/yourusername/social-media-ai-dashboard.git
cd social-media-ai-dashboard
Set up a virtual environment:

bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install dependencies:

bash
Copy
pip install -r requirements.txt
Set up environment variables:

Create a .env file in the project root with the following (optional, only for GHL integration):

ini
Copy
OPENAI_API_KEY=your-api-key-here
GHL_API_KEY=your-ghl-api-key-here
GHL_LOCATION_ID=your-location-id-here
Usage
Running the Local AI Dashboard:

To run the local version of the dashboard with GPT-2, execute:

bash
Copy
streamlit run dashboard_local.py
Using the Dashboard:

In the dashboard, you can input comments to test how the AI classifies and generates responses.

The Local AI Mode runs entirely offline, and no API key is required unless you enable GHL integration.

You can also clear conversations and test different comment types (LEAD, PRAISE, SPAM, QUESTION, COMPLAINT).

GHL Integration (Optional):

You can optionally connect to GoHighLevel for managing contacts and workflows. To enable GHL integration:

Provide your GHL API Key and Location ID in the sidebar.

The AI will trigger workflows and tag contacts in GHL based on comment classification (e.g., "LEAD" or "COMPLAINT").

Customization
AI Model Settings: The AI is set to use GPT-2 for text generation and BART for classification. You can change the model types in the code if needed.

Response Logic: The response generation is based on templates, but you can adjust these templates for better customization. Modify the REPLY_GENERATION_PROMPTS in the prompt.py file.

Example Prompts
LEAD:

Prompt: "Thank you for your interest! We’d love to help you. Please send us a direct message for more details."

PRAISE:

Prompt: "Thank you so much for your kind words! Your support means a lot to us."

COMPLAINT:

Prompt: "We’re really sorry about your experience. Please contact us directly for assistance."

QUESTION:

Prompt: "Thanks for asking! We’ll get back to you with more details."

SPAM:

Prompt: "Thank you for your comment. Feel free to reach out if you need help with our services."

Troubleshooting
If you experience slow responses or issues with generating replies, try adjusting the model settings (like temperature or max tokens).

If the AI is not responding correctly to your prompts, ensure the models are properly initialized and that your .env file is set up correctly.

License
This project is licensed under the MIT License - see the LICENSE file for details.

