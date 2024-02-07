import openai
import random
import time

openai.api_key = "your apikey"

head_breadth = "I want you to act as a Training Data Creator for Aspect Sentiment Triplet Extraction task. " \
         "Your goal is to draw inspiration from the #Given Training Data# to create five new training data. " \
         "These new training data must be comments about laptop. " \
         "These new training data should cover a rich variety of linguistic patterns, three sentiment polarities (positive, negative, neutral), complex sentence structures, and potentially ambiguous cases. "\
         +"Return directly the results without explanation or Note.\n#Given Training Data#:\n"
tail_breadth = "#New Training Data#:\n"

head_depth = "I want you to act as a advanced Training Data Rewriter for Aspect Sentiment Triplet Extraction task. " \
         "Your goal is to draw inspiration from the #Given Training Data# to rewrite a more complex version of #Given Training Data#. " \
         "You should increase the depth and breadth of #Given Training Data#. " \
         "The number of examples in #Rewritten Training Data# should be consistent with #Given Training Data#. Return directly the results without explanation or Note.\n#Given Training Data#:\n"
tail_depth = "#Rewritten Training Data#:\n"


with open("./14lap/seed_samples.txt", 'r', encoding='utf-8') as f:
    seed_samples = f.readlines()

for j in range(1000):
    selected_list = random.sample(seed_samples, 5)
    body = ""
    for index, example in enumerate(selected_list):
        body = body + str(index+1) + ". " + example
    if j % 2 == 0:
        question = head_breadth + body + tail_breadth
    else:
        question = head_depth + body + tail_depth
    print(question)
      # gpt-3.5-turbo
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": question}
        ],
        temperature=1.2,
        max_tokens=3000,
      )
    with open("./gpt_3.5_turbo_data.txt", 'a+', encoding='utf-8') as f:
        print(completion.choices[0].message["content"])
        f.write(completion.choices[0].message["content"] + "\n")
    time.sleep(random.randint(30, 50))
