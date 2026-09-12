FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

# 创建容器时的指令
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 运行容器时的指令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]