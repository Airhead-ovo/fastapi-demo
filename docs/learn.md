## alembic(アランビック)
alembic revision --autogenerate -m "add status to projects"
alembic upgrade head
alembic current

---

## fastapi分层
路由层 ルーター層
Schema层 スキーマ層
Service层 サービス層／ビジネスロジック層
Crud层 CRUD層 / データアクセス層（DAO層）
Model层　モデル層
Database层　データベース接続層

---

フロントエンド開発を担当しました。
Vue 3を使用して、ファイルアップロード機能を実装しました。
また、APIと連携して、必要な情報を取得する処理も実装しました。


ログイン時にパスワードを検証し、認証に成功した場合はJWTのアクセストークンを発行します。

---

## docker
### build image 创建镜像
docker build -t fastapi-demo .

### 通过镜像启动容器
docker run -p 8000:8000 fastapi-demo

### 查看运行的docker
docker ps

### 停止docker运行
docker stop c64f8ce47206

### 启动 compose.yaml 里的服务 启动前重新 build Image
docker compose up --build
### 本地启动
docker compose -f compose.yaml -f compose.dev.yaml up --build
### 服务器启动
docker compose up -d --build
### 关闭并删除容器
docker compose down
### 查看进程
docker compose ps

### 更新到requirements
pip install redis
pip freeze > requirements.txt

### volume负责持久化数据
docker volume ls

### 进入Redis Container
docker compose exec redis redis-cli

---

## 常见指令
### cat 查看文件
cat .env
### tail 查看最后几行文件  f是持续查看新的报错
tail -f app.log
docker compose logs -f
### grep 搜索文本
grep "ERROR" app.log 
### | 管道符 把左边的输出交给右边接着处理
docker compose logs | grep "ERROR"
### ps 看进程
ps
ps aux | grep uvicorn
```
出现
aaa              30459   0.0  0.0 435299856   1376 s014  S+    7:41PM   0:00.00 grep uvicorn
30459是进程  可以通过kill去终止
```
### kill终止进程
kill 30459
kill -9 30459  强制终止
### curl
curl http://localhost:8000/
### docker相关指令
docker compose ps  *查看进程*
docker ps *看整台机器正在运行的container*
docker compose logs api  *查看api日志*
docker compose logs --tail=100 api  *查看接口最近报错*
docker compose logs -f api   *实时查看接口报错*
docker compose restart api   *重启服务*
### 常见linux命令
mkdir logs *创建目录*
rm file.txt  *删除文件*
rmdir fastapi *删除文件夹*
cp a.txt b.txt *复制a到b*
mv old.txt new.txt  *移动*
sudo du -sh /home *查看home文件夹有多大*
sudo du -h --max-depth=1 /home | sort -h *查看home文件夹下的文件夹分别有多大*
df -h　*查看剩余磁盘空间*
free -h *查看内存*
top *查看cpu占用 top里面p按cpu排序 m按内存排序 q退出*

nano
Ctrl + O    保存（Write Out）
Enter       确认文件名 compose.yaml
Ctrl + X    退出
Ctrl + K　　删除当前整行