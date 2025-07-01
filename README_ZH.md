# 雷霆战机

一款使用 Pygame 构建的经典纵向卷轴太空射击游戏，具有现代化的架构和全面的测试。

## 游戏说明

在《雷霆战机》中，你将驾驶一架战斗机，在太空中与成群的敌人作战。使用方向键或 WASD 键移动，按空格键射击。随着游戏进行，敌人会变得更强、更多，强大的 Boss 会周期性出现。击败敌人和 Boss 来获取积分并收集强化道具。**通过击败最终 Boss 完成所有关卡，取得最终胜利！**

## 功能特点

- **完整战役**: 挑战多个关卡，最终挑战史诗级的最终 Boss
- **胜利系统**: 通过击败最终 Boss 完成游戏，并提供全面的胜利统计数据
- **🎨 动态关卡背景**: 每个关卡都具有独特的视觉主题和超平滑的过渡效果
  - **双缓冲技术**: 完全消除关卡切换时的视觉瑕疵和闪烁
  - **渐进式难度可视化**: 背景复杂度和氛围随游戏难度变化
  - **特殊效果**: 特定关卡的效果，包括太空风暴和小行星场
  - **平滑Alpha过渡**: 专业级3秒过渡，采用三次贝塞尔缓动
- **僚机系统**: 拾取道具可获得最多两架僚机，它们会发射追踪导弹并可充当护盾
- **增强的胜利界面**: 精美的胜利界面，在保留游戏背景的同时，通过半透明浮层展示通关统计数据
- **稳定的音频系统**: 带音量控制的背景音乐和音效，并具备音频问题自动恢复功能
- **模块化UI系统**: 遵循单一职责原则的组件化UI架构
- **配置管理**: 基于JSON的配置系统，并提供命令行工具
- **事件驱动架构**: 用于解耦游戏组件的综合事件系统
- **工厂模式**: 通过可配置的工厂创建实体
- **输入管理系统**: 解耦的输入处理，支持自定义按键绑定
- **增强的多语言支持**: 完整的国际化系统，针对中文字体渲染进行了优化
  - **动态语言切换**: 按L键在英文和中文之间切换
  - **优化的中文字体**: 基于TTF的字体系统，确保在macOS上可靠显示中文字符
  - **本地化UI元素**: 所有游戏文本包括关卡切换、Boss状态和通知均已本地化
  - **字体系统**: 基于ResourceManager的字体加载，带有自动后备方案
- **开发者模式**: 提供调试信息和配置选项
- **动态难度**: 可配置的游戏玩法参数
- **广泛的测试覆盖**: 拥有255个全面的测试用例，覆盖所有游戏机制

关于游戏机制、系统和技术规格的更详细信息，请参阅[项目详情](./docs/DETAILS_ZH.md)文档。

## 快速开始

### 系统要求

- Python 3.7+
- Pygame 2.0.0+
- 其他依赖项见 `requirements.txt` 文件

### 安装说明

1. **克隆仓库:**
   ```bash
   git clone https://github.com/mike861/thunder_fighter.git
   cd thunder_fighter
   ```

2. **创建并激活虚拟环境:**
   ```bash
   python -m venv venv
   # Windows 系统:
   # venv\Scripts\activate
   # macOS/Linux 系统:
   source venv/bin/activate
   ```

3. **安装依赖:**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行游戏:**
   ```bash
   python main.py
   ```

## 游戏玩法

### 控制方式

- **移动**: 方向键 (↑↓←→) 或 WASD
- **射击**: 空格键
- **发射导弹**: X (可用时)
- **暂停/恢复**: P
- **切换音乐**: M
- **切换音效**: S
- **调整音量**: +/- (加号/减号键)
- **切换语言**: L (在英文和中文之间切换)
- **退出游戏**: ESC

### 游戏目标

**目标**: 闯过所有10个关卡，击败最终Boss，赢得胜利！

- **前期关卡 (1-2级)**: 通过积累分数来升级
- **中后期关卡 (3-10级)**: 在每个关卡末尾击败Boss来升级
- **最终胜利**: 击败第10级的Boss以完成游戏
- **胜利奖励**: 获胜后将获得全面的统计数据，包括最终得分、生存时间和完成成就

### 视觉体验

雷霆战机采用**动态背景系统**来增强沉浸感：

