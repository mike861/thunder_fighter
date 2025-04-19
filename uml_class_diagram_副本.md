# Thunder Fighter - UML Class Diagram

```mermaid
classDiagram
    direction LR

    class pygame.sprite.Sprite {
        <<Abstract>>
        +update()
        +kill()
        #image
        #rect
        #mask
    }

    class Game {
        -screen
        -clock
        -running: bool
        -paused: bool
        -all_sprites: Group
        -bullets: Group
        -enemies: Group
        -boss_bullets: Group
        -enemy_bullets: Group
        -items: Group
        -player: Player
        -boss: Boss
        -score: Score
        -stars: list~Star~
        -sound_manager: SoundManager
        -font_large
        -font_medium
        -font_small
        +__init__()
        +run()
        +handle_events()
        +update()
        +render()
        +spawn_enemy()
        +spawn_boss()
        +spawn_random_item()
    }

    class Player {
        +health: int
        +shoot_delay: int
        +bullet_speed: int
        +bullet_paths: int
        +last_shot
        +damage_flash
        +__init__(all_sprites, bullets_group)
        +update()
        +shoot()
        +take_damage(damage)
        +heal(amount)
        +increase_bullet_speed(amount)
        +increase_bullet_paths()
    }
    pygame.sprite.Sprite <|-- Player

    class Enemy {
        +level: int
        +speedx: int
        +speedy: int
        +can_shoot: bool
        +shoot_delay: int
        +last_shot
        +__init__(game_time, all_sprites, enemy_bullets_group)
        +update()
        +shoot()
        +_determine_level(game_time)
        +get_level()
    }
    pygame.sprite.Sprite <|-- Enemy

    class Boss {
        +level: int
        +health: int
        +max_health: int
        +shoot_delay: int
        +bullet_count: int
        +damage_flash: int
        +original_image
        +flash_images
        +__init__(all_sprites, boss_bullets_group, level)
        +update()
        +shoot()
        +draw_health_bar(surface)
        +_create_flash_images()
    }
    pygame.sprite.Sprite <|-- Boss

    class Bullet {
        +speed: int
        +angle: float
        +speedx: float
        +speedy: float
        +__init__(x, y, speed, angle)
        +update()
    }
    pygame.sprite.Sprite <|-- Bullet

    class BossBullet {
        +speedy: int
        +__init__(x, y)
        +update()
    }
    pygame.sprite.Sprite <|-- BossBullet

    class EnemyBullet {
        +enemy_level: int
        +speedy: float
        +speedx: float
        +curve: bool
        +__init__(x, y, enemy_level)
        +update()
        +_create_enemy_bullet()
    }
    pygame.sprite.Sprite <|-- EnemyBullet

    class Item {
        <<Abstract>>
        +type: string
        +speedy: float
        +direction: int
        +angle: float
        +update()
    }
    pygame.sprite.Sprite <|-- Item

    class HealthItem {
        +__init__()
    }
    Item <|-- HealthItem

    class BulletSpeedItem {
        +speed_increase: int
        +__init__()
    }
    Item <|-- BulletSpeedItem

    class BulletPathItem {
        +__init__()
    }
    Item <|-- BulletPathItem

    class Explosion {
        +size: int
        +anim_speed: int
        +frame: int
        +last_update
        +__init__(center, size)
        +update()
    }
    pygame.sprite.Sprite <|-- Explosion

    class Score {
        +value: int
        +font
        +__init__()
        +update(points)
        +draw(surface)
    }

    class Star { 
        +x: int
        +y: int
        +speed: int
        +color: tuple
        +size: int
        +draw(surface)
        +update()
    }

    class SoundManager {
        -sounds: dict
        -music_volume: float
        -sound_volume: float
        -sound_enabled: bool
        -music_enabled: bool
        +__init__()
        +play_sound(key)
        +play_background_music(filename)
        +stop_music()
        +set_sound_volume(volume)
        +set_music_volume(volume)
        +toggle_sound()
        +toggle_music()
        +_load_sounds()
    }

    Game "1" *-- "1" Player
    Game "1" *-- "1" Score
    Game "1" *-- "1" SoundManager
    Game "1" *-- "0..1" Boss
    Game "1" o-- "*" Enemy : "contains" >
    Game "1" o-- "*" Bullet : "contains" >
    Game "1" o-- "*" BossBullet : "contains" >
    Game "1" o-- "*" EnemyBullet : "contains" >
    Game "1" o-- "*" Item : "contains" >
    Game "1" o-- "*" Star : "contains" >
    Game "1" ..> "thunder_fighter.utils.collisions" : "uses"
    Game "1" ..> "thunder_fighter.graphics.renderers" : "uses"
    Game "1" ..> "thunder_fighter.utils.stars" : "uses"

    Player ..> Bullet : "creates" >
    Enemy ..> EnemyBullet : "creates" >
    Boss ..> BossBullet : "creates" >

    Player ..> "thunder_fighter.graphics.renderers" : "uses"
    Enemy ..> "thunder_fighter.graphics.renderers" : "uses"
    Boss ..> "thunder_fighter.graphics.renderers" : "uses"
    Bullet ..> "thunder_fighter.graphics.renderers" : "uses"
    BossBullet ..> "thunder_fighter.graphics.renderers" : "uses"
    EnemyBullet ..> "thunder_fighter.graphics.renderers" : "uses"
    Item ..> "thunder_fighter.graphics.renderers" : "uses"
    HealthItem ..> "thunder_fighter.graphics.renderers" : "uses"
    BulletSpeedItem ..> "thunder_fighter.graphics.renderers" : "uses"
    BulletPathItem ..> "thunder_fighter.graphics.renderers" : "uses"

    "thunder_fighter.utils.collisions" ..> Player : "uses"
    "thunder_fighter.utils.collisions" ..> Enemy : "uses"
    "thunder_fighter.utils.collisions" ..> Boss : "uses"
    "thunder_fighter.utils.collisions" ..> Bullet : "uses"
    "thunder_fighter.utils.collisions" ..> BossBullet : "uses"
    "thunder_fighter.utils.collisions" ..> EnemyBullet : "uses"
    "thunder_fighter.utils.collisions" ..> Item : "uses"
    "thunder_fighter.utils.collisions" ..> Explosion : "creates" >

    "thunder_fighter.graphics.effects" ..> Explosion : "creates" >