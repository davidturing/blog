from pydantic import BaseModel, Field
from typing import List

class Entity(BaseModel):
    name: str = Field(description="实体名称，极其精炼，去除所有修饰词。")
    type: str = Field(description="实体分类，如：'Framework', 'Concept', 'Tool', 'Organization', 'Person'。")
    definition: str = Field(description="客观、冷静的实体定义（不超过50字），严禁包含主观赞美或情绪化表达。")

class Triple(BaseModel):
    subject: str = Field(description="主语实体名称，必须与 entities 列表中的某一个 name 完全一致。")
    predicate: str = Field(description="谓词/关系，如 '依赖于', '属于', '对比', '应用于'。")
    object_: str = Field(description="宾语实体名称，必须与 entities 列表中的某一个 name 完全一致。")
    context: str = Field(description="该关系成立的技术上下文或条件补充。")

class GraphData(BaseModel):
    entities: List[Entity] = Field(description="从文本中提取的核心实体列表。")
    triples: List[Triple] = Field(description="实体之间的核心逻辑关系三元组。")
    summary: str = Field(description="整段原始文本的客观技术摘要（150字以内），用于 RAG 检索。")

class FactCheckResult(BaseModel):
    passed: bool = Field(description="草稿是否 100% 符合事实？发现任何捏造实体或扭曲关系必须为 False。")
    feedback: str = Field(description="如果 passed 为 False，给出具体修改指令；如果 True，输出 'OK'。")
    hallucinations: List[str] = Field(description="列出所有捏造的具体知识点（无幻觉则为空）。")
