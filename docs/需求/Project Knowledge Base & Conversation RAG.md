# Project Knowledge Base & Conversation RAG 产品需求文档

## 1. 功能目标

为现有 AI Agent 系统增加两种知识库使用场景：

```text
普通 Conversation
→ 支持上传会话级临时文件
→ 文件仅供当前 Conversation 使用

Project
→ 拥有独立 Knowledge Base
→ Project 下可创建多个 Conversation
→ 所有 Project Conversation 共享 Project Knowledge Base
```

Agent 根据用户问题自行判断是否需要检索知识库，并基于检索结果回答。

---

## 2. 核心对象关系

整体产品关系：

```text
User
│
├── 普通 Conversation
│     ├── Messages
│     └── Temporary Files
│
└── Project
      │
      ├── Knowledge Base
      │     ├── Document A
      │     ├── Document B
      │     └── Document C
      │
      └── Conversations
            ├── Conversation A
            │     └── Messages
            ├── Conversation B
            │     └── Messages
            └── Conversation C
                  └── Messages
```

一个 Project 可以拥有多个 Conversation。

一个 Conversation 最多属于一个 Project。

---

## 3. Conversation 类型

不额外创建 `ProjectConversation`。

Conversation 本身支持两种状态：

```text
project_id = NULL
→ 普通 Conversation

project_id != NULL
→ Project Conversation
```

### 3.1 普通 Conversation

用户可以：

- 正常与 Agent 对话
- 上传临时文件
- 针对当前 Conversation 的文件提问
- 将 Conversation 移入某个 Project

临时文件只属于当前 Conversation，不影响其他普通 Conversation。

> 此处的“临时文件”指知识作用域仅限当前 Conversation，并不代表文件只存在于内存中。

因此用户刷新页面、退出登录后重新进入原 Conversation，文件仍然存在。

### 3.2 Project Conversation

用户进入某个 Project 后，可以创建多个 Conversation：

```text
Project A
├── Knowledge Base
├── Chat 1
├── Chat 2
└── + New Chat
```

所有 Project Conversation 默认共享该 Project 的 Knowledge Base。

例如：

```text
Project A Knowledge Base

architecture.txt
api.txt
permission.txt

        ↓

Chat 1：权限是怎么设计的？
Chat 2：总结一下 API
Chat 3：这个项目用了什么架构？
```

三个 Conversation 都可以检索相同的 Project Knowledge Base。

---

## 4. Project Knowledge Base

每个 Project 提供独立的知识库。

例如：

```text
Project A

[ Chat ]
[ Knowledge Base ]

Knowledge Base
--------------------------------
architecture.txt
permission.txt
rag-design.txt

              [ Upload Document ]
```

### 第一版支持格式

```text
.txt
```

后续可扩展：

```text
.pdf
.md
.docx
```

PDF、Markdown、Word 等格式暂时不进入第一版范围。

---

## 5. Document 管理

Project Knowledge Base 第一版支持：

- 上传 Document
- 查看 Document List
- 查看 Document 基本信息
- 预览 Document
- 删除 Document

Document 属于 Project，而不是某个具体 Conversation。

```text
Project 1
├── Document A
├── Document B
└── Document C
```

因此 Project 1 下所有 Conversation 都可以使用这些 Document。

---

## 6. 普通 Conversation 临时文件

普通 Conversation 支持直接上传文件。

例如：

```text
Conversation 8

用户：
[上传 test.txt]

用户：
这个文件主要讲了什么？

Agent：
...
```

文件只参与当前 Conversation 的知识检索。

例如：

```text
Conversation 8
└── test.txt
```

其他 Conversation：

```text
Conversation 9
Conversation 10
```

不能检索 `test.txt`。

---

## 7. Project Conversation 文件上传规则

Project Conversation 禁止直接上传临时文件。

如果用户需要增加知识，需要先进入：

```text
Project
 ↓
Knowledge Base
 ↓
Upload Document
 ↓
Chat
 ↓
提问
```

这样可以避免同时存在：

```text
Project Knowledge
+
Conversation Temporary Knowledge
```

导致知识作用域变得复杂。

---

## 8. 将普通 Conversation 移入 Project

普通 Conversation 支持：

```text
Move to Project
```

例如：

```text
Conversation 8

project_id = NULL

        ↓

Move to Project A

        ↓

project_id = Project A
```

### 8.1 Conversation 没有临时文件

提示用户：

> 确定将此会话移入「Project A」？

用户确认后完成移动。

### 8.2 Conversation 存在临时文件

例如：

```text
Conversation 8
├── test.txt
└── 123.txt
```

用户选择：

```text
Move to Project A
```

弹窗提示：

> **确定移入至「Project A」？**
>
> 此会话包含的临时文件 `test.txt`、`123.txt` 将自动移入「Project A」的知识库列表。
>
> 移动后，项目内的其他会话也可以使用这些文件。

用户可以选择：

```text
Cancel
Confirm
```

确认后：

```text
Conversation
project_id → Project A
```

同时：

```text
test.txt
123.txt
      ↓
Project A Knowledge Base
```

这些文件不再属于 Conversation 私有知识，而成为 Project Knowledge Base 的一部分。

