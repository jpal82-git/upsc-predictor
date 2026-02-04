"""
UPSC MULTI-ANGLE PREDICTOR — STREAMLIT APP
============================================
"Chai pe Selection" — ₹15 mein 10 Questions

Deploy: streamlit.io → Connect GitHub → Done!

Author: Built with Claude
Version: 1.0
"""

import streamlit as st
import anthropic
import base64
from datetime import datetime
import json
import re

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="UPSC Predictor | ₹15 = 10 Questions",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS — Makes it look professional
# =============================================================================

st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 1rem 2rem;
    }
    
    /* Header styling */
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a365d;
        text-align: center;
        margin-bottom: 0;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #e53e3e;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    .chai-tagline {
        background: linear-gradient(135deg, #f6e05e 0%, #ed8936 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        text-align: center;
        margin: 1.5rem 0;
    }
    
    .chai-tagline h2 {
        color: #744210;
        margin: 0;
        font-size: 1.5rem;
    }
    
    /* Question cards */
    .question-card {
        background: #f7fafc;
        border-left: 4px solid #3182ce;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .mcq-card {
        border-left-color: #38a169;
    }
    
    .mains-card {
        border-left-color: #805ad5;
    }
    
    .trap-alert {
        background: #fff5f5;
        border: 1px solid #fc8181;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* Pricing cards */
    .pricing-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
        border-color: #3182ce;
    }
    
    .pricing-card.featured {
        border-color: #ed8936;
        background: #fffaf0;
    }
    
    .price-tag {
        font-size: 2rem;
        font-weight: 700;
        color: #2d3748;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #718096;
        font-size: 0.9rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if 'credits' not in st.session_state:
    st.session_state.credits = 2  # Free credits for trial

if 'query_history' not in st.session_state:
    st.session_state.query_history = []

if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0

# =============================================================================
# SIDEBAR — Credits & Pricing
# =============================================================================

with st.sidebar:
    st.markdown("## ☕ Your Credits")
    st.markdown(f"### **{st.session_state.credits}** queries left")
    
    if st.session_state.credits <= 1:
        st.warning("Running low! Add more credits below.")
    
    st.markdown("---")
    
    st.markdown("## 💰 Add Credits")
    
    # Pricing options
    st.markdown("""
    | Plan | Price | Credits |
    |------|-------|---------|
    | ☕ **Try** | ₹15 | 1 |
    | 📚 Starter | ₹149 | 10 |
    | 🎯 Pro | ₹499 | 40 |
    | 🏆 Premium | ₹899 | 80 |
    """)
    
    # Payment button (placeholder - connect to Razorpay)
    if st.button("🛒 Buy Credits", use_container_width=True):
        st.info("Payment integration coming soon! For now, email us at support@upscpredictor.com")
    
    st.markdown("---")
    
    st.markdown("## 📊 Your Stats")
    st.markdown(f"Total queries: **{st.session_state.total_queries}**")
    
    st.markdown("---")
    
    st.markdown("### 🔗 Quick Links")
    st.markdown("- [Sample Output (PDF)](#)")
    st.markdown("- [How it Works](#how-it-works)")
    st.markdown("- [Contact Us](#)")

# =============================================================================
# MAIN CONTENT — Hero Section
# =============================================================================

st.markdown('<h1 class="hero-title">UPSC Multi-Angle Predictor</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">One Topic → 10 Questions → 5 GS Papers</p>', unsafe_allow_html=True)

st.markdown("""
<div class="chai-tagline">
    <h2>☕ ₹15 = Price of One Chai = 10 UPSC Questions</h2>
    <p style="margin:0.5rem 0 0 0; color:#744210;">Skip the chai. Crack the exam.</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# INPUT SECTION — Text or Image
# =============================================================================

st.markdown("## 📝 Enter Today's News Topic")

input_method = st.radio(
    "Choose input method:",
    ["✍️ Type/Paste Topic", "📷 Upload Screenshot"],
    horizontal=True,
    label_visibility="collapsed"
)

topic_text = None
uploaded_image = None

if input_method == "✍️ Type/Paste Topic":
    topic_text = st.text_area(
        "Enter any current affairs topic or news headline:",
        placeholder="Example: Governor delays NEET bill in Tamil Nadu\nExample: India-China LAC disengagement\nExample: RBI keeps repo rate unchanged",
        height=100
    )
else:
    uploaded_image = st.file_uploader(
        "Upload a screenshot of news article:",
        type=['png', 'jpg', 'jpeg'],
        help="Screenshot from Hindu, Indian Express, PIB, or any news source"
    )
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Screenshot", use_container_width=True)

# Generate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_clicked = st.button(
        "🚀 Generate 10 Questions (Uses 1 Credit)",
        use_container_width=True,
        type="primary",
        disabled=(st.session_state.credits < 1)
    )

if st.session_state.credits < 1:
    st.error("⚠️ No credits left! Please add credits to continue.")

# =============================================================================
# QUESTION GENERATION LOGIC
# =============================================================================

def generate_questions(topic: str, image_data: bytes = None) -> str:
    """
    Call Claude API to generate UPSC questions.
    """
    
    # Get API key - works with both Streamlit Cloud and Hugging Face Spaces
    import os
    api_key = None
    
    # Try Streamlit secrets first
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass
    
    # Try environment variable (Hugging Face uses this)
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        st.error("API key not configured. Please add ANTHROPIC_API_KEY to secrets.")
        return None
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing API: {str(e)}")
        return None
    
    # Build the prompt
    system_prompt = """You are an expert UPSC question paper setter with 20+ years experience. 
You have deep knowledge of UPSC exam patterns from analyzing 1,472 Prelims and 417 Mains previous year questions.

Your task: Generate 10 high-quality UPSC practice questions from the given topic.

OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════
TOPIC DETECTION
═══════════════════════════════════════════════════════════════════════════════
Primary Topic: [Detected topic]
Subject: [Polity/Economy/History/Geography/Environment/Ethics/IR/Security]
Paper: [GS-I/GS-II/GS-III/GS-IV]

Cross-Subject Angles Identified:
1. [Angle 1] - [Subject] - [Connection to main topic]
2. [Angle 2] - [Subject] - [Connection to main topic]
3. [Angle 3] - [Subject] - [Connection to main topic]

═══════════════════════════════════════════════════════════════════════════════
SECTION A: MCQs (5 Questions)
═══════════════════════════════════════════════════════════════════════════════

MCQ 1: [Archetype: P-01/P-06/P-07]
[Question text with options a, b, c, d]

✅ Answer: [Correct option]
⚠️ Trap Applied: [T-XX: Name] — [How trap is embedded]
📖 Explanation: [Brief explanation]

[Repeat for MCQ 2-5, with at least 2 from cross-subject angles]

═══════════════════════════════════════════════════════════════════════════════
SECTION B: MAINS QUESTIONS (5 Questions)
═══════════════════════════════════════════════════════════════════════════════

MAINS 1:
📋 Archetype: [EVAL-PC-3D-H / AN-ST-4D-D / etc.]
📝 Question: [Full question text] (15 marks, 250 words)

📝 Answer Framework:
┌─ Introduction (30 words): [What to write]
├─ Body Para 1 (50 words): [What to cover]
├─ Body Para 2 (50 words): [What to cover]
├─ Body Para 3 (50 words): [What to cover]
├─ Body Para 4 (40 words): [What to cover]
└─ Conclusion (30 words): [How to end]

📌 Must-Include:
• [Key case/committee/article 1]
• [Key case/committee/article 2]
• [Key case/committee/article 3]

❌ Traps to Avoid:
• Don't [common mistake 1]
• Don't [common mistake 2]
✓ Conclude with: [Balanced conclusion approach]

[Repeat for MAINS 2-5, including Ethics case study if relevant]

═══════════════════════════════════════════════════════════════════════════════

IMPORTANT RULES:
1. MCQs must embed realistic UPSC traps (T-01: Absolute words, T-02: Institution swap, T-06: Constitutional claims, T-20: May vs Shall, T-29: AND connector trap)
2. Mains must have 4D archetype code and word allocation
3. At least 3 questions must be from cross-subject angles
4. Include one Ethics case study if topic allows
5. All must-includes should be real (actual cases, committees, articles)
6. Constitutional balance in conclusions — reforms not revolution
"""

    # Build message content
    if image_data:
        # Image input
        base64_image = base64.standard_b64encode(image_data).decode("utf-8")
        
        # Detect image type
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            media_type = "image/png"
        else:
            media_type = "image/jpeg"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": "Read this news screenshot and generate 10 UPSC practice questions based on the topic/content shown. Follow the exact output format specified."
                    }
                ]
            }
        ]
    else:
        # Text input
        messages = [
            {
                "role": "user",
                "content": f"Generate 10 UPSC practice questions for this topic:\n\n{topic}\n\nFollow the exact output format specified."
            }
        ]
    
    # Call Claude API
    try:
        with st.spinner("🧠 Analyzing topic and generating questions..."):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=6000,
                system=system_prompt,
                messages=messages
            )
        
        return response.content[0].text
    
    except anthropic.APIError as e:
        st.error(f"API Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def display_output(output: str):
    """
    Display the generated questions in a nice format.
    """
    
    st.markdown("---")
    st.markdown("## 📋 Generated Questions")
    
    # Display in a nice container
    st.markdown(f"""
    <div style="background: #f7fafc; padding: 1.5rem; border-radius: 10px; border: 1px solid #e2e8f0;">
        <pre style="white-space: pre-wrap; font-family: 'Segoe UI', sans-serif; font-size: 0.95rem; line-height: 1.6;">{output}</pre>
    </div>
    """, unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="📥 Download as Text File",
        data=output,
        file_name=f"upsc_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )


# =============================================================================
# HANDLE GENERATION
# =============================================================================

if generate_clicked:
    if input_method == "✍️ Type/Paste Topic":
        if not topic_text or len(topic_text.strip()) < 5:
            st.warning("Please enter a valid topic (at least 5 characters)")
        else:
            output = generate_questions(topic_text)
            if output:
                st.session_state.credits -= 1
                st.session_state.total_queries += 1
                st.session_state.query_history.append({
                    'topic': topic_text,
                    'timestamp': datetime.now().isoformat(),
                    'output': output[:500] + "..."  # Store preview
                })
                display_output(output)
                st.balloons()
    else:
        if not uploaded_image:
            st.warning("Please upload an image first")
        else:
            image_bytes = uploaded_image.read()
            output = generate_questions(None, image_bytes)
            if output:
                st.session_state.credits -= 1
                st.session_state.total_queries += 1
                st.session_state.query_history.append({
                    'topic': "Image Upload",
                    'timestamp': datetime.now().isoformat(),
                    'output': output[:500] + "..."
                })
                display_output(output)
                st.balloons()

# =============================================================================
# HOW IT WORKS SECTION
# =============================================================================

st.markdown("---")
st.markdown('<a name="how-it-works"></a>', unsafe_allow_html=True)
st.markdown("## 🎯 How It Works")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    ### 1️⃣ Input
    Type topic or upload news screenshot
    """)

with col2:
    st.markdown("""
    ### 2️⃣ Analysis
    AI detects subject + 3 cross-angles
    """)

with col3:
    st.markdown("""
    ### 3️⃣ Generation
    10 questions with traps & frameworks
    """)

with col4:
    st.markdown("""
    ### 4️⃣ Practice
    MCQs + Mains with answer guidance
    """)

# =============================================================================
# WHAT MAKES US DIFFERENT
# =============================================================================

st.markdown("---")
st.markdown("## ✨ Why This is Different")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ❌ Generic AI (ChatGPT/Gemini)
    - Single subject questions only
    - No exam trap awareness
    - Generic answer formats
    - Missing key elements
    - One-sided conclusions
    """)

with col2:
    st.markdown("""
    ### ✅ UPSC Predictor
    - **Multi-angle**: 5 GS papers from 1 topic
    - **32 traps**: Real UPSC patterns embedded
    - **4D Archetypes**: Proper answer structure
    - **Must-includes**: Cases, committees, articles
    - **Constitutional balance**: Examiner-approved framing
    """)

# =============================================================================
# SAMPLE OUTPUT PREVIEW
# =============================================================================

st.markdown("---")
st.markdown("## 📄 Sample Output Preview")

with st.expander("Click to see sample output for 'CEC Impeachment' topic"):
    st.markdown("""
    ```
    ═══════════════════════════════════════════════════════════════
    TOPIC DETECTION
    ═══════════════════════════════════════════════════════════════
    Primary Topic: Election Commission / CEC Removal
    Subject: Polity & Governance
    Paper: GS-II
    
    Cross-Subject Angles Identified:
    1. Historical Evolution - GS-I - T.N. Seshan era reforms
    2. Federalism - GS-II - Centre-State in EC appointments
    3. Institutional Ethics - GS-IV - Independence vs accountability
    
    ═══════════════════════════════════════════════════════════════
    SECTION A: MCQs
    ═══════════════════════════════════════════════════════════════
    
    MCQ 1: [Archetype: P-01]
    Consider the following statements about CEC removal:
    1. CEC can be removed only through impeachment
    2. Removal procedure is same as Supreme Court judge
    3. Grounds are incapacity and proved misbehavior
    
    Which is/are correct?
    (a) 1 and 2 only  (b) 2 and 3 only  
    (c) 1 and 3 only  (d) 1, 2 and 3
    
    ✅ Answer: (b) 2 and 3 only
    ⚠️ Trap: T-01 (Absolute Words) — "only through impeachment" is 
       imprecise. Constitution says "in like manner" as SC judge.
    
    [... 4 more MCQs ...]
    
    ═══════════════════════════════════════════════════════════════
    SECTION B: MAINS
    ═══════════════════════════════════════════════════════════════
    
    MAINS 1:
    📋 Archetype: EVAL-PC-3D-H
    📝 Question: Critically examine the appointment and removal 
       process of CEC. Has the 2023 Act addressed SC's concerns?
    
    📝 Answer Framework:
    ┌─ Introduction (30 words): Recent controversy context
    ├─ Constitutional Framework (40 words): Article 324
    ├─ SC Judgment Analysis (50 words): Anoop Baranwal case
    ├─ 2023 Act Evaluation (50 words): New process
    ├─ Critical Assessment (50 words): Both sides
    └─ Way Forward (30 words): Balanced reforms
    
    📌 Must-Include:
    • Article 324(2) and 324(5)
    • Anoop Baranwal vs UOI (2023)
    • T.N. Seshan tenure reference
    
    [... 4 more Mains questions ...]
    ```
    """)

# =============================================================================
# PRICING SECTION
# =============================================================================

st.markdown("---")
st.markdown("## 💰 Simple Pricing")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="pricing-card featured">
        <h3>☕ Try</h3>
        <p class="price-tag">₹15</p>
        <p>1 Query</p>
        <p><small>Price of one chai!</small></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="pricing-card">
        <h3>📚 Starter</h3>
        <p class="price-tag">₹149</p>
        <p>10 Queries</p>
        <p><small>₹14.90 each</small></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="pricing-card">
        <h3>🎯 Pro</h3>
        <p class="price-tag">₹499</p>
        <p>40 Queries</p>
        <p><small>₹12.48 each</small></p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="pricing-card">
        <h3>🏆 Premium</h3>
        <p class="price-tag">₹899</p>
        <p>80 Queries</p>
        <p><small>₹11.24 each</small></p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div class="footer">
    <p><strong>UPSC Multi-Angle Predictor</strong></p>
    <p>Built for serious aspirants who want an edge.</p>
    <p>Questions? Email: support@upscpredictor.com</p>
    <p style="margin-top: 1rem; font-size: 0.8rem;">
        ☕ Skip the chai. Crack the exam.
    </p>
</div>
""", unsafe_allow_html=True)
