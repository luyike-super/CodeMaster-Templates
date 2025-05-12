# 添加调试信息来查看处理后的节点及其元数据
for node in index.docstore.docs.items():
    print("节点ID:", node.node_id)
    print("节点z文本:", node.text[:100] + "...")
    print("节点元数据:", node.metadata) 
    print("---")

"""
{
	"mata_date":{
		{'excerpt_keywords': '子集 数据 训练模型'}
		{'excerpt_keywords': '模型 时间 性能'}
	}
}
"""