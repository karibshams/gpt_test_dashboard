# dashboard_local.py - Local Dashboard with GPT-2 (No API Key Required)

import streamlit as st
from datetime import datetime
from app_local import LocalSocialMediaAI
from ghl_integration import GHLIntegration
import time

# Page configuration
st.set_page_config(
    page_title="Social Media AI Dashboard (Local)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-like styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: black;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: blue;
        border-radius: 15px;
        padding: 15px 20px;
        margin: 10px 0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border-left: 4px solid #10a37f;
    }
    
    .ai-message {
        background-color: black;
        border-radius: 15px;
        padding: 15px 20px;
        margin: 10px 0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border-left: 4px solid #6366f1;
    }
    
    /* Category badges */
    .category-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        margin: 5px 0;
    }
    
    .lead-badge { background-color: #10b981; color: white; }
    .praise-badge { background-color: #3b82f6; color: white; }
    .spam-badge { background-color: #ef4444; color: white; }
    .question-badge { background-color: #f59e0b; color: white; }
    .complaint-badge { background-color: #dc2626; color: white; }
    
    /* Local model status */
    .local-status {
        background-color: #e0f2fe;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid #0284c7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'ai_initialized' not in st.session_state:
    st.session_state.ai_initialized = False
if 'ghl_initialized' not in st.session_state:
    st.session_state.ghl_initialized = False

# Header
st.title("🤖 Social Media AI Testing Dashboard (Local Version)")
st.markdown("Test AI responses using local models - **No API Key Required!**")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Local AI Status
    st.markdown("""
    <div class="local-status">
        <strong>🖥️ Local AI Mode</strong><br>
        Running GPT-2 locally - No API needed!
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize AI button
    if not st.session_state.ai_initialized:
        if st.button("🚀 Initialize Local AI"):
            with st.spinner("Loading AI models... This may take 2-3 minutes on first run..."):
                try:
                    st.session_state.ai = LocalSocialMediaAI()
                    st.session_state.ai_initialized = True
                    st.success("✅ Local AI Ready!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.success("✅ Local AI Active")
    
    st.divider()
    
    # GHL Configuration (Optional)
    st.subheader("🔗 GoHighLevel Integration")
    st.info("Optional - Leave empty to test AI only")
    
    ghl_api_key = st.text_input("GHL API Key", type="password", key="ghl_api_key")
    ghl_location_id = st.text_input("GHL Location ID", key="ghl_location_id")
    
    if st.button("Connect to GHL"):
        if ghl_api_key and ghl_location_id:
            try:
                st.session_state.ghl = GHLIntegration(ghl_api_key, ghl_location_id)
                st.session_state.ghl_initialized = True
                st.success("✅ GHL Connected")
            except Exception as e:
                st.error(f"❌ GHL Error: {str(e)}")
    
    st.divider()
    
    # Test Options
    st.subheader("🧪 Test Options")
    show_processing_time = st.checkbox("Show Processing Time", value=True)
    show_confidence = st.checkbox("Show Classification Confidence", value=False)
    
    # Clear conversation
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat Interface")
    
    # Display conversation history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>📝 You:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            # AI response with category
            category_class = message["category"].lower() + "-badge"
            timing_info = f"<br><small>⏱️ {message.get('response_time', 0):.2f}s</small>" if show_processing_time else ""
            
            st.markdown(f"""
            <div class="ai-message">
                <strong>🤖 AI Response:</strong><br>
                {message["content"]}<br><br>
                <span class="category-badge {category_class}">
                    {message["category"]}
                </span>
                {timing_info}
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.header("📊 Analytics")
    
    # Category distribution
    if st.session_state.messages:
        categories = [msg["category"] for msg in st.session_state.messages if msg["role"] == "ai"]
        if categories:
            st.subheader("Category Distribution")
            
            # Count categories
            category_counts = {}
            for cat in categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            # Display metrics
            for cat, count in category_counts.items():
                st.metric(cat, count)
            
            # Performance metrics
            st.subheader("⏱️ Performance")
            response_times = [msg.get("response_time", 0) for msg in st.session_state.messages if msg["role"] == "ai"]
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                st.metric("Avg Response Time", f"{avg_time:.2f}s")
            st.metric("Total Processed", len(categories))

# Instructions if AI not initialized
if not st.session_state.ai_initialized:
    st.info("👆 Click 'Initialize Local AI' in the sidebar to start. First load will download models (~500MB).")

# Input area at the bottom
st.divider()

# Create input form
with st.form("comment_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area(
            "Enter a social media comment to test:",
            placeholder="Type your comment here... (e.g., 'I'm interested in your product!')",
            height=80,
            key="comment_input",
            disabled=not st.session_state.ai_initialized
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        submit_button = st.form_submit_button(
            "🚀 Send", 
            use_container_width=True,
            disabled=not st.session_state.ai_initialized
        )

# Process input
if submit_button and user_input and st.session_state.ai_initialized:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Show processing indicator
    with st.spinner("🤔 Local AI is processing..."):
        start_time = time.time()
        
        try:
            # Get AI response
            result = st.session_state.ai.process_comment(user_input)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Prepare AI message
            ai_message = {
                "role": "ai",
                "content": result['reply'],
                "category": result['category'],
                "timestamp": datetime.now(),
                "response_time": response_time
            }
            
            # Add AI message
            st.session_state.messages.append(ai_message)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Rerun to update display
    st.rerun()

# Footer with sample comments
st.divider()
st.subheader("💡 Sample Comments to Try")

sample_comments = {
    "🤝 Lead": "I'm interested in your services. How can I get started?",
    "🙌 Praise": "Amazing product! Best purchase I've made this year!",
    "🚫 Spam": "Click here for free followers!!! www.spam.com",
    "❓ Question": "What are your business hours?",
    "😡 Complaint": "My order hasn't arrived and it's been 2 weeks!"
}

cols = st.columns(5)
for idx, (label, comment) in enumerate(sample_comments.items()):
    with cols[idx]:
        if st.button(label, use_container_width=True, disabled=not st.session_state.ai_initialized):
            st.session_state.comment_input = comment
            st.rerun()

# Model information
with st.expander("ℹ️ About Local AI Models"):
    st.markdown("""
    **Models Used:**
    - **Classification**: BART-large-MNLI (Facebook) - Zero-shot classification
    - **Text Generation**: GPT-2 Medium - Response generation
    
    **Advantages:**
    - ✅ No API key required
    - ✅ Works offline after initial download
    - ✅ Free to use
    - ✅ Privacy - data stays on your machine
    
    **Limitations:**
    - ⚠️ Slower than API-based models
    - ⚠️ Less sophisticated responses than GPT-3.5/4
    - ⚠️ Requires ~1GB disk space for models
    """)

# Requirements info
with st.expander("📦 Installation Requirements"):
    st.code("""
# Install required packages:
pip install transformers torch streamlit

# For GPU acceleration (optional):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    """, language="bash")