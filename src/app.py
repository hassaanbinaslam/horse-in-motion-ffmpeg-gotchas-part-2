# src/app.py
import os
import boto3
import requests
import subprocess

OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET")
s3_client = boto3.client("s3")
TMP_DIR = "/tmp"


def download_frames():
    """Downloads the 15 horse frames into /tmp/video_frames"""
    frames_dir = os.path.join(TMP_DIR, "video_frames")
    os.makedirs(frames_dir, exist_ok=True)

    base_url = "https://raw.githubusercontent.com/hassaanbinaslam/myblog/5c15e72dde03112c5c8dea177bfed7c835aca399/posts/images/2025-07-28-the-horse-in-motion-ffmpeg-gotchas-part-1/video_frames"

    for i in range(1, 16):
        frame_number = str(i).zfill(2)
        image_url = f"{base_url}/frame{frame_number}.png"
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(os.path.join(frames_dir, f"frame{frame_number}.png"), "wb") as f:
                f.write(response.content)

    print("All frames downloaded.")
    # print("List the files names downloaded")
    # print(os.listdir(frames_dir))


def lambda_handler(event, context):
    try:
        print("Starting video creation process...")
        download_frames()

        # Paths in the Lambda's writable /tmp directory
        input_path = os.path.join(TMP_DIR, "video_frames/frame%02d.png")
        output_path = os.path.join(TMP_DIR, "output.mp4")

        # Path to the font file packaged with our function
        font_file = "./fonts/LiberationSans-Regular.ttf"

        # When a layer is used, its contents are available in the /opt directory.
        # Our FFmpeg binary is therefore at /opt/bin/ffmpeg.
        ffmpeg_cmd = [
            "/opt/bin/ffmpeg",
            "-stream_loop",
            "-1",
            "-framerate",
            "1.5",
            "-i",
            input_path,
            "-vf",
            f"drawtext=fontfile={font_file}:text='The Horse in Motion and FFmpeg Gotchas Part 3':fontcolor=white:fontsize=13:box=1:boxcolor=black@0.8:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,10)'",
            "-c:v",
            "libx264",  # THE PAYOFF: We can now use the superior encoder!
            "-r",
            "30",
            "-pix_fmt",
            "yuv420p",
            "-t",
            "40",
            output_path,
        ]

        print(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")

        # Execute the FFmpeg command
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)

        print("FFmpeg stdout:", result.stdout)
        print("FFmpeg stderr:", result.stderr)

        print(f"FFmpeg command successful. Uploading {output_path} to S3.")

        s3_client.upload_file(output_path, OUTPUT_BUCKET, "horse-in-motion.mp4")

        return {
            "statusCode": 200,
            "body": "Successfully created and uploaded horse-in-motion.mp4 to S3.",
        }

    except subprocess.CalledProcessError as e:
        print("FFmpeg failed to execute.")
        print("Return code:", e.returncode)
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        raise e
    except Exception as e:
        print(e)
        raise e
