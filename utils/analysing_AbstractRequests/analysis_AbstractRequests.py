from utils.schemas.template_schema import Tips
from utils.schemas.relation_schema import RelationList
from config_keys import api_groq_key, api_openai_key
from groq import Groq
from openai import OpenAI

# Клієнти для різних моделей
client_groq = Groq(api_key=api_groq_key)
client_openai = OpenAI(api_key=api_openai_key)

# Модель за замовчуванням для генерації шаблонів
default_model = "qwen3:latest"


def get_client(model):
    """Повертає клієнта для вибраної моделі"""
    if model == "llama-3.3-70b-versatile":
        return client_groq
    elif model == "qwen3:latest":
        # Для Ollama моделей використовуємо інший підхід
        return "ollama"
    else:
        raise ValueError(f"Unsupported model: {model}")


def template_request(user_request):
    """Генерація шаблону з фіксованою моделлю"""
    prompt = (
        f'''Fill in the fields as requested by the user. output a JSON object with:
        entities_of_interest: [e.g. "company", "person"]
        relationship_types: [e.g. "leadership", "influence"]
        keywords: list of up to 5 important keywords for the topic.
        user's request: {user_request}
'''
    )

    # Для генерації шаблонів використовуємо Ollama
    from ollama import chat

    response = chat(
        model=default_model,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        format=Tips.model_json_schema()
    )
    return Tips.model_validate_json(response.message.content)


def request(user_text, entities_of_interest, relationship_types, keywords, selected_model):
    """Аналіз тексту з вибраною моделлю"""
    prompt = (
        f'''You are an information extraction system.

        Task: From the provided text, extract all relations that match the user's intent.

        Entities: {entities_of_interest}  
        Relation types: {relationship_types}  
        Keywords: {keywords}  

        Output JSON fields:  
        object1, object2, relation_type, polarity (positive or neutral or negative), keywords  

        Text: {user_text}
        ''')

    client_type = get_client(selected_model)

    if client_type == "ollama":
        # Використовуємо Ollama для qwen3:latest
        from ollama import chat

        response = chat(
            model=selected_model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            format=RelationList.model_json_schema()
        )
        return RelationList.model_validate_json(response.message.content)

    else:
        # Використовуємо Groq або OpenAI
        chat_completion = client_type.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=selected_model,
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=4096,
        )

        result_text = chat_completion.choices[0].message.content.strip()
        return RelationList.model_validate_json(result_text)