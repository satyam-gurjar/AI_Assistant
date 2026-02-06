================================================================================
                         AI ASSISTANT - Quick Start Guide
================================================================================

Thank you for downloading AI Assistant!

--------------------------------------------------------------------------------
FIRST TIME SETUP (REQUIRED)
--------------------------------------------------------------------------------

Before you can run AI Assistant, you need to configure it:

1. FIND THE FILE: ".env.example" (it's in the same folder as this README)

2. RENAME IT TO: ".env"
   - Windows: Right-click → Rename → Change to ".env"
   - Mac/Linux: mv .env.example .env

3. EDIT THE FILE: Open ".env" with a text editor and change:
   
   API_BASE_URL=http://localhost:5000/api
   
   Replace "http://localhost:5000/api" with your actual AI server URL.
   Example: http://192.168.1.100:8080/api

4. SAVE THE FILE

5. RUN AI ASSISTANT:
   - Windows: Double-click AIAssistant.exe
   - Mac: Double-click AIAssistant.app
   - Linux: Run ./AIAssistant in terminal

--------------------------------------------------------------------------------
WHAT IS THE API_BASE_URL?
--------------------------------------------------------------------------------

AI Assistant connects to an AI backend server to process your requests.
You need to have an AI server running (or access to one) and know its URL.

If you don't have a server yet, you need to:
- Set up your own AI backend server
- Get access credentials to an existing server
- Configure the server URL in the .env file

--------------------------------------------------------------------------------
TROUBLESHOOTING
--------------------------------------------------------------------------------

Problem: Nothing happens when I double-click the application
Solution: You probably haven't created the .env file yet. See FIRST TIME SETUP.

Problem: Application shows "Connection Error" or "Cannot connect to server"
Solutions:
  - Check that your server is running
  - Verify the API_BASE_URL in .env is correct
  - Check your firewall/network settings
  - Make sure the server URL is accessible from your computer

Problem: Application window is blank or crashes
Solutions:
  - Check that .env file exists and is properly formatted
  - Look at the logs/ai_assistant.log file for error details
  - Make sure all required fields in .env are filled out

--------------------------------------------------------------------------------
SUPPORT
--------------------------------------------------------------------------------

For more help, visit:
https://github.com/satyam-gurjar/AI_Assistant

--------------------------------------------------------------------------------

Enjoy using AI Assistant! 🚀
