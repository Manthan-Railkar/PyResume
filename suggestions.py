import google.generativeai as Genai 
Api_key="" 
Genai.configure(api_key=Api_key) 
model = Genai.GenerativeModel("gemini-2.0-flash") 

chat = model.start_chat()