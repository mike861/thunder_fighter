"""
实体生成系统

统一管理敌人、道具、Boss等的生成逻辑。
整合各个工厂类的调用。
"""

import random
from typing import Dict, List, Any, Optional
from thunder_fighter.utils.logger import logger


class SpawningSystem:
    """实体生成系统类"""
    
    def __init__(self):
        self.enemy_factory = None
        self.boss_factory = None
        self.item_factory = None
        self.spawn_timers = {}
        self.spawn_rates = {}
        self.last_spawn_times = {}
        
        # 初始化生成参数
        self._setup_spawn_parameters()
        
        # 延迟初始化工厂（避免循环导入）
        self._factories_initialized = False
    
    def _setup_spawn_parameters(self):
        """设置生成参数"""
        self.spawn_rates = {
            'enemy': 2.0,      # 每2秒生成一个敌人
            'boss': 30.0,      # 每30秒生成一个Boss
            'item': 10.0,      # 每10秒可能生成一个道具
        }
        
        # 重置上次生成时间
        self.last_spawn_times = {
            'enemy': 0.0,
            'boss': 0.0,
            'item': 0.0,
        }
    
    def _init_factories(self):
        """初始化工厂类"""
        if not self._factories_initialized:
            try:
                from thunder_fighter.entities.enemy_factory import EnemyFactory
                from thunder_fighter.entities.boss_factory import BossFactory
                from thunder_fighter.entities.item_factory import ItemFactory
                
                self.enemy_factory = EnemyFactory()
                self.boss_factory = BossFactory()
                self.item_factory = ItemFactory()
                
                self._factories_initialized = True
                logger.info("Spawning system factories initialized")
            except ImportError as e:
                logger.error(f"Failed to initialize factories: {e}")
    
    def update(self, dt: float, game_state: Dict[str, Any]):
        """更新生成逻辑"""
        if not self._factories_initialized:
            self._init_factories()
        
        current_time = game_state.get('game_time', 0.0)
        
        self._update_enemy_spawning(dt, current_time, game_state)
        self._update_boss_spawning(dt, current_time, game_state)
        self._update_item_spawning(dt, current_time, game_state)
    
    def _update_enemy_spawning(self, dt: float, current_time: float, game_state: Dict[str, Any]):
        """更新敌人生成"""
        if not self.enemy_factory:
            return
        
        # 检查是否到了生成时间
        if current_time - self.last_spawn_times['enemy'] >= self.spawn_rates['enemy']:
            try:
                # 根据游戏等级调整敌人难度
                game_level = game_state.get('level', 1)
                enemy_level = min(game_level, 5)  # 最大等级5
                
                # 生成敌人
                enemy = self.enemy_factory.create_enemy(
                    level=enemy_level,
                    x=random.randint(50, game_state.get('screen_width', 800) - 50),
                    y=-50
                )
                
                # 添加到sprite组
                enemies_group = game_state.get('enemies_group')
                all_sprites = game_state.get('all_sprites')
                
                if enemies_group and all_sprites:
                    enemies_group.add(enemy)
                    all_sprites.add(enemy)
                
                self.last_spawn_times['enemy'] = current_time
                logger.debug(f"Enemy spawned at level {enemy_level}")
                
            except Exception as e:
                logger.error(f"Error spawning enemy: {e}")
    
    def _update_boss_spawning(self, dt: float, current_time: float, game_state: Dict[str, Any]):
        """更新Boss生成"""
        if not self.boss_factory:
            return
        
        # 检查是否到了生成时间且没有活跃的Boss
        if (current_time - self.last_spawn_times['boss'] >= self.spawn_rates['boss'] and
            not game_state.get('boss_active', False)):
            
            try:
                # 根据游戏等级调整Boss难度
                game_level = game_state.get('level', 1)
                boss_level = min(game_level // 2 + 1, 3)  # Boss等级稍低但不超过3
                
                # 生成Boss
                boss = self.boss_factory.create_boss(
                    level=boss_level,
                    x=game_state.get('screen_width', 800) // 2,
                    y=100
                )
                
                # 添加到sprite组
                bosses_group = game_state.get('bosses_group')
                all_sprites = game_state.get('all_sprites')
                
                if bosses_group and all_sprites:
                    bosses_group.add(boss)
                    all_sprites.add(boss)
                
                self.last_spawn_times['boss'] = current_time
                logger.info(f"Boss spawned at level {boss_level}")
                
            except Exception as e:
                logger.error(f"Error spawning boss: {e}")
    
    def _update_item_spawning(self, dt: float, current_time: float, game_state: Dict[str, Any]):
        """更新道具生成"""
        if not self.item_factory:
            return
        
        # 随机生成道具（概率性）
        if (current_time - self.last_spawn_times['item'] >= self.spawn_rates['item'] and
            random.random() < 0.3):  # 30%概率生成道具
            
            try:
                # 随机选择道具类型
                item_types = ['health', 'bullet_speed', 'bullet_path', 'player_speed']
                item_type = random.choice(item_types)
                
                # 生成道具
                item = self.item_factory.create_item(
                    item_type=item_type,
                    x=random.randint(50, game_state.get('screen_width', 800) - 50),
                    y=-30
                )
                
                # 添加到sprite组
                items_group = game_state.get('items_group')
                all_sprites = game_state.get('all_sprites')
                
                if items_group and all_sprites:
                    items_group.add(item)
                    all_sprites.add(item)
                
                self.last_spawn_times['item'] = current_time
                logger.debug(f"Item spawned: {item_type}")
                
            except Exception as e:
                logger.error(f"Error spawning item: {e}")
    
    def set_spawn_rate(self, entity_type: str, rate: float):
        """设置生成速率"""
        if entity_type in self.spawn_rates:
            self.spawn_rates[entity_type] = rate
            logger.info(f"Spawn rate for {entity_type} set to {rate}")
    
    def reset_spawn_times(self):
        """重置生成时间"""
        current_time = 0.0
        for entity_type in self.last_spawn_times:
            self.last_spawn_times[entity_type] = current_time
        logger.info("Spawn times reset")
    
    def get_spawn_statistics(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        return {
            'spawn_rates': self.spawn_rates.copy(),
            'last_spawn_times': self.last_spawn_times.copy(),
            'factories_initialized': self._factories_initialized,
        }