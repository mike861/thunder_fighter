# 雷霆战机 (Thunder Fighter)

一个使用 Python 和 Pygame 制作的简单太空射击游戏。

## 游戏说明

在游戏中，玩家控制一架战斗机在太空中与敌人对抗。使用方向键控制飞机移动，空格键发射子弹。
随着游戏时间推移，敌人会变得更加强大和频繁，而且每隔一段时间会出现一个强大的 Boss，击败它可以获得更多的分数。

## 游戏特点

- 自绘的图形和粒子效果
- 随着游戏时间增加的难度系统
- 多种敌人类型和射击模式
- Boss 战，具有独特的攻击模式
- 多种道具掉落系统
- 增强型子弹系统
- 爆炸特效和视觉反馈
- 标准化日志系统
- 完整的音效和背景音乐系统
- 游戏暂停功能
- 完整测试覆盖，通过43个测试用例

## 游戏内部机制

### 敌人系统
- **敌人等级**: 敌人分为0-10级，等级越高，生命值、速度和攻击力越高
- **敌人生成**: 随着游戏时间增加，生成的敌人数量和等级也会提高
- **敌人射击**: 1级以上的敌人可以射击，射击频率和子弹速度随等级提高
  - 低级敌人(1-4): 发射简单的红色子弹，直线下落
  - 中级敌人(5-7): 发射橙色子弹，可能有水平移动
  - 高级敌人(8-10): 发射蓝色或紫色子弹，可能有曲线轨迹

### 子弹系统
- **玩家子弹**: 根据收集的道具，最多可有4种射击路径
- **敌人子弹**: 根据敌人等级有不同外观、速度和伤害
- **Boss子弹**: 特殊的大型子弹，伤害较高

### 道具系统
- **生命道具**: 恢复玩家生命值
- **子弹速度道具**: 提高玩家子弹速度
- **子弹路径道具**: 增加玩家射击路径数量
- **玩家速度道具**: 提升玩家移动速度。
- **道具生成**: 随着游戏进行和击败敌人获得积分，会随机生成道具

### Boss系统
- **Boss等级**: Boss分为1-3级，等级越高越强大
- **Boss生成**: 每隔一定时间会生成一个Boss
- **Boss攻击**: 发射多颗子弹，数量和模式随等级变化

### 音效系统
- **背景音乐**: 游戏过程中循环播放的背景音乐
- **射击音效**: 玩家发射子弹时播放
- **爆炸音效**: 敌人和Boss被击毁时播放
- **受伤音效**: 玩家受到伤害时播放
- **死亡音效**: 玩家飞机被击毁时播放
- **道具获取音效**: 拾取道具时播放
- **击败Boss音效**: 成功击败Boss时播放
- **音量控制**: 可调整音效和音乐音量

### 日志系统
- 标准化的日志输出，支持不同级别(DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 通过环境变量`THUNDER_FIGHTER_LOG_LEVEL`可调整日志级别
- 所有游戏事件都有英文日志记录，便于调试和监控

## 控制说明

- 方向键 (↑↓←→) 或 WASD: 控制飞机移动
- 空格键: 发射子弹
- P: 暂停/恢复游戏
- F3: 显示详细敌人等级分布信息 (开发模式)
- M: 开启/关闭背景音乐
- S: 开启/关闭音效
- +/-: 调整音量
- ESC: 退出游戏

## 项目结构

项目采用模块化结构设计，便于维护和扩展：

```
thunder_fighter/
├── __init__.py                 # 包初始化
├── constants.py                # 常量定义
├── game.py                     # 游戏主逻辑
├── graphics/                   # 图形渲染相关
│   ├── __init__.py
│   ├── effects.py              # 特效系统
│   └── renderers.py            # 渲染函数
├── sprites/                    # 游戏精灵类
│   ├── __init__.py
│   ├── boss.py                 # Boss类
│   ├── bullets.py              # 子弹类
│   ├── enemy.py                # 敌人类
│   ├── explosion.py            # 爆炸效果类
│   ├── items.py                # 道具类 (生命, 子弹速度/路径, 玩家速度)
│   └── player.py               # 玩家类
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── collisions.py           # 碰撞检测
│   ├── logger.py               # 日志系统
│   ├── score.py                # 分数系统
│   ├── sound_manager.py        # 音效管理
│   └── stars.py                # 背景星星
└── assets/                     # 游戏资源
    ├── sounds/                 # 音效文件
    └── music/                  # 背景音乐
main.py                         # 主入口脚本
requirements.txt                # 依赖列表
README_CN.md                    # 中文说明文件
README.md                       # 英文说明文件 (将创建)
uml_class_diagram.md            # UML类图
.gitignore                      # Git忽略配置
```

## 运行方式

确保安装了 Python 和 Pygame，然后运行：

```bash
python main.py
```

要调整日志级别，可以设置环境变量：

```bash
# Windows
set THUNDER_FIGHTER_LOG_LEVEL=DEBUG
python main.py

# Linux/macOS
THUNDER_FIGHTER_LOG_LEVEL=DEBUG python main.py
```

## 依赖项

- Python 3.6+
- Pygame 2.0+

## 音效资源

游戏使用了以下音效和音乐文件：

1. 将WAV或MP3格式的音效文件放置在`thunder_fighter/assets/sounds/`目录：
   - player_shoot.wav - 玩家射击音效
   - player_hit.wav - 玩家受伤音效
   - player_death.wav - 玩家死亡音效
   - enemy_explosion.wav - 敌人爆炸音效
   - boss_death.wav - Boss死亡音效
   - item_pickup.wav - 道具拾取音效 (目前所有道具类型共用)

2. 将MP3格式的背景音乐放置在`thunder_fighter/assets/music/`目录：
   - background_music.mp3 - 游戏背景音乐

如果这些文件不存在，游戏会自动处理缺失音效，不会影响正常游戏。

## 开发状态

- ✅ 核心游戏机制已实现
- ✅ 多级敌人系统与多样行为
- ✅ Boss战斗系统与独特攻击模式
- ✅ 道具掉落与收集系统
- ✅ 音效系统与音量控制
- ✅ 完整测试覆盖
- ✅ 游戏优化与完善

## 测试

游戏包含一套完整的测试套件，共43个测试用例覆盖所有主要组件：
- 玩家机制与交互
- 敌人行为与等级计算
- Boss战斗机制
- 道具生成与效果
- 碰撞检测
- 游戏状态管理

运行测试：
```bash
pytest
```

## 技术细节

- 使用面向对象编程设计游戏实体
- 精灵组(Sprite Groups)管理游戏对象碰撞检测
- 自定义渲染系统创建游戏视觉效果
- 标准化日志系统跟踪游戏事件
- 音效管理器控制游戏音效播放
- 模块化架构便于扩展和维护
- 测试驱动开发确保代码质量与可靠性

## 开发者

这个游戏是作为 Python 游戏开发练习项目创建的。
