# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# # Check both possible spellings
# api_key = os.getenv("BREVO_API_KEY") or os.getenv("BERVO_API_KEY")
# sender_email = os.getenv("BREVO_SENDER_EMAIL", "smoiz38021@gmail.com")
# recipient_email = "smoiz38021@gmail.com"

# print(f"Loaded API Key: {api_key[:12]}..." if api_key else "API Key NOT found!")
# print(f"Sender Email: {sender_email}")

# url = "https://api.brevo.com/v3/smtp/email"
# headers = {
#     "accept": "application/json",
#     "api-key": api_key,
#     "content-type": "application/json"
# }
# payload = {
#     "sender": {"name": "Bug Diagnosis Platform", "email": sender_email},
#     "to": [{"email": recipient_email}],
#     "subject": "Test Verification Email",
#     "htmlContent": "<html><body><h3>Brevo API is working perfectly!</h3></body></html>"
# }

# response = requests.post(url, json=payload, headers=headers)
# print(f"Status Code: {response.status_code}")
# print(f"Response: {response.text}")

import os
import resend
from dotenv import load_dotenv

load_dotenv()


resend.api_key =os.getenv("Resend_API") 

params = {
    "from": "Bug Platform <onboarding@resend.dev>",  # Free testing sender
    "to": ["smoiz38021@gmail.com"],
    "subject": "Action Required: Verify Fix Outcome",
    "html": "<h3>Defect Verification Required</h3><p>Please review your pending bug tickets.</p>",
}

response = resend.Emails.send(params)
print(response)