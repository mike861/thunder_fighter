# Thunder Fighter 测试指南

## 概述

本指南提供了有关 Thunder Fighter 测试的全面信息，包括测试结构、最佳实践以及添加新测试的指导。该项目维护着 390 多个综合测试，以确保代码质量和功能可靠性。

## 目录

1. [测试架构](#测试架构)
2. [测试分类](#测试分类)
3. [运行测试](#运行测试)
4. [编写新测试](#编写新测试)
5. [测试覆盖率分析](#测试覆盖率分析)
6. [测试最佳实践](#测试最佳实践)
7. [专门的测试套件](#专门的测试套件)
8. [常见测试模式](#常见测试模式)
9. [测试差距与优先级](#测试差距与优先级)
10. [性能与基准测试](#性能与基准测试)

## 测试架构

### 测试结构

Thunder Fighter 采用分层的测试结构，实现了关注点分离：

```
tests/
├── e2e/                     # 端到端测试 (9个测试)
│   └── test_game_flow.py    # 完整的游戏流程场景
├── integration/             # 集成测试 (9个测试)
│   └── test_event_flow.py   # 系统交互测试
├── unit/                    # 单元测试 (70+个测试)
│   ├── entities/            # 实体工厂测试
│   ├── test_pause_system.py # 暂停功能测试
│   └── test_*.py            # 单个组件测试
├── graphics/                # 视觉组件测试 (80个测试)
│   ├── test_ui_components.py # UI组件测试
│   ├── test_renderers.py    # 渲染系统测试
│   └── test_background.py   # 背景系统测试
├── utils/                   # 工具类测试 (43个测试)
│   ├── test_resource_manager.py
│   ├── test_config_manager.py
│   └── test_collisions.py
└── state/                   # 状态管理测试 (40个测试)
    ├── test_state_machine.py
    └── test_game_state.py
```

### 测试分布

| 类别 | 测试数量 | 覆盖焦点 |
|----------|------------|----------------|
| 图形 | 80 (30.8%) | UI组件, 渲染 |
| 工具类 | 43 (16.5%) | 资源管理, 配置 |
| 状态 | 40 (15.4%) | 状态机, 游戏流程 |
| 精灵 | 27 (10.4%) | 游戏对象行为 |
| 单元/实体 | 27 (10.4%) | 工厂模式, 实体创建 |
| 端到端 | 9 (3.5%) | 完整工作流 |
| 集成 | 9 (3.5%) | 系统交互 |

## 测试分类

### 端到端测试

**目的**: 验证完整的游戏工作流和系统集成。

**关键测试领域**:
- 游戏初始化和组件设置
- 关卡进程逻辑
- Boss 击败处理
- 物品收集机制
- 玩家死亡场景
- 资源管理集成

**示例测试模式**:
```python
def test_complete_game_flow():
    """测试从开始到击败Boss的完整游戏流程。"""
    game = initialize_test_game()
    
    # 验证初始化
    assert game.is_initialized()
    
    # 模拟游戏进程
    game.advance_to_level(2)
    assert game.current_level == 2
    
    # 测试Boss生成和击败
    boss = game.spawn_boss()
    game.defeat_boss(boss)
    
    # 验证状态转换
    assert game.current_level == 3
```

### 集成测试

**目的**: 测试不同系统和组件之间的交互。

**关键关注领域**:
- 事件系统传播
- 组件交互工作流
- 跨系统的错误处理
- 组件间的状态同步

**示例测试模式**:
```python
def test_event_system_integration():
    """测试事件在多个系统中的传播。"""
    event_system = EventSystem()
    
    # 注册多个监听器
    collision_system = Mock()
    scoring_system = Mock()
    
    event_system.register(collision_system, EventType.ENEMY_DEFEATED)
    event_system.register(scoring_system, EventType.ENEMY_DEFEATED)
    
    # 分发事件并验证传播
    event = EnemyDefeatedEvent(enemy_id=123, points=100)
    event_system.dispatch(event)
    
    collision_system.handle.assert_called_once_with(event)
    scoring_system.handle.assert_called_once_with(event)
```

### 单元测试

**目的**: 独立测试单个组件和功能。

**关键领域**:
- 实体工厂和创建逻辑
- 单个系统组件
- 工具函数和辅助类
- 配置管理

**示例测试模式**:
```python
def test_enemy_factory_creation():
    """测试敌人T工厂是否能创建具有正确属性的敌人。"""
    factory = EnemyFactory()
    
    enemy = factory.create_enemy(level=3, game_time=10)
    
    assert enemy.level == 3
    assert enemy.can_shoot == (enemy.level >= ENEMY_SHOOT_LEVEL)
    assert enemy.speed > 0
    assert hasattr(enemy, 'image')
    assert hasattr(enemy, 'rect')
```

## 运行测试

### 基本测试执行

```bash
# 运行所有测试
./venv/bin/python -m pytest tests/ -v

# 运行特定类别的测试
./venv/bin/python -m pytest tests/unit/ -v          # 单元测试
./venv/bin/python -m pytest tests/integration/ -v   # 集成测试
./venv/bin/python -m pytest tests/e2e/ -v           # 端到端测试

# 运行测试并生成覆盖率报告
./venv/bin/python -m pytest tests/ --cov=thunder_fighter --cov-report=html
```

### 测试过滤和选择

```bash
# 运行匹配模式的测试
./venv/bin/python -m pytest tests/ -k "test_enemy" -v

# 运行特定文件中的测试
./venv/bin/python -m pytest tests/unit/entities/test_factories.py -v

# 运行带有特定标记的测试
./venv/bin/python -m pytest tests/ -m "slow" -v

# 只运行失败的测试
./venv/bin/python -m pytest tests/ --lf
```

### 测试配置

测试通过 `pyproject.toml` 进行配置:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers"
markers = [
    "slow: 标记测试为慢速 (使用 '-m "not slow"' 取消选择)",
    "integration: 标记测试为集成测试",
    "e2e: 标记测试为端到端测试"
]
```

## 编写新测试

### 测试文件组织

**文件命名约定**:
- 单元测试: `test_<component_name>.py`
- 集成测试: `test_<system>_integration.py`
- 端到端测试: `test_<workflow>_flow.py`

**类命名约定**:
- 测试类: `Test<ComponentName>`
- 测试方法: `test_<specific_behavior>`

### 测试结构模板

```python
"""
<组件名> 的测试。

描述此测试模块涵盖的内容以及任何特殊注意事项。
"""

from unittest.mock import MagicMock, patch
import pytest

from thunder_fighter.<module> import <Component>


class Test<ComponentName>:
    """测试 <Component> 类。"""

    def setup_method(self):
        """在每个测试方法之前设置测试环境。"""
        self.component = <Component>()
        # 初始化任何需要的模拟对象或测试数据

    def test_initialization(self):
        """测试组件是否以正确的默认值初始化。"""
        # 测试基本初始化
        assert self.component.is_initialized()
        
    def test_core_functionality(self):
        """测试组件的核心功能。"""
        # 测试主要用例
        result = self.component.main_method()
        assert result is not None
        
    def test_error_handling(self):
        """测试组件是否能优雅地处理错误。"""
        # 测试错误条件
        with pytest.raises(ValueError):
            self.component.invalid_operation()
            
    def test_edge_cases(self):
        """测试组件在边界条件下的行为。"""
        # 测试边界条件
        pass
```

### 模拟指南

**尽可能使用真实对象**:
```python
# 首选：使用真实的轻量级对象
def test_with_real_objects():
    event_system = EventSystem()
    event = PlayerMovedEvent(x=100, y=200)
    # 使用实际对象进行测试
```

**模拟外部依赖**:
```python
# 模拟外部系统 (pygame, 文件I/O, 网络)
@patch('pygame.sprite.Sprite.__init__')
def test_sprite_creation(self, mock_sprite_init):
    mock_sprite_init.return_value = None
    sprite = EnemySprite()
    # 测试精灵创建逻辑
```

**在接口边界进行模拟**:
```python
# 在系统边界进行模拟
def test_resource_loading():
    with patch('thunder_fighter.utils.resource_manager.load_image') as mock_load:
        mock_load.return_value = Mock()
        # 测试资源管理逻辑
```

## 测试覆盖率分析

### 当前覆盖率状态

| 模块 | 当前覆盖率 | 目标覆盖率 |
|--------|------------------|-----------------|
| 核心游戏逻辑 | ~85% | 90% |
| UI组件 | ~90% | 95% |
| 工具类 | ~95% | 95% |
| 输入系统 | ~40% | 85% |
| 事件系统 | ~75% | 85% |
| **总计** | ~75% | >85% |

### 覆盖率命令

```bash
# 生成覆盖率报告
./venv/bin/python -m pytest tests/ --cov=thunder_fighter

# 生成HTML格式的覆盖率报告
./venv/bin/python -m pytest tests/ --cov=thunder_fighter --cov-report=html

# 在终端中查看覆盖率及缺失的代码行
./venv/bin/python -m pytest tests/ --cov=thunder_fighter --cov-report=term-missing

# 检查特定模块的覆盖率
./venv/bin/python -m pytest tests/ --cov=thunder_fighter.systems --cov-report=term
```

## 测试最佳实践

### 面向接口的测试

**测试公共API，而非实现细节**:
```python
# 好的实践：测试公共接口
def test_player_takes_damage():
    player = Player()
    initial_health = player.health
    
    player.take_damage(10)
    
    assert player.health == initial_health - 10

# 应避免：测试私有方法
def test_private_method():
    player = Player()
    # 不要测试 player._update_internal_state()
```

### 测试独立性

**每个测试都应是隔离的**:
```python
class TestPlayer:
    def setup_method(self):
        """为每个测试创建新的实例。"""
        self.player = Player()
        
    def test_shooting(self):
        """此测试不依赖于其他测试。"""
        bullets = self.player.shoot()
        assert len(bullets) > 0
        
    def test_movement(self):
        """具有独立设置的独立测试。"""
        self.player.move(10, 0)
        assert self.player.rect.x == 10
```

### 清晰的测试描述

**使用描述性的测试名称**:
```python
# 好的实践：意图清晰
def test_enemy_shoots_when_level_above_threshold():
    """测试当等级 >= SHOOT_LEVEL 时敌人可以射击。"""
    
def test_player_loses_wingman_when_taking_damage():
    """测试僚机在玩家生命值减少前被摧毁。"""

# 应避免：模糊的名称
def test_enemy_behavior():
def test_player_stuff():
```

### 测试数据管理

**使用真实的测试数据**:
```python
# 好的实践：使用游戏中的常量
def test_boss_spawning():
    game_level = 2  # Boss从第2级开始生成
    spawn_interval = BOSS_SPAWN_INTERVAL
    
# 创建与游戏实际情况相符的测试数据
TEST_ENEMY_CONFIGS = {
    'level_0': {'can_shoot': False, 'speed': 2},
    'level_3': {'can_shoot': True, 'speed': 4},
}
```

## 专门的测试套件

### 暂停系统测试

**关键测试领域**:
- 感知暂停的时间计算
- 暂停/恢复期间的状态同步
- 多次暂停/恢复循环
- 边界情况和错误处理

**示例测试模式**:
```python
def test_pause_aware_timing_calculation():
    """测试游戏时间是否正确排除了暂停持续时间。"""
    pause_manager = PauseManager()
    start_time = time.time()
    
    # 模拟10秒的游戏时间
    with patch('time.time', return_value=start_time + 10):
        elapsed = pause_manager.calculate_game_time(start_time)
        assert elapsed == 10
    
    # 暂停20秒
    pause_manager.pause()
    with patch('time.time', return_value=start_time + 30):
        elapsed = pause_manager.calculate_game_time(start_time)
        assert elapsed == 10  # 暂停期间不增加时间
    
    # 恢复并再增加15秒
    pause_manager.resume()
    with patch('time.time', return_value=start_time + 45):
        elapsed = pause_manager.calculate_game_time(start_time)
        assert elapsed == 25  # 10 + 15, 不包括20秒的暂停
```

### 输入系统测试

**关键测试领域**:
- 针对macOS截屏干扰的回退机制
- 按键绑定和重映射
- 输入状态同步
- F1重置功能

**示例测试模式**:
```python
def test_input_fallback_mechanism():
    """测试当正常处理失败时的输入回退机制。"""
    handler = InputHandler()
    
    # 模拟正常处理失败的场景
    with patch.object(handler, '_process_normal', side_effect=Exception):
        # 模拟P键按下
        pygame_event = create_mock_keydown_event(pygame.K_p)
        
        events = handler.process_event(pygame_event)
        
        # 验证回退机制是否创建了正确的暂停事件
        assert len(events) == 1
        assert events[0].type == GameEventType.PAUSE_TOGGLE
```

### 本地化测试

**关键测试领域**:
- 字体加载和渲染
- 语言切换功能
- 文本渲染无“豆腐块”
- 多语言UI布局

**示例测试模式**:
```python
def test_chinese_font_rendering():
    """测试中文文本渲染时没有豆腐块。"""
    lang_manager = LanguageManager()
    lang_manager.set_language('zh')
    
    # 测试字体加载
    font = lang_manager.get_font('notification', 24)
    assert font is not None
    
    # 测试文本渲染
    chinese_text = "暂停游戏"
    surface = font.render(chinese_text, True, (255, 255, 255))
    
    # 验证surface不为空 (没有豆腐块)
    assert surface.get_width() > 0
    assert surface.get_height() > 0
```

## 常见测试模式

### 事件系统测试

```python
def test_event_dispatch_and_handling():
    """测试事件分发给多个监听器。"""
    event_system = EventSystem()
    listener1 = Mock()
    listener2 = Mock()
    
    event_system.register(listener1, EventType.ENEMY_DEFEATED)
    event_system.register(listener2, EventType.ENEMY_DEFEATED)
    
    event = EnemyDefeatedEvent(enemy_id=123, points=100)
    event_system.dispatch(event)
    
    listener1.handle.assert_called_once_with(event)
    listener2.handle.assert_called_once_with(event)
```

### 工厂模式测试

```python
def test_factory_creates_configured_entities():
    """测试工厂是否能根据配置创建实体。"""
    factory = EnemyFactory()
    
    # 测试不同配置
    configs = [
        {'level': 1, 'expected_shooting': False},
        {'level': 3, 'expected_shooting': True},
    ]
    
    for config in configs:
        enemy = factory.create_enemy(level=config['level'])
        assert enemy.can_shoot == config['expected_shooting']
```

### 状态机测试

```python
def test_state_transitions():
    """测试状态机是否能正确处理转换。"""
    state_machine = StateMachine()
    
    # 测试有效转换
    assert state_machine.transition_to(GameState.PLAYING)
    assert state_machine.current_state == GameState.PLAYING
    
    # 测试无效转换
    with pytest.raises(InvalidTransitionError):
        state_machine.transition_to(GameState.INVALID)
```

## 测试差距与优先级

### 高优先级差距 (1周内添加)

1. **输入系统测试** (需要15-20个测试):
   ```python
   tests/unit/input/
   ├── test_input_handler.py      # 回退机制
   ├── test_input_manager.py      # 事件协调
   └── test_key_bindings.py       # 按键映射和F1重置
   ```

2. **暂停系统增强** (需要5-8个测试):
   ```python
   tests/unit/test_pause_system.py
   - test_pause_aware_timing
   - test_repeated_pause_resume_cycles
   - test_pause_state_synchronization
   ```

3. **本地化测试** (需要5-8个测试):
   ```python
   tests/unit/test_localization.py
   - test_chinese_font_rendering
   - test_language_switching
   - test_notification_font_sizes
   ```

### 中等优先级 (2-3周内)

1. **性能测试**:
   ```python
   tests/performance/
   ├── test_rendering_performance.py
   ├── test_collision_performance.py
   └── test_memory_usage.py
   ```

2. **边界情况测试**:
   ```python
   tests/edge_cases/
   ├── test_extreme_entity_counts.py
   ├── test_rapid_input_sequences.py
   └── test_memory_limits.py
   ```

## 性能与基准测试

### 性能测试框架

```python
import time
import pytest

class TestPerformance:
    @pytest.mark.slow
    def test_collision_detection_performance(self):
        """测试大量实体下的碰撞检测性能。"""
        collision_system = CollisionSystem()
        
        # 创建包含大量实体的测试场景
        entities = [create_test_entity() for _ in range(1000)]
        
        start_time = time.time()
        collision_system.check_collisions(entities)
        elapsed_time = time.time() - start_time
        
        # 断言性能阈值
        assert elapsed_time < 0.016  # 60 FPS 阈值
```

### 内存使用测试

```python
import psutil
import os

def test_memory_usage_stability():
    """测试内存使用是否不会过度增长。"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # 模拟游戏循环
    game = Game()
    for _ in range(1000):
        game.update()
    
    final_memory = process.memory_info().rss
    memory_growth = final_memory - initial_memory
    
    # 断言内存增长是合理的
    assert memory_growth < 10 * 1024 * 1024  # 增长小于10MB
```

## 结论

本测试指南为维护和扩展 Thunder Fighter 的综合测试套件提供了基础。通过遵循这些模式和实践，开发者可以：

- 为新功能添加健壮的测试
- 保持高代码覆盖率
- 确保系统可靠性
- 及早发现回归问题
- 验证所有游戏系统的功能

有关具体的技术实现细节，请参阅[技术细节](../TECHNICAL_DETAILS_ZH.md)。有关架构指导，请参阅[架构指南](../ARCHITECTURE_ZH.md)。

---

*最后更新: 2025年1月*
*测试数量: 390+个综合测试*
*总体覆盖率目标: >85%*
