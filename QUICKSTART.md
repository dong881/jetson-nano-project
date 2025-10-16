# Snake Game with RL - Quick Start Guide

## 快速開始指南 (Quick Start Guide)

### 簡介 (Introduction)

這是一個完整的貪食蛇遊戲，具有以下特點：
- 人類可玩模式（使用方向鍵操控）
- AI 訓練模式（觀看機器人學習玩遊戲）
- 完整的 UI 界面
- 為 Jetson Nano 優化，支援 CUDA 加速

This is a complete Snake game with:
- Human playable mode (arrow key controls)
- AI training mode (watch the robot learn to play)
- Complete UI interface
- Optimized for Jetson Nano with CUDA support

---

## 安裝方式 (Installation Methods)

### 方法 1: 標準安裝 (Method 1: Standard Installation)

```bash
# 1. 克隆專案 (Clone the project)
git clone https://github.com/dong881/jetson-nano-project.git
cd jetson-nano-project

# 2. 安裝依賴 (Install dependencies)
pip install -r requirements.txt

# 3. 運行遊戲 (Run the game)
python main.py
```

### 方法 2: Jetson Nano 一鍵安裝 (Method 2: Jetson Nano One-Click Setup)

```bash
# 在 Jetson Nano 上執行設置腳本 (Run setup script on Jetson Nano)
chmod +x setup_jetson.sh
./setup_jetson.sh

# 啟動遊戲 (Launch game)
./run.sh
```

### 方法 3: Docker 部署 (Method 3: Docker Deployment) - 推薦 Jetson Nano 使用

```bash
# 1. 允許 X11 連接 (Allow X11 connections)
xhost +local:docker

# 2. 使用 Docker Compose 構建並運行 (Build and run with Docker Compose)
docker-compose up --build
```

---

## 遊戲規則 (Game Rules)

1. **目標**: 吃到紅色蘋果讓蛇身增長，獲得分數
   - **Goal**: Eat red apples to grow the snake and score points

2. **控制**: 使用方向鍵移動（上下左右）
   - **Controls**: Use arrow keys to move (up, down, left, right)

3. **失敗條件**:
   - 撞到邊界牆壁
   - 撞到自己的身體
   - **Game Over Conditions**:
     - Hit the boundary walls
     - Hit your own body

4. **計分系統**:
   - 每吃一個蘋果：+1 分
   - 記錄歷史最高分
   - **Scoring System**:
     - Each apple: +1 point
     - High score is saved

---

## 使用說明 (Usage Instructions)

### 人類遊玩模式 (Human Play Mode)

1. 啟動程式後，預設為人類遊玩模式
   - The program starts in human play mode by default

2. 使用方向鍵控制蛇的移動：
   - Use arrow keys to control the snake:
   - ↑ 向上 (Up)
   - ↓ 向下 (Down)
   - ← 向左 (Left)
   - → 向右 (Right)

3. 嘗試吃到蘋果並避免撞牆或撞到自己
   - Try to eat apples and avoid walls or yourself

4. 遊戲結束後會自動重置
   - Game resets automatically after game over

### AI 訓練模式 (AI Training Mode)

1. 點擊「Switch to Training」按鈕切換到訓練模式
   - Click "Switch to Training" button to switch to training mode

2. AI 會自動開始訓練
   - AI will start training automatically

3. 右側面板顯示訓練統計：
   - Right panel shows training statistics:
   - 當前分數 (Current score)
   - 記錄分數 (Record score)
   - 遊戲次數 (Games played)

4. 當 AI 達到新紀錄時，模型會自動保存
   - Model is automatically saved when AI achieves new record

5. 可點擊「Save Model」手動保存訓練進度
   - Click "Save Model" to manually save training progress

6. 切換回人類模式時會自動保存當前訓練進度
   - Training progress is automatically saved when switching back to human mode

### 按鈕說明 (Button Functions)

- **Switch to Training / Switch to Human**: 切換遊戲模式
  - Toggle between game modes

- **Reset Game**: 重置當前遊戲
  - Reset current game

- **Save Model**: 手動保存 AI 模型（僅訓練模式可用）
  - Manually save AI model (training mode only)

---

## API 使用 (API Usage)

### 為自定義 RL Agent 使用 API (Using API for Custom RL Agents)

```python
from snake_game import SnakeGameAI
from agent import Agent

# 初始化遊戲和 Agent (Initialize game and agent)
game = SnakeGameAI()
agent = Agent()

# 訓練循環 (Training loop)
while True:
    # 獲取當前狀態 (Get current state)
    state = agent.get_state(game)
    
    # 從 Agent 獲取動作 (Get action from agent)
    action = agent.get_action(state)
    
    # 執行動作 (Perform action)
    reward, game_over, score = game.play_step(action)
    
    # 訓練 Agent (Train agent)
    agent.train_short_memory(state, action, reward, next_state, game_over)
    
    if game_over:
        game.reset()
        agent.train_long_memory()
```

### 狀態表示 (State Representation)

遊戲狀態是一個 11 維向量：
The game state is an 11-dimensional vector:

1-3. 危險檢測（直走、右轉、左轉）
     - Danger detection (straight, right, left)

4-7. 移動方向（左、右、上、下）
     - Moving direction (left, right, up, down)

8-11. 食物位置（左、右、上、下）
      - Food location (left, right, up, down)

### 動作空間 (Action Space)

- `[1, 0, 0]`: 直走 (Continue straight)
- `[0, 1, 0]`: 右轉 (Turn right)
- `[0, 0, 1]`: 左轉 (Turn left)

