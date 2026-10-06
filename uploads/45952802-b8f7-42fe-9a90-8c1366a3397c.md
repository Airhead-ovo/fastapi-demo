## GET / POST / PUT / PATCH / DELETE

| Method   | 意思   | 你的例子          |
| -------- | ---- | ------------- |
| `GET`    | 获取   | 获取 Project    |
| `POST`   | 创建   | 创建 Project    |
| `PUT`    | 整体替换 | 整个 Project 换掉 |
| `PATCH`  | 部分修改 | 只修改 name      |
| `DELETE` | 删除   | 删除 Project    |

PUT 更偏向整个资源替换, PATCH可以只改某个字段

## 状态码
200 OK
请求成功

201 Created
创建成功

204 No Content
成功，但是没有返回内容

400 Bad Request
请求本身有问题

401 Unauthorized
没登录 / Token无效

403 Forbidden
登录了，但是没权限

404 Not Found
找不到资源

422 Unprocessable Content
FastAPI参数 / Pydantic校验失败

500 Internal Server Error
后端炸了