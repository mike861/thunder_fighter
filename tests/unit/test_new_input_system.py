"""
新输入系统单元测试

测试重构后的输入系统，验证其核心功能和可测试性改进。
"""

import pytest
import pygame
from unittest.mock import Mock

from thunder_fighter.input import (
    InputSystem,
    create_for_testing,
    Command,
    CommandType,
    Event,
    EventType,
    TestEventSource,
    TestKeyboardState, 
    TestClock,
    TestLogger,
    TestScenario
)


class TestInputSystemCore:
    """测试输入系统核心功能"""
    
    def test_system_creation(self):
        """测试系统创建"""
        system, controllers = create_for_testing()
        
        assert system is not None
        assert 'event_source' in controllers
        assert 'keyboard_state' in controllers
        assert 'clock' in controllers
        assert 'logger' in controllers
    
    def test_simple_key_press_to_command(self):
        """测试简单按键转换为命令"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        
        # 模拟空格键按下
        event_source.add_key_down(pygame.K_SPACE)
        
        # 处理输入
        commands = system.update()
        
        # 验证生成了射击命令
        assert len(commands) == 1
        assert commands[0].type == CommandType.SHOOT
        assert commands[0].get_data('key') == pygame.K_SPACE
    
    def test_movement_commands(self):
        """测试移动命令"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        
        # 测试所有移动键
        movement_keys = [
            (pygame.K_UP, CommandType.MOVE_UP),
            (pygame.K_DOWN, CommandType.MOVE_DOWN),
            (pygame.K_LEFT, CommandType.MOVE_LEFT),
            (pygame.K_RIGHT, CommandType.MOVE_RIGHT),
            (pygame.K_w, CommandType.MOVE_UP),
            (pygame.K_s, CommandType.MOVE_DOWN),
            (pygame.K_a, CommandType.MOVE_LEFT),
            (pygame.K_d, CommandType.MOVE_RIGHT),
        ]
        
        for key, expected_command in movement_keys:
            # 清除之前的事件和状态
            event_source.clear_events()
            system.reset_state()  # 重置状态，清除冷却
            
            # 添加按键事件
            event_source.add_key_down(key)
            
            # 处理输入
            commands = system.update()
            
            # 验证
            assert len(commands) == 1
            assert commands[0].type == expected_command
    
    def test_modifier_keys(self):
        """测试修饰键"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        
        # 添加带修饰键的事件
        event = Event(
            type=EventType.KEY_DOWN,
            key_code=pygame.K_SPACE,
            modifiers={'ctrl': True, 'shift': False, 'alt': False}
        )
        event_source.add_event(event)
        
        # 处理输入
        commands = system.update()
        
        # 验证修饰键被正确传递
        assert len(commands) == 1
        assert commands[0].get_data('modifiers')['ctrl'] is True
        assert commands[0].get_data('modifiers')['shift'] is False
    
    def test_continuous_movement(self):
        """测试持续移动"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        clock = controllers['clock']
        
        # 按下 W 键
        event_source.add_key_down(pygame.K_w)
        
        # 第一次处理 - 初始按键
        commands = system.update()
        assert len(commands) == 1
        assert commands[0].type == CommandType.MOVE_UP
        assert commands[0].get_data('continuous') is False
        
        # 推进时间
        clock.advance(0.1)
        
        # 第二次处理 - 持续按键
        commands = system.update()
        assert len(commands) == 1
        assert commands[0].type == CommandType.MOVE_UP
        assert commands[0].get_data('continuous') is True
    
    def test_command_cooldown(self):
        """测试命令冷却"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        clock = controllers['clock']
        
        # 设置较长的冷却时间
        system.configure_cooldown(0.5)
        
        # 快速连续按键
        event_source.add_key_down(pygame.K_SPACE)
        commands1 = system.update()
        
        # 立即再次按键
        clock.advance(0.1)  # 只推进0.1秒，小于冷却时间
        event_source.add_key_down(pygame.K_SPACE)
        commands2 = system.update()
        
        # 第一次应该成功，第二次应该被冷却阻止
        assert len(commands1) == 1
        assert len(commands2) == 0
        
        # 等待冷却结束
        clock.advance(0.5)
        event_source.add_key_down(pygame.K_SPACE)
        commands3 = system.update()
        
        # 现在应该可以再次触发
        assert len(commands3) == 1


class TestCommandHandlers:
    """测试命令处理器系统"""
    
    def test_command_handler_registration(self):
        """测试命令处理器注册"""
        system, controllers = create_for_testing()
        
        # 注册处理器
        shoot_called = False
        def on_shoot(cmd):
            nonlocal shoot_called
            shoot_called = True
        
        system.on_command(CommandType.SHOOT, on_shoot)
        
        # 触发命令
        event_source = controllers['event_source']
        event_source.add_key_down(pygame.K_SPACE)
        system.update()
        
        # 验证处理器被调用
        assert shoot_called is True
    
    def test_multiple_handlers_same_command(self):
        """测试同一命令的多个处理器"""
        system, controllers = create_for_testing()
        
        # 注册多个处理器
        handler1_called = False
        handler2_called = False
        
        def handler1(cmd):
            nonlocal handler1_called
            handler1_called = True
        
        def handler2(cmd):
            nonlocal handler2_called
            handler2_called = True
        
        system.on_command(CommandType.SHOOT, handler1)
        system.on_command(CommandType.SHOOT, handler2)
        
        # 触发命令
        event_source = controllers['event_source']
        event_source.add_key_down(pygame.K_SPACE)
        system.update()
        
        # 验证所有处理器被调用
        assert handler1_called is True
        assert handler2_called is True
    
    def test_handler_removal(self):
        """测试处理器移除"""
        system, controllers = create_for_testing()
        
        # 注册处理器
        handler_called = False
        def handler(cmd):
            nonlocal handler_called
            handler_called = True
        
        system.on_command(CommandType.SHOOT, handler)
        
        # 移除处理器
        system.remove_command_handler(CommandType.SHOOT, handler)
        
        # 触发命令
        event_source = controllers['event_source']
        event_source.add_key_down(pygame.K_SPACE)
        system.update()
        
        # 验证处理器没有被调用
        assert handler_called is False


class TestInputSystemStates:
    """测试输入系统状态管理"""
    
    def test_key_held_detection(self):
        """测试按键长按检测"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        
        # 检查初始状态
        assert not system.is_key_held(pygame.K_w)
        
        # 按下键
        event_source.add_key_down(pygame.K_w)
        system.update()
        
        # 检查长按状态
        assert system.is_key_held(pygame.K_w)
        
        # 释放键
        event_source.add_key_up(pygame.K_w)
        system.update()
        
        # 检查释放后状态
        assert not system.is_key_held(pygame.K_w)
    
    def test_multiple_held_keys(self):
        """测试多个按键同时长按"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        
        # 按下多个键
        event_source.add_key_down(pygame.K_w)
        event_source.add_key_down(pygame.K_a)
        system.update()
        
        # 检查状态
        held_keys = system.get_held_keys()
        assert pygame.K_w in held_keys
        assert pygame.K_a in held_keys
        assert len(held_keys) == 2
    
    def test_system_enable_disable(self):
        """测试系统启用/禁用"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        
        # 禁用系统
        system.disable()
        
        # 尝试输入
        event_source.add_key_down(pygame.K_SPACE)
        commands = system.update()
        
        # 应该没有命令生成
        assert len(commands) == 0
        
        # 启用系统
        system.enable()
        
        # 再次尝试输入
        event_source.add_key_down(pygame.K_SPACE)
        commands = system.update()
        
        # 现在应该有命令
        assert len(commands) == 1
    
    def test_state_reset(self):
        """测试状态重置"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        
        # 按下一些键
        event_source.add_key_down(pygame.K_w)
        event_source.add_key_down(pygame.K_SPACE)
        system.update()
        
        # 验证有按键被持续按下
        assert len(system.get_held_keys()) > 0
        
        # 重置状态
        system.reset_state()
        
        # 验证状态被清除
        assert len(system.get_held_keys()) == 0


class TestTimeAndStats:
    """测试时间控制和统计"""
    
    def test_precise_timing_control(self):
        """测试精确的时间控制"""
        system, controllers = create_for_testing(initial_time=1000.0)
        event_source = controllers['event_source']
        clock = controllers['clock']
        
        # 在特定时间添加事件
        event_source.add_key_down(pygame.K_SPACE)
        commands = system.update()
        
        # 验证时间戳
        assert len(commands) == 1
        assert commands[0].timestamp == 1000.0
        
        # 推进时间
        clock.advance(5.0)
        event_source.add_key_down(pygame.K_x)
        commands = system.update()
        
        # 验证新时间戳
        assert len(commands) == 1
        assert commands[0].timestamp == 1005.0
    
    def test_system_statistics(self):
        """测试系统统计"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        
        # 获取初始统计
        initial_stats = system.get_stats()
        assert initial_stats['total_commands'] == 0
        
        # 生成一些命令
        event_source.add_key_down(pygame.K_SPACE)
        event_source.add_key_down(pygame.K_x)
        system.update()
        
        # 检查统计更新
        updated_stats = system.get_stats()
        assert updated_stats['total_commands'] == 2
        assert updated_stats['events_processed'] == 2


