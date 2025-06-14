import pandas as pd
import os
import base64

df = pd.read_csv('lig_descriptor.csv')

html_head = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>分子3D结构浏览器</title>
    <script src="https://3Dmol.org/build/3Dmol.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .main { display: flex; }
        .viewer-box { width: 600px; height: 480px; margin: 40px; border: 1px solid #ccc; background: #fff; border-radius: 8px; }
        .list-box { margin: 40px; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 20px; min-width: 400px; }
        .mol-name { cursor: pointer; padding: 8px; border-bottom: 1px solid #eee; }
        .mol-name:hover { background: #f0f0f0; }
        .mol-name.selected { background: #d0eaff; font-weight: bold; }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
    </style>
</head>
<body>
<h1>分子3D结构浏览器</h1>
<div class="main">
    <div id="mainviewer" class="viewer-box"></div>
    <div class="list-box">
"""

html_tail = """
    </div>
</div>
<script>
let xyzData = [];
function decode64(b64) {
    return decodeURIComponent(escape(window.atob(b64)));
}
"""

# 生成分子名列表和xyz数据
for idx, row in df.iterrows():
    name = row['name']
    xyz_path = os.path.join('Structure', f'{name}.xyz')
    if not os.path.exists(xyz_path):
        continue
    with open(xyz_path, 'r') as f:
        xyz_content = f.read()
    xyz_b64 = base64.b64encode(xyz_content.encode('utf-8')).decode('ascii')
    html_head += f'<div class="mol-name" onclick="showMol({idx})" id="molname_{idx}">{name}</div>\n'
    html_tail += f'xyzData.push("{xyz_b64}");\n'

html_tail += """
let viewer = $3Dmol.createViewer("mainviewer", {backgroundColor: "white"});
function showMol(idx) {
    let xyz = decode64(xyzData[idx]);
    viewer.clear();
    viewer.addModel(xyz, "xyz");
    viewer.setStyle({}, {stick:{radius:0.2}, sphere:{scale:0.3}});
    viewer.zoomTo();
    viewer.render();
    // 高亮当前分子名
    let names = document.getElementsByClassName("mol-name");
    for (let i = 0; i < names.length; i++) {
        names[i].classList.remove("selected");
    }
    document.getElementById("molname_" + idx).classList.add("selected");
}
// 默认显示第一个分子
if(xyzData.length > 0) showMol(0);
</script>
</body>
</html>
"""

with open('molecule_3d_viewer.html', 'w', encoding='utf-8') as f:
    f.write(html_head + html_tail)

print("已生成 molecule_3d_viewer.html，点击分子名即可切换3D结构！")