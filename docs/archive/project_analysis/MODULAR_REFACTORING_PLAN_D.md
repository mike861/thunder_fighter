# Thunder Fighter 模块化微调重构方案D - 详细实施计划

## 概述

基于项目处于内部测试阶段，无需过度考虑向后兼容性，我们采用方案D进行模块化微调，引入**Systems概念**来重组代码结构。

## 方案D核心理念

将代码按照**系统职责**而非传统的**对象类型**进行组织：
- **Systems**: 游戏系统逻辑（碰撞、分数、生成、输入等）
- **Entities**: 游戏对象定义和工厂
- **Graphics**: 视觉渲染和效果
- **Utils**: 纯工具类

## 详细目录结构设计

### 目标结构
```
thunder_fighter/
├── __init__.py
├── __main__.py              # 新增
├── game.py                  # 保留在根目录
├── config.py                # 保留在根目录
├── constants.py             # 保留在根目录
├── systems/                 # 新增：游戏系统
│   ├── __init__.py
│   ├── collision.py         # 从utils/collisions.py移入并重构
│   ├── scoring.py           # 从utils/score.py移入并重构
│   ├── spawning.py          # 新增：统一管理所有生成逻辑
│   ├── physics.py           # 新增：物理系统（移动、边界等）
│   └── input/               # 移入input作为子系统
│       ├── __init__.py
│       ├── handler.py       # 重命名input_handler.py
│       ├── manager.py       # 重命名input_manager.py
│       ├── facade.py        # 重命名input_system.py
│       ├── events.py        # 保留input_events.py
│       ├── bindings.py      # 保留key_bindings.py
│       └── adapters/        # 保留适配器目录
│           ├── __init__.py
│           └── pygame_adapter.py
├── entities/                # 重构：游戏对象和工厂
│   ├── __init__.py
│   ├── base.py              # 新增：基础实体类
│   ├── player/              # 新增子目录
│   │   ├── __init__.py
│   │   ├── player.py        # 从sprites移入
│   │   ├── player_factory.py # 从entities移入
│   │   └── wingman.py       # 从sprites移入
│   ├── enemies/             # 新增子目录
│   │   ├── __init__.py
│   │   ├── enemy.py         # 从sprites移入
│   │   ├── enemy_factory.py # 从entities移入
│   │   ├── boss.py          # 从sprites移入
│   │   └── boss_factory.py  # 从entities移入
│   ├── projectiles/         # 新增子目录
│   │   ├── __init__.py
│   │   ├── bullets.py       # 从sprites移入
│   │   ├── missile.py       # 从sprites移入
│   │   └── projectile_factory.py # 从entities移入
│   └── items/               # 新增子目录
│       ├── __init__.py
│       ├── items.py         # 从sprites移入
│       └── item_factory.py  # 从entities移入
├── graphics/                # 扩展：图形系统
│   ├── __init__.py
│   ├── renderers.py         # 保留
│   ├── background.py        # 保留
│   ├── effects/             # 新增子目录
│   │   ├── __init__.py
│   │   ├── explosion.py     # 从sprites移入
│   │   ├── particles.py     # 新增：粒子效果系统
│   │   └── stars.py         # 从utils移入
│   └── ui/                  # 保留现有结构
│       ├── __init__.py
│       ├── manager.py       # 重命名ui_manager.py
│       └── components/      # 重新组织UI组件
│           ├── __init__.py
│           ├── health_bar.py
│           ├── notification_manager.py
│           ├── boss_status_display.py
│           ├── game_info_display.py
│           ├── player_stats_display.py
│           ├── dev_info_display.py
│           └── screen_overlay_manager.py
├── events/                  # 保留：事件系统
├── localization/            # 保留：国际化
├── state/                   # 保留：状态管理
├── utils/                   # 精简：只保留纯工具类
│   ├── __init__.py
│   ├── logger.py
│   ├── resource_manager.py
│   ├── config_manager.py
│   ├── config_tool.py
│   ├── sound_manager.py
│   └── pause_manager.py
└── assets/                  # 保留：游戏资源
```

## 分阶段实施计划

### 阶段1：准备和规划（1天）

