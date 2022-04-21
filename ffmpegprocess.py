import ffmpeg
from uuid import uuid4


# concatenates a list of videos into one with given width, height and fps
# name of the output video is uuid-generated
def concatenate(video_names, width, height, fps):
    videos = [ffmpeg.input(vid) for vid in video_names]
    data = [videos[i // 2].video.filter('scale', w=width, h=height)
                                .filter('setsar', sar=width / height)
                                .filter('fps', fps=fps)
            if i % 2 == 0 else videos[i // 2].audio for i in range(len(videos) * 2)]
    joined = ffmpeg.concat(*data, v=1, a=1).node
    v3 = joined[0]
    a3 = joined[1]

    out_filename = f"{uuid4()}.mp4"
    out = ffmpeg.output(v3, a3, out_filename)
    out.run()
    return out_filename
