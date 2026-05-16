import json
from collections import defaultdict

def generate_pedigree_data(json_file="input.json"):
    """コアラのJSONデータを読み込んで、家系図構造を生成"""
    
    with open(json_file, "r", encoding="utf-8") as f:
        koala_data = json.load(f)
    
    # IDをキーにしたマップを作成
    koala_by_id = {koala.get("id"): koala for koala in koala_data}

    nodes = [];
    edges = [];
    x = 0;
    y = 0;
    g={}
    for idx,(k,v) in enumerate(koala_by_id.items()):
        dam_id = v.get("dam_id")
        dam_name = ""
        if dam_id == "#N/A" :
            dam_id = None
        if dam_id :
            dam = koala_by_id.get(dam_id);
            if dam :
                dam_name = dam.get("name", "")
        sire_id = v.get("sire_id")
        sire_name = ""
        if sire_id == "#N/A" :
            sire_id = None
        if sire_id :
            sire = koala_by_id.get(sire_id);
            if sire :
                sire_name = sire.get("name", "")
        
        nodes.append({
            'id': k,
            'name': v.get('name',''), 
            'sex': v.get('sex', ''),
            'born': v.get('born', ''),
            'died': v.get('died', ''),
            'alive': v.get('alive', True),
            'remarks': v.get('remarks', ''),
            'generation': 0,  # 後で計算,
            'dam_name': dam_name,
            'sire_name': sire_name
            })
        if dam_id :
            edges.append({ 'parent': dam_id, 'child': k, 'parent_name': dam_name });
            g.setdefault(k, []).append(dam_id)
        if sire_id :
            edges.append({ 'parent': sire_id, 'child': k, 'parent_name': sire_name });
            g.setdefault(k, []).append(sire_id)
    #
    for k in nodes :
        stk = [];
        def dfs(node_id, visited,stk,k):
            if node_id in visited:
                return;
            visited.add(node_id);
            stk.append(node_id);
            k['generation'] = max(k.get('generation',0),len(stk)-1);
            for parent_id in g.get(node_id, []):
                dfs(parent_id, visited,stk,k)
            stk.pop()
            return;
        if k['id'] in g :
            dfs(k['id'], set(),stk,k);
    nodes.sort(key=lambda x: (x['generation'], x['id']))
    
    # JSONデータとして出力
    output = {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_koalas": len(nodes),
            "total_edges": len(edges),
        }
    }
    
    return output

if __name__ == "__main__":
    pedigree_data = generate_pedigree_data()
    
    # pedigree_data.jsonへ保存
    with open("pedigree_data.json", "w", encoding="utf-8") as f:
        json.dump(pedigree_data, f, ensure_ascii=False, indent=2)
    
    # 統計情報を表示
    print("=== コアラ家系図データ生成完了 ===")
    print(f"\n出力ファイル: pedigree_data.json")