#### 1.1 创建新目录结构
```bash
# 创建systems目录
mkdir -p thunder_fighter/systems/input/adapters

# 创建entities子目录
mkdir -p thunder_fighter/entities/{player,enemies,projectiles,items}

# 创建graphics/effects目录
mkdir -p thunder_fighter/graphics/effects

# 重组UI目录
mkdir -p thunder_fighter/graphics/ui/components
```

#### 1.2 备份当前状态
```bash
# 创建备份分支
git checkout -b backup-before-refactoring

# 提交当前状态
git add -A
git commit -m "backup: 重构前的完整项目状态"

# 创建新的重构分支
git checkout -b refactoring-systems-concept
```

### 阶段2：Systems目录建立（2天）

#### 2.1 创建系统文件

**2.1.1 碰撞系统** (`systems/collision.py`)
```python
"""
碰撞检测系统

统一管理所有游戏实体间的碰撞检测逻辑。
从utils/collisions.py重构而来，增加系统化管理。
"""

import pygame
from typing import List, Tuple, Optional
from ..entities.base import GameObject
from ..graphics.effects.explosion import Explosion
from ..utils.logger import logger


class CollisionSystem:
    """碰撞检测系统类"""
    
    def __init__(self):
        self.collision_handlers = {}
        self._setup_collision_handlers()
    
    def _setup_collision_handlers(self):
        """设置碰撞处理器映射"""
        # 实现具体的碰撞处理逻辑
        pass
    
    def check_all_collisions(self, game_state):
        """检查所有碰撞"""
        # 重构原有的碰撞检测函数
        pass
```

**2.1.2 分数系统** (`systems/scoring.py`)
```python
"""
分数管理系统

统一管理游戏分数、等级、成就等相关逻辑。
从utils/score.py重构而来。
"""

from typing import Dict, List, Callable
from ..utils.logger import logger


class ScoringSystem:
    """分数管理系统类"""
    
    def __init__(self):
        self.score = 0
        self.level = 1
        self.score_multiplier = 1.0
        self.achievement_callbacks: List[Callable] = []
    
    def add_score(self, points: int, source: str = ""):
        """添加分数"""
        actual_points = int(points * self.score_multiplier)
        self.score += actual_points
        logger.info(f"Score added: {actual_points} from {source}")
        self._check_level_up()
    
    def _check_level_up(self):
        """检查是否升级"""
        # 实现升级逻辑
        pass
```

**2.1.3 生成系统** (`systems/spawning.py`)
```python
"""
实体生成系统

统一管理敌人、道具、Boss等的生成逻辑。
整合各个工厂类的调用。
"""

import random
from typing import Dict, List, Any
from ..entities.enemies.enemy_factory import EnemyFactory
from ..entities.enemies.boss_factory import BossFactory
from ..entities.items.item_factory import ItemFactory
from ..utils.logger import logger


class SpawningSystem:
    """实体生成系统类"""
    
    def __init__(self):
        self.enemy_factory = EnemyFactory()
        self.boss_factory = BossFactory()
        self.item_factory = ItemFactory()
        self.spawn_timers = {}
    
    def update(self, dt: float, game_state: Dict[str, Any]):
        """更新生成逻辑"""
        self._update_enemy_spawning(dt, game_state)
        self._update_boss_spawning(dt, game_state)
        self._update_item_spawning(dt, game_state)
    
    def _update_enemy_spawning(self, dt: float, game_state: Dict[str, Any]):
        """更新敌人生成"""
        # 实现敌人生成逻辑
        pass
```

**2.1.4 物理系统** (`systems/physics.py`)
```python
"""
物理系统

管理游戏中的物理相关逻辑：移动、边界检测、速度控制等。
"""

import pygame
from typing import List, Tuple
from ..entities.base import GameObject


class PhysicsSystem:
    """物理系统类"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gravity = 0  # 太空游戏通常无重力
    
    def update_movement(self, entities: List[GameObject], dt: float):
        """更新所有实体的移动"""
        for entity in entities:
            self._update_entity_movement(entity, dt)
            self._check_boundaries(entity)
    
    def _update_entity_movement(self, entity: GameObject, dt: float):
        """更新单个实体移动"""
        # 实现移动逻辑
        pass
    
    def _check_boundaries(self, entity: GameObject):
        """检查边界"""
        # 实现边界检测
        pass
```

