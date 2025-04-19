import pygame
import random
from thunder_fighter.sprites.explosion import Explosion
from thunder_fighter.sprites.enemy import Enemy
from thunder_fighter.sprites.items import HealthItem, BulletSpeedItem, BulletPathItem, PlayerSpeedItem
from thunder_fighter.graphics.effects import create_explosion, create_hit_effect
from thunder_fighter.utils.logger import logger

SCORE_THRESHOLD = 200  # Every 200 points might spawn an item

def check_bullet_enemy_collisions(enemies, bullets, all_sprites, score, 
                                  last_score_checkpoint, score_threshold, items_group):
    """Check collisions between bullets and enemies"""
    try:
        # 返回详细的结果
        result = {
            'enemy_hit': False,  # 是否击中敌人
            'score_checkpoint': last_score_checkpoint, # 当前得分检查点
            'enemy_count': 0,  # 击中的敌人数量
            'generated_item': False  # 是否生成了道具
        }
        
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        result['enemy_count'] = len(hits)
        result['enemy_hit'] = bool(hits)  # 如果有击中，设为True
        
        for hit in hits:
            # Add score based on enemy level
            enemy_level = getattr(hit, 'level', 0)
            score_value = 10 + enemy_level * 2
            score.update(score_value)
            
            # Create explosion effect
            explosion = Explosion(hit.rect.center, 40)
            all_sprites.add(explosion)
            
            # Check if we need to generate item based on score checkpoints
            current_score_checkpoint = score.value // score_threshold
            if current_score_checkpoint > last_score_checkpoint:
                # Get random item from factory, considering game time
                from thunder_fighter.sprites.items import create_random_item
                game_time = min(10, current_score_checkpoint // 2)  # Estimate game time based on score
                
                # Pass all required parameters to create_random_item
                create_random_item(game_time, all_sprites, items_group)
                # Item is already added to sprite groups in create_random_item
                
                last_score_checkpoint = current_score_checkpoint
                result['generated_item'] = True
                logger.info(f"Score milestone reached: {score.value}. Item spawned.")
        
        result['score_checkpoint'] = last_score_checkpoint
        return result
    except Exception as e:
        logger.error(f"Error in bullet-enemy collision check: {e}", exc_info=True)
        return {'enemy_hit': False, 'score_checkpoint': last_score_checkpoint, 'enemy_count': 0, 'generated_item': False}

def check_bullet_boss_collisions(boss, bullets, all_sprites):
    """Check collisions between player bullets and boss"""
    if boss is None:
        return {'boss_hit': False, 'boss_defeated': False, 'damage': 0}
    
    result = {
        'boss_hit': False,
        'boss_defeated': False,
        'damage': 0
    }
    
    try:
        # 添加调试日志
        logger.debug(f"Checking bullet-boss collisions. Boss rect: {boss.rect}, Health: {boss.health}")
        logger.debug(f"Bullets in group: {len(bullets)}")
        
        # 对于pygame.sprite.spritecollide，第一个参数需要是单个sprite
        # 确保boss是一个sprite实例而不是group
        if hasattr(boss, 'rect') and hasattr(boss, 'health'):
            # 使用碰撞掩码进行更精确的碰撞检测 - 使用遮罩可以提高碰撞检测的准确性
            boss_hits = pygame.sprite.spritecollide(
                boss, bullets, True, 
                pygame.sprite.collide_mask
            )
            
            # 记录碰撞结果
            hits_count = len(boss_hits)
            if hits_count > 0:
                logger.debug(f"Boss hit by {hits_count} bullets")
            
            result['boss_hit'] = bool(boss_hits)
            result['damage'] = len(boss_hits) * 10  # 每颗子弹10点伤害
            
            for hit in boss_hits:
                boss.health -= 10
                boss.damage_flash = 5  # 设置闪烁帧数
                # 创建小爆炸效果
                explosion = Explosion(hit.rect.center, 20)
                all_sprites.add(explosion)
                
                # 检查Boss是否被击败
                if boss.health <= 0:
                    # 创建大爆炸
                    for _ in range(10):
                        pos_x = random.randint(boss.rect.left, boss.rect.right)
                        pos_y = random.randint(boss.rect.top, boss.rect.bottom)
                        explosion = Explosion((pos_x, pos_y), 60)
                        all_sprites.add(explosion)
                    
                    boss.kill()
                    result['boss_defeated'] = True
                    logger.info(f"Boss defeated!")
        else:
            logger.error(f"Invalid boss instance: missing rect or health attribute")
        
        return result
    except Exception as e:
        logger.error(f"Error in bullet-boss collision check: {e}", exc_info=True)
        return {'boss_hit': False, 'boss_defeated': False, 'damage': 0}
    
def check_enemy_player_collisions(player, enemies, all_sprites):
    """Check collisions between enemies and player"""
    result = {
        'was_hit': False,
        'game_over': False,
        'damage': 0
    }
    
    try:
        hits = pygame.sprite.spritecollide(player, enemies, True)
        result['was_hit'] = bool(hits)
        
        for hit in hits:
            # 根据敌人等级增加伤害
            enemy_level = getattr(hit, 'level', 0)  # 获取敌人等级，默认为0
            damage = 15 + enemy_level * 1  # 基础伤害15，每级额外1点伤害
            player.health -= damage
            result['damage'] += damage
            
            # 创建爆炸
            explosion = Explosion(hit.rect.center, 40)
            all_sprites.add(explosion)
            
            # 如果玩家生命值为0，游戏结束
            if player.health <= 0:
                result['game_over'] = True
        
        return result
    except Exception as e:
        logger.error(f"Error in enemy-player collision check: {e}", exc_info=True)
        return {'was_hit': False, 'game_over': False, 'damage': 0}
    
def check_boss_bullet_player_collisions(player, boss_bullets, all_sprites):
    """Check collisions between boss bullets and player"""
    result = {
        'was_hit': False,
        'game_over': False,
        'damage': 0
    }
    
    try:
        hits = pygame.sprite.spritecollide(player, boss_bullets, True)
        result['was_hit'] = bool(hits)
        result['damage'] = len(hits) * 15  # 每颗Boss子弹15点伤害
        
        for hit in hits:
            player.health -= 15
            # 创建爆炸
            explosion = Explosion(hit.rect.center, 30)
            all_sprites.add(explosion)
            
            # 如果玩家生命值为0，游戏结束
            if player.health <= 0:
                result['game_over'] = True
        
        return result
    except Exception as e:
        logger.error(f"Error in boss_bullet-player collision check: {e}", exc_info=True)
        return {'was_hit': False, 'game_over': False, 'damage': 0}

def check_enemy_bullet_player_collisions(player, enemy_bullets, all_sprites):
    """Check collisions between enemy bullets and player"""
    result = {
        'was_hit': False,
        'game_over': False,
        'damage': 0
    }
    
    try:
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        result['was_hit'] = bool(hits)
        
        for hit in hits:
            # 根据敌人子弹等级计算伤害
            enemy_level = getattr(hit, 'enemy_level', 0)  # 获取子弹等级，默认为0
            damage = 5 + enemy_level * 1  # 基础伤害5，每级额外1点伤害
            player.health -= damage
            result['damage'] += damage
            
            # 创建爆炸
            explosion = Explosion(hit.rect.center, 20 + enemy_level)
            all_sprites.add(explosion)
            
            # 如果玩家生命值为0，游戏结束
            if player.health <= 0:
                result['game_over'] = True
        
        return result
    except Exception as e:
        logger.error(f"Error in enemy_bullet-player collision check: {e}", exc_info=True)
        return {'was_hit': False, 'game_over': False, 'damage': 0}
    
def check_items_player_collisions(player, items, all_sprites):
    """Check collisions between items and player"""
    result = {
        'item_collected': False,
        'item_types': []
    }
    
    try:
        hits = pygame.sprite.spritecollide(player, items, True)
        result['item_collected'] = bool(hits)
        
        for hit in hits:
            item_type = getattr(hit, 'type', 'unknown')
            result['item_types'].append(item_type)
            
            # Default effect values
            color = (255, 255, 255, 150) # Default white
            effect_size = 30
            
            # 根据道具类型执行不同操作
            if item_type == 'health':
                # 恢复生命值
                healing_amount = 25
                player.health = min(100, player.health + healing_amount)
                # 绿色恢复效果
                color = (0, 255, 0, 150)
                effect_size = 30
                
            elif item_type == 'bullet_speed':
                # 增加子弹速度
                speed_increase = getattr(hit, 'speed_increase', 1)
                new_speed = player.increase_bullet_speed(speed_increase)
                # 蓝色速度效果
                color = (0, 191, 255, 150)
                effect_size = 35
                
            elif item_type == 'bullet_path':
                # 增加弹道数量
                new_paths = player.increase_bullet_paths()
                # 黄色弹道效果
                color = (255, 255, 0, 150)
                effect_size = 40
            
            elif item_type == 'player_speed': # Handle new item type
                # 增加玩家移动速度
                speed_increase = getattr(hit, 'speed_increase', 1)
                new_speed = player.increase_player_speed(speed_increase)
                # 绿色速度效果 (use a distinct green)
                color = (0, 200, 0, 180) 
                effect_size = 38
                
            # 创建道具效果
            explosion = Explosion(hit.rect.center, effect_size)
            explosion.image.fill((0, 0, 0, 0)) # Make background transparent
            pygame.draw.circle(explosion.image, color, 
                              (explosion.size // 2, explosion.size // 2), 
                              explosion.size // 2)
            all_sprites.add(explosion)
        
        return result
    except Exception as e:
        logger.error(f"Error in item-player collision check: {e}", exc_info=True)
        return {'item_collected': False, 'item_types': []} 