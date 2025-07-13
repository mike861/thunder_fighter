# 雷霆战机架构指南

## 概述

雷霆战机采用现代化的模块化架构，旨在实现可维护性、可测试性和可扩展性。该系统围绕事件驱动通信、基于系统的设计和明确的关注点分离构建。

## 核心设计原则

### 事件驱动架构
游戏组件通过 `EventSystem` 进行通信，而非直接耦合。所有游戏事件都在 `events/game_events.py` 中定义。

### 基于系统的架构
核心游戏逻辑被组织到 `systems/` 目录下的专用系统中：
- `CollisionSystem` - 统一处理所有实体交互的碰撞检测和解决
- `ScoringSystem` - 集中管理分数，包含关卡进度和成就跟踪
- `SpawningSystem` - 协调实体生成，集成所有工厂类
- `PhysicsSystem` - 处理游戏物理相关的移动、边界和碰撞检测

### 工厂模式
在 `entities/` 目录下按类型组织实体创建：
- `entities/enemies/` - `EnemyFactory` 和 `BossFactory`，具有难度缩放功能
- `entities/projectiles/` - `ProjectileFactory`，用于子弹和导弹
- `entities/items/` - `ItemFactory`，用于强化道具和收藏品
- `entities/player/` - 玩家和僚机实体管理

### 单一职责
每个系统都有明确的边界和专注的职责。

## 系统架构

### 输入系统架构

**统一输入系统**：在 `systems/input/` 中实现清晰的输入架构：
- `InputHandler` - 原始事件处理，包含对 macOS 截屏干扰的处理
- `InputManager` - 事件协调和状态管理
- `InputFacade` - 面向游戏逻辑的高级输入接口

分层架构提供：
- **原始事件处理**：平台特定的事件处理，带回退机制
- **状态管理**：输入状态协调和验证
- **游戏接口**：面向游戏逻辑的高级输入接口

### 状态管理系统

**状态模式**：通过 `state/` 目录下的 `StateMachine` 管理游戏状态：

#### 核心组件
1. **GameState** - 保存所有游戏状态信息的数据结构
2. **GameStateManager** - 集中管理状态数据和转换
3. **StateMachine** - 通用状态机框架
4. **State** - 单个游戏状态的抽象基类
5. **Concrete States** - 每种游戏模式的具体实现
6. **StateFactory** - 用于创建状态实例的工厂

#### 状态类型
- **MenuState** - 主菜单（待未来实现）
- **PlayingState** - 包含敌人/Boss/物品生成的活动游戏状态
- **PausedState** - 游戏暂停，音乐音量已调整
- **GameOverState** - 游戏结束画面，处理重启/退出
- **VictoryState** - 胜利画面，包含完成统计数据
- **LevelTransitionState** - 关卡过渡动画，时长 3 秒

#### 主要特性
- **集中式状态管理**：所有游戏状态集中管理
- **类型安全的状态转换**：清晰、经过验证的转换
- **事件驱动架构**：状态变更监听器和回调
- **关注点分离**：每个状态处理自己的逻辑

### 背景系统架构

**双缓冲动态背景**：革命性的视觉增强系统

#### 技术实现
- **双缓冲技术**：使用 alpha 混合进行预渲染
- **超平滑过渡**：使用三次贝塞尔曲线缓动，持续 3 秒
- **基于关卡的主题**：反映难度进阶的独特视觉主题
- **增强的特效**：支持 alpha 通道的太空风暴和小行星带

#### 视觉主题
- **第 1 关 - 深空**：蓝/黑色调，宁静的氛围
- **第 2 关 - 星云区**：紫/蓝色调，星云密度增加
- **第 3 关 - 小行星带**：棕/橙色调，带有动态小行星带
- **第 4 关 - 红色区域**：红/橙色调，伴有太空风暴粒子
- **第 5 关 - 最终之战**：暗红/黑色调，风暴效果强烈

#### 性能优化
- **缓冲复用**：仅在屏幕尺寸变化时重新创建表面
- **硬件加速**：使用 `pygame.BLEND_ALPHA_SDL2`
- **高效的 Alpha 处理**：最小化状态变更

## 组件系统

### UI 系统架构

