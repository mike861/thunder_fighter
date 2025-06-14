# 雷霆战机

一款使用 Pygame 构建的经典纵向卷轴太空射击游戏。

## 游戏说明

在《雷霆战机》中，你将驾驶一架战斗机，在太空中与成群的敌人作战。使用方向键或 WASD 键移动，按空格键射击。随着游戏进行，敌人会变得更强、更多，强大的 Boss 会周期性出现。击败敌人和 Boss 来获取积分并收集强化道具。

## 功能特点

- 动态关卡进程，难度逐渐增加
- 多种具有不同行为模式的敌人类型
- 史诗级 Boss 战，具有变化的攻击模式
- 强化道具系统（生命值、速度、子弹增强）
- 爆炸和撞击的粒子效果与动画
- 支持堆叠通知的动态用户界面
- 多语言支持（目前支持英文和中文）
- 响应灵敏的控制和碰撞检测
- 带音量控制的背景音乐和音效
- 完善的日志系统
- 经过全面测试的代码库（43 个测试通过）

关于游戏机制、资源和技术方面的更详细信息，请参阅[项目详情](docs/DETAILS_CN.md)。

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
    git clone https://github.com/yourusername/thunder_fighter.git
    cd thunder_fighter
    ```
    (请将 `yourusername` 替换为实际的仓库路径)

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
-   **(开发模式) 显示敌人等级:** F3

## 测试

项目包含一套全面的测试套件，覆盖了游戏机制、碰撞检测和组件。目前所有 43 个测试均已通过。

-   **运行所有测试:**
    ```bash
    pytest
    ```

-   **运行特定文件中的测试:**
    ```bash
    pytest tests/sprites/test_boss.py
    ```

## 项目结构

```
thunder_fighter/
├── assets/         # 游戏资源 (图像, 声音, 音乐)
├── docs/           # 详细文档
│   └── DETAILS_CN.md
├── graphics/       # 渲染, 特效, UI
├── localization/   # 语言文件 (en.py, zh.py)
├── sprites/        # 游戏实体 (玩家, 敌人, boss等)
├── tests/          # 单元测试
├── utils/          # 辅助函数, 管理器 (声音, 分数等)
├── __init__.py
├── config.py       # 游戏配置
├── constants.py    # 游戏常量
└── game.py         # 游戏主类
main.py             # 主入口脚本
requirements.txt    # Python 依赖项
README.md           # 英文 README
README_CN.md        # 本文件 (中文 README)
.gitignore
LICENSE             # 项目许可证
```

## 开发指南

### 多语言支持

游戏通过 `thunder_fighter/localization/` 目录支持多种语言。

1.  语言文件 (例如 `en.py`, `zh.py`) 存储文本字符串的键值对。
2.  `LanguageManager` 根据 `config.py` 加载相应的语言。
3.  游戏内文本使用 `_()` 函数获取 (例如 `_("Game Over")`)。
4.  使用 'L' 键在游戏中切换语言。

**添加新语言的步骤:**

1.  在 `thunder_fighter/localization/` 目录下通过复制 `en.py` 创建一个新的语言文件 (例如西班牙语 `es.py`)。
2.  翻译新文件中的所有字符串值。
3.  将语言代码 (例如 `'es'`) 添加到 `thunder_fighter/config.py` 中的 `AVAILABLE_LANGUAGES` 列表。
4.  如果需要特殊处理（对于简单添加不太可能），则更新 `LanguageManager`。

## 许可证

本项目基于 MIT 许可证 - 详情请参阅 `LICENSE` 文件。

## 致谢

-   Pygame 社区
-   开源游戏开发资源
-   贡献者和测试者
