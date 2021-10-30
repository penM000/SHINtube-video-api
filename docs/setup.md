# セットアップ方法

## 実行環境の構築
### docker インストール
dockerのインストールを行います。
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo groupadd docker
# sudo 無しで実行するためのオプション設定
sudo usermod -aG docker $USER
# 再ログイン後にsudoなしで実行できることを確認
docker ps
```

#### nvidia driverのインストール(オプション)
ここではUbuntuでのドライバのインストール方法を解説します。
Ubuntu以外の場合ではCUDA11.4.1に対応したドライバを導入してください。

***注意:セキュアブートが有効な場合は予期しない操作が追加される場合があります。***

搭載されているGPUに対して最適なドライバを検索します
```bash
ubuntu-drivers devices
# 出力
vendor   : NVIDIA Corporation
model    : TU104GL [Quadro RTX 5000]
driver   : nvidia-driver-470 - distro non-free recommended ←推奨ドライバ
driver   : nvidia-driver-460-server - distro non-free
driver   : oem-fix-gfx-nvidia-ondemandmode - third-party free
driver   : nvidia-driver-460 - distro non-free
driver   : nvidia-driver-418-server - distro non-free
driver   : nvidia-driver-450-server - distro non-free
driver   : nvidia-driver-470-server - distro non-free
driver   : xserver-xorg-video-nouveau - distro free builtin
```
今回の例では```nvidia-driver-470```が推奨されているためこれをインストールします。インストール完了後に再起動を行います。
```bash
sudo apt install nvidia-driver-470
sudo reboot
```
再起動後、```nvidia-smi ```を実行し、ドライバが正しく導入されていることを確認します。
```bash
nvidia-smi 
Sat Oct 30 11:18:18 2021       
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 470.74       Driver Version: 470.74       CUDA Version: 11.4     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Quadro RTX 5000     Off  | 00000000:3B:00.0 Off |                  Off |
| 33%   27C    P8    17W / 230W |     15MiB / 16125MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
```


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