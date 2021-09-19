# エンコーダーについて
本システムでは、ffmpegを用いて、動画のデコード、エンコードを行っています。
入力可能な動画形式は下記を参照してください。
# nvidia (nvenc)
下記ページのデコード表に対応しているものが入力できます。
[Video Encode and Decode GPU Support Matrix](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new)
# intel (vaapi)
Hardware Supportのに表記されているものが利用可能です。
ただし、vaapiでは、ハードウエアデコードできないものはソフトウエアデコードが実行されます。
[QuickSync](https://trac.ffmpeg.org/wiki/Hardware/QuickSync)
# ソフトウエア (CPU)
ffmpegが対応している形式が利用可能です。