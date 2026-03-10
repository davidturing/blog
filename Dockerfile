FROM python:3.12-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    g++ \
    gcc \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制测试代码
COPY symbol_switch_cumsum_bodo.py .
COPY symbol_switch_cumsum_pandas.py .
COPY symbol_switch_cumsum_polars.py .
COPY symbol_switch_cumsum_duckdb.py .

# 设置环境变量
ENV PYTHONPATH=/app

# 默认运行Bodo测试
CMD ["python", "symbol_switch_cumsum_bodo.py"]