---

## 訓練細節 (Training Details)

### 超參數 (Hyperparameters)

- 學習率 (Learning Rate): 0.001
- 折扣因子 (Gamma): 0.9
- 探索率 (Epsilon): 80 - n_games
- 批次大小 (Batch Size): 1000
- 記憶體大小 (Memory Size): 100,000
- 隱藏層大小 (Hidden Layer): 256

### 獎勵系統 (Reward System)

- +10: 吃到蘋果 (Eating an apple)
- -10: 遊戲結束（碰撞）(Game over - collision)
- 0: 正常移動 (Normal move)

---

## 檔案結構 (File Structure)

```
jetson-nano-project/
├── main.py              # 主程式 UI（含模式切換）
├── snake_game.py        # 遊戲邏輯（人類 & AI 模式）
├── agent.py             # RL Agent 實現
├── model.py             # 神經網路和訓練器
├── test_snake_game.py   # 單元測試
├── demo.py              # 演示腳本
├── create_screenshot.py # UI 截圖生成器
├── requirements.txt     # Python 依賴
├── Dockerfile           # Jetson Nano 的 Docker 映像
├── docker-compose.yml   # Docker compose 配置
├── run.sh               # 快速啟動腳本
├── setup_jetson.sh      # Jetson Nano 設置腳本
├── model/               # 儲存模型的目錄
└── README.md            # 詳細文檔
```

---

## 測試 (Testing)

執行單元測試：
Run unit tests:

```bash
# 設置虛擬顯示驅動（無頭環境）
# Set dummy video driver (headless environment)
export SDL_VIDEODRIVER=dummy

# 執行測試 (Run tests)
python test_snake_game.py
```

執行演示：
Run demo:

```bash
python demo.py
```

---

## 故障排除 (Troubleshooting)

### Docker 構建 GPG 金鑰錯誤 (Docker Build GPG Key Error)

如果在執行 `docker-compose up --build` 時遇到 GPG 金鑰驗證錯誤：
If you encounter a GPG key verification error during `docker-compose up --build`:

```
E: The repository 'https://apt.kitware.com/ubuntu bionic InRelease' is not signed.
```

此問題已在最新的 Dockerfile 中修復。如果仍然遇到此問題：
This has been fixed in the latest Dockerfile. If you still encounter this issue:

1. 確保使用最新版本的 Dockerfile
   Make sure you're using the latest version of the Dockerfile

2. 嘗試無快取重建：
   Try rebuilding without cache:
```bash
docker-compose build --no-cache
docker-compose up
```

### NVIDIA Docker 運行時庫衝突 (NVIDIA Docker Runtime Library Conflict)

如果遇到以下錯誤：
If you encounter an error like:
```
nvidia-container-cli: mount error: file creation failed: /var/lib/docker/overlay2/.../merged/usr/lib/libvisionworks.so: file exists
```

此問題已在最新的 Dockerfile 中修復。該錯誤發生在 NVIDIA 容器運行時嘗試掛載容器映像中已存在的庫時。修復方法是在構建過程中刪除衝突的 NVIDIA 庫，允許運行時從主機掛載新副本。
This issue has been fixed in the latest Dockerfile. The error occurs when the NVIDIA container runtime tries to mount libraries that already exist in the container image. The fix removes conflicting NVIDIA libraries during the build process, allowing the runtime to mount fresh copies from the host.

如果仍然遇到此問題：
If you still encounter this issue:
1. 確保使用最新版本的 Dockerfile
   Make sure you're using the latest version of the Dockerfile
2. 嘗試無快取重建：
   Try rebuilding without cache:
```bash
docker-compose build --no-cache
docker-compose up
```

### Docker 顯示問題 (Docker Display Issues)

```bash
xhost +local:docker
export DISPLAY=:0
```

### CUDA 不可用 (CUDA Not Available)

檢查 NVIDIA 運行時：
Check NVIDIA runtime:

```bash
docker run --runtime nvidia nvidia/cuda:11.0-base nvidia-smi
```

### PyGame 顯示錯誤 (PyGame Display Error)

對於無頭系統，需要設置虛擬顯示：
For headless systems, set up virtual display:

```bash
sudo apt-get install xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```

---

## 效能 (Performance)

在 Jetson Nano 上：
On Jetson Nano:

- 訓練速度：~60 FPS
  - Training speed: ~60 FPS

- 推理速度：即時（60+ FPS）
  - Inference speed: Real-time (60+ FPS)

- 模型大小：~500KB
  - Model size: ~500KB

- 記憶體使用：訓練時 ~500MB
  - Memory usage: ~500MB during training

---

## 特色功能 (Key Features)

✅ 完整的遊戲 UI 界面
   - Complete game UI interface

✅ 人類可玩 + AI 訓練模式切換
   - Human playable + AI training mode switch

✅ 即時訓練視覺化
   - Real-time training visualization

✅ 自動模型保存
   - Automatic model saving

✅ 持久化高分記錄
   - Persistent high score tracking

✅ Docker 一鍵部署
   - Docker one-click deployment

✅ CUDA 加速支援
   - CUDA acceleration support

✅ 完整的 API 介面供 RL 使用
   - Complete API interface for RL

✅ 單元測試覆蓋
   - Unit test coverage

---

## 貢獻 (Contributing)

歡迎貢獻！請隨時提交 Pull Request。
Contributions are welcome! Please feel free to submit a Pull Request.

## 授權 (License)

MIT License

---

## 聯絡 (Contact)

如有問題或建議，請開 Issue。
For questions or suggestions, please open an Issue.