- **第1关 - 深空**: 宁静的蓝/黑色星空，开启你的征程
- **第2关 - 星云场**: 紫/蓝色星云，难度开始上升
- **第3关 - 小行星带**: 棕/橙色小行星场，伴有动画碎片效果
- **第4关 - 红色禁区**: 危险的红色太空，带有粒子风暴效果
- **第5关 - 最终决战**: 阴森的暗红色氛围，迎接终极挑战

每次关卡之间的过渡都采用**专业级平滑动画**，没有任何视觉瑕疵或闪烁，创造出电影般的体验，完美反映了任务不断升级的紧张感。

### 僚机系统

从第 3 游戏关卡开始，可能会出现新的强化道具。拾取该道具会为你提供一架"僚机"，它会跟在你的飞船侧翼。

- **火力支援**: 每架僚机会自动向附近的敌人发射追踪导弹，并在 Boss 出现时优先攻击 Boss
- **护盾**: 僚机会充当护盾，吸收敌人的火力。在承受一定量伤害后，僚机会被摧毁
- **数量限制**: 你最多可以同时拥有两架僚机
- **参数配置**: 僚机的初始数量、最大数量和编队间距均可在 `thunder_fighter/constants.py` 文件中进行配置

## 配置管理

《雷霆战机》包含一个全面的配置系统，允许你自定义游戏的各个方面。

### 配置工具

使用内置的配置工具来管理设置：

```bash
# 显示当前配置
python -m thunder_fighter.utils.config_tool show

# 设置音乐音量为 80%
python -m thunder_fighter.utils.config_tool set sound music_volume 0.8

# 开启开发者模式
python -m thunder_fighter.utils.config_tool set debug dev_mode true

# 设置难度为困难
python -m thunder_fighter.utils.config_tool set gameplay difficulty hard

# 重置所有设置为默认值
python -m thunder_fighter.utils.config_tool reset
```

### 可用设置

| 板块 | 设置 | 描述 | 默认值 |
|---------|---------|-------------|---------|
| **声音** | `music_volume` | 背景音乐音量 (0.0-1.0) | 0.5 |
| | `sound_volume` | 音效音量 (0.0-1.0) | 0.7 |
| | `music_enabled` | 开启/关闭音乐 | true |
| | `sound_enabled` | 开启/关闭音效 | true |
| **显示** | `fullscreen` | 开启全屏模式 | false |
| | `screen_scaling` | 屏幕缩放因子 | 1.0 |
| **游戏性** | `difficulty` | 游戏难度 (easy/normal/hard) | normal |
| | `initial_lives` | 初始生命值 | 3 |
| **调试** | `dev_mode` | 开启开发者模式 | false |
| | `log_level` | 日志级别 | INFO |

### 配置文件

设置会自动保存到 `~/.thunder_fighter/config.json`。如果需要，你也可以直接编辑此文件。

### 高级配置

```bash
# 调整日志级别 (可选)
# 设置 THUNDER_FIGHTER_LOG_LEVEL 环境变量
# Windows
set THUNDER_FIGHTER_LOG_LEVEL=DEBUG
python main.py

# Linux/macOS
THUNDER_FIGHTER_LOG_LEVEL=DEBUG python main.py
```

## 软件架构

《雷霆战机》采用现代化的模块化架构，旨在提高可维护性和可扩展性。

### 核心系统

- **事件驱动架构**: 综合的事件系统，实现游戏组件间的解耦通信
- **工厂模式**: 用于敌人、Boss、物品和射弹的可配置实体创建系统
- **输入管理**: 解耦的输入处理，具有可自定义的按键绑定和事件回调
- **状态管理**: 强大的游戏状态处理与转换管理
- **配置系统**: 基于JSON的配置，支持运行时更新和命令行工具

### UI 系统

UI系统已完全重构为模块化组件：

- **HealthBarComponent**: 动态生命条，具有颜色编码的状态
- **NotificationManager**: 游戏通知和成就系统
- **GameInfoDisplay**: 显示分数、关卡和已用时间
- **PlayerStatsDisplay**: 显示玩家统计数据和升级信息
- **BossStatusDisplay**: 显示Boss的生命值和战斗模式
- **ScreenOverlayManager**: 处理暂停、胜利和游戏结束界面
- **DevInfoDisplay**: 开发者调试信息（FPS、坐标等）

### 音频系统

- **实例管理**: 每个游戏实例都有自己的声音管理器
- **可配置音量**: 独立的音乐和音效控制
- **健康监控**: 系统自动恢复和音乐连续性
- **格式支持**: 支持 MP3、WAV、OGG 音频格式

## 测试

项目包含一个全面的测试套件，共有255个测试，覆盖了游戏的所有方面：

