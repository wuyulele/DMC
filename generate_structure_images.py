import pandas as pd
import os
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import rdDepictor
import base64
from io import BytesIO

def xyz_to_mol(xyz_file):
    """将XYZ文件转换为RDKit分子对象"""
    with open(xyz_file, 'r') as f:
        lines = f.readlines()
    
    # 跳过前两行（原子数和注释）
    lines = lines[2:]
    
    # 创建分子对象
    mol = Chem.Mol()
    mol = Chem.RWMol(mol)
    
    # 添加原子和3D坐标
    conf = Chem.Conformer()
    for i, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) >= 4:
            symbol = parts[0]
            x, y, z = map(float, parts[1:4])
            atom = Chem.Atom(symbol)
            atom_idx = mol.AddAtom(atom)
            conf.SetAtomPosition(atom_idx, (x, y, z))
    
    # 添加构象到分子
    mol.AddConformer(conf)
    mol = mol.GetMol()
    
    return mol

def mol_to_image(mol, size=(400, 400)):
    """将分子对象转换为3D图片"""
    # 优化3D构象
    try:
        # 使用MMFF94s力场优化
        AllChem.MMFFOptimizeMolecule(mol)
    except:
        print("力场优化失败，使用原始坐标")
    
    # 创建绘图对象，使用SVG格式以获得更好的质量
    drawer = rdMolDraw2D.MolDraw2DSVG(size[0], size[1])
    
    # 设置绘图选项
    drawer.drawOptions().addStereoAnnotation = True
    drawer.drawOptions().addAtomIndices = False
    drawer.drawOptions().bondLineWidth = 2
    drawer.drawOptions().multipleBondOffset = 0.2
    
    # 绘制分子
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    
    # 获取SVG数据
    svg = drawer.GetDrawingText()
    
    # 转换为base64编码
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f'data:image/svg+xml;base64,{b64}'

def main():
    # 读取CSV文件
    df = pd.read_csv('lig_descriptor.csv')
    
    # 创建新的列用于存储图片
    df['structure_image'] = ''
    
    # 处理每个分子
    for idx, row in df.iterrows():
        name = row['name']
        xyz_file = os.path.join('Structure', f'{name}.xyz')
        
        if os.path.exists(xyz_file):
            try:
                # 转换XYZ为分子对象
                mol = xyz_to_mol(xyz_file)
                
                # 生成图片
                img_data = mol_to_image(mol)
                
                # 更新DataFrame
                df.at[idx, 'structure_image'] = img_data
                
                print(f'处理完成: {name} ({idx + 1}/42)')
            except Exception as e:
                print(f'处理 {name} 时出错: {str(e)}')
        else:
            print(f'找不到文件: {xyz_file}')
    
    # 保存新的CSV文件
    df.to_csv('lig_descriptor_with_images.csv', index=False)
    print('处理完成！新文件已保存为: lig_descriptor_with_images.csv')
    
    # 生成HTML文件
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>分子结构查看器</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .molecule-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
            }
            .molecule-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                width: 450px;
                text-align: center;
            }
            .molecule-name {
                font-size: 18px;
                margin-bottom: 10px;
                color: #333;
            }
            img {
                max-width: 400px;
                height: auto;
            }
            h1 {
                text-align: center;
                color: #2c3e50;
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <h1>分子结构查看器</h1>
        <div class="molecule-container">
    """
    
    # 添加分子数据
    for idx, row in df.iterrows():
        html_content += f"""
            <div class="molecule-card">
                <div class="molecule-name">{row['name']}</div>
                <img src="{row['structure_image']}" alt="{row['name']}的结构">
            </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # 保存HTML文件
    with open('molecule_viewer.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print('HTML文件已生成: molecule_viewer.html')

if __name__ == '__main__':
    main() 