"""
新输入系统演示

展示如何使用新的输入系统替代旧的输入处理方式。
这个演示展示了新系统的主要特性和用法。
"""

import pygame
import sys
from thunder_fighter.input import (
    InputSystem,
    create_for_production,
    CommandType,
    InputSystemBuilder
)

def demo_basic_usage():
    """演示基本用法"""
    print("=== 基本用法演示 ===")
    
    # 创建生产环境的输入系统
    input_system = create_for_production(enable_debug=True)
    
    # 注册命令处理器
    def on_move_up(cmd):
        print(f"向上移动! 时间: {cmd.timestamp:.3f}")
    
    def on_shoot(cmd):
        print(f"射击! 按键: {cmd.get_data('key')}")
    
    def on_pause(cmd):
        print("游戏暂停!")
        return True  # 表示要退出演示
    
    input_system.on_command(CommandType.MOVE_UP, on_move_up)
    input_system.on_command(CommandType.SHOOT, on_shoot)
    input_system.on_command(CommandType.PAUSE, on_pause)
    
    print("按键说明:")
    print("- W/UP: 向上移动")
    print("- SPACE: 射击")
    print("- P: 暂停/退出演示")
    print("- ESC: 退出")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        clock.tick(60)
        
        # 处理输入
        commands = input_system.update()
        
        # 检查是否需要退出
        for cmd in commands:
            if cmd.type == CommandType.PAUSE or cmd.type == CommandType.QUIT:
                running = False
                break
        
        # 处理pygame事件（用于窗口关闭）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    print("基本用法演示结束\n")

def demo_builder_pattern():
    """演示构建器模式"""
    print("=== 构建器模式演示 ===")
    
    # 使用构建器创建自定义输入系统
    input_system = (InputSystemBuilder()
                   .with_pygame(enable_debug=True)
                   .with_repeat_config(delay=0.3, rate=0.1)  # 自定义重复配置
                   .with_cooldown(0.1)  # 减少冷却时间
                   .build())
    
    # 自定义键位映射
    custom_mapping = {
        pygame.K_j: CommandType.MOVE_LEFT,
        pygame.K_l: CommandType.MOVE_RIGHT,
        pygame.K_i: CommandType.MOVE_UP,
        pygame.K_k: CommandType.MOVE_DOWN,
        pygame.K_SPACE: CommandType.SHOOT,
        pygame.K_ESCAPE: CommandType.QUIT
    }
    
    input_system.set_key_mapping(custom_mapping)
    
    # 注册处理器
    def on_any_command(cmd):
        direction_map = {
            CommandType.MOVE_LEFT: "←",
            CommandType.MOVE_RIGHT: "→", 
            CommandType.MOVE_UP: "↑",
            CommandType.MOVE_DOWN: "↓",
            CommandType.SHOOT: "💥"
        }
        
        if cmd.type in direction_map:
            symbol = direction_map[cmd.type]
            continuous = " (持续)" if cmd.get_data('continuous') else ""
            print(f"{symbol}{continuous}")
    
    # 为所有移动和射击命令注册同一个处理器
    for cmd_type in [CommandType.MOVE_LEFT, CommandType.MOVE_RIGHT, 
                     CommandType.MOVE_UP, CommandType.MOVE_DOWN, CommandType.SHOOT]:
        input_system.on_command(cmd_type, on_any_command)
    
    print("自定义键位:")
    print("- J/L: 左右移动")
    print("- I/K: 上下移动") 
    print("- SPACE: 射击")
    print("- ESC: 退出")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        clock.tick(60)
        
        # 处理输入
        commands = input_system.update()
        
        # 检查退出命令
        for cmd in commands:
            if cmd.type == CommandType.QUIT:
                running = False
                break
        
        # 处理pygame事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    print("构建器模式演示结束\n")

def demo_statistics():
    """演示统计功能"""
    print("=== 统计功能演示 ===")
    
    input_system = create_for_production()
    
    # 注册处理器来统计命令
    command_stats = {}
    
    def count_commands(cmd):
        cmd_type = cmd.type
        command_stats[cmd_type] = command_stats.get(cmd_type, 0) + 1
    
    # 为所有命令类型注册统计器
    for cmd_type in CommandType:
        input_system.on_command(cmd_type, count_commands)
    
    print("随意按键，按ESC查看统计信息")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        clock.tick(60)
        
        # 处理输入
        commands = input_system.update()
        
        # 检查退出命令
        for cmd in commands:
            if cmd.type == CommandType.QUIT:
                running = False
                break
        
        # 处理pygame事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    # 显示统计
    print("\n统计结果:")
    print("-" * 30)
    
    # 系统统计
    system_stats = input_system.get_stats()
    print(f"总命令数: {system_stats['total_commands']}")
    print(f"总事件数: {system_stats['events_processed']}")
    print(f"系统启用: {system_stats['enabled']}")
    
    # 命令类型统计
    print("\n各命令统计:")
    for cmd_type, count in sorted(command_stats.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {cmd_type.value}: {count}")
    
    print("统计功能演示结束\n")

def main():
    """主函数"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("新输入系统演示")
    
    print("Thunder Fighter 新输入系统演示")
    print("=" * 50)
    
    try:
        demo_basic_usage()
        demo_builder_pattern()
        demo_statistics()
        
        print("所有演示完成!")
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()