class TestTestHelpers:
    """测试测试辅助工具"""
    
    def test_test_scenario_builder(self):
        """测试测试场景构建器"""
        # 创建测试环境
        event_source = TestEventSource()
        keyboard = TestKeyboardState()
        clock = TestClock()
        
        # 使用场景构建器
        scenario = TestScenario(event_source, clock, keyboard)
        
        # 构建复杂场景
        scenario.at_time(0.0).press_key(pygame.K_w) \
               .wait(0.5).press_key(pygame.K_SPACE) \
               .wait(0.1).release_key(pygame.K_w) \
               .wait(0.2).release_key(pygame.K_SPACE)
        
        # 验证时间轴
        assert clock.now() == 0.8
        assert not keyboard.is_pressed(pygame.K_SPACE)  # 应该已经释放
        assert not keyboard.is_pressed(pygame.K_w)
    
    def test_logger_verification(self):
        """测试日志验证"""
        logger = TestLogger(print_logs=False)
        
        # 记录不同级别的日志
        logger.debug("Debug message")
        logger.info("Info message") 
        logger.warning("Warning message")
        logger.error("Error message")
        
        # 验证日志记录
        assert logger.count_level('DEBUG') == 1
        assert logger.count_level('INFO') == 1
        assert logger.count_level('WARNING') == 1
        assert logger.count_level('ERROR') == 1
        
        # 验证特定消息
        info_logs = logger.get_logs('INFO')
        assert "Info message" in info_logs


