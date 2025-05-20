import os
import base64
import sys
import numpy as np
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
# 添加项目根路径，便于导入 config 和模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config
from PIL import Image

from model_module.calculate_embeded import calaculate_embeded
from faiss_module.build_index import build_index
from faiss_module.search_index import search_index
from worker import generate_embeddings_task

app = Flask(__name__)

DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'datasets')
INDEX_PATH = getattr(config, "INDEX_PATH", "index.bin")
FEATURES_PATH = getattr(config, "FEATURE_PATH", "features.npy")
IDS_PATH = getattr(config, "ID_PATH", "ids.npy")
UPLOAD_FOLDER = config.UPLOAD_FOLDER
DISTRIBUTED_AVAILABLE = getattr(config, "DISTRIBUTED_AVAILABLE", False)
id_map = {}

UPLOAD_HTML = """
<!doctype html>
<title>图片检索</title>
<h1>上传查询图片</h1>
<form id="upload-form" method=post enctype=multipart/form-data>
  <input type=file name=query_img accept="image/*" onchange="previewImage(event)">
  <input type=hidden name=crop_x id=crop_x>
  <input type=hidden name=crop_y id=crop_y>
  <input type=hidden name=crop_w id=crop_w>
  <input type=hidden name=crop_h id=crop_h>
  <input type=submit value=上传>
</form>
<div>
  <canvas id="preview-canvas" style="max-width:400px;max-height:400px;"></canvas>
</div>
<form method=post>
  <button type=submit name=build_index value=1>本地构建/重建数据集索引</button>
  <button type=submit name=build_index_distributed value=1>远程构建/重建数据集索引</button>
</form>
<script>
function previewImage(event) {
    var file = event.target.files[0];
    var reader = new FileReader();
    reader.onload = function(e){
        var img = new Image();
        img.onload = function(){
            var canvas = document.getElementById('preview-canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            var ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            // 简单框选逻辑
            let startX, startY, isDown = false;
            canvas.onmousedown = function(ev){
                isDown = true;
                startX = ev.offsetX;
                startY = ev.offsetY;
            };
            canvas.onmouseup = function(ev){
                if(!isDown) return;
                isDown = false;
                let endX = ev.offsetX;
                let endY = ev.offsetY;
                let x = Math.min(startX, endX);
                let y = Math.min(startY, endY);
                let w = Math.abs(endX - startX);
                let h = Math.abs(endY - startY);
                // 画框
                ctx.drawImage(img, 0, 0);
                ctx.strokeStyle = "red";
                ctx.lineWidth = 2;
                ctx.strokeRect(x, y, w, h);
                // 设置隐藏域
                document.getElementById('crop_x').value = x;
                document.getElementById('crop_y').value = y;
                document.getElementById('crop_w').value = w;
                document.getElementById('crop_h').value = h;
            };
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}
</script>
{% if build_msg %}
    <p style="color:green;">{{ build_msg }}</p>
{% endif %}
{% if results %}
    <h2>检索结果：</h2>
    <ol>
    {% for fname, idx, img_url in results %}
        <li>
            <div>
                <img src="{{ img_url }}" style="max-width:160px;max-height:160px;border:1px solid #ccc;">
                <br>
                {{ fname }} (编号: {{ idx }})
            </div>
        </li>
    {% endfor %}
    </ol>
{% endif %}
"""

def prepare_index(distributed=False):
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    img_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(img_exts) and f != 'query.jpg']
    img_files.sort()
    features = []
    ids = []
    id_map.clear()
    if distributed and DISTRIBUTED_AVAILABLE:
        print("尝试使用远程特征提取构建索引...")
        task_futures = []
        for idx, fname in enumerate(img_files):
            path = os.path.join(DATASET_DIR, fname)
            with open(path, 'rb') as f:
                img_data = f.read()
            img_data_b64 = base64.b64encode(img_data).decode('utf-8')
            try:
                future = generate_embeddings_task.delay(img_data_b64)
                task_futures.append((idx, fname, future))
            except Exception as e:
                print(f"远程任务提交失败: {e}")
                return False
        for idx, fname, future in task_futures:
            try:
                embedding_list = future.get(timeout=60)
                embedding = np.array(embedding_list, dtype='float32').reshape(1, -1)
                id_map[idx] = fname
                features.append(embedding.squeeze())
                ids.append(idx)
            except Exception as e:
                print(f"处理图片 {fname} 时发生错误: {e}")
                return False
        print("已采用远程特征提取。")
    else:
        print("采用本地特征提取构建索引...")
        embedder = calaculate_embeded()
        for idx, fname in enumerate(img_files):
            path = os.path.join(DATASET_DIR, fname)
            img = Image.open(path)
            feat = embedder.calculate(img)
            id_map[idx] = fname
            features.append(feat)
            ids.append(idx)
        print("已采用本地特征提取。")
    features = np.stack(features).astype('float32')
    ids = np.array(ids, dtype='int64')
    np.save(FEATURES_PATH, features)
    np.save(IDS_PATH, ids)
    print(f"特征已保存到 {FEATURES_PATH}，ID已保存到 {IDS_PATH}")
    print("索引已构建完成。")
    print("数据集特征与索引构建完成，可以进行图片检索。")
    return True

@app.route('/', methods=['GET', 'POST'])
def upload_and_search():
    results = None
    build_msg = None
    img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
    img_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(img_exts) and f != 'query.jpg']
    img_files.sort()
    if request.method == 'POST':
        if request.form.get('build_index'):
            prepare_index(distributed=False)
            build_msg = "本地数据集特征与索引已构建完成，可以进行图片检索。"
        elif request.form.get('build_index_distributed'):
            if DISTRIBUTED_AVAILABLE:
                ok = prepare_index(distributed=True)
                if ok:
                    build_msg = "远程数据集特征与索引已构建完成，可以进行图片检索。"
                else:
                    build_msg = "远程构建失败，已跳过。"
            else:
                build_msg = "远程worker不可用，无法远程构建。"
        else:
            file = request.files.get('query_img')
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                # 裁剪参数
                try:
                    x = int(request.form.get('crop_x', 0))
                    y = int(request.form.get('crop_y', 0))
                    w = int(request.form.get('crop_w', 0))
                    h = int(request.form.get('crop_h', 0))
                except Exception:
                    x, y, w, h = 0, 0, 0, 0
                img = Image.open(save_path)
                if w > 0 and h > 0:
                    img = img.crop((x, y, x + w, y + h))
                embedder = calaculate_embeded()
                query_feat = embedder.calculate(img).reshape(1, -1)
                indices = search_index(query_feat, top_k=5)
                # 生成图片URL
                results = []
                for idx in indices:
                    fname = img_files[idx]
                    img_path = os.path.join(DATASET_DIR, fname)
                    img_url = '/show_image/' + fname
                    results.append((fname, idx, img_url))
    return render_template_string(UPLOAD_HTML, results=results, build_msg=build_msg)

@app.route('/show_image/<filename>')
def show_image(filename):
    from flask import send_from_directory
    return send_from_directory(DATASET_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=19198)
