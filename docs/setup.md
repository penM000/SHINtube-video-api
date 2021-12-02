# セットアップ方法

## 実行環境の構築

### docker インストール
dockerのインストールを行います。
```bash
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh
sudo groupadd docker
# sudo 無しで実行するためのオプション設定
sudo usermod -aG docker $USER
# 再ログイン後にsudoなしで実行できることを確認
docker ps
```

### docker-compose インストール
docker-composeのインストールを行います。
最新のバーションについては[こちらから確認できます。][docker-compose]

**注意:docker-compose ver.2から「```docker compose```」にコマンドが変更されています。**
```bash
version=v2.0.1
curl -OL https://github.com/docker/compose/releases/download/$version/docker-compose-linux-x86_64
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo mv docker-compose-linux-x86_64 /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
# docker-composeでも実行できるようにする
cat <<EOF | sudo tee /usr/local/bin/docker-compose
#!/bin/bash
docker compose \$@
EOF
sudo chmod +x /usr/local/bin/docker-compose
```

```bash
docker compose ps
docker-compose ps
```

### nvidia ハードウエアエンコード(オプション)
#### nvidia driverのインストール
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
#### NVIDIA ContainerToolkitのセットアップ
[こちらを参考に][nvidia-docker2]```nvidia-docker2```のインストールを行います。
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```
コンテナ内で```nvidia-smi```が実行できることを確認します
。
```bash
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

+-----------------------------------------------------------------------------+
| NVIDIA-SMI 470.74       Driver Version: 470.74       CUDA Version: 11.4     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Quadro RTX 5000     Off  | 00000000:3B:00.0 Off |                  Off |
| 33%   27C    P8    18W / 230W |     15MiB / 16125MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
```

## SHINtube-video-apiの構築
この章ではSHINtube-video-apiの起動を行います。

githubからレポジトリを取得します。
```bash
git clone https://github.com/penM000/SHINtube-video-api
```

取得したレポジトリ内には、
```docker-compose-general.yml```および```docker-compose-nvenc.yml```があります。
このうちどちらかを、```docker-compose.yml```にコピーします、
nvidiaによるハードウエアエンコードを行う場合には、```docker-compose-nvenc.yml```をコピーしてください。
```bash
cd SHINtube-video-api
# vaapi ソフトウエアエンコード用
cp ./docker-compose-general.yml docker-compose.yml 
# nvenc vaapi ソフトウエアエンコード用
cp ./docker-compose-nvenc.yml docker-compose.yml 
```


```docker-compose.yml```内には、動画の保存場所に関する設定があります。
デフォルトでは、クローンされたレポジトリ内の```video```フォルダを参照しています。
保存先を変更する場合は```./video```を他のパスに変更してください。
```yml
volumes:
  videodata:
    driver: local
    driver_opts:
      type: 'none'
      o: 'bind'
      device: '$PWD/video' # 動画の保尊先として利用するパスに変更する
```

もし、一度作成してしまった場合、上記で宣言したvolumesは削除されません。
そのため、volumesの変更を行う場合は下記のコマンドでvolumesの削除を行う必要があります。
(ホストのバインドマウントの場合はファイルは消えません)
```bash
docker-compose down --volumes --remove-orphans
```



次にコンテナイメージの作成を行います。***注意:nvencの場合時間がかかります***
```bash
docker-compose build --no-cache
```

システムの起動を行います。
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

**注意:「nvenc・vaapi・software」の順にどれか一つが有効になります。**
```bash
curl http://127.0.0.1:8000/encode_test
# 結果
{"vaapi":false,"nvenc_sw_decode1":true,"nvenc_sw_decode2":true,"software":false}
```

[nvidia-docker2]: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker
[docker-compose]: https://github.com/docker/compose/releases