class TestIntegrationScenarios:
    """集成测试场景"""
    
    def test_complex_game_sequence(self):
        """测试复杂的游戏序列"""
        system, controllers = create_for_testing()
        event_source = controllers['event_source']
        clock = controllers['clock']
        
        # 记录所有生成的命令
        all_commands = []
        def command_collector(cmd):
            all_commands.append(cmd)
        
        # 注册收集器
        for cmd_type in CommandType:
            system.on_command(cmd_type, command_collector)
        
        # 模拟游戏序列：移动 + 射击 + 暂停
        # 1. 开始向上移动
        event_source.add_key_down(pygame.K_w)
        system.update()
        
        # 2. 持续移动一段时间
        for _ in range(5):
            clock.advance(0.05)
            system.update()
        
        # 3. 开始射击（同时移动）
        event_source.add_key_down(pygame.K_SPACE)
        system.update()
        
        # 4. 暂停游戏
        clock.advance(0.1)
        event_source.add_key_down(pygame.K_p)
        system.update()
        
        # 分析命令序列
        move_commands = [cmd for cmd in all_commands if cmd.type == CommandType.MOVE_UP]
        shoot_commands = [cmd for cmd in all_commands if cmd.type == CommandType.SHOOT]
        pause_commands = [cmd for cmd in all_commands if cmd.type == CommandType.PAUSE]
        
        # 验证序列
        assert len(move_commands) >= 6  # 初始 + 5次重复
        assert len(shoot_commands) == 1
        assert len(pause_commands) == 1
        
        # 验证时间顺序
        assert move_commands[0].timestamp < shoot_commands[0].timestamp
        assert shoot_commands[0].timestamp < pause_commands[0].timestamp
    
    def test_error_recovery(self):
        """测试错误恢复"""
        system, controllers = create_for_testing()
        logger = controllers['logger']
        
        # 注册一个会抛出异常的处理器
        def failing_handler(cmd):
            raise ValueError("Test error")
        
        system.on_command(CommandType.SHOOT, failing_handler)
        
        # 触发命令（应该不会崩溃）
        event_source = controllers['event_source']
        event_source.add_key_down(pygame.K_SPACE)
        commands = system.update()
        
        # 验证系统仍然正常工作
        assert len(commands) == 1
        
        # 验证错误被记录
        error_logs = logger.get_logs('ERROR')
        assert len(error_logs) > 0
        assert "Test error" in str(error_logs)