from groq import Groq
import template  # Import template
import os

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("The 'GROQ_API_KEY' environment variable is not set or not found.")

client = Groq(api_key=api_key)

def chat_completion(user_message):
    user_message = user_message[0]['content'] if isinstance(user_message, list) and 'content' in user_message[0] else user_message

    stream = client.chat.completions.create(
        messages=[
            # System message with role instruction
            {
                "role": "system",
                "content": template.CEO,  # Use the instruction from template
            },
            # User message
            {
                "role": "user",
                "content": user_message,
            }
        ],
        model="mixtral-8x7b-32768",  # Model
        temperature=0.5,  # Optionals
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=True,
    )

    # Get the completion
    response_text = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content

    return response_text  # This should return 'response_text', not 'response_text1'