**基于模块化组件的 UI**，位于 `graphics/ui/`：
- `HealthBarComponent` - 动态生命值显示，具有颜色编码状态
- `NotificationManager` - 游戏通知和成就系统
- `GameInfoDisplay` - 分数、关卡和已用时间显示
- `PlayerStatsDisplay` - 玩家统计和升级信息（带重置方法）
- `BossStatusDisplay` - Boss 生命值和战斗模式（带重置方法）
- `ScreenOverlayManager` - 暂停、胜利和游戏结束画面
- `DevInfoDisplay` - 开发者调试信息（FPS、位置等）

### 配置系统

**基于 JSON 的配置**：存储在 `~/.thunder_fighter/config.json`
- 通过 `config_tool.py` 进行运行时配置更新
- 所有游戏参数均可通过 `constants.py` 配置
- 支持环境变量 (`THUNDER_FIGHTER_LOG_LEVEL`)

### 资源管理

**集中式资源加载**：`ResourceManager` 提供：
- 资源缓存和优化
- 针对特定平台优化的字体管理
- 包含健康状况监控的声音和音乐管理
- 支持多种格式（PNG、JPG 等）的图像加载

### 暂停管理

**专用的 PauseManager 组件**：在 `utils/pause_manager.py` 中提取了暂停逻辑
- 暂停感知的计时计算和冷却机制
- 全面的统计数据跟踪
- 支持依赖注入，增强可测试性

## 实体架构

### 基础实体系统

**分层实体结构**，位于 `entities/base.py`：
- `GameObject` - 所有游戏对象的基类
- `Entity` - 带有生命周期管理的增强型游戏实体
- `EntityFactory` - 用于实体创建的基类工厂

### 按类型组织的实体系统