#### 2.2 重构Input系统移入systems

**移动并重命名文件**：
```bash
# 移动input系统到systems
mv thunder_fighter/input/* thunder_fighter/systems/input/

# 重命名文件以明确职责
cd thunder_fighter/systems/input/
mv input_handler.py handler.py
mv input_manager.py manager.py
mv input_system.py facade.py
mv input_events.py events.py
mv key_bindings.py bindings.py
```

### 阶段3：Entities目录重组（2天）

#### 3.1 创建基础实体类

**3.1.1 基础实体类** (`entities/base.py`)
```python
"""
基础实体类定义

定义所有游戏对象的基类和通用接口。
"""

import pygame
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any


class GameObject(pygame.sprite.Sprite, ABC):
    """游戏对象基类"""
    
    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.health = 1
        self.max_health = 1
        self.active = True
    
    @abstractmethod
    def update(self, dt: float):
        """更新游戏对象状态"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """渲染游戏对象"""
        pass
    
    def take_damage(self, damage: int) -> bool:
        """承受伤害，返回是否被摧毁"""
        self.health -= damage
        return self.health <= 0


class Entity(GameObject):
    """具体实体类，提供默认实现"""
    
    def update(self, dt: float):
        """默认更新实现"""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def render(self, screen: pygame.Surface):
        """默认渲染实现"""
        if hasattr(self, 'image') and hasattr(self, 'rect'):
            screen.blit(self.image, self.rect)


class EntityFactory(ABC):
    """实体工厂基类"""
    
    @abstractmethod
    def create(self, *args, **kwargs) -> GameObject:
        """创建实体实例"""
        pass
```

#### 3.2 按类型组织实体文件

**3.2.1 移动玩家相关文件**：
```bash
# 移动玩家文件
mv thunder_fighter/sprites/player.py thunder_fighter/entities/player/
mv thunder_fighter/sprites/wingman.py thunder_fighter/entities/player/
mv thunder_fighter/entities/player_factory.py thunder_fighter/entities/player/
```

**3.2.2 移动敌人相关文件**：
```bash
# 移动敌人文件
mv thunder_fighter/sprites/enemy.py thunder_fighter/entities/enemies/
mv thunder_fighter/sprites/boss.py thunder_fighter/entities/enemies/
mv thunder_fighter/entities/enemy_factory.py thunder_fighter/entities/enemies/
mv thunder_fighter/entities/boss_factory.py thunder_fighter/entities/enemies/
```

**3.2.3 移动弹药相关文件**：
```bash
# 移动弹药文件
mv thunder_fighter/sprites/bullets.py thunder_fighter/entities/projectiles/
mv thunder_fighter/sprites/missile.py thunder_fighter/entities/projectiles/
mv thunder_fighter/entities/projectile_factory.py thunder_fighter/entities/projectiles/
```

**3.2.4 移动道具相关文件**：
```bash
# 移动道具文件
mv thunder_fighter/sprites/items.py thunder_fighter/entities/items/
mv thunder_fighter/entities/item_factory.py thunder_fighter/entities/items/
```

### 阶段4：Graphics目录优化（1天）

#### 4.1 整理图形效果

```bash
# 移动爆炸效果
mv thunder_fighter/sprites/explosion.py thunder_fighter/graphics/effects/

# 移动星空效果
mv thunder_fighter/utils/stars.py thunder_fighter/graphics/effects/

# 重命名UI管理器
mv thunder_fighter/graphics/ui_manager.py thunder_fighter/graphics/ui/manager.py

# 移动UI组件到components子目录
mv thunder_fighter/graphics/ui/*.py thunder_fighter/graphics/ui/components/
mv thunder_fighter/graphics/ui/components/manager.py thunder_fighter/graphics/ui/
```

#### 4.2 创建粒子效果系统

