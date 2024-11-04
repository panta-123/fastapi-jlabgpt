import logging

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder, PromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.components.generators.mistral import MistralChatGenerator
from haystack_integrations.components.retrievers.chroma import ChromaEmbeddingRetriever
from app.core.db.chromdb import document_store
from app.core.config import settings


logger = logging.getLogger(__name__)

def retrival(query: str):
    logging.info(query)
    logging.info(type(query))
    querying = Pipeline()

    # embedding model
    embedding_model_name = "intfloat/e5-large-v2"
    query_embedder = SentenceTransformersTextEmbedder(model = embedding_model_name, prefix="passage")
    querying.add_component("query_embedder", query_embedder)

    # retriever model
    querying.add_component("retriever", ChromaEmbeddingRetriever(document_store))

    # ranker model
    ranker = TransformersSimilarityRanker()
    ranker.warm_up()
    querying.add_component(instance=ranker, name="ranker")

    messages = [ChatMessage.from_user("Given the following information, answer the question. Context: {% for document in documents %}{{ document.content }}{% endfor %} Question: {{ query }}?")]
    querying.add_component(instance=ChatPromptBuilder(template=messages), name="prompt_builder")
    querying.add_component(instance=MistralChatGenerator(api_key=Secret.from_token(settings.MISTRAL_API_KEY), model="mistral-tiny", generation_kwargs = {"max_tokens" : 4096}, streaming_callback=print_streaming_chunk), name="llm") # generation_kwargs = {"temperature" : 0 - 0.9}


    # connect components
    querying.connect("query_embedder", "retriever")
    querying.connect("retriever.documents", "ranker.documents")
    querying.connect("ranker.documents", "prompt_builder.documents")
    querying.connect("prompt_builder.prompt", "llm.messages")
    

    #results = querying.run({ "query_embedder": {"text": query}, "retriever": { "top_k": 5}, "ranker": {"query": query, "top_k": 2} })
    response = querying.run({ "query_embedder": {"text": query}, "retriever": { "top_k": 5}, "ranker": {"query": query, "top_k": 2}, "prompt_builder": {"query": query}})
    def generate():
        response = querying.run({
            "query_embedder": {"text": query},
            "retriever": {"top_k": 5},
            "ranker": {"query": query, "top_k": 2},
            "prompt_builder": {"query": query}
        })
        for reply in response["llm"]["replies"]:
            if isinstance(reply, ChatMessage):
                yield reply.content
            else:
                yield reply
    return generate()


    #for d in results["ranker"]["documents"]:
    #    print(d.meta, d.score)

    #return results["ranker"]["documents"]
    #return response["llm"]["replies"]

"""
## Add prompt builder and connect context to prompt to LLM
rag_pipeline.add_component(instance=PromptBuilder(template=prompt_template), name="prompt_builder")
rag_pipeline.add_component(instance=OpenAIGenerator(model="gpt-4o"), name="llm")
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")
"""