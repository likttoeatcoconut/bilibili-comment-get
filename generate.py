import pandas as pd
import json

def generate_fine_tuning_data():
    # 读取Excel文件
    df = pd.read_excel(r'bilibili_videos.xlsx')
    
    # 获取标题和热评列的准确列名
    title_column = df.columns[2]  # 第三列是标题
    comment_column = df.columns[7]  # 第八列是热评
    
    # 创建结果列表
    result = []
    
    # 遍历每一行数据
    for index, row in df.iterrows():
        item = {
            "instruction": "你是一个擅长生成有趣或犀利评论的AI助手。请根据用户提供的视频标题进行评论。",
            "input": str(row[title_column]).strip() if pd.notna(row[title_column]) else "",
            "output": str(row[comment_column]).strip() if pd.notna(row[comment_column]) else ""
        }
        result.append(item)
    
    # 写入JSON文件
    with open('magic_conch.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def generate_jsonl_dataset():
    # 读取Excel文件
    df = pd.read_excel(r'bilibili_videos3_filter.xlsx')

    # 获取标题和热评列的准确列名
    title_column = df.columns[2]  # 第三列是标题
    comment_column = df.columns[7]  # 第八列是热评
    
    # 创建结果列表
    result = []
    
    # 遍历每一条数据
    for index, row in df.iterrows():
        # 构建messages数组
        messages = [
            {"role": "system", "content": "请根据用户提供的视频标题进行评论。"},
            {"role": "user", "content": str(row[title_column]).strip() if pd.notna(row[title_column]) else ""},
            {"role": "assistant", "content": str(row[comment_column]).strip() if pd.notna(row[comment_column]) else ""}
        ]
        
        # 构建符合要求的JSON对象
        json_obj = {
            "messages": messages
        }
        
        result.append(json_obj)
    
    # 写入JSONL文件
    with open('magic_conch2.jsonl', 'w', encoding='utf-8') as f:
        for item in result:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    # generate_fine_tuning_data()
    generate_jsonl_dataset()
    # print("已成功生成 magic_conch.json 和 magic_conch.jsonl 文件")