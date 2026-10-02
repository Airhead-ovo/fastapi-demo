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
