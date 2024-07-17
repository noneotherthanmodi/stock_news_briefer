import ollama

response_text = ollama.chat(
    model='llama3',
    messages=[
        {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
    ],
  )

# print(dict(response_text).keys)
# print(response_text)


print(response_text['message']['content'])
