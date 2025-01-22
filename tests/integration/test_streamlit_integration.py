import unittest
import streamlit as st
from streamlit.testing.v1 import AppTest
from core.modes.mode_manager import ModeManager, Mode
from app.components.file_uploader import FileUploader
from app.components.chat_interface import ChatInterface

class TestStreamlitIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_config = "test_config.json"
        cls.mode_manager = ModeManager(cls.test_config)
        cls.at = AppTest.from_file("app/main.py")
    
    def setUp(self):
        """Reset state before each test"""
        self.mode_manager.switch_mode(Mode.PRIVATE)
        if 'chat_history' in st.session_state:
            del st.session_state['chat_history']
    
    def test_mode_switch_ui(self):
        """Test mode switching through UI"""
        # Find the mode switch toggle
        mode_switch = self.at.select("mode_switch")
        self.assertIsNotNone(mode_switch)
        
        # Test switching to public mode
        mode_switch.click()
        self.assertEqual(self.mode_manager.get_current_mode(), Mode.PUBLIC)
        
        # Verify UI updates
        status_text = self.at.select("mode_status").value
        self.assertIn("PUBLIC", status_text)
    
    def test_file_upload_integration(self):
        """Test file upload functionality"""
        # Prepare test file
        test_content = b"Test medical document content"
        file_uploader = self.at.select("pdf_uploader")
        
        # Upload file
        file_uploader.upload("test.pdf", test_content)
        
        # Verify file processing status
        status = self.at.select("upload_status").value
        self.assertIn("Success", status)
        
        # Verify file appears in the file list
        file_list = self.at.select("uploaded_files").value
        self.assertIn("test.pdf", file_list)
    
    def test_chat_interface_integration(self):
        """Test chat interface with backend integration"""
        # Initialize chat interface
        chat = ChatInterface()
        
        # Send test message
        chat.send_message("What are the symptoms of diabetes?")
        
        # Verify response
        chat_history = st.session_state.get('chat_history', [])
        self.assertTrue(len(chat_history) >= 2)  # Question and answer
        
        # Verify mode-specific behavior
        self.mode_manager.switch_mode(Mode.PUBLIC)
        chat.send_message("Show me public resources about diabetes")
        
        # Check if response includes public resources
        latest_response = st.session_state['chat_history'][-1]
        self.assertIn("public", latest_response.lower())
    
    def test_error_handling_ui(self):
        """Test UI error handling"""
        # Test invalid file upload
        file_uploader = self.at.select("pdf_uploader")
        file_uploader.upload("invalid.txt", b"Invalid content")
        
        # Verify error message
        error_message = self.at.select("error_message").value
        self.assertIn("PDF", error_message)
        
        # Test chat interface error handling
        chat = ChatInterface()
        chat.send_message("")  # Empty message
        
        error_display = self.at.select("chat_error").value
        self.assertIn("empty", error_display.lower())

if __name__ == '__main__':
    unittest.main()