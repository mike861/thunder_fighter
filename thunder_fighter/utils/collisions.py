import pygame
import random
from thunder_fighter.sprites.explosion import Explosion
from thunder_fighter.sprites.enemy import Enemy
from thunder_fighter.sprites.items import HealthItem, BulletSpeedItem, BulletPathItem, PlayerSpeedItem
from thunder_fighter.graphics.effects import create_explosion, create_hit_effect
from thunder_fighter.utils.logger import logger

SCORE_THRESHOLD = 200  # Every 200 points might spawn an item

def check_missile_enemy_collisions(missiles, enemies, all_sprites, score):
    """Checks missile-enemy collisions and creates appropriate effects."""
    hits = pygame.sprite.groupcollide(missiles, enemies, True, False)
    
    for missile, hit_enemies in hits.items():
        for enemy in hit_enemies:
            if hasattr(enemy, 'damage'):
                # It's a boss, apply damage.
                if enemy.damage(50): # damage() returns True if boss is defeated
                    explosion = create_explosion(enemy.rect.center, 'lg')
                    all_sprites.add(explosion)
                    score.update(500) # Bonus for boss kill with missile
                else:
                    # Hit but not destroyed
                    hit_effect = create_hit_effect(*missile.rect.center)
                    all_sprites.add(hit_effect)
            else:
                # It's a regular enemy, kill it.
                enemy.kill()
                explosion = create_explosion(enemy.rect.center, 'md')
                all_sprites.add(explosion)
                score.update(25) # More points for missile kill

def check_bullet_enemy_collisions(enemies, bullets, all_sprites, score, 
                                  last_score_checkpoint, score_threshold, items_group, player):
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
                from thunder_fighter.sprites.items import create_random_item
                # Hack: Get game_level from a sprite's group's game reference if available
                # This is not ideal, but avoids a large refactor to pass 'game' down.
                game_level = 1
                game_time = 0 # Placeholder for game_time
                if all_sprites.sprites():
                    game_instance = getattr(all_sprites.sprites()[0], 'game', None)
                    if game_instance:
                        game_level = getattr(game_instance, 'game_level', 1)
                        game_time = getattr(game_instance, 'game_time', 0)

                create_random_item(game_time, game_level, all_sprites, items_group, player)
                
                last_score_checkpoint = current_score_checkpoint
                result['generated_item'] = True
                logger.debug(f"Score milestone reached: {score.value}. Item spawned.")
        
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
                # 使用boss的damage方法处理伤害
                boss_defeated = boss.damage(10)
                
                # 创建小爆炸效果
                explosion = Explosion(hit.rect.center, 20)
                all_sprites.add(explosion)
                
                # 检查Boss是否被击败
                if boss_defeated:
                    # 创建大爆炸
                    for _ in range(10):
                        pos_x = random.randint(boss.rect.left, boss.rect.right)
                        pos_y = random.randint(boss.rect.top, boss.rect.bottom)
                        explosion = Explosion((pos_x, pos_y), 60)
                        all_sprites.add(explosion)
                    
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
            
            # 使用take_damage处理伤害和效果
            if player.take_damage(damage):
                result['game_over'] = True
            
            result['damage'] += damage
            
            # 创建爆炸
            explosion = Explosion(hit.rect.center, 20 + enemy_level)
            all_sprites.add(explosion)
        
        return result
    except Exception as e:
        logger.error(f"Error in enemy_bullet-player collision check: {e}", exc_info=True)
        return {'was_hit': False, 'game_over': False, 'damage': 0}
    
def check_items_player_collisions(items, player, ui_manager):
    """Check collisions between items and player"""
    
    hits = pygame.sprite.spritecollide(player, items, True)
    for hit in hits:
        item_type = getattr(hit, 'type', 'unknown')
        
        # 根据道具类型执行不同操作
        if item_type == 'health':
            player.heal()
        elif item_type == 'bullet_speed':
            player.increase_bullet_speed()
        elif item_type == 'bullet_path':
            player.increase_bullet_paths()
        elif item_type == 'player_speed':
            player.increase_player_speed()
        elif item_type == 'wingman':
            player.add_wingman()
        
        # 显示通知
        if ui_manager:
            ui_manager.show_item_collected(item_type)
        
        # 播放音效
        from thunder_fighter.utils.sound_manager import sound_manager
        sound_manager.play_sound('item_pickup') 