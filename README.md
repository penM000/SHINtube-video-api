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
### SHINtube-video-api
- docker インストール


- 任意の場所でGitのリポジトリをクローン
```bash
git clone https://github.com/penM000/SHINtube-video-api
```

- 使用するハードウエアエンコードを選択
```bash
# vaapi ソフトウエアエンコード用
cp ./docker-compose-general.yml docker-compose.yml 
# nvenc vaapi ソフトウエアエンコード用
cp ./docker-compose-nvenc.yml docker-compose.yml 
```
- 動画保保存する場所
```yml
volumes:
  videodata:
    driver: local
    driver_opts:
      type: 'none'
      o: 'bind'
      device: './video' # 動画の保尊先として利用するパスに変更する
```

- コンテナイメージの作成(nvencの場合時間がかかります)
```bash
docker-compose build --no-cache
```
- 起動
```bash
docker-compose up -d
```

- 起動確認
```bash
curl http://127.0.0.1:8000/
# 結果
{"message":"Hello Bigger Applications!"}
```

- エンコードテスト
期待するエンコーダーが利用可能であることを確認
※softwareは他が利用不可の時のみ利用可能
```bash
curl http://127.0.0.1:8000/encode_test
# 結果
{"vaapi":true,"nvenc_hw_decode":true,"nvenc_sw_decode":true,"software":false}
```



## ドキュメンテーション
 - [LMSへの登録について](./docs/RegistrationLMS.md)
 - [configファイルについて](./docs/ConfigSetting.md)
 - [動画のアップロードについて](./docs/SHINtubeManual.md#動画のアップロード・編集)
 - [DeepLinkについて](./docs/SHINtubeManual.md#DeepLinkについて)
 - [グレーディングサービスについて](./docs/SHINtubeManual.md#グレーディングサービスについて)
 - [利用規約について](./docs/AboutManual.md)

## 貢献
[GitHub](https://github.com/kuropengin/SHINtube)で私たちに⭐を頂けると嬉しいです！

バグを見つけたり、理解しにくいと感じた場合は、遠慮なく[問題](.github/CONTRIBUTING.md)を開いてください。

## 特別な感謝
開発全体を通してサポートしてくれた信州大学およびバックエンド開発者の[penM000](https://github.com/penM000)に感謝します。

## Licence
[LICENSE](.github/LICENSE)

