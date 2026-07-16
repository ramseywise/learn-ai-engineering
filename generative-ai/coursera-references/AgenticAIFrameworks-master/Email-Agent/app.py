"""
Streamlit Course Assistant Chatbot with Email Integration
"""

import streamlit as st
import os
from dotenv import load_dotenv
from helper_functions.gmail_auth import init_gmail_service
from agent import run_agent, set_gmail_service
from course_data import COURSE_INFO
import tempfile

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Course Assistant",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'gmail_service' not in st.session_state:
    st.session_state.gmail_service = None

if 'service_initialized' not in st.session_state:
    st.session_state.service_initialized = False

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []


def initialize_gmail_service():
    """Initialize Gmail service"""
    try:
        client_file = 'client_secrets.json'
        if not os.path.exists(client_file):
            st.error("⚠️ client_secrets.json not found. Please add it to the project directory.")
            return None
        
        service = init_gmail_service(client_file)
        return service
    except Exception as e:
        st.error(f"Error initializing Gmail service: {str(e)}")
        return None


def save_uploaded_files(uploaded_files):
    """Save uploaded files to temporary directory and return paths"""
    if not uploaded_files:
        return None
    
    temp_paths = []
    for uploaded_file in uploaded_files:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_paths.append(tmp_file.name)
    
    return temp_paths


def main():
    
    # Debug: Print session state info
    print(f"\n{'='*80}")
    print(f" STREAMLIT SESSION STATE DEBUG")
    print(f"   Messages count: {len(st.session_state.messages)}")
    print(f"   Conversation history count: {len(st.session_state.conversation_history)}")
    print(f"   Service initialized: {st.session_state.service_initialized}")
    print(f"{'='*80}\n")
    
    # Header
    st.title("🎓 Course Assistant Chatbot")
    st.markdown(f"### {COURSE_INFO['course_code']} - {COURSE_INFO['course_name']}")
    st.markdown(f"**Professor:** {COURSE_INFO['professor']['name']} | **Semester:** {COURSE_INFO['semester']}")
    st.divider()
    
    # Sidebar with course info
    with st.sidebar:
        st.header(" Course Info")
        
        with st.expander(" Schedule", expanded=False):
            st.write(f"**Lectures:** {COURSE_INFO['schedule']['lecture_times']}")
            st.write(f"**Location:** {COURSE_INFO['schedule']['location']}")
            st.write(f"**Lab:** {COURSE_INFO['schedule']['lab_sessions']}")
        
        with st.expander(" Important Dates", expanded=False):
            for date_name, date_value in COURSE_INFO['important_dates'].items():
                st.write(f"**{date_name.replace('_', ' ').title()}:** {date_value}")
        
        with st.expander(" Office Hours", expanded=False):
            st.write(f"**Location:** {COURSE_INFO['professor']['office']}")
            st.write(f"**Hours:** {COURSE_INFO['professor']['office_hours']}")
        
        st.divider()
        
        # Gmail service status
        st.header(" Email Service")
        if not st.session_state.service_initialized:
            if st.button("Initialize Email Service", type="primary"):
                with st.spinner("Initializing Gmail service..."):
                    service = initialize_gmail_service()
                    if service:
                        st.session_state.gmail_service = service
                        set_gmail_service(service)
                        st.session_state.service_initialized = True
                        st.success("✅ Email service initialized!")
                        st.rerun()
        else:
            st.success("✅ Email service active")
            if st.button("Reinitialize Service"):
                st.session_state.service_initialized = False
                st.rerun()
        
        st.divider()
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
    
    # Main chat interface
    st.header("💬 Ask me anything about the course!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "files" in message and message["files"]:
                st.caption(f"📎 Attached: {', '.join(message['files'])}")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "📎 Attach files (optional - will be included if you send an email)",
        accept_multiple_files=True,
        help="Upload any documents you want to attach to your email to the professor"
    )
    
    # Display uploaded files
    if uploaded_files:
        st.info(f" {len(uploaded_files)} file(s) ready to attach: {', '.join([f.name for f in uploaded_files])}")
    
    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        print(f"\n NEW MESSAGE RECEIVED: {prompt}")
        print(f" Current conversation history before adding: {len(st.session_state.conversation_history)} messages")
        
        # Add user message to chat
        file_names = [f.name for f in uploaded_files] if uploaded_files else []
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "files": file_names
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            if file_names:
                st.caption(f" Attached: {', '.join(file_names)}")
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Save uploaded files if any
                    temp_file_paths = None
                    if uploaded_files:
                        temp_file_paths = save_uploaded_files(uploaded_files)
                    
                    # Initialize service if sending email and not initialized
                    if not st.session_state.service_initialized:
                        if "email" in prompt.lower() or "send" in prompt.lower():
                            service = initialize_gmail_service()
                            if service:
                                st.session_state.gmail_service = service
                                set_gmail_service(service)
                                st.session_state.service_initialized = True
                    
                    print(f" Calling run_agent with history of {len(st.session_state.conversation_history)} messages")
                    
                    # Run agent with conversation history
                    try:
                        response = run_agent(
                            prompt, 
                            temp_file_paths,
                            conversation_history=st.session_state.conversation_history
                        )
                        print(f" Got response: {response[:100]}...")
                    except Exception as agent_error:
                        print(f"⚠️ Agent error (checking if email was sent): {agent_error}")
                        # Check if it's the tool message error but email was actually sent
                        error_str = str(agent_error)
                        if "tool" in error_str.lower() and "Email successfully sent" in str(agent_error):
                            response = "✅ Email successfully sent to Professor "
                            print("✅ Recovered: Email was sent successfully despite error")
                        else:
                            raise  # Re-raise if it's a different error
                    
                    # Clean up temp files
                    if temp_file_paths:
                        for temp_path in temp_file_paths:
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                    
                    st.markdown(response)
                    
                    # Show success notification if email was sent
                    if "✅ Email successfully sent" in response:
                        st.success("📧 Email has been sent to the professor!", icon="✅")
                    
                    # Add to conversation history AFTER getting response
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": prompt
                    })
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    print(f" Conversation history after adding: {len(st.session_state.conversation_history)} messages")
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    print(f"❌ ERROR: {e}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Welcome message if no messages
    if not st.session_state.messages:
        st.info("""
        
        
        **Try asking:**
        - "When is the final exam?"
        - "What are the office hours?"
        - "Tell me about the grading policy"
        - "Send an email to the professor about my question"
        """)


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error(" OPENAI_API_KEY not found in environment variables. Please add it to your .env file.")
        st.stop()
    
    main()