**4.2.1 粒子系统** (`graphics/effects/particles.py`)
```python
"""
粒子效果系统

统一管理各种粒子特效：爆炸、尾迹、闪光等。
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from ...utils.logger import logger


class Particle:
    """单个粒子类"""
    
    def __init__(self, x: float, y: float, velocity: Tuple[float, float], 
                 color: Tuple[int, int, int], lifetime: float, size: int = 2):
        self.x = x
        self.y = y
        self.velocity_x, self.velocity_y = velocity
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.active = True
    
    def update(self, dt: float):
        """更新粒子状态"""
        if not self.active:
            return
        
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.active = False
    
    def render(self, screen: pygame.Surface):
        """渲染粒子"""
        if not self.active:
            return
        
        # 计算透明度（基于剩余生命时间）
        alpha_ratio = self.lifetime / self.max_lifetime
        alpha = int(255 * alpha_ratio)
        
        # 创建带透明度的表面
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(surf, color_with_alpha, (self.size, self.size), self.size)
        
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    """粒子系统管理器"""
    
    def __init__(self):
        self.particles: List[Particle] = []
    
    def create_explosion(self, x: float, y: float, particle_count: int = 20):
        """创建爆炸效果"""
        colors = [(255, 255, 0), (255, 128, 0), (255, 0, 0)]  # 黄、橙、红
        
        for _ in range(particle_count):
            # 随机方向和速度
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            
            color = random.choice(colors)
            lifetime = random.uniform(0.5, 1.5)
            size = random.randint(2, 4)
            
            particle = Particle(x, y, velocity, color, lifetime, size)
            self.particles.append(particle)
    
    def update(self, dt: float):
        """更新所有粒子"""
        for particle in self.particles[:]:  # 使用切片复制以便安全删除
            particle.update(dt)
            if not particle.active:
                self.particles.remove(particle)
    
    def render(self, screen: pygame.Surface):
        """渲染所有粒子"""
        for particle in self.particles:
            particle.render(screen)
    
    def clear(self):
        """清空所有粒子"""
        self.particles.clear()
```

### 阶段5：Import路径更新（2天）

#### 5.1 更新所有import语句

创建一个脚本来批量更新import路径：

**5.1.1 创建import更新脚本** (`scripts/update_imports.py`)
```python
"""
Import路径更新脚本

自动更新所有Python文件中的import语句以匹配新的目录结构。
"""

import os
import re
from pathlib import Path

# 定义旧路径到新路径的映射
IMPORT_MAPPINGS = {
    # Utils中的游戏逻辑移到systems
    'from thunder_fighter.utils.collisions import': 'from thunder_fighter.systems.collision import',
    'from thunder_fighter.utils.score import': 'from thunder_fighter.systems.scoring import',
    'from thunder_fighter.utils.stars import': 'from thunder_fighter.graphics.effects.stars import',
    
    # Input系统移到systems
    'from thunder_fighter.input.input_handler import': 'from thunder_fighter.systems.input.handler import',
    'from thunder_fighter.input.input_manager import': 'from thunder_fighter.systems.input.manager import',
    'from thunder_fighter.input.input_system import': 'from thunder_fighter.systems.input.facade import',
    'from thunder_fighter.input.input_events import': 'from thunder_fighter.systems.input.events import',
    'from thunder_fighter.input.key_bindings import': 'from thunder_fighter.systems.input.bindings import',
    
    # Sprites移到entities
    'from thunder_fighter.sprites.player import': 'from thunder_fighter.entities.player.player import',
    'from thunder_fighter.sprites.enemy import': 'from thunder_fighter.entities.enemies.enemy import',
    'from thunder_fighter.sprites.boss import': 'from thunder_fighter.entities.enemies.boss import',
    'from thunder_fighter.sprites.bullets import': 'from thunder_fighter.entities.projectiles.bullets import',
    'from thunder_fighter.sprites.missile import': 'from thunder_fighter.entities.projectiles.missile import',
    'from thunder_fighter.sprites.items import': 'from thunder_fighter.entities.items.items import',
    'from thunder_fighter.sprites.wingman import': 'from thunder_fighter.entities.player.wingman import',
    'from thunder_fighter.sprites.explosion import': 'from thunder_fighter.graphics.effects.explosion import',
    
    # Entities工厂移到对应子目录
    'from thunder_fighter.entities.player_factory import': 'from thunder_fighter.entities.player.player_factory import',
    'from thunder_fighter.entities.enemy_factory import': 'from thunder_fighter.entities.enemies.enemy_factory import',
    'from thunder_fighter.entities.boss_factory import': 'from thunder_fighter.entities.enemies.boss_factory import',
    'from thunder_fighter.entities.projectile_factory import': 'from thunder_fighter.entities.projectiles.projectile_factory import',
    'from thunder_fighter.entities.item_factory import': 'from thunder_fighter.entities.items.item_factory import',
    
    # UI重组
    'from thunder_fighter.graphics.ui_manager import': 'from thunder_fighter.graphics.ui.manager import',
}

def update_file_imports(file_path: Path):
    """更新单个文件的import语句"""
    if not file_path.suffix == '.py':
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 应用所有映射
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # 如果有修改，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated imports in: {file_path}")
    
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    thunder_fighter_dir = project_root / 'thunder_fighter'
    tests_dir = project_root / 'tests'
    
    # 更新主项目文件
    for py_file in thunder_fighter_dir.rglob('*.py'):
        update_file_imports(py_file)
    
    # 更新测试文件
    for py_file in tests_dir.rglob('*.py'):
        update_file_imports(py_file)
    
    # 更新根目录的main.py
    main_py = project_root / 'main.py'
    if main_py.exists():
        update_file_imports(main_py)
    
    print("Import update completed!")

if __name__ == "__main__":
    main()
```

