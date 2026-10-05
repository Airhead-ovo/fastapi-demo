import dashscope
def get_embedding(text: str) -> list[float]:
  response = dashscope.TextEmbedding.call(
    model="text-embedding-v4",
    input=text,
    dimension=1024
  )
  if response.status_code != 200:
    raise RuntimeError(
      f"Embedding failed: {response.message}"
    )
  embedding = response.output["embeddings"][0]["embedding"]

  return embedding

