import google.generativeai as genai
genai.configure(api_key='your_key')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello world")
print(response.text)