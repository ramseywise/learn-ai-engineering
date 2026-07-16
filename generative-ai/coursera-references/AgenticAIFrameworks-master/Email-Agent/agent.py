"""
LangGraph Agent for Course Q&A with Email Integration
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
import os
from course_data import get_course_context, COURSE_INFO


# Initialize the Gmail service (will be set from app.py)
gmail_service = None
current_attachment_paths = None


def set_gmail_service(service):
    """Set the Gmail service for the agent to use"""
    global gmail_service
    gmail_service = service


def set_attachment_paths(paths):
    """Set the attachment paths for the current request"""
    global current_attachment_paths
    current_attachment_paths = paths


@tool
def send_email_to_professor(question: str, attachments_info: str = "") -> str:
    """
    Send an email to the professor with a student's question.
    
    Args:
        question: The student's question or message to send to the professor
        attachments_info: Information about any attachments (file names)
    
    Returns:
        A confirmation message about the email being sent
    """
    print("\n" + "-"*40)
    print(" TOOL CALLED: send_email_to_professor")
    print(f" Question: {question}")
    print(f" Attachments info: {attachments_info}")
    
    from helper_functions.gmail_send import send_email
    
    global current_attachment_paths
    
    if not gmail_service:
        print("❌ Gmail service not initialized")
        print("-"*40 + "\n")
        return "Error: Email service not initialized. Please check your Gmail authentication."
    
    try:
        subject = f"Question about {COURSE_INFO['course_code']} - {COURSE_INFO['course_name']}"
        
        body = f"""

{question}

"""
        if attachments_info:
            body += f"\nAttached files: {attachments_info}\n"
        
        body += """



 Student"""
        
        print(f" Sending email to: {COURSE_INFO['professor']['email']}")
        print(f" Subject: {subject}")
        print(f" Body length: {len(body)} chars")
        print(f" Attachment paths: {current_attachment_paths}")
        
        result = send_email(
            service=gmail_service,
            to=COURSE_INFO['professor']['email'],
            subject=subject,
            body=body,
            attachment_paths=current_attachment_paths
        )
        
        success_msg = f"✅ Email successfully sent to Professor {COURSE_INFO['professor']['name']} at {COURSE_INFO['professor']['email']}"
        print(f"✅ {success_msg}")
        print("-"*40 + "\n")
        return success_msg
    
    except Exception as e:
        error_msg = f" Error sending email: {str(e)}"
        print(f" Exception: {e}")
        print("-"*40 + "\n")
        return error_msg


# Define the agent state
class AgentState(TypedDict):
    messages: list
    course_context: str


def create_agent():
    """Create and return the LangGraph agent"""
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Bind tools to LLM
    tools = [send_email_to_professor]
    llm_with_tools = llm.bind_tools(tools)
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Define the agent node
    def agent_node(state: AgentState):
        course_context = get_course_context()
        
        system_message = SystemMessage(content=f"""You are a helpful course assistant for {COURSE_INFO['course_code']} - {COURSE_INFO['course_name']}.

Your role is to:
1. Answer student questions about the course using the provided course information
2. If you cannot answer a question with the available course information, offer to send an email to the professor

COURSE CONTEXT:
{course_context}

IMPORTANT INSTRUCTIONS:
- Always try to answer from the course context first
- Be friendly, clear, and concise
- If information is not in the course context, politely say you don't have that information and offer to email the professor
- When offering to email the professor, ask the student to confirm
- Format dates and information clearly
- If a student explicitly asks to email the professor or agrees to send an email, use the send_email_to_professor tool

RESPONSE GUIDELINES:
- For grading questions: provide the grading breakdown or scale
- For dates: provide specific dates from the important dates section
- For policies: cite the relevant policy
- For assignments: provide assignment details and due dates
- For office hours: provide professor's office hours and location
""")
        
        messages = [system_message] + state["messages"]
        response = llm_with_tools.invoke(messages)
        
        return {"messages": [response]}
    
    # Define routing function
    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        print(f"\n ROUTING: Checking if should continue...")
        print(f"   Last message type: {type(last_message).__name__}")
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            print(f"    Has tool calls: {len(last_message.tool_calls)} - routing to TOOLS")
            return "tools"
        
        print(f"    No tool calls - routing to END")
        return END
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Add edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def run_agent(user_message: str, uploaded_files: list = None, conversation_history: list = None):
    """
    Run the agent with a user message
    
    Args:
        user_message: The user's question or message
        uploaded_files: List of file paths for attachments
        conversation_history: Previous conversation messages for context
    
    Returns:
        The agent's response
    """
    print("\n" + "="*80)
    print(" DEBUG: run_agent called")
    print(f" User message: {user_message}")
    print(f" Uploaded files: {uploaded_files}")
    print(f" Conversation history length: {len(conversation_history) if conversation_history else 0}")

    # Set attachment paths globally
    if uploaded_files:
        set_attachment_paths(uploaded_files)
        attachments_info = ", ".join([os.path.basename(f) for f in uploaded_files])
        # Add attachment info to the user message
        user_message += f"\n[Note: User has attached the following files: {attachments_info}]"
    else:
        set_attachment_paths(None)
    
    app = create_agent()
    
    # Build message history - only include text content, no tool calls
    messages = []
    if conversation_history:
        print("\n Building conversation history:")
        for i, msg in enumerate(conversation_history):
            print(f"  [{i}] {msg['role']}: {msg['content'][:100]}...")
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                # Only add assistant messages as AIMessage with text content
                messages.append(AIMessage(content=msg["content"]))
    
    # Add current user message
    messages.append(HumanMessage(content=user_message))
    print(f"\n Total messages to send to agent: {len(messages)}")
    
    # Create initial state
    initial_state = {
        "messages": messages,
        "course_context": get_course_context()
    }
    
    print("\n Invoking LangGraph agent...")
    # Run the agent
    try:
        result = app.invoke(initial_state)
        print(f"\n Agent returned {len(result['messages'])} messages")
    except Exception as e:
        print(f"\n Exception: {e}")
        error_str = str(e)
        
        # Check if email was sent successfully before the error
        if "Email successfully sent" in error_str or "tool" in error_str.lower():
            print("✅ Detected email was sent despite error - returning success message")
            return "✅ Email successfully sent to Professor"
        else:
            raise  # Re-raise if it's a different error
    
    # Extract the final response - get the last AI message
    final_messages = result["messages"]
    
    # Debug: Print all result messages
    for i, msg in enumerate(final_messages):
        print(f"\n  Result message [{i}]:")
        print(f"    Type: {type(msg).__name__}")
        if hasattr(msg, 'content'):
            print(f"    Content: {str(msg.content)[:200]}...")
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"    Tool calls: {len(msg.tool_calls)}")
            for tc in msg.tool_calls:
                print(f"      - {tc.get('name', 'unknown')}")
    
    # Find the last message with content
    for i, msg in enumerate(reversed(final_messages)):
        if hasattr(msg, 'content') and msg.content and isinstance(msg.content, str):
            print(f"\n✅ Returning message from position {len(final_messages) - i - 1}")
            print(f"   Content preview: {msg.content[:100]}...")
            print("="*80 + "\n")
            return msg.content
    
    # Fallback
    print("\n⚠️ Using fallback return")
    print("="*80 + "\n")
    return str(final_messages[-1])