#### 5.2 更新__init__.py文件

**5.2.1 更新各级__init__.py文件**以提供便捷导入：

**thunder_fighter/systems/__init__.py**:
```python
"""
游戏系统模块

包含所有游戏核心系统的实现。
"""

from .collision import CollisionSystem
from .scoring import ScoringSystem
from .spawning import SpawningSystem
from .physics import PhysicsSystem

__all__ = [
    'CollisionSystem',
    'ScoringSystem', 
    'SpawningSystem',
    'PhysicsSystem',
]
```

**thunder_fighter/entities/__init__.py**:
```python
"""
游戏实体模块

包含所有游戏对象的定义和工厂类。
"""

from .base import GameObject, Entity, EntityFactory

# 便捷导入
from .player.player import Player
from .player.player_factory import PlayerFactory
from .enemies.enemy import Enemy
from .enemies.enemy_factory import EnemyFactory
from .enemies.boss import Boss
from .enemies.boss_factory import BossFactory

__all__ = [
    'GameObject', 'Entity', 'EntityFactory',
    'Player', 'PlayerFactory',
    'Enemy', 'EnemyFactory',
    'Boss', 'BossFactory',
]
```

### 阶段6：测试验证（1天）

#### 6.1 运行所有测试

```bash
# 运行完整测试套件
python -m pytest tests/ -v

# 如果有失败，逐个修复import问题
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/sprites/ -v
```

#### 6.2 创建重构验证测试

