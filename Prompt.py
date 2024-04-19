def search(self, user_query):
    embedding = create_embedding(user_query)
    result = self.query_vector_db(embedding)

    print("Sources:")
    for source in result['list_of_sources']:
        print(source)

    knowledge_base = "\n".join(result['list_of_knowledge_base'])

    # Ask the user query using chat prompt
    response = self.ask_chatgpt(knowledge_base, user_query)

    return {
        'sources': result['list_of_sources'],
        'response': response
    }
