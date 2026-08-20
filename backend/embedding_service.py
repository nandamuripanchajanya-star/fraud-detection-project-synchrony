from fastembed import TextEmbedding


MODEL_NAME = "BAAI/bge-small-en-v1.5"

_model = TextEmbedding(
    model_name=MODEL_NAME
)


def generate_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    embedding = next(
        _model.embed([text])
    )

    return embedding.tolist()