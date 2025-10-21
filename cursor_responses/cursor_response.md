# CUDA/CuDNN 版本不相容問題解決方案

## 問題分析

您遇到的問題是 CUDA/CuDNN 版本不相容，導致 PyTorch 無法載入所需的 GPU 加速庫，導致程式崩潰。

### 錯誤核心說明
- **首要錯誤**：`ImportError: /usr/local/lib/libcudnn.so.8: version 'libcudnn.so.8' not found (required by /usr/local/lib/python3.6/dist-packages/torch/lib/libtorch_python.so)`
- **根本原因**：PyTorch 1.10 需要 cuDNN 8 版，但系統實際上只有 cuDNN 7.x (`libcudnn.so.7.6.3`)
- **錯誤做法**：用軟連結硬繞製造了 `libcudnn.so.8`，這種做法會在執行期造成錯誤

### 其他警告/提示
- 對 CUDA 的庫檔案也有多個相容性警告或找不到，例如 `libcublas.so.10` `libcurand.so.10` `libcufft.so.10` 等等
- `PyTorch 1.10 requires cuDNN 8`，官方明確要求環境需升級
- `Upgrade JetPack to 4.6.x (L4T r32.7.x) or install libcudnn8 on the host.`

## 解決方案

### 方案一：升級 JetPack（推薦）

```bash
# 檢查當前 JetPack 版本
cat /etc/nv_tegra_release

# 升級到 JetPack 4.6.x 或更新版本
sudo apt update
sudo apt upgrade
sudo apt install nvidia-jetpack
```

### 方案二：手動安裝 cuDNN 8

1. **下載正確的 cuDNN 8 版本**：
```bash
# 下載 cuDNN 8.6.0 for Jetson (arm64/aarch64)
wget https://developer.download.nvidia.com/compute/cudnn/8.6.0/local_installers/8.6.0.163/cudnn-linux-aarch64-8.6.0.163_cuda11-archive.tar.xz
```

2. **安裝 cuDNN 8**：
```bash
# 解壓縮
tar -xvf cudnn-linux-aarch64-8.6.0.163_cuda11-archive.tar.xz

# 複製庫文件
sudo cp cudnn-linux-aarch64-8.6.0.163_cuda11-archive/include/cudnn*.h /usr/local/cuda/include
sudo cp cudnn-linux-aarch64-8.6.0.163_cuda11-archive/lib/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*

# 創建正確的符號連結
cd /usr/local/cuda/lib64
sudo ln -sf libcudnn.so.8.6.0 libcudnn.so.8
sudo ln -sf libcudnn.so.8 libcudnn.so
```

3. **更新庫路徑**：
```bash
# 更新 ldconfig
sudo ldconfig

# 驗證安裝
ldconfig -p | grep cudnn
```

### 方案三：使用相容的 PyTorch 版本

如果無法安裝 cuDNN 8，可以降級到與 cuDNN 7 相容的 PyTorch 版本：

```bash
# 卸載當前 PyTorch
pip3 uninstall torch torchvision torchaudio

# 安裝與 cuDNN 7 相容的 PyTorch 1.9
pip3 install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
```

## 驗證修復

安裝完成後，驗證修復：

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"cuDNN version: {torch.backends.cudnn.version()}")
```

## 避免的錯誤做法

❌ **不要這樣做**：
```bash
# 錯誤：用 cuDNN 7 偽裝成 cuDNN 8
sudo ln -sf libcudnn.so.7.6.3 libcudnn.so.8
```

✅ **正確做法**：
- 安裝真正的 cuDNN 8 版本
- 確保版本號匹配 PyTorch 要求
- 使用正確的架構版本（arm64/aarch64 for Jetson）

## 額外建議

1. **檢查 CUDA 版本相容性**：
   - PyTorch 1.10 需要 CUDA 11.1+
   - 確保 CUDA 版本與 cuDNN 版本相容

2. **Docker 環境注意事項**：
   - 如果使用 Docker，確保基礎映像包含正確的 CUDA/cuDNN 版本
   - 考慮使用 NVIDIA 官方 PyTorch Docker 映像

3. **環境變數設定**：
```bash
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export CUDA_HOME=/usr/local/cuda
```

## 中文快速結論

您目前的 Jetson Nano Docker 環境缺少正確版本的 cuDNN 8，導致 PyTorch 找不到必需的 GPU 加速庫（cuDNN v8）。要解決請升級 JetPack 或安裝真正的 cuDNN 8，避免只用軟連結 fake 版本，否則一定會出錯。