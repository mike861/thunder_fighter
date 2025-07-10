#!/usr/bin/env python3
"""
Advanced Chinese to English comment translator for Python files.

This script provides intelligent translation of Chinese comments and docstrings
in Python files, focusing on complete sentence translation and proper context.
"""

import os
import re
import ast
import tokenize
from typing import List, Dict, Tuple, Optional
from io import StringIO

class AdvancedCommentTranslator:
    """Advanced translator for Chinese comments in Python code"""
    
    def __init__(self):
        # Complete sentence translations for common documentation patterns
        self.sentence_translations = {
            # Module descriptions
            "基础entity类definitions": "Base entity class definitions",
            "definitions了allgameobjects基类和通用接口": "Definitions for all game objects base classes and common interfaces",
            "definitionsallgameobjects基类和通用接口": "Definitions for all game objects base classes and common interfaces",
            "游戏系统模块": "Game Systems Module",
            "包含所有游戏核心系统的实现": "Contains all core game system implementations",
            "图形效果模块": "Graphics Effects Module", 
            "包含所有视觉效果相关的实现": "Contains all visual effects related implementations",
            "Entity生成System": "Entity Spawning System",
            "统一managementenemy、item、Boss等生成逻辑": "Unified management of enemy, item, Boss spawning logic",
            
            # Class descriptions
            "gameobjects基类": "Base class for game objects",
            "game objects基类": "Base class for game objects",
            "具体entity类,提供默认implementations": "Concrete entity class providing default implementations",
            "具体entity类,提供默认implementation": "Concrete entity class providing default implementation",
            "entityfactory基类": "Base class for entity factories",
            "可movemententity基类": "Base class for movable entities",
            "有lifeentity基类": "Base class for living entities",
            "living entity基类": "Base class for living entities",
            
            # Method descriptions
            "updategameobjectsstate": "Update game object state",
            "rendergameobjects": "Render game objects",
            "默认updateimplementations": "Default update implementation",
            "默认updateimplementation": "Default update implementation",
            "默认renderimplementations": "Default render implementation", 
            "默认renderimplementation": "Default render implementation",
            "createentity实例": "Create entity instance",
            "批量createentity": "Create entities in batch",
            "settingsposition": "Set position",
            "getposition": "Get position",
            "settingsvelocity": "Set velocity",
            "getvelocity": "Get velocity",
            "settingsmovement方向(归一化向量)": "Set movement direction (normalized vector)",
            "setmovement direction(归一化向量)": "Set movement direction (normalized vector)",
            "朝向目标movement": "Move towards target",
            "move towards target": "Move towards target",
            "承受伤害,returnwhether被摧毁": "Take damage, return whether destroyed",
            "take damage,returnwhether被摧毁": "Take damage, return whether destroyed",
            "承受伤害,returnwhether死亡": "Take damage, return whether dead",
            "take damage,returnwhetherdeath": "Take damage, return whether dead",
            "恢复life值": "Restore health",
            "恢复health": "Restore health",
            "受伤时回调": "Callback when damaged",
            "治疗时回调": "Callback when healed",
            "healing时回调": "Callback when healed",
            "死亡时回调": "Callback when dead",
            "death时回调": "Callback when dead",
            "getlife值百分比": "Get health percentage",
            "gethealthpercentage": "Get health percentage",
            
            # Input system translations
            "Pygame 适配器 - 隔离 pygame 依赖": "Pygame Adapter - Isolate pygame dependencies",
            "这个moduleimplementations了 pygame related适配器": "This module implements pygame related adapters",
            "将 pygame event和state转换为标准接口": "Convert pygame events and state to standard interfaces",
            "隔离外部依赖": "Isolate external dependencies",
            "Pygame event源适配器": "Pygame event source adapter",
            "initialize Pygame event源": "Initialize Pygame event source",
            "日志接口(可选)": "Logger interface (optional)",
            "getall待processevent": "Get all events to be processed",
            "转换后 Event objects列表": "List of converted Event objects",
            "get pygame event": "Get pygame events",
            "清空event队列": "Clear event queue",
            "转换 pygame event为标准event": "Convert pygame event to standard event",
            "pygame eventobjects": "Pygame event objects",
            "转换后 Event objects,或 None": "Converted Event objects, or None",
            "get修饰键state": "Get modifier key state",
            "修饰键state字典": "Modifier key state dictionary",
            "Pygame 键盘state适配器": "Pygame keyboard state adapter",
            "initialize Pygame 键盘state": "Initialize Pygame keyboard state",
            "check指定键whether按下": "Check whether specified key is pressed",
            "True if键被按下,else False": "True if key is pressed, else False",
            "getall按下键": "Get all pressed keys",
            "当前按下all键码列表": "List of all currently pressed key codes",
            "Pygame 时钟适配器": "Pygame clock adapter",
            "initialize Pygame 时钟": "Initialize Pygame clock",
            "get当前time": "Get current time",
            "当前time戳(秒)": "Current timestamp (seconds)",
            "get帧time间隔": "Get frame time interval",
            "上一帧到这一帧time间隔(秒)": "Time interval from last frame to current frame (seconds)",
            "get pygame time或systemtime作为后备": "Get pygame time or system time as fallback",
            "控制帧率(if使用 pygame 时钟)": "Control frame rate (if using pygame clock)",
            "目标帧率": "Target frame rate",
            "实际经过毫秒数": "Actual elapsed milliseconds",
            "简单time控制": "Simple time control",
            "默认 60 FPS": "Default 60 FPS",
            "简单 Pygame 兼容日志implementations": "Simple Pygame compatible logging implementation",
            "initialize日志器": "Initialize logger",
            "whether启用调试output": "Whether to enable debug output",
            "record调试信息": "Record debug information",
            "record一般信息": "Record general information",
            "record警告信息": "Record warning information",
            "recorderror信息": "Record error information",
            "create完整 Pygame 适配器集合": "Create complete Pygame adapter set",
            "whether启用调试日志": "Whether to enable debug logging",
            
            # Test adapter translations
            "测试适配器 - 提供完全可控测试环境": "Test Adapter - Provide fully controllable test environment",
            "这个moduleimplementations了测试用适配器": "This module implements test adapters",
            "提供完全可控input环境": "Provide fully controllable input environment",
            "支持精确time控制和state模拟": "Support precise time control and state simulation",
            "用于单元测试": "For unit testing",
            "注意:本module中类不是pytest测试类": "Note: Classes in this module are not pytest test classes",
            "而是用于单元测试Mockobjects": "But are Mock objects for unit testing",
            "告诉 pytest 这个module不Contains测试类": "Tell pytest this module does not contain test classes",
            "测试event源 - 完全可控event队列": "Test event source - fully controllable event queue",
            "initialize测试event源": "Initialize test event source",
            "添加测试event": "Add test event",
            "要添加event": "Event to add",
            "添加按键按下event便捷方法": "Convenient method to add key down event",
            "修饰键state": "Modifier key state",
            "添加按键释放event便捷方法": "Convenient method to add key up event",
            "添加按键序列(按下然后释放)": "Add key sequence (press then release)",
            "按键持续time": "Key hold time",
            "event列表(会清空内部队列)": "Event list (will clear internal queue)",
            "settingswhether自动添加time戳": "Set whether to auto-add timestamps",
            "推进time(用于time戳spawn)": "Advance time (for timestamp generation)",
            "settings当前time": "Set current time",
            "get待processevent数量": "Get number of events to process",
            "测试键盘state - 完全可控键盘state模拟": "Test keyboard state - fully controllable keyboard state simulation",
            "initialize测试键盘state": "Initialize test keyboard state",
            "模拟按键按下": "Simulate key press",
            "模拟按键释放": "Simulate key release",
            "同时按下多个键": "Press multiple keys simultaneously",
            "键码列表": "Key code list",
            "同时释放多个键": "Release multiple keys simultaneously",
            "清除all按键state": "Clear all key states",
            "模拟按键序列": "Simulate key sequence",
            "键码序列": "Key code sequence",
            "每个键maintaintime": "Time to maintain each key",
            "在实际测试中,这里会配合 TestClock 使用": "In actual testing, this will be used with TestClock",
            "getstatechange历史": "Get state change history",
            "测试时钟 - 完全可控time流逝": "Test clock - fully controllable time flow",
            "initialize测试时钟": "Initialize test clock",
            "初始time": "Initial time",
            "推进time": "Advance time",
            "要推进秒数": "Seconds to advance",
            "按帧推进time": "Advance time by frames",
            "要推进帧数": "Frames to advance",
            "直接settingstime": "Directly set time",
            "新time": "New time",
            "reset时钟": "Reset clock",
            "gettimechange历史": "Get time change history",
            "测试日志器 - 收集日志消息用于验证": "Test logger - collect log messages for verification",
            "initialize测试日志器": "Initialize test logger",
            "whether打印日志到控制台": "Whether to print logs to console",
            "内部日志record方法": "Internal log recording method",
            "get日志消息": "Get log messages",
            "过滤日志级别(可选)": "Filter log level (optional)",
            "日志消息列表": "List of log messages",
            "清空日志": "Clear logs",
            "checkwhether有指定级别日志": "Check whether there are logs of specified level",
            "统计指定级别日志数量": "Count logs of specified level",
            "create完整测试环境": "Create complete test environment",
            "whether打印日志": "Whether to print logs",
            "同步time": "Synchronize time",
            "测试场景构建器 - 简化复杂测试场景create": "Test scenario builder - simplify complex test scenario creation",
            "initialize测试场景": "Initialize test scenario",
            "测试event源": "Test event source",
            "测试时钟": "Test clock",
            "测试键盘state": "Test keyboard state",
            "settings当前操作time": "Set current operation time",
            "在当前time按下键": "Press key at current time",
            "在当前time释放键": "Release key at current time",
            "等待指定time": "Wait for specified time",
            "execute按键序列(按下-等待-释放)": "Execute key sequence (press-wait-release)",
            "为了backward compatibility,保留旧名称": "For backward compatibility, keep old names",
            "公开API使用Mock前缀": "Public API uses Mock prefix",
            
            # Command system translations
            "命令模式implementations - 解耦input和game逻辑": "Command pattern implementation - decouple input and game logic",
            "这个moduledefinitions了game命令system": "This module defines the game command system",
            "将inputevent转换为game命令": "Convert input events to game commands",
            "implementationsinputsystem和game逻辑完全解耦": "Implement complete decoupling of input system and game logic",
            "game命令类型枚举": "Game command type enumeration",
            "movement命令": "Movement commands",
            "动作命令": "Action commands",
            "system命令": "System commands",
            "调试命令": "Debug commands",
            "game命令": "Game command",
            "表示一个具体game命令": "Represents a specific game command",
            "Contains命令类型、time戳和relateddata": "Contains command type, timestamp and related data",
            "这是inputsystem和game逻辑之间接口": "This is the interface between input system and game logic",
            "initialize后process,确保data字典总是存在": "Post-initialization processing, ensure data dictionary always exists",
            "安全get命令data": "Safely get command data",
            "settings命令data": "Set command data",
            "checkwhether为movement命令": "Check whether it is a movement command",
            "checkwhether为动作命令": "Check whether it is an action command",
            "checkwhether为system命令": "Check whether it is a system command",
            
            # Processor translations
            "核心inputprocess逻辑,完全可测试": "Core input processing logic, fully testable",
            "这个moduleimplementations了inputsystem核心逻辑": "This module implements the core logic of input system",
            "不依赖任何外部库": "Does not depend on any external libraries",
            "通过依赖注入方式使用抽象接口": "Use abstract interfaces through dependency injection",
            "implementations完全可测试性": "Implement complete testability",
            "纯净inputprocess器": "Pure input processor",
            "核心inputprocess逻辑": "Core input processing logic",
            "负责将inputevent转换为game命令": "Responsible for converting input events to game commands",
            "通过依赖注入使用外部接口": "Use external interfaces through dependency injection",
            "完全可测试": "Fully testable",
            "initializeinputprocess器": "Initialize input processor",
            "event源接口": "Event source interface",
            "键盘state接口": "Keyboard state interface",
            "时钟接口": "Clock interface",
            "键码到命令类型映射": "Key code to command type mapping",
            "日志接口(可选)": "Logger interface (optional)",
            "state跟踪": "State tracking",
            "configurationparameters": "Configuration parameters",
            "首次重复前delayed": "Delay before first repeat",
            "重复间隔": "Repeat interval",
            "命令冷却time": "Command cooldown time",
            "持续命令集合(如movement)": "Continuous command set (like movement)",
            "统计信息": "Statistics",
            "processinput并return命令列表": "Process input and return command list",
            "spawn命令列表": "Generated command list",
            "processevent队列中event": "Process events in event queue",
            "process持续按键": "Process held keys",
            "update统计": "Update statistics",
            "在发生error时return空列表,avoid崩溃": "Return empty list on error to avoid crash",
            "process单个event": "Process single event",
            "inputevent": "Input event",
            "spawn命令(if有)": "Generated command (if any)",
            "process按键按下event": "Process key down event",
            "按键event": "Key event",
            "添加到持续按键集合": "Add to held key set",
            "check键位映射": "Check key mapping",
            "check命令冷却": "Check command cooldown",
            "initialize为-1avoid冷却问题": "Initialize to -1 to avoid cooldown issues",
            "update命令time": "Update command time",
            "create命令": "Create command",
            "process按键释放event": "Process key up event",
            "从持续按键集合中移除": "Remove from held key set",
            "对于某些命令,可能需要在释放时spawnstop命令": "For some commands, may need to generate stop command on release",
            "目前不需要,但保留接口": "Currently not needed, but keep interface",
            "process持续按键(用于movement等连续动作)": "Process held keys (for continuous actions like movement)",
            "当前time": "Current time",
            "checkwhethertime for重复time": "Check whether it's time for repeat",
            "resetprocess器state": "Reset processor state",
            "update键位映射": "Update key mapping",
            "settings按键重复configuration": "Set key repeat configuration",
            "首次重复delayed(秒)": "Delay before first repeat (seconds)",
            "settings命令冷却time": "Set command cooldown time",
            "冷却time(秒)": "Cooldown time (seconds)",
            "getprocess器统计信息": "Get processor statistics",
            "check指定键whether正在被按住": "Check whether specified key is being held",
            "getall正在被按住键": "Get all keys being held",
            
            # Common mixed patterns
            "基础图像(子类需要settings具体图像)": "Base image (subclasses need to set specific image)",
            "基础图像(子类需要set具体图像)": "Base image (subclasses need to set specific image)",
            "updateposition": "Update position",
            "update精灵内置update(if有动画等)": "Update sprite built-in update (if has animation etc)",
            "according to方向和velocitycalculatevelocity": "Calculate velocity according to direction and velocity",
            "create基础rect": "Create base rect",
        }
        
        # Pattern-based translations for remaining mixed text
        self.pattern_replacements = [
            # Fix remaining mixed patterns
            (r'(\w+)系统', r'\1 system'),
            (r'(\w+)模块', r'\1 module'),
            (r'(\w+)接口', r'\1 interface'),
            (r'(\w+)实现', r'\1 implementation'),
            (r'(\w+)工厂', r'\1 factory'),
            (r'(\w+)适配器', r'\1 adapter'),
            (r'(\w+)管理', r'\1 management'),
            (r'(\w+)处理', r'\1 processing'),
            (r'(\w+)控制', r'\1 control'),
            (r'(\w+)状态', r'\1 state'),
            (r'(\w+)事件', r'\1 event'),
            (r'(\w+)命令', r'\1 command'),
            
            # Fix specific artifacts
            ('gameobjects', 'game objects'),
            ('eventobjects', 'event objects'),
            ('Mockobjects', 'Mock objects'),
            ('implementations', 'implementation'),
            ('Contains', 'contains'),
            ('whether', 'whether'),
            ('returnwhether', 'return whether'),
            ('if', 'if'),
            ('else', 'else'),
            ('get', 'get'),
            ('set', 'set'),
            ('create', 'create'),
            ('update', 'update'),
            ('process', 'process'),
            ('check', 'check'),
            ('settings', 'set'),
            ('initialize', 'initialize'),
            ('definitions', 'definitions'),
            ('record', 'record'),
            ('spawn', 'generate'),
            ('maintain', 'maintain'),
            ('execute', 'execute'),
            ('avoid', 'avoid'),
            ('time', 'time'),
            ('state', 'state'),
            ('event', 'event'),
            ('command', 'command'),
            ('data', 'data'),
            ('list', 'list'),
            ('object', 'object'),
            ('class', 'class'),
            ('method', 'method'),
            ('function', 'function'),
            ('parameter', 'parameter'),
            ('return', 'return'),
            ('value', 'value'),
            ('type', 'type'),
            ('interface', 'interface'),
            ('implementation', 'implementation'),
        ]

    def translate_text(self, text: str) -> str:
        """Translate Chinese text to English using advanced pattern matching"""
        
        # Skip if no Chinese characters
        if not self._contains_chinese(text):
            return text
        
        # First try exact sentence match
        if text.strip() in self.sentence_translations:
            return self.sentence_translations[text.strip()]
        
        # Try partial sentence matches
        translated = text
        for chinese_pattern, english_pattern in self.sentence_translations.items():
            if chinese_pattern in translated:
                translated = translated.replace(chinese_pattern, english_pattern)
        
        # Apply pattern-based replacements
        for pattern, replacement in self.pattern_replacements:
            translated = re.sub(pattern, replacement, translated)
        
        # Clean up whitespace and formatting
        translated = re.sub(r'\s+', ' ', translated).strip()
        
        return translated

    def _contains_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def translate_file(self, file_path: str) -> bool:
        """Translate all Chinese comments and docstrings in a Python file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
        
        lines = content.split('\n')
        modified = False
        
        # Process line by line to handle comments and docstrings
        for i, line in enumerate(lines):
            original_line = line
            
            # Handle single-line comments
            if '#' in line:
                parts = line.split('#', 1)
                if len(parts) == 2:
                    code_part = parts[0]
                    comment_part = parts[1].strip()
                    
                    if self._contains_chinese(comment_part):
                        translated_comment = self.translate_text(comment_part)
                        lines[i] = f"{code_part}# {translated_comment}"
                        modified = True
                        print(f"  Line {i+1}: Comment")
                        print(f"    Original: {comment_part}")
                        print(f"    Translated: {translated_comment}")
            
            # Handle docstring lines (triple quotes)
            elif '"""' in line or "'''" in line:
                # Find the content between quotes
                quote_char = '"""' if '"""' in line else "'''"
                
                # Single line docstring
                if line.count(quote_char) >= 2:
                    start_idx = line.find(quote_char)
                    end_idx = line.rfind(quote_char)
                    if start_idx != end_idx:
                        docstring_content = line[start_idx + 3:end_idx]
                        if self._contains_chinese(docstring_content):
                            translated_content = self.translate_text(docstring_content)
                            lines[i] = line[:start_idx + 3] + translated_content + line[end_idx:]
                            modified = True
                            print(f"  Line {i+1}: Docstring")
                            print(f"    Original: {docstring_content}")
                            print(f"    Translated: {translated_content}")
                
                # Multi-line docstring start
                elif line.count(quote_char) == 1:
                    # Find the end of the docstring
                    docstring_lines = []
                    docstring_start = i
                    
                    # Extract the first line content after opening quotes
                    first_line_content = line[line.find(quote_char) + 3:].strip()
                    if first_line_content:
                        docstring_lines.append(first_line_content)
                    
                    # Look for the closing quotes
                    for j in range(i + 1, len(lines)):
                        if quote_char in lines[j]:
                            # Extract content before closing quotes
                            last_line_content = lines[j][:lines[j].find(quote_char)].strip()
                            if last_line_content:
                                docstring_lines.append(last_line_content)
                            break
                        else:
                            # Full line is part of docstring
                            docstring_lines.append(lines[j].strip())
                    
                    # Translate the docstring content
                    full_docstring = '\n'.join(docstring_lines)
                    if self._contains_chinese(full_docstring):
                        translated_docstring = self.translate_text(full_docstring)
                        
                        # Replace the docstring lines
                        indent = len(line) - len(line.lstrip())
                        indent_str = ' ' * indent
                        
                        translated_lines = translated_docstring.split('\n')
                        new_lines = [f"{indent_str}{quote_char}"]
                        
                        for trans_line in translated_lines:
                            if trans_line.strip():
                                new_lines.append(f"{indent_str}{trans_line}")
                        
                        new_lines.append(f"{indent_str}{quote_char}")
                        
                        # Replace the original lines
                        end_line = j if 'j' in locals() else i
                        lines[docstring_start:end_line + 1] = new_lines
                        modified = True
                        
                        print(f"  Lines {docstring_start+1}-{end_line+1}: Multi-line docstring")
                        print(f"    Original: {full_docstring[:50]}...")
                        print(f"    Translated: {translated_docstring[:50]}...")
        
        # Write back to file if modified
        if modified:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                print(f"✓ Updated {file_path}")
                return True
            except Exception as e:
                print(f"Error writing {file_path}: {e}")
                return False
        
        return False

    def translate_directory(self, directory: str) -> int:
        """Translate all Python files in a directory"""
        modified_count = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    print(f"Processing {file_path}...")
                    
                    if self.translate_file(file_path):
                        modified_count += 1
        
        return modified_count


def main():
    """Main function to run the advanced translator"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python translate_comments_v2.py <file_or_directory>")
        print("Example: python translate_comments_v2.py thunder_fighter/")
        print("Example: python translate_comments_v2.py thunder_fighter/systems/spawning.py")
        sys.exit(1)
    
    target = sys.argv[1]
    translator = AdvancedCommentTranslator()
    
    if os.path.isfile(target) and target.endswith('.py'):
        print(f"Translating comments in file: {target}")
        if translator.translate_file(target):
            print("✓ File updated successfully")
        else:
            print("No Chinese comments found or no changes needed")
    
    elif os.path.isdir(target):
        print(f"Translating comments in directory: {target}")
        modified_count = translator.translate_directory(target)
        print(f"✓ Updated {modified_count} files")
    
    else:
        print(f"Error: {target} is not a valid Python file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()