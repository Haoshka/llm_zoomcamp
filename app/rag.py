import ingest
import json

from time import time

from groq import Groq



client = Groq() 
# api_key=os.environ.get("GROQ_API_KEY")s
index = ingest.load_index()

def search(query):
    boost = {
        'exercise_name': 2.11,
        'type_of_activity': 1.46,
        'type_of_equipment': 0.65,
        'body_part': 2.65,
        'type': 1.31,
        'muscle_groups_activated': 2.54,
        'instructions': 0.74
    }

    results = index.search(
        query=query, filter_dict={}, boost_dict=boost, num_results=10
    )

    return results



prompt_template = """
You're a fitness instructor. Answer the QUESTION based on the CONTEXT from our exercises database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

entry_template = """
exercise_name: {exercise_name}
type_of_activity: {type_of_activity}
type_of_equipment: {type_of_equipment}
body_part: {body_part}
type: {type}
muscle_groups_activated: {muscle_groups_activated}
instructions: {instructions}
""".strip()

def build_prompt(query, search_results):
    context = ""

    for doc in search_results:
        context = context + entry_template.format(**doc) + "\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


# def llm(prompt, model="gpt-4o-mini"):
#     response = client.chat.completions.create(
#         model=model, messages=[{"role": "user", "content": prompt}]
#     )

#     answer = response.choices[0].message.content

#     token_stats = {
#         "prompt_tokens": response.usage.prompt_tokens,
#         "completion_tokens": response.usage.completion_tokens,
#         "total_tokens": response.usage.total_tokens,
#     }

#     return answer, token_stats



def llm(prompt, model="llama-3.3-70b-versatile"):
    response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=500,
)

    return response.choices[0].message.content


def rag(query, model='llama-3.3-70b-versatile'):
    search_results = search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt, model=model)

    answer_data = {
    "answer": answer,
    "model_used": model,
    #"response_time": took,
    #"relevance": relevance.get("Relevance", "UNKNOWN"),
    # "relevance_explanation": relevance.get(
    #     "Explanation", "Failed to parse evaluation"
    # ),
    # "prompt_tokens": token_stats["prompt_tokens"],
    # "completion_tokens": token_stats["completion_tokens"],
    # "total_tokens": token_stats["total_tokens"],
    # "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
    # "eval_completion_tokens": rel_token_stats["completion_tokens"],
    # "eval_total_tokens": rel_token_stats["total_tokens"],
    # "openai_cost": openai_cost,
    }

    return answer_data



# def rag(query, model="gpt-4o-mini"):
#     t0 = time()

#     search_results = search(query)
#     prompt = build_prompt(query, search_results)
#     answer, token_stats = llm(prompt, model=model)

#     relevance, rel_token_stats = evaluate_relevance(query, answer)

#     t1 = time()
#     took = t1 - t0

#     openai_cost_rag = calculate_openai_cost(model, token_stats)
#     openai_cost_eval = calculate_openai_cost(model, rel_token_stats)

#     openai_cost = openai_cost_rag + openai_cost_eval

#     answer_data = {
#         "answer": answer,
#         "model_used": model,
#         "response_time": took,
#         "relevance": relevance.get("Relevance", "UNKNOWN"),
#         "relevance_explanation": relevance.get(
#             "Explanation", "Failed to parse evaluation"
#         ),
#         "prompt_tokens": token_stats["prompt_tokens"],
#         "completion_tokens": token_stats["completion_tokens"],
#         "total_tokens": token_stats["total_tokens"],
#         "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
#         "eval_completion_tokens": rel_token_stats["completion_tokens"],
#         "eval_total_tokens": rel_token_stats["total_tokens"],
#         "openai_cost": openai_cost,
#     }

#     return answer_data
