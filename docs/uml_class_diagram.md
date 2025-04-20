# Thunder Fighter - UML Class Diagram

```mermaid
classDiagram
    direction LR

    class pygame.sprite.Sprite {
        <<Abstract>>
        +image
        +rect
        +mask
        +update()
        +kill()
        +alive()
    }

    class Game {
        -screen
        -clock
        -all_sprites : Group
        -bullets : Group
        -enemies : Group
        -boss_bullets : Group
        -enemy_bullets : Group
        -items : Group
        -stars : list~Star~
        -player : Player
        -boss : Boss
        -score : Score
        -font_large
        -font_medium
        -font_small
        -running : bool
        -paused : bool
        +__init__()
        +spawn_enemy()
        +spawn_boss()
        +spawn_random_item()
        +handle_events()
        +update()
        +render()
        +run()
    }

    class Player {
        -health
        -shoot_delay
        -speed
        -bullet_speed
        -bullet_paths
        +__init__(all_sprites, bullets_group)
        +update()
        +shoot()
        +take_damage(damage)
        +heal(amount)
        +increase_bullet_speed(amount)
        +increase_bullet_paths()
    }
    pygame.sprite.Sprite <|-- Player
    Game "1" *-- "1" Player
    Player o-- Bullet : creates >

    class Enemy {
        -level
        -speedy
        -speedx
        -can_shoot : bool
        -shoot_delay
        +__init__(game_time, all_sprites, enemy_bullets_group)
        +update()
        +shoot()
        +get_level()
    }
    pygame.sprite.Sprite <|-- Enemy
    Game *-- "0..*" Enemy : contains in group
    Enemy o-- EnemyBullet : creates >

    class Boss {
        -level
        -original_image
        -flash_images : list
        -mask
        -health
        -max_health
        -shoot_delay
        -bullet_count
        -damage_flash
        +__init__(all_sprites, boss_bullets_group, level)
        -_create_flash_images()
        +update()
        +shoot()
        +draw_health_bar(surface)
    }
    pygame.sprite.Sprite <|-- Boss
    Game "1" *-- "0..1" Boss
    Boss o-- BossBullet : creates >

    class Bullet {
        -speed
        -angle
        +__init__(x, y, speed, angle)
        +update()
    }
    pygame.sprite.Sprite <|-- Bullet
    Game *-- "0..*" Bullet : contains in group

    class BossBullet {
        -speedy
        +__init__(x, y)
        +update()
    }
    pygame.sprite.Sprite <|-- BossBullet
    Game *-- "0..*" BossBullet : contains in group

    class EnemyBullet {
        -enemy_level
        -speedy
        -speedx
        -curve : bool
        +__init__(x, y, enemy_level)
        -_create_enemy_bullet()
        +update()
    }
    pygame.sprite.Sprite <|-- EnemyBullet
    Game *-- "0..*" EnemyBullet : contains in group

    class Item {
        <<Abstract>>
        -type : str
        -speedy
        +update()
    }
    pygame.sprite.Sprite <|-- Item

    class HealthItem {
        +__init__()
    }
    Item <|-- HealthItem
    Game *-- "0..*" HealthItem : contains in group

    class BulletSpeedItem {
        -speed_increase
        +__init__()
    }
    Item <|-- BulletSpeedItem
    Game *-- "0..*" BulletSpeedItem : contains in group

    class BulletPathItem {
        +__init__()
    }
    Item <|-- BulletPathItem
    Game *-- "0..*" BulletPathItem : contains in group


    class Explosion {
        -size
        -frame
        +__init__(center, size)
        +update()
    }
    pygame.sprite.Sprite <|-- Explosion
    Game *-- "0..*" Explosion : contains in group

    class Star {
        -speed
        -size
        +__init__(x, y)
        +update()
        +draw(surface)
    }
    pygame.sprite.Sprite <|-- Star
    Game *-- "0..*" Star : contains in list

    class HitEffect {
      -alpha
      +__init__(x, y)
      +update()
    }
    pygame.sprite.Sprite <|-- HitEffect
    Game *-- "0..*" HitEffect : contains in group

    class Score {
        -value
        -font
        +__init__()
        +update(points)
        +draw(surface)
    }
    Game "1" *-- "1" Score

    class SoundManager {
        -sounds : dict
        -sound_enabled : bool
        -music_enabled : bool
        -sound_volume : float
        -music_volume : float
        +__init__(...)
        +play_sound(sound_key)
        +play_background_music(filename)
        +set_sound_volume(volume)
        +set_music_volume(volume)
    }
    Game ..> SoundManager : uses

    note for pygame.sprite.Sprite "Represents a base Pygame sprite"
    note for Item "Abstract base class for items (conceptual)"
