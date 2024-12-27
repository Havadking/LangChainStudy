import json
import os

import requests
from moviepy import ImageSequenceClip, VideoFileClip, AudioFileClip, concatenate_videoclips
from zhipuai import ZhipuAI
from pydub import AudioSegment

from src.reading.rag_full.rag_langchain import resolve_assets

client = ZhipuAI(api_key="5db19c1ae349cab11aff7a42bae9fbbb.vVLtpm7VpSf8WQDY")


def save_story(data, name):
    file_path = "../resources/story/" + str(name) + ".md"

    # 将 story 保存为 Markdown 文件
    with open(file_path, "w", encoding="utf-8") as md_file:
        md_file.write("# 生成的故事内容\n\n")  # 添加标题
        md_file.write(data)

    print(f"故事内容已成功保存为 Markdown 文件：{file_path}")


def generate_image(back_ground, uid, no):
    """
    生成图片
    """
    print(f"开始生成第{no}个图片")
    prompt = "根据下列我提供的背景表述，生成一张卡通风格的绘本图片。背景图片的描述为: " + back_ground

    response = client.images.generations(
        model="cogview-3-plus",
        prompt=prompt,
    )
    print(response.data[0].url)
    url = response.data[0].url
    os.makedirs("../resources/picture/" + str(uid), exist_ok=True)
    save_path = "../resources/picture/" + str(uid) + "/" + str(uid) + "-" + str(no) + ".png"  # 保存到本地的文件名
    # print("save_path:" + save_path)
    # 下载文件
    download_file(url, save_path)
    print(f"文件已保存到: {save_path}")
    return save_path