**工厂模式实现**：
- **enemies/** - 具有难度缩放的敌人实体和工厂
- **projectiles/** - 具有跟踪能力的子弹和导弹
- **items/** - 具有可配置效果的强化道具和收藏品
- **player/** - 具有编队管理的玩家和僚机实体

## 图形与特效

### 视觉特效系统

**模块化特效架构**，位于 `graphics/effects/`：
- `notifications.py` - 完整的通知系统，带位置属性
- `explosions.py` - 爆炸和命中效果函数
- `flash_effects.py` - 闪光效果管理系统

### 渲染系统

**优化的渲染管线**：
- 用于批量操作的精灵组
- 用于频繁创建实体的对象池
- 关键部分性能分析

## 测试架构

### 全面的测试覆盖

**375 项测试**，按类别组织：
- **单元测试 (90+)**：实体工厂、组件、暂停系统、本地化
- **集成测试 (9)**：事件系统流程、组件交互
- **端到端测试 (9)**：完整的游戏流程场景
- **系统测试**：核心系统架构验证
- **事件测试**：事件驱动架构测试
- **本地化测试**：多语言支持测试

### 测试原则
- **面向接口的测试**：测试关注行为和公共接口
- **依赖注入**：增强接口以便于测试
- **模拟外部依赖**：适当模拟 Pygame 表面、声音
- **全面覆盖**：关键系统覆盖率达 90% 以上

## 性能考量

### 优化策略
- **精灵组**：实体管理的批量操作
- **对象池**：复用频繁创建的实体
- **资源缓存**：资源加载优化
- **事件驱动更新**：仅处理相关变更

### 内存管理
- **延迟初始化**：需要时才加载资源
- **缓冲复用**：高效的表面管理
- **清理协议**：正确的资源释放

## 未来架构增强

### 计划改进
1. **状态持久化**：保存/加载游戏状态
2. **嵌套状态**：主状态内的子状态
3. **动态光照**：背景与游戏事件的交互
4. **增强的粒子系统**：高级环境效果
5. **组件实体系统 (ECS)**：全面迁移至 ECS 架构

### 扩展点
- 自定义状态验证规则
- 特定于状态的配置
- 动态实体创建
- 分析与监控集成

## 代码组织

### 目录结构

雷霆战机遵循模块化的目录结构，关注点分离清晰：

```
thunder_fighter/
├── assets/                   # 游戏资源 (字体, 图像, 声音, 音乐)
│   ├── fonts/               # 本地化字体文件
│   ├── images/              # 精灵图像和图形
│   ├── music/               # 背景音乐文件
│   └── sounds/              # 音效文件
├── entities/                # 按类型组织的游戏实体
│   ├── base.py             # 基础实体类和工厂
│   ├── enemies/            # 敌人实体和工厂
│   │   ├── boss.py         # Boss 实体实现
│   │   ├── boss_factory.py # 具有难度缩放的 Boss 创建
│   │   ├── enemy.py        # 敌人实体实现
│   │   └── enemy_factory.py # 敌人创建和关卡进度
│   ├── items/              # 强化道具和收藏品
│   │   ├── item_factory.py # 物品创建和生成逻辑
│   │   └── items.py        # 物品实体实现
│   ├── player/             # 玩家相关实体
│   │   ├── player.py       # 玩家实体和控制
│   │   └── wingman.py      # 僚机伴侣实体
│   └── projectiles/        # 子弹和导弹
│       ├── bullets.py      # 子弹实体实现
│       ├── missile.py      # 带跟踪功能的导弹实体
│       └── projectile_factory.py # 射弹创建系统
├── events/                 # 事件驱动架构
│   ├── event_system.py    # 核心事件系统实现
│   └── game_events.py     # 游戏特定事件定义
├── graphics/               # 渲染和视觉效果
│   ├── background.py       # 动态背景系统
│   ├── renderers.py        # 核心渲染函数
│   ├── effects/            # 视觉效果系统
│   │   ├── explosion.py    # 爆炸效果实现
│   │   ├── explosions.py   # 爆炸管理函数
│   │   ├── flash_effects.py # 闪光效果系统
│   │   ├── notifications.py # 通知系统
│   │   ├── particles.py    # 粒子效果系统
│   │   └── stars.py        # 星空背景元素
│   └── ui/                 # 用户界面组件
│       ├── manager.py      # UI 管理和协调
│       └── components/     # 模块化 UI 组件
│           ├── boss_status_display.py # Boss 生命值和状态
│           ├── dev_info_display.py    # 开发者调试信息
│           ├── game_info_display.py   # 分数和关卡显示
│           ├── health_bar.py          # 玩家生命条
│           ├── notification_manager.py # 通知系统
│           ├── player_stats_display.py # 玩家统计数据
│           └── screen_overlay_manager.py # 游戏状态覆盖层
├── localization/           # 多语言支持
│   ├── en.json            # 英文翻译
│   ├── zh.json            # 中文翻译
│   ├── font_support.py    # 字体管理系统
│   └── loader.py          # 语言加载抽象
├── sprites/                # 旧版精灵类 (为兼容性保留)
│   ├── boss.py            # 旧版 Boss 精灵
│   ├── bullets.py         # 旧版子弹精灵
│   ├── enemy.py           # 旧版敌人精灵
│   ├── explosion.py       # 旧版爆炸精灵
│   ├── items.py           # 旧版物品精灵
│   ├── missile.py         # 旧版导弹精灵
│   ├── player.py          # 旧版玩家精灵
│   └── wingman.py         # 旧版僚机精灵
├── state/                  # 游戏状态管理
│   ├── game_state.py      # 游戏状态数据结构
│   ├── game_states.py     # 具体状态实现
│   └── state_machine.py   # 通用状态机框架
├── systems/                # 核心游戏系统
│   ├── collision.py       # 统一碰撞检测
│   ├── physics.py         # 移动和物理
│   ├── scoring.py         # 分数管理系统
│   ├── spawning.py        # 实体生成协调
│   └── input/             # 统一输入管理
│       ├── facade.py      # 高级输入接口
│       ├── handler.py     # 原始事件处理
│       ├── manager.py     # 事件协调
│       ├── adapters/      # 平台特定适配器
│       │   ├── pygame_adapter.py # Pygame 输入适配器
│       │   └── test_adapter.py   # 测试输入适配器
│       └── core/          # 核心输入处理
│           ├── boundaries.py # 输入边界验证
│           ├── commands.py   # 输入命令系统
│           ├── events.py     # 输入事件定义
│           └── processor.py  # 输入处理逻辑
├── utils/                  # 工具模块
│   ├── collisions.py      # 碰撞工具函数
│   ├── config_manager.py  # 配置管理
│   ├── config_tool.py     # 命令行配置工具
│   ├── logger.py          # 日志系统
│   ├── pause_manager.py   # 暂停管理系统
│   ├── resource_manager.py # 资源加载和缓存
│   ├── score.py           # 分数跟踪工具
│   └── sound_manager.py   # 音频管理系统
├── config.py              # 游戏配置设置
├── constants.py           # 游戏常量和参数
└── game.py               # 主游戏类和游戏循环
```

### 核心模块

#### 游戏循环和主逻辑
- **`game.py`** - 主游戏类，包含游戏循环、实体管理和核心游戏逻辑
- **`config.py`** - 配置加载和管理
- **`constants.py`** - 所有游戏常量、参数和可配置值的来源

#### 实体系统
- **`entities/base.py`** - 所有游戏实体和工厂模式的基类
- **`entities/enemies/`** - 具有渐进难度和 Boss 战的敌人实体
- **`entities/player/`** - 玩家角色和僚机伴侣系统
- **`entities/projectiles/`** - 具有跟踪能力的子弹和导弹系统
- **`entities/items/`** - 强化道具和收藏品系统

#### 核心系统
- **`systems/collision.py`** - 统一处理所有实体交互的碰撞检测
- **`systems/scoring.py`** - 集中管理分数和关卡进度
- **`systems/spawning.py`** - 协调所有工厂的实体生成
- **`systems/physics.py`** - 移动、边界和物理计算
- **`systems/input/`** - 包含平台特定处理的完整输入管理

#### 图形和 UI
- **`graphics/background.py`** - 具有关卡特定主题的动态背景系统
- **`graphics/renderers.py`** - 核心渲染函数和精灵管理
- **`graphics/effects/`** - 包括爆炸、粒子和通知在内的视觉效果
- **`graphics/ui/`** - 遵循单一职责设计的模块化 UI 组件

#### 状态管理
- **`state/state_machine.py`** - 通用状态机框架
- **`state/game_states.py`** - 具体游戏状态实现（游戏进行中、暂停、胜利等）
- **`state/game_state.py`** - 游戏状态数据结构和管理

#### 事件系统
- **`events/event_system.py`** - 核心事件驱动架构实现
- **`events/game_events.py`** - 游戏特定事件定义和类型

#### 工具系统
- **`utils/resource_manager.py`** - 带缓存的集中式资源加载
- **`utils/sound_manager.py`** - 带健康状况监控和自动恢复的音频系统
- **`utils/pause_manager.py`** - 暂停感知的计时和状态管理
- **`utils/config_tool.py`** - 命令行配置管理工具
- **`utils/logger.py`** - 标准化日志系统

#### 本地化
- **`localization/loader.py`** - 带依赖注入的语言加载抽象
- **`localization/font_support.py`** - 平台特定的字体管理
- **`localization/*.json`** - 语言翻译文件

### 文件职责

#### 关键游戏文件
1. **`game.py`** - 管理所有游戏系统和主循环的中央协调器
2. **`constants.py`** - 所有可配置游戏参数的唯一真实来源
3. **`config.py`** - 配置系统接口和验证

#### 实体管理
1. **工厂类** - 具有配置预设的集中式实体创建
2. **实体实现** - 核心游戏对象行为和交互
3. **基类** - 共享功能和继承层次结构

#### 系统架构
1. **核心系统** - 具有清晰接口的独立、专注的系统
2. **输入系统** - 具有平台抽象的分层输入处理
3. **状态管理** - 类型安全的状态转换和生命周期管理

#### 资源和资源管理
1. **资源管理器** - 具有缓存策略的高效资源加载
2. **声音管理器** - 具有错误恢复功能的健壮音频系统
3. **字体支持** - 具有平台优化的多语言字体处理

### 架构优势

- **模块化设计**：每个目录都有明确的职责
- **清晰的依赖关系**：导入路径遵循一致的模式
- **可测试性**：关注点分离使得全面测试成为可能
- **可维护性**：相关功能按逻辑分组
- **可扩展性**：可以在不破坏现有系统的情况下添加新功能

## 结论

雷霆战机的架构成功地平衡了性能、可维护性和可扩展性。基于系统的设计与事件驱动的通信为当前的游戏玩法提供了坚实的基础，同时为未来的增强和功能提供了可能。
