"""
Utility functions for the medical chatbot
"""
import streamlit as st

class SessionManager:
    """Manages Streamlit session state"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "show_diagnosis" not in st.session_state:
            st.session_state.show_diagnosis = False
    
    @staticmethod
    def get_messages():
        """Get current chat messages"""
        return st.session_state.messages
    
    @staticmethod
    def add_message(role, content, image=None):
        """
        Add message to chat history
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            image: Optional PIL image
        """
        message = {"role": role, "content": content}
        if image is not None:
            message["image"] = image
        st.session_state.messages.append(message)
    
    @staticmethod
    def clear_messages():
        """Clear all messages"""
        st.session_state.messages = []
    
    @staticmethod
    def set_diagnosis_mode(show):
        """Set diagnosis mode state"""
        st.session_state.show_diagnosis = show
    
    @staticmethod
    def get_diagnosis_mode():
        """Get current diagnosis mode state"""
        return st.session_state.show_diagnosis

class ErrorHandler:
    """Handles error display and logging"""
    
    @staticmethod
    def display_error(message):
        """Display error message to user"""
        st.error(message)
    
    @staticmethod
    def display_success(message):
        """Display success message to user"""
        st.success(message)
    
    @staticmethod
    def display_info(message):
        """Display info message to user"""
        st.info(message)
    
    @staticmethod
    def display_warning(message):
        """Display warning message to user"""
        st.warning(message)