def download_file(url, save_path):
    """
    下载文件并保存到指定路径
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        # print("文件下载完成")
    except Exception as e:
        print(f"下载文件时出错: {e}")


def generate_voice(dialog, uid, no):
    print(f"开始生成第{no}个语音")
    """
    生成语音
    """
    res = requests.post('http://36.212.164.141:9966/tts', data={
        "text": dialog,
        "prompt": "[break_6]",
        "voice": "7777.pt",
        "speed": 4,
        "temperature": 0.1,
        "top_p": 0.701,
        "top_k": 20,
        "refine_max_new_token": 384,
        "infer_max_new_token": 2048,
        "text_seed": 42,
        "skip_refine": 0,
        "custom_voice": 0
    })
    # print(res.json())

    # 检查响应是否成功
    if res.status_code == 200:
        response_data = res.json()
        if response_data.get("code") == 0:
            url = response_data["url"]  # 获取文件的 URL
            os.makedirs("../resources/audio/" + str(uid), exist_ok=True)
            save_path = "../resources/audio/" + str(uid) + "/" + str(uid) + "-" + str(no) + ".wav"  # 保存到本地的文件名
            # print("save_path:" + save_path)
            # 下载文件
            download_file(url, save_path)
            print(f"文件已保存到: {save_path}")
            return save_path
        else:
            print(f"生成语音失败，服务器返回错误: {response_data['msg']}")
    else:
        print(f"请求失败，HTTP 状态码: {res.status_code}")


def save_script(data: dict, name: int):
    file_path = "../resources/script/" + str(name) + ".json"
    # 将字典保存为 JSON 文件
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(f"字典已成功保存到 {file_path}")


def generate_video_without_audio(image_list, scene_switch_points, audio_duration, fps, output_path):
    """
    根据图片、场景切换点、音频时长生成无声视频。
    参数：
    - image_list: 图片路径列表。
    - scene_switch_points: 场景切换时间点（秒），列表中的值为切换时间点。
    - audio_duration: 音频总时长（秒）。
    - fps: 视频帧率（帧/秒）。
    - output_path: 输出视频文件路径。
    """
    # 计算需要插入的图片的总数
    audio_duration += 7
    total_frames = int(audio_duration * fps)
    current_image_index = 0
    frames = []

    image_list.sort(key=lambda x: int(x.split('-')[-1].split('.')[0]))
    print(image_list)
    print(scene_switch_points)

    # 遍历每个时间点生成帧
    for frame in range(total_frames):
        current_time = frame / fps  # 当前帧的时间点
        # 检查是否需要切换场景
        if current_image_index < len(scene_switch_points) and current_time >= scene_switch_points[current_image_index]:
            current_image_index += 1

        # 限制图片索引不超出范围
        current_image_index = min(current_image_index, len(image_list) - 1)
        # 添加当前图片的路径
        frames.append(image_list[current_image_index])

    # 生成无声视频
    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile(output_path, codec="libx264", audio=False)


def combine_wav_files(folder_path, output_path):
    """
    读取文件夹中的 .wav 文件，获取时长并合并成一个大的 .wav 文件。

    参数：
    - folder_path: 包含 .wav 文件的文件夹路径。
    - output_path: 合并后保存的文件路径。

    返回：
    - durations: 每个 .wav 文件的时长数组（单位：秒）。
    """

    # 1.获取文件夹中的所有.wav 文件
    wav_files = [f for f in os.listdir(folder_path) if f.endswith(".wav")]

    # 2.按文件名后缀排序
    wav_files.sort(key=lambda x: int(x.split('-')[-1].split('.')[0]))

    durations = []
    combined_audio = AudioSegment.empty()

    # 3.循环处理所有的语音文件
    for wav_file in wav_files:
        # 3.1 读取.wav 文件
        audio = AudioSegment.from_wav(os.path.join(folder_path, wav_file))
        # 3.2 获取音频的时长并保存
        duration = int(len(audio) / 1000)
        durations.append(duration)
        # 3.3 合并音频
        combined_audio += audio

    # 4.保存合并后的音频文件
    combined_audio.export(output_path, format="wav")
    sum_duration = sum(durations)
    durations = cumulative_sum(durations)
    return durations, sum_duration


def get_all_file_paths(folder_path):
    """
    读取指定路径下的所有文件，并返回文件的绝对路径列表。

    参数：
    - folder_path: 要读取文件的文件夹路径。

    返回：
    - file_paths: 包含所有文件绝对路径的数组。
    """
    file_paths = []

    # 遍历文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 获取文件的绝对路径
            absolute_path = os.path.abspath(os.path.join(root, file))
            file_paths.append(absolute_path)

    return file_paths


def cumulative_sum(arr):
    """
    将数组中的每个值转换成它和之前所有值的和。

    参数：
    - arr: 原始数组。

    返回：
    - result: 转换后的数组。
    """
    result = []
    cumulative = 0
    for value in arr:
        cumulative += value
        result.append(cumulative)
    return result


def combine_video_audio(video_path, audio_path, output_path):
    """
    将视频和音频合并成一个有声视频。

    参数：
    - video_path: 输入视频文件的路径。
    - audio_path: 输入音频文件的路径。
    - output_path: 输出有声视频的路径。
    """
    # 读取视频文件
    video_clip = VideoFileClip(video_path)

    # 读取音频文件
    audio_clip = AudioFileClip(audio_path)


    # 确保音频和视频的时长一致
    audio_clip = audio_clip.subclipped(0, min(video_clip.duration, audio_clip.duration))
    video_clip = video_clip.subclipped(0, min(video_clip.duration, audio_clip.duration))

    # 将音频添加到视频
    video_with_audio = video_clip.with_audio(audio_clip)

    # 保存有声视频
    video_with_audio.write_videofile(output_path, codec="libx264", audio_codec="aac")

def generate_video(uid):
    """
    生成视频
    """
    # 获取语音和图片的地址
    audio_folder = resolve_assets("../resources/audio/" + str(uid))
    image_folder = resolve_assets("../resources/picture/" + str(uid))
    video_folder = resolve_assets("../resources/video/" + str(uid))
    os.makedirs(video_folder, exist_ok=True)
    print(image_folder + "/final.mp4")
    print(audio_folder + "/final.wav")
    # 读取图片和音频的地址
    image_list = get_all_file_paths(image_folder)

    # 语音合成并获取每个语音时长
    print("开始进行语音合成")
    durations, sum_duration = combine_wav_files(audio_folder, audio_folder + "/final.wav")
    print(f"语音合成完成,总时长为{sum_duration}秒")

    # 合成无声视频
    print("开始进行视频合成")
    generate_video_without_audio(image_list, durations, sum_duration, 24,
                                 image_folder + "/final.mp4")
    print("视频合成完成")

    # 开始合成有声视频
    print("开始合成有声视频")
    combine_video_audio(image_folder + "/final.mp4", audio_folder + "/final.wav",
                        video_folder + "/final.mp4")
    print("有声视频合成成功")


