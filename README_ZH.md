# 雷霆战机

一款使用 Pygame 构建的经典纵向卷轴太空射击游戏。

## 游戏说明

在《雷霆战机》中，你将驾驶一架战斗机，在太空中与成群的敌人作战。使用方向键或 WASD 键移动，按空格键射击。随着游戏进行，敌人会变得更强、更多，强大的 Boss 会周期性出现。击败敌人和 Boss 来获取积分并收集强化道具。**通过击败最终 Boss 完成所有关卡，取得最终胜利！**

## 功能特点

- **完整战役**: 挑战多个关卡，最终挑战史诗级的最终 Boss。
- **胜利系统**: 通过击败最终 Boss 完成游戏，并提供全面的胜利统计数据。
- 动态关卡进程，难度逐渐增加
- 多种具有不同行为模式的敌人类型
- 史诗级 Boss 战，具有变化的攻击模式
- 强化道具系统（生命值、速度、子弹增强）
- **僚机系统:** 拾取道具可获得最多两架僚机，它们会发射追踪导弹并可充当护盾。
- 爆炸和撞击的粒子效果与动画
- **增强的胜利界面**: 精美的胜利界面，在保留游戏背景的同时，通过半透明浮层展示通关统计数据。
- 支持堆叠通知的动态用户界面
- 多语言支持（目前支持英文和中文）
- 响应灵敏的控制和碰撞检测
- **稳定的音频系统**: 带音量控制的背景音乐和音效，并具备音频问题自动恢复功能。
- 完善的日志系统
- **广泛的测试覆盖**: 拥有94个全面的测试用例，覆盖所有游戏机制。
- **本地化**: 所有面向用户的UI文本都通过本地化模块加载，并提供英文和中文翻译。

关于游戏机制、系统和技术规格的更详细信息，请参阅[项目详情](./docs/DETAILS_ZH.md)文档。

## 游戏截图

_(如果可用，在此处添加游戏截图)_ 
<!-- ![游戏截图](screenshots/gameplay.png) -->

## 系统要求

- Python 3.7+
- Pygame 2.0.0+
- 其他依赖项见 `requirements.txt` 文件

## 安装说明

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/mike861/thunder_fighter.git
    cd thunder_fighter
    ```

2.  **创建并激活虚拟环境:**
    ```bash
    python -m venv venv
    # Windows 系统:
    # venv\Scripts\activate
    # macOS/Linux 系统:
    source venv/bin/activate
    ```

3.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```

## 游戏操作

1.  **运行游戏:**
    ```bash
    python main.py
    ```

2.  **调整日志级别 (可选):**
    设置 `THUNDER_FIGHTER_LOG_LEVEL` 环境变量 (例如 `DEBUG`, `INFO`, `WARNING`).
    ```bash
    # Windows
    # set THUNDER_FIGHTER_LOG_LEVEL=DEBUG
    # python main.py
    
    # Linux/macOS
    # THUNDER_FIGHTER_LOG_LEVEL=DEBUG python main.py
    ```

### 控制方式

-   **移动:** 方向键 (↑↓←→) 或 WASD
-   **射击:** 空格键
-   **暂停/恢复:** P
-   **切换音乐:** M
-   **切换音效:** S
-   **调整音量:** +/- (加号/减号键)
-   **切换语言:** L (在英文和中文之间切换)
-   **退出游戏:** ESC

### 游戏目标

**目标**: 闯过所有10个关卡，击败最终Boss，赢得胜利！

- **前期关卡 (1-2级)**: 通过积累分数来升级。
- **中后期关卡 (3-10级)**: 在每个关卡末尾击败Boss来升级。
- **最终胜利**: 击败第10级的Boss以完成游戏。
- **胜利奖励**: 获胜后将获得全面的统计数据，包括最终得分、生存时间和完成成就。

### 僚机系统

从第 3 游戏关卡开始，可能会出现新的强化道具。拾取该道具会为你提供一架"僚机"，它会跟在你的飞船侧翼。

-   **火力支援**: 每架僚机会自动向附近的敌人发射追踪导弹，并在 Boss 出现时优先攻击 Boss。
-   **护盾**: 僚机会充当护盾，吸收敌人的火力。在承受一定量伤害后，僚机会被摧毁。
-   **数量限制**: 你最多可以同时拥有两架僚机。
-   **参数配置**: 僚机的初始数量、最大数量和编队间距均可在 `thunder_fighter/constants.py` 文件中进行配置。

## 测试

项目包含一套全面的测试套件，覆盖了游戏机制、碰撞检测、胜利条件和所有组件。目前所有 94 个测试均已通过，确保了游戏的稳定性和可靠性。

-   **运行所有测试:**
    ```bash
    pytest
    ```

-   **运行特定文件中的测试:**
    ```bash
    pytest tests/sprites/test_boss.py
    ```

-   **运行胜利系统测试:**
    ```bash
    pytest tests/test_game_victory.py
    ```

## 项目结构

```
thunder_fighter/
├── docs/           # 详细文档
│   ├── DETAILS.md
│   └── DETAILS_ZH.md
├── thunder_fighter/
│   ├── assets/     # 游戏资源 (音效, 音乐)
│   ├── graphics/   # 渲染、特效和UI
│   ├── localization/ # 语言文件 (en.json, zh.json)
│   ├── sprites/    # 游戏实体 (玩家, 敌人, Boss等)
│   ├── utils/      # 辅助函数和管理器
│   ├── config.py   # 游戏配置
│   ├── constants.py# 游戏常量
│   └── game.py     # 主游戏类
├── tests/          # 单元测试 (94个全面测试)
├── main.py         # 主入口脚本
├── requirements.txt # Python 依赖
├── README.md       # 英文 README
├── README_ZH.md    # 本文档
└── LICENSE         # 项目许可证
```

## 开发指南

### 多语言支持

游戏通过 `thunder_fighter/localization/json/` 目录支持多种语言。

1.  语言文件 (例如 `en.json`, `zh.json`)