**6.2.1 创建重构验证测试** (`tests/test_refactoring_verification.py`)
```python
"""
重构验证测试

验证重构后的目录结构和import路径是否正确。
"""

import pytest
import importlib
from pathlib import Path

def test_systems_imports():
    """测试systems模块是否可以正确导入"""
    try:
        from thunder_fighter.systems.collision import CollisionSystem
        from thunder_fighter.systems.scoring import ScoringSystem
        from thunder_fighter.systems.spawning import SpawningSystem
        from thunder_fighter.systems.physics import PhysicsSystem
        assert True
    except ImportError as e:
        pytest.fail(f"Systems import failed: {e}")

def test_entities_imports():
    """测试entities模块是否可以正确导入"""
    try:
        from thunder_fighter.entities.base import GameObject, Entity
        from thunder_fighter.entities.player.player import Player
        from thunder_fighter.entities.enemies.enemy import Enemy
        assert True
    except ImportError as e:
        pytest.fail(f"Entities import failed: {e}")

def test_graphics_effects_imports():
    """测试graphics.effects模块是否可以正确导入"""
    try:
        from thunder_fighter.graphics.effects.explosion import Explosion
        from thunder_fighter.graphics.effects.stars import Stars
        from thunder_fighter.graphics.effects.particles import ParticleSystem
        assert True
    except ImportError as e:
        pytest.fail(f"Graphics effects import failed: {e}")

def test_input_system_imports():
    """测试input系统是否可以正确导入"""
    try:
        from thunder_fighter.systems.input.handler import InputHandler
        from thunder_fighter.systems.input.manager import InputManager
        from thunder_fighter.systems.input.facade import InputSystem
        assert True
    except ImportError as e:
        pytest.fail(f"Input system import failed: {e}")

def test_directory_structure():
    """测试目录结构是否符合预期"""
    project_root = Path(__file__).parent.parent
    tf_dir = project_root / 'thunder_fighter'
    
    # 检查关键目录是否存在
    expected_dirs = [
        'systems',
        'systems/input',
        'entities/player',
        'entities/enemies', 
        'entities/projectiles',
        'entities/items',
        'graphics/effects',
        'graphics/ui/components',
    ]
    
    for dir_path in expected_dirs:
        full_path = tf_dir / dir_path
        assert full_path.exists(), f"Directory {dir_path} does not exist"
        assert full_path.is_dir(), f"{dir_path} is not a directory"

def test_old_directories_cleaned():
    """测试旧目录是否已清理"""
    project_root = Path(__file__).parent.parent
    tf_dir = project_root / 'thunder_fighter'
    
    # 检查旧目录是否已删除或为空
    old_sprites_dir = tf_dir / 'sprites'
    old_entities_dir = tf_dir / 'entities'
    old_input_dir = tf_dir / 'input'
    
    # sprites目录应该被删除
    assert not old_sprites_dir.exists(), "Old sprites directory still exists"
    
    # entities目录应该只包含子目录，没有直接的工厂文件
    if old_entities_dir.exists():
        factory_files = list(old_entities_dir.glob('*_factory.py'))
        assert len(factory_files) == 0, f"Old factory files still in entities/: {factory_files}"
    
    # input目录应该被删除
    assert not old_input_dir.exists(), "Old input directory still exists"
```

#### 6.3 游戏功能验证

```bash
# 尝试启动游戏验证基本功能
python main.py

# 运行配置工具验证
python -m thunder_fighter.utils.config_tool show
```

### 阶段7：文档更新（1天）

#### 7.1 更新项目文档

更新以下文档文件：
- README.md
- CLAUDE.md
- docs/目录下的所有架构文档

#### 7.2 创建重构说明文档

**7.2.1 创建重构完成报告** (`REFACTORING_COMPLETION_REPORT.md`)

### 阶段8：清理和优化（1天）

#### 8.1 删除空目录和临时文件

```bash
# 删除空的旧目录
find thunder_fighter/ -type d -empty -delete

# 删除移动过程中可能产生的临时文件
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

#### 8.2 代码质量检查

```bash
# 运行代码格式检查
ruff check thunder_fighter/
ruff format thunder_fighter/

# 运行类型检查
mypy thunder_fighter/
```

## 实施时间表

| 阶段 | 任务 | 预计时间 | 关键产出 |
|------|------|----------|----------|
| 1 | 准备和规划 | 1天 | 目录结构、备份 |
| 2 | Systems目录建立 | 2天 | 核心系统类、Input重组 |
| 3 | Entities目录重组 | 2天 | 按类型组织的实体 |
| 4 | Graphics目录优化 | 1天 | 效果系统、UI重组 |
| 5 | Import路径更新 | 2天 | 更新脚本、路径修正 |
| 6 | 测试验证 | 1天 | 验证测试、功能测试 |
| 7 | 文档更新 | 1天 | 更新文档、架构说明 |
| 8 | 清理和优化 | 1天 | 代码质量、最终清理 |

**总计：11天**

## 风险控制

1. **每个阶段都有git提交点**，可以随时回滚
2. **保持备份分支**，确保数据安全
3. **逐步验证**，每移动一个模块就测试一次
4. **分模块实施**，降低复杂度
5. **自动化脚本**，减少手工错误

## 预期收益

1. **更清晰的系统概念**：代码按功能系统组织
2. **更好的可维护性**：相关代码集中管理
3. **更强的扩展性**：新系统容易添加
4. **更好的测试性**：系统可以独立测试
5. **更现代的架构**：符合游戏开发最佳实践