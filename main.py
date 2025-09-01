import requests
import time
import hashlib
import pandas as pd
import os
from datetime import datetime
import re


def get_recommend_videos(cookie_value):
    """
    获取B站推荐视频列表
    
    Args:
        cookie_value (str): B站登录后的Cookie值
        
    Returns:
        dict: 推荐视频响应数据
    """

    # 请求URL和参数
    url = "https://api.bilibili.com/x/web-interface/wbi/index/top/feed/rcmd"
    params = {
        "web_location": "1430650",
        "y_num": "4",
        "fresh_type": "3",
        "feed_version": "V8",
        "fresh_idx_1h": "2",
        "fetch_row": "1",
        "fresh_idx": "2",
        "brush": "0",
        "device": "win",
        "homepage_ver": "1",
        "ps": "10",
        "last_y_num": "4",
        "screen": "906-674",
        "seo_info": "",
        "last_showlist": "av_114945890980825,av_114954111816756,av_114941176647118,av_114945857422669,av_n_114913376734531,ad_5614,av_114947551991715,av_n_114941461796206,av_n_114947250001846,av_n_114906665980026;av_n_114924986635761,av_n_114935287779286,av_n_114907253049538,av_n_114949296754219,av_n_114952853525709,ad_n_5637,av_n_114917738812051,av_n_114827041184017,av_n_114845898773470,av_n_114952350205245,av_n_114923728341723,av_n_114930204346466",
        "uniq_id": "108641565034",
        "w_rid": "8b6ff8452b9f67df1e890238b9ad696b",
        "wts": "1754119379"
    }

    # 请求头
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "origin": "https://www.bilibili.com",
        "priority": "u=1, i",
        "referer": "https://www.bilibili.com/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        "Cookie": cookie_value
    }

    # 发送GET请求
    response = requests.get(url, params=params, headers=headers)

    # 返回JSON响应
    return response.json()


def extract_video_info(json_data):
    """
    从返回的JSON数据中提取视频信息
    
    Args:
        json_data (dict): B站API返回的JSON数据
        
    Returns:
        list: 包含视频信息的列表
    """
    video_list = []

    # 检查响应是否成功
    if json_data and json_data.get("code") == 0:
        # 提取视频数据数组
        data = json_data.get("data", {})
        items = data.get("item", [])

        # 遍历视频数组，提取需要的信息
        for item in items:
            # 对item进行空值检查
            if not item:
                continue

            # 安全地提取owner信息
            owner = item.get("owner", {}) if item.get("owner") is not None else {}

            # 安全地提取stat信息
            stat = item.get("stat", {}) if item.get("stat") is not None else {}
            if item.get("id") == 0:
                continue
            video_info = {
                "aid": item.get("id", "") if item.get("id") is not None else "",  # 视频av号
                "bvid": item.get("bvid", "") if item.get("bvid") is not None else "",  # 视频bv号
                "title": item.get("title", "") if item.get("title") is not None else "",  # 视频标题
                "author": owner.get("name", "") if owner.get("name") is not None else "",  # 作者名
                "duration": item.get("duration", 0) if item.get("duration") is not None else 0,  # 视频时长
                "view_count": stat.get("view", 0) if stat.get("view") is not None else 0,  # 播放量
                "like_count": stat.get("like", 0) if stat.get("like") is not None else 0,  # 点赞数
                "cover_url": item.get("pic", "") if item.get("pic") is not None else "",  # 封面图片URL
            }
            video_list.append(video_info)

    return video_list


def print_video_info(video_list):
    """
    打印视频信息
    
    Args:
        video_list (list): 视频信息列表
    """
    if not video_list:
        print("没有找到视频数据")
        return

    print(f"共找到 {len(video_list)} 个视频:")
    print("-" * 100)

    for i, video in enumerate(video_list, 1):
        print(f"{i}. 标题: {video['title']}")
        print(f"   AV号: {video['aid']}")
        print(f"   BV号: {video['bvid']}")
        print(f"   作者: {video['author']}")
        print(f"   时长: {video['duration']}秒")
        print(f"   播放量: {video['view_count']}")
        print(f"   点赞数: {video['like_count']}")
        print(f"   封面: {video['cover_url']}")
        print(f"   热评: {video['top1_comment']}")

        print("-" * 100)


class CommentListRequestDTO:
    """
    评论列表请求DTO，对应Java中的CommentListRequestDTO类
    """

    def __init__(self, oid, jsonp="jsonp", next_page=1, type_val=1, mode=3, plat=1, timestamp=1146258991018):
        """
        初始化评论列表请求参数
        
        Args:
            oid (int): 视频ID
            jsonp (str): JSONP标识，默认为"jsonp"
            next_page (int): 下一页标识，默认为1
            type_val (int): 评论类型，默认为1 (视频评论)
            mode (int): 排序模式，默认为3
            plat (int): 平台类型，默认为1
            timestamp (int): 时间戳，默认为1146258991018
        """
        self.oid = oid
        self.jsonp = jsonp
        self.next = next_page
        self.type = type_val
        self.mode = mode
        self.plat = plat
        self.timestamp = timestamp

    def to_map(self):
        """
        将对象属性转换为字典，用于查询参数
        
        Returns:
            dict: 包含所有属性的字典
        """
        params = {
            "oid": self.oid,
            "jsonp": self.jsonp,
            "next": self.next,
            "type": self.type,
            "mode": self.mode,
            "plat": self.plat,
            "_": self.timestamp
        }
        return params


