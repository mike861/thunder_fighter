#!/usr/bin/env python3
"""
Script to convert Chinese comments and docstrings to English in Python files.
"""

import os
import re
import sys

# Dictionary of Chinese to English translations for common terms
TRANSLATIONS = {
    # Module descriptions
    "游戏系统模块": "Game Systems Module",
    "图形效果模块": "Graphics Effects Module",
    "实体模块": "Entity Module",
    "输入系统模块": "Input System Module",
    "用户界面模块": "User Interface Module",
    "粒子系统模块": "Particle System Module",
    "碰撞系统模块": "Collision System Module",
    "评分系统模块": "Scoring System Module",
    "物理系统模块": "Physics System Module",
    "生成系统模块": "Spawning System Module",
    
    # Common descriptions - more comprehensive
    "包含所有游戏核心系统的实现。": "Contains all core game system implementations.",
    "包含所有视觉效果相关的实现。": "Contains all visual effects related implementations.",
    "包含所有实体相关的实现。": "Contains all entity related implementations.",
    "包含所有输入处理相关的实现。": "Contains all input processing related implementations.",
    "包含所有用户界面相关的实现。": "Contains all user interface related implementations.",
    "包含游戏中所有实体的基类和工厂。": "Contains base classes and factories for all game entities.",
    "包含输入系统的核心组件。": "Contains core components of the input system.",
    "包含输入事件的定义。": "Contains input event definitions.",
    "包含输入适配器的实现。": "Contains input adapter implementations.",
    "包含所有碰撞检测相关的实现。": "Contains all collision detection related implementations.",
    "包含所有得分系统相关的实现。": "Contains all scoring system related implementations.",
    "包含所有物理系统相关的实现。": "Contains all physics system related implementations.",
    "包含所有生成系统相关的实现。": "Contains all spawning system related implementations.",
    
    # More granular phrases
    "包含": "Contains",
    "所有": "all", 
    "相关": "related",
    "实现": "implementations",
    "模块": "module",
    "系统": "system",
    "的": "",
    "。": ".",
    "，": ",",
    "（": "(",
    "）": ")",
    "【": "[",
    "】": "]",
    "：": ":",
    "；": ";",
    
    # Comment phrases  
    "基础类": "Base classes",
    "工厂类": "Factory classes",
    "导入": "Import",
    "兼容性": "Compatibility",
    "保持": "maintain",
    "向后兼容": "backward compatibility",
    "重构后": "After refactoring",
    "按类型组织": "organized by type",
    "定义": "definitions",
    "对象": "objects",
    "根据": "according to",
    "调整": "adjust",
    "难度": "difficulty",
    "生成": "spawn",
    "检查": "check",
    "是否": "whether",
    "到了": "time for",
    "时间": "time",
    "update": "update",
    "尝试": "try",
    "创建": "create",
    "记录": "record",
    "上次": "last",
    "失败": "failed",
    "错误": "error",
    "如果": "if",
    "否则": "else",
    "返回": "return",
    "获取": "get",
    "设置": "set",
    "初始化": "initialize",
    "参数": "parameters",
    "配置": "configuration",
    "延迟": "delayed",
    "避免": "avoid",
    "循环": "circular",
    "重置": "reset",
    
    # Specific terms
    "敌人": "enemy",
    "玩家": "player", 
    "游戏": "game",
    "系统": "system",
    "管理": "management",
    "管理器": "manager",
    "工厂": "factory",
    "实体": "entity",
    "子弹": "bullet",
    "导弹": "missile",
    "道具": "item",
    "爆炸": "explosion",
    "粒子": "particle",
    "效果": "effect",
    "输入": "input",
    "输出": "output",
    "事件": "event",
    "状态": "state",
    "界面": "interface",
    "用户": "user",
    "图形": "graphics",
    "渲染": "rendering",
    "显示": "display",
    "音频": "audio",
    "声音": "sound",
    "音乐": "music",
    "配置": "configuration",
    "设置": "settings",
    "资源": "resource",
    "加载": "loading",
    "保存": "saving",
    "文件": "file",
    "数据": "data",
    "碰撞": "collision",
    "检测": "detection",
    "物理": "physics",
    "移动": "movement",
    "位置": "position",
    "速度": "velocity",
    "加速度": "acceleration",
    "生命": "life",
    "血量": "health",
    "得分": "score",
    "等级": "level",
    "难度": "difficulty",
    "暂停": "pause",
    "重启": "restart",
    "结束": "end",
    "胜利": "victory",
    "失败": "failure",
    "开始": "start",
    "停止": "stop",
    "继续": "continue",
    "退出": "exit",
    "进入": "enter",
    "离开": "leave",
    "更新": "update",
    "初始化": "initialize",
    "创建": "create",
    "删除": "delete",
    "销毁": "destroy",
    "修改": "modify",
    "变更": "change",
    "处理": "process",
    "执行": "execute",
    "运行": "run",
    "计算": "calculate",
    "绘制": "draw",
    "渲染": "render"
}

def convert_chinese_in_file(file_path):
    """Convert Chinese text in a Python file to English."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Convert specific translations
        for chinese, english in TRANSLATIONS.items():
            content = content.replace(chinese, english)
        
        # If content changed, write it back
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Converted: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_python_files(directory):
    """Find all Python files in a directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    """Main function to convert Chinese text in Python files."""
    if len(sys.argv) != 2:
        print("Usage: python convert_chinese_to_english.py <directory_or_file>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if os.path.isfile(target) and target.endswith('.py'):
        # Single file processing
        python_files = [target]
        print(f"Processing single file: {target}")
    elif os.path.isdir(target):
        # Directory processing
        python_files = find_python_files(target)
        print(f"Found {len(python_files)} Python files to process...")
    else:
        print(f"Error: {target} is not a valid Python file or directory")
        sys.exit(1)
    
    converted_count = 0
    
    for file_path in python_files:
        if convert_chinese_in_file(file_path):
            converted_count += 1
    
    print(f"\nConversion complete! Converted {converted_count} files.")

if __name__ == "__main__":
    main()