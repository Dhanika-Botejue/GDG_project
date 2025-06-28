from datetime import date
import google.generativeai as genai
import PIL.Image

# Authenticate
genai.configure(api_key="AIzaSyDVoG8-gIUOydy8gUUwNBKxSVmSO9-_jms")

# Load image using PIL
image = PIL.Image.open(input("File path: "))  # replace with your image path

model = genai.GenerativeModel("gemini-1.5-flash")

today = date.today().isoformat()

prompt = f"""From the content I'm giving you (a screenshot or PDF), extract study tasks and return them in this exact JSON format:

[
  {{
    "subject": "Subject Name",
    "task": "What needs to be done",
    "due_date": "YYYY-MM-DD",
    "reminder": true  // true if it's due today, else false
  }},
  ...
]

Make sure:
- Use today's date as {today} to determine if `reminder` should be true.
- Only include tasks that have a clear due date.
- Keep task descriptions short but clear.

Here is the content:"""

response = model.generate_content([prompt, image])

# Print the response
print(response.text)