def get_comment_list(params, cookie_value):
    """
    获取视频评论列表
    
    Args:
        params (dict): 请求参数字典
        cookie_value (str): B站登录后的Cookie值
        
    Returns:
        dict: 评论列表响应数据
    """

    # 请求URL
    url = "https://api.bilibili.com/x/v2/reply/main"

    # 请求头
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "origin": "https://www.bilibili.com",
        "priority": "u=1, i",
        "referer": "https://www.bilibili.com/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        "Cookie": cookie_value
    }

    # 发送GET请求
    response = requests.get(url, params=params, headers=headers)
    print(response)
    # 返回JSON响应
    return response.json()


def get_video_and_comment(cookie):
    try:
        # 获取推荐视频
        result = get_recommend_videos(cookie)

        # 提取视频信息
        videos = extract_video_info(result)
        rs = []
        # 打印视频信息
        for video in videos:
            # 延迟1s
            time.sleep(1)
            dto = CommentListRequestDTO(oid=video['aid'])
            comment_list = get_comment_list(dto.to_map(), cookie)
            if comment_list.__sizeof__() > 0:
                if 'data' in comment_list and 'replies' in comment_list['data'] and comment_list['data']['replies']:
                    video['top1_comment'] = comment_list['data']['replies'][0]['content']['message']
                else:
                    video['top1_comment'] = "无评论"
        return videos
    except Exception as e:
        print(f"请求失败: {e}")
        # 打印堆栈


def clean_excel_string(text):
    """
    清理Excel不支持的非法字符
    
    Args:
        text (str): 需要清理的文本
        
    Returns:
        str: 清理后的文本
    """
    if not isinstance(text, str):
        return text
    
    # Excel不支持的字符包括：x00-x08, x0B-x0C, x0E-x1F, x7F-x9F
    # 使用正则表达式移除这些字符
    cleaned_text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    return cleaned_text


def save_to_excel(videos, filename="bilibili_videos.xlsx"):
    """
    将视频信息保存到Excel文件中
    
    Args:
        videos (list): 视频信息列表
        filename (str): Excel文件名
    """
    # 准备数据
    data = []
    for video in videos:
        data.append({
            'AV号': clean_excel_string(video.get('aid', '')),
            'BV号': clean_excel_string(video.get('bvid', '')),
            '标题': clean_excel_string(video.get('title', '')),
            '作者': clean_excel_string(video.get('author', '')),
            '时长(秒)': video.get('duration', 0),
            '播放量': video.get('view_count', 0),
            '点赞数': video.get('like_count', 0),
            '热评': clean_excel_string(video.get('top1_comment', '')),
            '获取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    # 创建DataFrame
    new_df = pd.DataFrame(data)

    # 如果文件存在，则读取现有数据并追加
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_excel(filename, index=False)
        print(f"数据已追加到 {filename}，共 {len(combined_df)} 条记录")
    else:
        # 文件不存在，创建新文件
        new_df.to_excel(filename, index=False)
        print(f"新文件 {filename} 已创建，共 {len(new_df)} 条记录")


def loop_get_videos_and_comments(cookie, loop_count=3, delay=5):
    """
    循环获取视频和评论信息并保存到Excel
    
    Args:
        cookie (str): B站Cookie
        loop_count (int): 循环次数
        delay (int): 每次请求间隔时间（秒）
    """
    all_videos = []

    for i in range(loop_count):
        print(f"第 {i + 1} 次获取视频信息...")
        videos = get_video_and_comment(cookie)
        if videos:
            all_videos.extend(videos)
            print(f"第 {i + 1} 次获取到 {len(videos)} 个视频")
        else:
            print(f"第 {i + 1} 次未获取到视频信息")

        # 避免请求过于频繁
        if i < loop_count - 1:  # 最后一次不需要延迟
            time.sleep(delay)

    return all_videos


if __name__ == "__main__":
    cookie = "[B站cookie]"
    i = 0
    while i < 100:
        # 循环获取视频和评论信息
        videos = loop_get_videos_and_comments(cookie, loop_count=100, delay=5)

        # 保存到Excel文件
        if videos:
            save_to_excel(videos, "bilibili_videos3.xlsx")
        else:
            print("未获取到任何视频信息")

        # 打印视频信息
        print_video_info(videos)
        i += 1