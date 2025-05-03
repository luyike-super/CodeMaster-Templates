from llama_index.core.data_structs import Node
from llama_index.core.schema import NodeWithScore
from llama_index.postprocessor.dashscope_rerank import DashScopeRerank
"""
    使用示意
"""
nodes = [
    NodeWithScore(node=Node(text="text1"), score=0.7),
    NodeWithScore(node=Node(text="text2"), score=0.8),
]

dashscope_rerank = DashScopeRerank(top_n=5)
results = dashscope_rerank.postprocess_nodes(nodes, query_str="<user query>")
for res in results:
    print("Text: ", res.node.get_content(), "Score: ", res.score)