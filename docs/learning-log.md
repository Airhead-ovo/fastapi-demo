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
- RAG
- Evaluation
## Day 1
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

## Day 2
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