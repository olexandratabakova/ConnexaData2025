from ollama import chat
from utils.schemas.template_schema import Tips
from utils.schemas.relation_schema import RelationList

model = "qwen3:latest"


def template_request(user_request):
    prompt = (
        f'''Fill in the fields as requested by the user. output a JSON object with:
        entities_of_interest: [e.g. "company", "person"]
        relationship_types: [e.g. "leadership", "influence"]
        keywords: list of up to 5 important keywords for the topic.
        user's request: {user_request}
'''
    )

    response = chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        format=Tips.model_json_schema()
    )
    return Tips.model_validate_json(response.message.content)


def request(user_text, entities_of_interest, relationship_types, keywords):
    prompt = (
        f'''You are an information extraction system.

        Task: From the provided text, extract all relations that match the user's intent.

        Entities: {entities_of_interest}  
        Relation types: {relationship_types}  
        Keywords: {keywords}  

        Output JSON fields:  
        object1, object2, relation_type, polarity, keywords  

        Text: {user_text}
        ''')

    response = chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        format=RelationList.model_json_schema()
    )
    return RelationList.model_validate_json(response.message.content)