### 测试分类

- **单元测试 (27个)**: 实体工厂、独立组件
- **集成测试 (9个)**: 事件系统流程、组件交互
- **端到端测试 (9个)**: 完整的游戏流程场景
- **组件测试 (204个)**: 精灵、图形、工具、状态管理

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定类别的测试
python -m pytest tests/integration/ -v    # 集成测试
python -m pytest tests/unit/ -v          # 单元测试
python -m pytest tests/e2e/ -v           # 端到端测试

# 运行特定测试文件
python -m pytest tests/sprites/test_boss.py -v
python -m pytest tests/graphics/test_ui_components.py -v
```

### 测试覆盖范围

所有测试目前均已通过，确保了在以下方面的稳定性和可靠性：
- 游戏机制和碰撞检测
- 胜利和失败条件
- UI组件和渲染
- 配置管理
- 事件系统和工厂模式
- 输入处理和状态转换

## 项目结构

```
thunder_fighter/
├── docs/                       # 详细文档
│   ├── DETAILS.md             # 游戏机制详情
│   ├── DETAILS_ZH.md          # 中文文档
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── STATE_MANAGEMENT_SYSTEM.md
│   ├── SEPARATION_OF_CONCERNS_SUMMARY.md
│   ├── UI_REFACTORING_SUMMARY.md
│   └── TEST_CASE_REVIEW.md
├── thunder_fighter/
│   ├── assets/                # 游戏资源 (音效, 音乐)
│   ├── entities/              # 实体工厂与创建逻辑
│   ├── events/                # 事件系统与游戏事件
│   ├── graphics/              # 渲染、特效、UI组件
│   │   ├── ui/               # 模块化UI组件
│   │   ├── ui_manager.py     # 主UI门面
│   │   ├── renderers.py      # 实体渲染函数
│   │   ├── background.py     # 动态背景系统
│   │   └── effects.py        # 视觉效果
│   ├── input/                 # 输入管理与按键绑定
│   ├── localization/          # 语言文件 (en.json, zh.json)
│   ├── sprites/               # 游戏实体 (玩家, 敌人, Boss等)
│   ├── state/                 # 游戏状态管理
│   ├── utils/                 # 辅助函数和管理器
│   ├── config.py              # 游戏配置
│   ├── constants.py           # 游戏常量
│   └── game.py                # 主游戏类
├── tests/                     # 全面的测试套件 (255个测试)
│   ├── e2e/                  # 端到端测试
│   ├── integration/          # 集成测试
│   ├── unit/                 # 单元测试
│   ├── graphics/             # UI和渲染测试
│   ├── sprites/              # 实体测试
│   ├── state/                # 状态管理测试
│   └── utils/                # 工具测试
├── main.py                    # 主入口脚本
├── requirements.txt           # Python 依赖
├── pytest.ini                # 测试配置
├── README.md                  # 英文 README
├── README_ZH.md               # 中文 README
└── LICENSE                    # 项目许可证
```

## 已知问题

-   **中文显示问题**: 在某些系统（尤其是 macOS）上，切换到中文时可能会出现乱码或"豆腐块"(□□□)，而不是正确的字符。这是一个字体渲染问题，目前正在调查中。

## 开发

### 配置

```bash
# 查看当前配置
python -m thunder_fighter.utils.config_tool show

# 修改设置
python -m thunder_fighter.utils.config_tool set sound music_volume 0.8
python -m thunder_fighter.utils.config_tool set debug dev_mode true

# 重置为默认值
python -m thunder_fighter.utils.config_tool reset
```

### 贡献代码

1. Fork 本仓库
2. 创建一个新的功能分支
3. 在你的分支上进行修改并编写测试
4. 确保所有测试都通过 (`pytest tests/ -v`)
5. 提交一个 Pull Request

## 相关文档

- [游戏机制详情](docs/DETAILS_ZH.md)
- [配置管理](docs/IMPLEMENTATION_SUMMARY.md)
- [状态管理系统](docs/STATE_MANAGEMENT_SYSTEM.md)
- [UI重构总结](docs/UI_REFACTORING_SUMMARY.md)
- [关注点分离原则](docs/SEPARATION_OF_CONCERNS_SUMMARY.md)
- [测试用例审查](docs/TEST_CASE_REVIEW.md)

## 许可证

本项目基于 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 游戏截图

_(如果可用，在此处添加游戏截图)_
<!-- ![游戏截图](screenshots/gameplay.png) -->
