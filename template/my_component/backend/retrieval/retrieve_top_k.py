import replicate
import streamlit as st
from scipy.spatial import distance


@st.cache_data
def get_embedding(text):
    embed = replicate.run(
        "replicate/"
        "all-mpnet-base-v2"
        ":b6b7585c9640cd7a9572c6e129c9549d79c9c31f0d3fdce7baac7c67ca38f305",
        input={
            "text": text
        }
    )
    return embed[0]['embedding']


def retrieve_top_k(query, docs, k):
    query_embedding = get_embedding(query)
    doc_embeddings = [get_embedding(doc) for doc in docs]
    cos_distances = [distance.cosine(docs_emb, query_embedding) for docs_emb in doc_embeddings]
    zipped = zip(docs, cos_distances)
    sorted_docs = sorted(zipped, key=lambda x: x[1])
    return [d[0] for d in sorted_docs]
