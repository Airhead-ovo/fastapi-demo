def split_text(
  text: str,
  chunk_size=500,
  overlap=50
):
  if overlap >= chunk_size:
    raise ValueError("overlap must be smaller than chunk_size")
  chunks = []
  start = 0
  while start < len(text):
    chunk = text[start: start + chunk_size]
    start += chunk_size - overlap
    chunks.append(chunk)

  return chunks
