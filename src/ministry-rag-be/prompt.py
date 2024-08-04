from chromadb import QueryResult


def generate_prompt(question: str, context: QueryResult) -> str:
    prompt = f'''You are a chatbot with the task of answering the user's questions with only the context information provided.
    All the context information comes from a set of spoken messages compiled into the Life-Study of the Bible by Witness Lee.
    The user asks: "{question}"
    The context is: "{context['documents'][0]}"
    '''
    return prompt