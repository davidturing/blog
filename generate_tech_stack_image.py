import dashscope
import os
from dashscope import ImageSynthesis

# 从环境变量或凭据文件获取 API 密钥
api_key = None

# 尝试从凭据文件读取
try:
    with open('.credentials/api_keys.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                if key == 'DASHSCOPE_API_KEY':
                    api_key = value.strip('"\'')
                    break
except FileNotFoundError:
    pass

# 如果没找到，尝试环境变量
if not api_key:
    api_key = os.getenv('DASHSCOPE_API_KEY')

if not api_key:
    print("Error: DASHSCOPE_API_KEY not found")
    exit(1)

dashscope.api_key = api_key

# 生成图像
prompt = """Professional tech stack architecture diagram showing 2026 Python Data Analyst/Scientist standard configuration. 
The diagram should have a modern, clean design with the following sections arranged logically:
- Core Environment (Python 3.14, uv package manager, VS Code)
- Data Processing Stack (Polars, DuckDB, Pandas 3.0 with Arrow icons)
- Visualization & BI (Plotly, Tableau, Power BI logos)
- Machine Learning & AI (PyTorch, Hugging Face, scikit-learn)
- MLOps & Engineering (MLflow, Docker, FastAPI)
- Distributed Computing (Dask, Ray, PySpark)

Use a dark blue to purple gradient background (#093572 to #6a0dad), white and light blue text/icons for high contrast.
Include technical icons and clean lines connecting related components. Professional blueprint aesthetic with technical precision.
High resolution 2K quality, 16:9 aspect ratio."""

response = ImageSynthesis.call(
    model='wanx-v1',
    prompt=prompt,
    size='1024*1024',
    n=1
)

if response.status_code == 200:
    image_url = response.output.results[0].url
    print(f"Image generated successfully: {image_url}")
    
    # 下载图像
    import requests
    img_data = requests.get(image_url).content
    with open('python_data_analyst_2026_stack.png', 'wb') as f:
        f.write(img_data)
    print("Image saved as python_data_analyst_2026_stack.png")
else:
    print(f"Error: {response.code} - {response.message}")