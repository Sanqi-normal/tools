# 功能：读取 JSON 文件，提取 content 并向量化。用 Faiss 构建索引，加速相似度搜索。输入新对话后，检索并返回 JSON 中语义最相近的10个条目
# 最后更新时间： 2025/2/25
# 说明：初始是为了长期记忆用的，试验效果

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# 初始化向量化模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# JSON 文件路径
json_file = "alice_history.json"

# 读取 JSON 文件并向量化
def load_and_index_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取 content 并向量化
    contents = [entry["content"] for entry in data]
    vectors = model.encode(contents, show_progress_bar=True)
    
    # 初始化 Faiss 索引
    vector_dim = vectors.shape[1]  # 向量维度（通常 384 或 768，取决于模型）
    index = faiss.IndexHNSWFlat(vector_dim, 32)  # HNSW 索引
    index.hnsw.efConstruction = 40  # 构建时搜索深度
    index.hnsw.efSearch = 64       # 查询时搜索深度
    index.add(vectors)
    
    return data, index

# 检索语义最相近的10条条目
def retrieve_most_similar(query, data, index):
    # 将查询向量化
    query_vector = model.encode([query])[0].reshape(1, -1)
    
    # 搜索最相似的10个向量
    distances, indices = index.search(query_vector, 10)  # top-10
    most_similar_indices = indices[0]
    
    # 返回对应的10个 JSON 条目
    return [data[i] for i in most_similar_indices]

# 主函数
def main():
    # 加载 JSON 并构建索引
    data, index = load_and_index_json(json_file)
    print(f"已加载 {len(data)} 条记忆，索引构建完成。")
    
    # 交互式输入
    while True:
        query = input("请输入对话（输入 'exit' 退出）：")
        if query.lower() == 'exit':
            break
        
        # 检索并输出
        results = retrieve_most_similar(query, data, index)
        print("最相似的10个条目：")
        for result in results:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        print()

if __name__ == "__main__":
    main()
