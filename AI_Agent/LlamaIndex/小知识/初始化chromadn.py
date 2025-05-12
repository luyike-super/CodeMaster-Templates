# 使用 Chroma 作为向量存储
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

# 初始化 Chroma 客户端
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("quickstart")

# 创建向量存储
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 创建存储上下文
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 使用存储上下文创建索引
index = VectorStoreIndex.from_documents(
    documents, 
    storage_context=storage_context
)