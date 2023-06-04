mkdir conv
FOR /F "tokens=*" %%G IN ('dir /b *.mp4') DO C:\bin\ffmpeg.6.0\bin\ffmpeg.exe -i "%%G" -vcodec libx264 -acodec aac "conv\%%G"

