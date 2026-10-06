def split_text(
  text: str,
  chunk_size=500,
  overlap=50
):
  # 优先保持段落完整；
  # 超长段落优先按句子拆；
  # 只有单句本身超过 chunk_size 时，才使用原来的固定长度 + overlap 兜底。
  if overlap >= chunk_size:
    raise ValueError("overlap must be smaller than chunk_size")

  paragraphs = text.split("\n") # 先拆成段落
  paragraphs = [ # 过滤掉空字符
    paragraph
    for paragraph in paragraphs
    if paragraph.strip()
  ]

  chunks = []
  current_chunk = ""
  for paragraph in paragraphs: # 以500为上限拆分
    if len(current_chunk + paragraph) > chunk_size:
      if current_chunk:
        chunks.append(current_chunk)
        current_chunk = ""
      if len(paragraph) > chunk_size: # 如果本身就超过chunk_size
        chunks.extend(split_sentences(paragraph, chunk_size, overlap)) 
      else:
        current_chunk = paragraph

    else:
      current_chunk = current_chunk + "\n" + paragraph

  if current_chunk:
    chunks.append(current_chunk)

  return chunks

# 单句长度超过500的情况
# 固定按照500的size和50重叠去拆
def split_fixed(
  text: str,
  chunk_size=500,
  overlap=50
):
  chunks = []
  start = 0

  while start < len(text):
    chunk = text[start:start + chunk_size]
    chunks.append(chunk)
    start += chunk_size - overlap

  return chunks

def split_sentences(
  paragraph: str,
  chunk_size=500,
  overlap=50
):
  chunks = []
  current_chunk = ""
  sentences = [
    f"{sentence}。"
    for sentence in paragraph.split("。")
    if sentence.strip()
  ]
  for sentence in sentences:
    if len(current_chunk + sentence) > chunk_size:
      if current_chunk:
        chunks.append(current_chunk)
        current_chunk = ""
      if len(sentence) > chunk_size:
        chunks.extend(split_fixed(sentence, chunk_size, overlap))
      else: 
        current_chunk = sentence
    else:
      current_chunk = current_chunk + sentence

  if current_chunk:
    chunks.append(current_chunk)

  return chunks
  