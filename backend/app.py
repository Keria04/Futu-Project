from flask import Flask, jsonify
import numpy as np
import faiss

app = Flask(__name__)

@app.route('/')
def hello():
    # ...与 /faiss-search 相同的逻辑...
    d = 4
    nb = 10
    np.random.seed(1234)
    xb = np.random.random((nb, d)).astype('float32')
    index = faiss.IndexFlatL2(d)
    index.add(xb)
    xq = np.random.random((1, d)).astype('float32')
    k = 3
    D, I = index.search(xq, k)
    return jsonify({
        "query": xq.tolist(),
        "indices": I.tolist(),
        "distances": D.tolist()
    })

@app.route('/faiss-search')
def faiss_search():
    # 构造一些随机向量作为索引
    d = 4  # 向量维度
    nb = 10  # 索引向量数量
    np.random.seed(1234)
    xb = np.random.random((nb, d)).astype('float32')

    # 构建FAISS索引
    index = faiss.IndexFlatL2(d)
    index.add(xb)

    # 查询向量
    xq = np.random.random((1, d)).astype('float32')
    k = 3  # 返回最近的3个
    D, I = index.search(xq, k)

    # 返回结果
    return jsonify({
        "query": xq.tolist(),
        "indices": I.tolist(),
        "distances": D.tolist()
    })

if __name__ == '__main__':
    app.run(debug=True)