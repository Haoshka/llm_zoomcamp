import ingest
import json

from time import time

from groq import Groq

client = Groq()
# api_key=os.environ.get("GROQ_API_KEY")
index = ingest.load_index()


def search(query):
    boost = {
        'document type': 3.0,
        'description': 2.5,
        'issued by': 1.2,
        'used by': 1.0,
        'mode of transport': 0.8,
        'notes': 0.5
    }

    results = index.search(
        query=query,
        filter_dict={},  # optional filters later (e.g., mode='Sea')
        boost_dict=boost,
        num_results=5
    )

    return results


prompt_template = """
You're a freight forwarding specialist. Answer the QUESTION based on the provided shipping documents database.
Use only the facts from the KNOWLEDGE BASE when answering the QUESTION.

QUESTION: {question}

KNOWLEDGE BASE:
{context}
""".strip()

entry_template = """
document type: {document type}
description: {description}
issued by: {issued by}
used by: {used by}
mode of transport: {mode of transport}
notes: {notes}
""".strip()


def build_prompt(query, search_results):
    context = ""
    
    for doc in search_results:
        context = context + entry_template.format(**doc) + "\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


def llm(prompt, model="llama-3.3-70b-versatile"):
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    answer = response.choices[0].message.content

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return answer, token_stats


evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model="llama-3.3-70b-versatile")

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result, tokens


def calculate_openai_cost(model, tokens):
    openai_cost = 0

    if model == "llama-3.3-70b-versatile":
        openai_cost = (
            tokens["prompt_tokens"] * 0.00015 + tokens["completion_tokens"] * 0.0006
        ) / 1000
    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return openai_cost


# def rag(query, model='llama-3.3-70b-versatile'):
#     search_results = search(query)
#     prompt = build_prompt(query, search_results)
#     answer = llm(prompt, model=model)

#     answer_data = {
#     "answer": answer,
    # "model_used": model,
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
    # }

    # return answer_data



def rag(query, model="llama-3.3-70b-versatile"):
    t0 = time()

    search_results = search(query)
    prompt = build_prompt(query, search_results)
    answer, token_stats = llm(prompt, model=model)

    relevance, rel_token_stats = evaluate_relevance(query, answer)

    t1 = time()
    took = t1 - t0

    openai_cost_rag = calculate_openai_cost(model, token_stats)
    openai_cost_eval = calculate_openai_cost(model, rel_token_stats)

    openai_cost = openai_cost_rag + openai_cost_eval

    answer_data = {
        "answer": answer,
        "model_used": model,
        "response_time": took,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get(
            "Explanation", "Failed to parse evaluation"
        ),
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],
        "openai_cost": openai_cost,
    }

    return answer_data
