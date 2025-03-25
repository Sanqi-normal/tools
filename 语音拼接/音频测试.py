import pypinyin
from pydub import AudioSegment
from pydub.playback import play
import os
import winsound
from pathlib import Path

# 拼音音频片段目录
PINYIN_DIR = "C:\\Users\\*\\Music\\demo\\pinyin_segments"  # 替换为你的拼音音频保存目录

def get_pinyin(text):
    """将输入文字转换为带声调的拼音序列"""
    pinyin_list = pypinyin.pinyin(text, style=pypinyin.TONE, errors='ignore')
    return [item[0] for item in pinyin_list if item]

def play_pinyin_sequence(pinyins):
    """按顺序播放拼音音频"""
    for pinyin in pinyins:
        audio_path = f"{PINYIN_DIR}/{pinyin}.wav"
        if Path(audio_path).exists():
            print(f"播放: {pinyin}")
            # 使用 winsound 播放音频（Windows 专用）
            winsound.PlaySound(audio_path, winsound.SND_FILENAME)
        else:
            print(f"拼音音频缺失: {pinyin}，跳过")

def main():
    print("拼音语音播放测试工具")
    print("输入中文文字，按 Enter 播放，输入 'exit' 退出")
    
    while True:
        # 获取用户输入
        text = input("请输入文字: ").strip()
        
        if text.lower() == 'exit':
            print("退出程序")
            break
        
        if not text:
            print("输入为空，请重新输入")
            continue
        
        # 转换为拼音
        pinyins = get_pinyin(text)
        print(f"拼音序列: {pinyins}")
        
        # 播放拼音音频
        play_pinyin_sequence(pinyins)

if __name__ == "__main__":
    # 安装依赖：pip install pypinyin
    main()
