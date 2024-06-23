import yt_dlp
import ffmpeg
import re
import os
import shutil

def time_str_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    raise ValueError("Invalid time format. Please use 'min:sec'.")

def clean_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def download_and_convert_youtube_video(url, start_time, end_time, download_full=False, include_audio=True):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4' if include_audio else 'bestvideo[ext=mp4]',
            'outtmpl': 'temp_video.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')
        
        output_filename = clean_filename(video_title) + ".mov"
        
        print("Converting and trimming video...")
        
        input_args = {'ss': start_time, 't': end_time-start_time} if not download_full else {}
        
        input_stream = ffmpeg.input('temp_video.mp4', **input_args)
        
        if include_audio:
            output = (
                input_stream
                .output(output_filename, vcodec='libx264', acodec='aac', 
                        video_bitrate='5000k', audio_bitrate='192k')
            )
        else:
            output = (
                input_stream
                .output(output_filename, vcodec='libx264', video_bitrate='5000k', an=None)
            )
        
        output.overwrite_output().run(capture_stdout=True, capture_stderr=True)
        
        os.remove('temp_video.mp4')  
        print(f"Video downloaded, converted, and saved to {output_filename}")
        
        video_dir = 'video'  
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
        
        shutil.move(output_filename, os.path.join(video_dir, output_filename))
        print(f"Moved {output_filename} to {video_dir}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    url = input("Enter the YouTube URL: ")
    
    download_full = input("Download full video? (y/n): ").lower() == 'y'
    include_audio = input("Include audio? (y/n): ").lower() == 'y'
    
    if not download_full:
        start_time_str = input("Enter the start time (min:sec): ")
        end_time_str = input("Enter the end time (min:sec): ")
        start_time = time_str_to_seconds(start_time_str)
        end_time = time_str_to_seconds(end_time_str)
    else:
        start_time = end_time = 0
    
    download_and_convert_youtube_video(url, start_time, end_time, download_full, include_audio)
