# SHINtube-video-api
Video sharing platform for Shinshu University.

SHINtube-video-apiはffmpegを利用して動画のエンコード、配信を行う動画配信プラットフォームのバックエンドです。
利用の際はフロントエンドの[kuropengin/SHINtube](https://github.com/kuropengin/SHINtube)及び、LTIが利用可能なLMSが必要になります。


## 機能
- エンコード管理
- エンコードエンジン
    - nvenc
    - vaapi
    - ソフトウエア
- 動画配信

## 動作環境
### 動作確認済み環境
- Linux 
- python 3.8 以上

### 推奨環境
- ハードウエアエンコードが可能なシステム
    - vaapi(intel Kabylake以上)
    - nvenc(NVIDIA Turing TU116 以上)
- docker-compose

## セットアップ
[こちらを参照][setup]



## Licence
[LICENSE](.github/LICENSE)

[setup]: docs/setup.md

