import os
import hashlib
import subprocess
from PIL import Image, ImageDraw, ImageFont

VIDEO_CACHE_DIR = "generated_videos"
ASSETS_DIR = "assets"
os.makedirs(VIDEO_CACHE_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

def wrap_text(text: str, max_chars: int = 40):
    words = text.split()
    lines = []
    current_line = []
    current_len = 0
    for word in words:
        if current_len + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_len += len(word) + 1
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def create_contextual_scene_frame(title: str, visual_type: str, content: str, output_path: str):
    """Har scene ke topic ke anusaar dynamic visual card frame render karta hai."""
    width, height = 1280, 720
    # Professional Dark Classroom Gradient Canvas
    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Accent Top Header Bar
    draw.rectangle([(0, 0), (width, 80)], fill=(30, 58, 138))
    draw.text((40, 25), "🎓 EduAI Interactive Classroom Lesson", fill=(255, 255, 255))

    # Scene Title Badge
    draw.rounded_rectangle([(40, 110), (1240, 180)], radius=10, fill=(30, 41, 59), outline=(59, 130, 246), width=2)
    draw.text((60, 130), f"Topic: {title}", fill=(248, 250, 252))

    # Main Visual Illustration Box (Based on scene content)
    draw.rounded_rectangle([(40, 210), (1240, 670)], radius=12, fill=(2, 6, 23), outline=(71, 85, 105), width=2)

    badge_text = f"MODE: {visual_type.upper()}"
    draw.text((60, 230), badge_text, fill=(56, 189, 248))

    # Render contextual explanation & code/diagram text
    clean_content = content.replace("```python", "").replace("```", "").strip()
    lines = wrap_text(clean_content, max_chars=65)[:14]

    y_offset = 280
    for line in lines:
        if visual_type == "code":
            draw.text((60, y_offset), line, fill=(74, 222, 128))  # Terminal Green
        elif visual_type == "formula":
            draw.text((60, y_offset), line, fill=(251, 191, 36))  # Amber Formula
        else:
            draw.text((60, y_offset), f"• {line}", fill=(226, 232, 240))
        y_offset += 26

    img.save(output_path)

def generate_avatar_video(audio_path: str, title: str = "Concept Explanation", visual_type: str = "bullet_points", visual_content: str = "") -> str:
    """Scene details aur speech audio ko lekar contextual dynamic MP4 video banata hai."""
    file_hash = hashlib.md5((audio_path + title + visual_content).encode()).hexdigest()
    frame_path = os.path.join(ASSETS_DIR, f"frame_{file_hash}.png")
    output_mp4 = os.path.join(VIDEO_CACHE_DIR, f"scene_{file_hash}.mp4")

    if os.path.exists(output_mp4):
        return output_mp4

    # Generate custom frame for this specific topic example
    create_contextual_scene_frame(title, visual_type, visual_content, frame_path)

    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ffmpeg_exe = "ffmpeg"

    cmd = [
        ffmpeg_exe,
        "-y",
        "-loop", "1",
        "-i", frame_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_mp4
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    if os.path.exists(frame_path):
        os.remove(frame_path)

    return output_mp4