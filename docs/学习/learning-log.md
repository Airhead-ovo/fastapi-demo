##　速查目录
### md 格式
| 名詞 | 発音 | 中国語 | 短语 |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
### Python / Backend
- [async / await](#async--await)
- [FastAPI Dependency](#fastapi-dependency)
- [Pydantic](#pydantic)
- [异常处理](#异常处理)
- [SQLAlchemy](#SQLAlchemy)
> [Transaction / Rollback](#Transaction--Rollback)
- Redis
- Docker
### Agent
- Tool Calling
- Planner / Executor
- Context
- Memory
- [RAG](#RAG)
- Evaluation
### async / await
| 名詞 | 発音 | 中国語 |
| --- | --- | --- |
| 同期処理| どうきしょり |　
| 非同期処理 | ひどうきしょり |
| 並行処理 | へいこう | 并发执行 |
> async 不是让一个任务执行得更快，而是让程序在等待 I/O 时，可以先去干别的事。async 主要提高的是I/O 场景下的并发处理能力。
> async は処理そのものを速くするというより、待ち時間を有効活用するための仕組みです　　　`そのもの本身`

- 同期処理
```python
import time

def call_llm():
  print("llm 開始")
  time.sleep(3)
  print("llm 終了")
  return "llm result"

def call_tool():
  print("tool 開始")
  time.sleep(5)
  print("tool 終了")
  return "tool result"

start = time.time()

llm_result = call_llm()
tool_result = call_tool()

print(llm_result)
print(tool_result)

print(f"总耗时：{time.time() - start:.2f}s")
# .2f 浮点数展示 保留两位小数
```
```
(.venv) aaa@aaadeMacBook-Air fastapi-demo % python async_demo.py
llm 開始
llm 終了
tool 開始
tool 終了
llm result
tool result
总耗时：8.01s
```
---
- 非同期処理
```python
import time
import asyncio

async def call_llm():
  print("llm 開始")
  await asyncio.sleep(3)
  print("llm 終了")
  return "llm result"

async def call_tool():
  print("tool 開始")
  await asyncio.sleep(5)
  print("tool 終了")
  return "tool result"

async def main():
  start = time.time()

  llm_result, tool_result = await asyncio.gather(
    call_llm(),
    call_tool()
  )
  print(llm_result)
  print(tool_result)
  print(f"总耗时：{time.time() - start:.2f}s")

asyncio.run(main())
```

```
aaa@aaadeMacBook-Air fastapi-demo % python async_demo.py
llm 開始
tool 開始
llm 終了
tool 終了
llm result
tool result
总耗时：5.00s
```
- asyncio 的核心是什么？
> python 的asyncio 是靠事件循环来运行的, 遇到需要await和等i/o的时候,就先暂停这个任务, 开始执行其他的任务, 把等待的时间利用起来
> await で待ち時間が発生したら、その間に他のタスクを実行する。なので、待ち時間をうまく使える仕組みです
- pythonって、普通はどんな時に await を使う
> http请求, 数据库操作, redis, 文件io, 等待网络
> await は　I/Oなど待ち時間がある非同期処理で使います

- IO Bound
> 等网络  等数据库 等 Redis 等文件 等第三方 API
> この場合は await を使う必要がある
- CPU Bound
> 处理 500 万条数据 图片压缩 视频编码 复杂数学计算 训练模型
> この場合は await を使う必要がない

- 误区
```python
result1 = await call_llm()
result2 = await call_tool()
```
这里仍然是8s, 因为需要等待上一个结束后,才开始下一个.
如果两个任务互不依赖，才可以
```python
llm_result, tool_result = await asyncio.gather(
    call_llm(),
    call_tool(),
)
```

### Fastapi Dependency
| 名詞 | 発音 | 中国語 | 短语 |
| --- | --- | --- |
| 依存性注入| いぞんせいちゅうにゅう |　依赖注入 |
| 結合度 | けつごうど | 耦合 | 結合度を下げる |
|  |  |  |
> Dependency Injection，依赖注入：某个接口需要什么东西，不让它自己创建，而是由 FastAPI 帮它准备好，再传进去。
> 必要なものを自分で作るのではなく、外から渡してもらう仕組みです
- depends は何ですか
> depends を使うと、ルーターとデータベースや認証処理の結合度を下げることができる
> depends 可以降低 Router 与数据库、认证处理之间的耦合。

### Pydantic
> Pydantic = 数据校验 + 数据结构定义

### Transaction / Rollback
> Transaction 保证一组数据库操作要么全部成功，要么全部失败。
> トランザクションでは、複数の処理を一つの単位として扱います。途中で失敗した場合は、すべてロールバックできます。

- flush()
> 数据虽然已经发给数据库，但还没有正式提交。
> flushはSQLをデータベースに送りますが、まだコミットはしません
```
db.add()
↓
“这个对象准备写入”

db.flush()
↓
“现在把 SQL 发给数据库，但先别最终确认”

db.commit()
↓
“确认，正式提交事务”
```
```python
def update_message_service (
  data,
  db,
  current_user
):
  try:
    #  ...多个用到crud的业务逻辑 在curd中不用写commit 统一在service后写
    delete_messages_from(
      message,
      db
    )

    touch_conversation(conversation)

    db.commit()
    db.refresh(message)
    return message

  except Exception:
    db.rollback() # 发生报错回滚
    raise # 提升异常报错
```

### 条件表达式
C = A if condition else B

```
pinned_at = datetime.now() if data.is_pinned else None
```
### 排序 ASC / DESC
```text
ASC  = ascending 升序
     = 小 → 大
     = 早 → 晚

DESC = descending 降序
     = 大 → 小
     = 晚 → 早
```

```text
nulls_last : 有 pinned_at 的排前面, NULL 的排后面
```

### RAG
RAG是让LLM回答前, 先从知识库检索相关内容, 再结合检索结果生成答案的技术
RAG = Retrieval + Augmented + Generation
搜索 + 增强 + 生成
> 在自己的知识库里检索相关资料, 把资料作为context交给llm, llm根据资料生成回答
```
解决的问题是:
LLM 不知道企业内部数据
LLM 知识可能过期
文档太长无法全部塞入 Context
需要让回答基于指定知识来源
```
#### 文档处理和chunking
当前支持PDF,txt,md,  pdf用pymupdf来提取文本再统一进入切分
- Chunking(文本切分): 整篇文档太长; 小块文本更容易相关性匹配; 可以减少无关上下文和token消耗
- Chunk overlap: 故意让两个 Chunk 重叠, 防止重要信息被切断, 造成信息损失
```text
段落优先 → 句子切分 → 固定长度兜底 → Overlap
```
#### Embedding 向量化
> Embedding是把一段文字转换成一串能够表示其语义的数字, 变成类似[0.21, -0.53, 0.71, ...]的数组向量(Vector)

> 上传文档的时候, 提前把chunk都变成向量存到数据库, 用户提问时把问题转换成向量再与数据库对比, 通过检索(Retrieval)找到相似度最接近的

知识入库过程
```
上传 .txt
 ↓
读取文本
 ↓
split_text()
 ↓
Chunk
 ↓
Embedding Model
 ↓
1024维 Vector
 ↓
PostgreSQL + pgvector
```
使用余弦距离判断语义, 距离越小语义越近
```
DocumentChunk.embedding.cosine_distance(question_embedding)
```
向量检索的优点是能够识别语义相近但是用词不同的内容, 缺点是对专业术语, 年份, 型号等关键词不够敏感
#### Retrieval 检索 
1. 用户提出问题 `为什么不能让 AI 判断用户权限`
2. 先把问题变成vector `question_embedding = get_embedding(question)`
3. 把问题vector拿去与数据库存储的chunk vector对比, Cosine Distance, Distance越低表示语意越近
```
  distance = DocumentChunk.embedding.cosine_distance(
    question_embedding
  )
```
4. Threshold 阈值设置
即使完全没有相关内容，数据库依然可以找出最像的三个即Top-k
所以需要增加 `MAX_DISTANCE = 0.6`

#### Keyword Search 关键词检索
把问题拆成关键词, 去匹配chunk
```
question = “找到 2025 年聚乙烯催化剂的实验报告。”
keywords = ["2025", "聚乙烯", "催化剂", "实验报告"]
DocumentChunk.content.ilike(f"%{keyword}%")
```
ILIKE是不区分 大小写的匹配模式, %表示任意长度的字符
多个关键词可以使用or_(*conditions), 命中任意一个就能进入候选集
BM25 通常考虑词频（TF）、逆文档频率（IDF）和文档长度归一化等因素。

#### Hybrid Search 混合检索
结合向量检索和关键词检索, 使用RRF公式计算得分
\[
\operatorname{RRF}(d)=\sum_{r\in R}\frac{1}{k+\operatorname{rank}_r(d)}
\]

- \(d\)：某个 Chunk。
- \(R\)：不同检索结果列表。
- \(\operatorname{rank}_r(d)\)：Chunk 在某一路检索中的排名。
- \(k\)：平滑参数，常用 60。

#### Augmentation 增强
1. 检索出来三个chunk: Chunk A, Chunk B, Chunk C
2. 通过join组合  `context = "\n\n".join(contents) `
3. 把文字context交给llm

#### Generation 生成
最基础的rag架构
```
Question
 ↓
Embedding
 ↓
Vector Search
 ↓
Top-K
 ↓
Threshold
 ↓
Context
 ↓
Prompt
 ↓
LLM
 ↓
Answer
```
```
chunks = search_chunks_service(...)

context = augment_context_service(chunks)

answer = generate_rag_answer(
    question,
    context
)
```

### MCP