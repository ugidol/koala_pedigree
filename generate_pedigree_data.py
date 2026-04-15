import json
from collections import defaultdict

def generate_pedigree_data(json_file="input.json"):
    """コアラのJSONデータを読み込んで、家系図構造を生成"""
    
    with open(json_file, "r", encoding="utf-8") as f:
        koala_data = json.load(f)
    
    # IDをキーにしたマップを作成
    koala_by_id = {koala.get("id"): koala for koala in koala_data}
    
    # 世代を計算 (IDベース)
    generation_map = {}
    
    def calculate_generation(koala_id, memo=None):
        if memo is None:
            memo = {}
        if koala_id in memo:
            return memo[koala_id]
        
        koala_info = koala_by_id.get(koala_id)
        if not koala_info:
            memo[koala_id] = 0
            return 0
        
        parents = []
        dam_id = koala_info.get("dam_id")
        sire_id = koala_info.get("sire_id")
        
        # dam_idとsire_idが有効か確認（#N/AやNoneを除外）
        if dam_id and dam_id != "#N/A":
            parents.append(dam_id)
        if sire_id and sire_id != "#N/A":
            parents.append(sire_id)
        
        if not parents:
            memo[koala_id] = 0
            return 0
        
        try:
            parent_gen = max(calculate_generation(p, memo) for p in parents)
            gen_num = parent_gen + 1
        except (ValueError, RecursionError):
            gen_num = 0
        
        memo[koala_id] = gen_num
        return gen_num
    
    # 全コアラについて世代を計算
    generation_memo = {}
    generations = defaultdict(list)
    
    for koala in koala_data:
        koala_id = koala.get("id")
        gen = calculate_generation(koala_id, generation_memo)
        generation_map[koala_id] = gen
        generations[gen].append(koala)
    
    # ノードを準備（位置情報を追加）
    nodes = []
    edges = []
    node_width = 80
    node_height = 40
    level_spacing = 200
    peer_spacing = 120
    cols_per_row = 10  # 横に10頭ずつ配置
    
    # 世代ごとにコアラを配置
    id_to_node_id = {}
    node_id_counter = 0
    
    for gen_num in sorted(generations.keys()):
        koalas_in_gen = generations[gen_num]
        for idx, koala in enumerate(koalas_in_gen):
            koala_id = koala.get("id")
            node_id_counter += 1
            node_id = f"koala_{node_id_counter}"
            id_to_node_id[koala_id] = node_id
            
            sex = koala.get("sex", "M")
            # 10頭ごとに行を変更
            row = idx // cols_per_row
            col = idx % cols_per_row
            x = col * peer_spacing + 50
            y = gen_num * level_spacing + row * 120
            
            node_info = {
                "id": node_id,
                "name": koala.get("name", "Unknown"),
                "sex": sex,
                "generation": gen_num,
                "x": x,
                "y": y,
                "born": koala.get("born", ""),
                "died": koala.get("died", ""),
                "alive": koala.get("alive", True),
                "dam_id": koala.get("dam_id", ""),
                "sire_id": koala.get("sire_id", "")
            }
            nodes.append(node_info)
    
    # エッジを追加（実在する親子関係）
    for koala in koala_data:
        koala_id = koala.get("id")
        if koala_id not in id_to_node_id:
            continue
        
        child_node_id = id_to_node_id[koala_id]
        
        dam_id = koala.get("dam_id")
        sire_id = koala.get("sire_id")
        
        # dam_idで親子関係を追加
        if dam_id and dam_id != "#N/A" and dam_id in id_to_node_id:
            parent_node_id = id_to_node_id[dam_id]
            parent_name = koala_by_id.get(dam_id, {}).get("name", "Unknown")
            edges.append({"parent": parent_node_id, "child": child_node_id, "parent_name": parent_name})
        
        # sire_idで親子関係を追加
        if sire_id and sire_id != "#N/A" and sire_id in id_to_node_id:
            parent_node_id = id_to_node_id[sire_id]
            parent_name = koala_by_id.get(sire_id, {}).get("name", "Unknown")
            edges.append({"parent": parent_node_id, "child": child_node_id, "parent_name": parent_name})
    
    # JSONデータとして出力
    output = {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_koalas": len(nodes),
            "total_edges": len(edges),
            "max_generation": max(generation_map.values()) if generation_map else 0,
            "generations": {str(k): len(v) for k, v in generations.items()}
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
    print(f"総コアラ数: {pedigree_data['metadata']['total_koalas']}")
    print(f"親子関係数: {pedigree_data['metadata']['total_edges']}")
    print(f"最大世代数: {pedigree_data['metadata']['max_generation']}")
    print(f"世代別統計: {pedigree_data['metadata']['generations']}")
    print(f"\n出力ファイル: pedigree_data.json")
