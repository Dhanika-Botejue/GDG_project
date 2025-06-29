from datetime import date
import google.generativeai as genai
import PIL.Image
import json

# Authenticate
genai.configure(api_key="AIzaSyDVoG8-gIUOydy8gUUwNBKxSVmSO9-_jms")

def extract_tasks_from_image(image_path):
    # Load image using PIL
    image = PIL.Image.open(image_path)

    model = genai.GenerativeModel("gemini-1.5-flash")

    today = date.today().isoformat()

    prompt = f"""From the content I'm giving you (a screenshot), extract study tasks and return them in this exact JSON format:

[
  {{
    "subject": "Subject Name",
    "task": "What needs to be done",
    "due_date": "YYYY-MM-DD",
    "reminder": true,  // true if it's due today, else false
    "completed": false
  }},
  ...
]

Make sure:
- Use today's date as {today} to determine if `reminder` should be true.
- Always set "completed" to false.
- Only include tasks that have a clear due date.
- Keep task descriptions short but clear.

Here is the content:"""

    response = model.generate_content([prompt, image])

    raw_text = response.text.strip()

    # Remove ```json ... ``` markdown if present
    if raw_text.startswith("```") and raw_text.endswith("```"):
        raw_text = "\n".join(raw_text.split("\n")[1:-1])  # removes first and last lines


    try:
        return json.loads(raw_text)
    except Exception as e:
        print("Failed to parse JSON:", e)
        return []