### 8.3 一致性要求

Conversation 移动与文件迁移必须作为一个完整业务操作处理。

不能出现：

```text
Conversation 移动成功
但是 File 移动失败
```

也不能出现：

```text
File 已进入 Project
但是 Conversation 没有移动
```

---

## 9. RAG 行为

### 9.1 普通 Conversation

知识检索范围：

```text
Current Conversation
        ↓
Conversation Files
        ↓
Chunks
```

只允许检索当前 Conversation 上传的文件。

逻辑范围：

```text
WHERE conversation_id = current_conversation.id
```

不能搜索其他 Conversation 的文件。

### 9.2 Project Conversation

知识检索范围：

```text
Current Conversation
        ↓
Project
        ↓
Project Documents
        ↓
Chunks
```

逻辑范围：

```text
WHERE project_id = current_project.id
```

同一个 Project 下的所有 Conversation 共享该知识范围。

---

## 10. Agent 行为

用户不需要主动指定：

```text
project_id
conversation_id
document_id
```

这些信息应该尽可能由当前应用上下文确定。

例如用户当前位于：

```text
Project A
└── Chat 3
```

用户直接询问：

> 文档里权限是怎么设计的？

Agent 判断该问题需要查询知识库：

```text
Agent
 ↓
knowledge_search
```

后端根据当前 Conversation 判断 Knowledge Scope。

完整流程：

```text
User
 ↓
Conversation Context
 ↓
Agent
 ↓
是否需要知识库？
 ├─ No
 │   ↓
 │ 正常回答 / 调用其他 Tool
 │
 └─ Yes
      ↓
 knowledge_search
      ↓
判断 Conversation 类型
      ↓
┌────────────────────────────┐
│                            │
普通 Chat                Project Chat
│                            │
Conversation Files       Project Documents
│                            │
└─────────────┬──────────────┘
              ↓
           Retrieval
              ↓
          Tool Result
              ↓
           Agent LLM
              ↓
            Answer
```

---

## 11. RAG Pipeline

### 11.1 文档入库

```text
File
 ↓
Parse
 ↓
Text
 ↓
Chunk
 ↓
Embedding
 ↓
Vector
 ↓
Vector DB
```

### 11.2 用户提问

```text
Question
 ↓
Embedding
 ↓
Knowledge Scope Filter
 ↓
Vector Search
 ↓
Top-K
 ↓
Distance Threshold
 ↓
Relevant Chunks
 ↓
Agent
 ↓
Answer
```

Knowledge Scope：

```text
普通 Conversation
→ Conversation Scope

Project Conversation
→ Project Scope
```

---

## 12. 权限要求

所有 Knowledge 相关操作必须验证当前用户权限。

包括：

- `knowledge_search`
- Document Upload
- Document Preview
- Document Delete
- Conversation File Upload
- Conversation Move
- Conversation File → Project Document

不能仅相信 Agent 或前端传入的：

```text
project_id
conversation_id
document_id
```

后端必须根据当前用户验证其是否有权访问对应资源。

---

## 13. 第一版范围

### 需要完成

- Conversation 支持关联 Project
- 普通 Conversation 上传 TXT
- Conversation 级 RAG
- Project Knowledge Base
- Project Document List
- TXT Preview
- Project 下创建多个 Conversation
- Project 级 RAG
- 普通 Conversation → Project
- 移动 Conversation 时临时文件 → Project Knowledge Base
- Agent 自动判断是否调用 `knowledge_search`

### 暂时不做

- PDF
- DOCX
- Markdown
- OCR
- Hybrid Search
- BM25
- Reranker
- Query Rewrite
- Multi Query Retrieval
- Parent-Child Chunk
- 复杂 Chunk Strategy
- RAG Evaluation
- Embedding Queue
- 大文件异步处理
- 多人 Project 权限

以上内容作为后续 RAG 进阶阶段实现。

---

## 14. 验收场景

### 场景 A：普通 Conversation

```text
创建 Chat A
 ↓
上传 test.txt
 ↓
询问 test.txt 中的问题
 ↓
Agent 正确检索并回答
```

然后：

```text
创建 Chat B
 ↓
询问相同问题
 ↓
不能检索 Chat A 的 test.txt
```

---

### 场景 B：Project Knowledge Base

```text
Project A
 ↓
上传 rag.txt
```

然后：

```text
Project A / Chat 1
→ 可以根据 rag.txt 回答

Project A / Chat 2
→ 同样可以根据 rag.txt 回答

Project B / Chat
→ 不能检索 rag.txt
```

---

### 场景 C：Conversation 移入 Project

初始状态：

```text
普通 Chat A
├── test.txt
└── 123.txt
```

执行：

```text
Move to Project A
```

系统弹窗：

> 确定移入至「Project A」？
>
> 此会话包含的临时文件 `test.txt`、`123.txt` 将自动移入「Project A」的知识库列表。

用户确认：

```text
Chat A.project_id = Project A
```

同时：

```text
Project A Knowledge Base
├── test.txt
└── 123.txt
```

之后创建：

```text
Project A / Chat B
```

Chat B 同样能够检索：

```text
test.txt
123.txt
```

---