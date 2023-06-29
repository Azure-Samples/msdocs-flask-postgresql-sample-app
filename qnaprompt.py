# import os
# import openai
# import load


# def prompt(input):
#     openai.api_key = os.getenv("OPENAI_API_KEY")
#     openai.api_base = os.getenv("OPENAI_ENDPOINT")
#     openai.api_type = os.getenv("OPENAI_TYPE")
#     openai.api_version = os.getenv("OPENAI_VERSION")


#     response = openai.Completion.create(
#         engine=os.getenv("OPENAI_DEPLOYMENT"),
#         prompt="Reset previous conversations and context. This is a question : 'What is the size of the sun?' \nPlease find an answer into the paragraph below and summarize it in one sentence.\n\nThe Sun is the star at the center of the Solar System. It is a nearly perfect ball of hot plasma, heated to incandescence by nuclear fusion reactions in its core. The Sun radiates this energy mainly as light, ultraviolet, and infrared radiation, and is the most important source of energy for life on Earth. The Sun's radius is about 695,000 kilometers (432,000 miles), or 109 times that of Earth. Its mass is about 330,000 times that of Earth, comprising about 99.86% of the total mass of the Solar System.",
#         temperature=0.3,
#         max_tokens=1000,
#         top_p=1,
#         frequency_penalty=0,
#         presence_penalty=0,
#         stop=None)
        
#     print('qna_prompt')
#     return 'Hello world'

    # prompt='What is the color of the sky?'
    # person_type = 'child'

    # # Send a completion call to generate an answer
    # print('Sending a test completion job')



    # # output_text = response['choices'][0]['message']['content']
    # print("ChatGPT API reply:", response)