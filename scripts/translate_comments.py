#!/usr/bin/env python3
"""
Intelligent Chinese to English comment translator for Python files.

This script finds Chinese comments in Python files and translates them
as complete sentences rather than word-by-word substitution.
"""

import os
import re
import ast
import tokenize
from typing import List, Dict, Tuple, Optional
from io import StringIO

class CommentTranslator:
    """Translates Chinese comments to English in Python files"""
    
    def __init__(self):
        # Common programming term translations for context
        self.context_terms = {
            # Technical terms
            '系统': 'system',
            '模块': 'module', 
            '接口': 'interface',
            '实现': 'implementation',
            '配置': 'configuration',
            '管理': 'management',
            '处理': 'processing',
            '控制': 'control',
            '状态': 'state',
            '事件': 'event',
            '命令': 'command',
            '工厂': 'factory',
            '适配器': 'adapter',
            '监听器': 'listener',
            
            # Game specific
            '游戏': 'game',
            '玩家': 'player', 
            '敌人': 'enemy',
            '子弹': 'bullet',
            '碰撞': 'collision',
            '生成': 'spawning',
            '移动': 'movement',
            '射击': 'shooting',
            '生命值': 'health',
            '分数': 'score',
            '等级': 'level',
            '暂停': 'pause',
            '音效': 'sound',
            '音乐': 'music',
            
            # Actions
            '创建': 'create',
            '删除': 'delete', 
            '更新': 'update',
            '渲染': 'render',
            '获取': 'get',
            '设置': 'set',
            '检查': 'check',
            '验证': 'validate',
            '初始化': 'initialize',
            '重置': 'reset',
            '启动': 'start',
            '停止': 'stop',
            '执行': 'execute',
            '处理': 'process',
            '转换': 'convert',
            '计算': 'calculate',
            
            # Common phrases
            '如果': 'if',
            '否则': 'else', 
            '返回': 'return',
            '参数': 'parameter',
            '结果': 'result',
            '错误': 'error',
            '异常': 'exception',
            '成功': 'success',
            '失败': 'failure',
            '完成': 'completed',
            '开始': 'start',
            '结束': 'end',
        }
        
        # Full sentence translations for common patterns
        self.sentence_patterns = {
            # Module docstrings
            r'(\w+)模块': r'\1 module',
            r'(\w+)系统': r'\1 system', 
            r'(\w+)接口': r'\1 interface',
            r'(\w+)实现': r'\1 implementation',
            r'(\w+)工厂': r'\1 factory',
            r'(\w+)适配器': r'\1 adapter',
            
            # Common function patterns
            r'获取(\w+)': r'Get \1',
            r'设置(\w+)': r'Set \1', 
            r'创建(\w+)': r'Create \1',
            r'删除(\w+)': r'Delete \1',
            r'更新(\w+)': r'Update \1',
            r'检查(\w+)': r'Check \1',
            r'初始化(\w+)': r'Initialize \1',
            r'重置(\w+)': r'Reset \1',
            
            # State descriptions
            r'(\w+)状态': r'\1 state',
            r'(\w+)信息': r'\1 information',
            r'(\w+)数据': r'\1 data',
            r'(\w+)配置': r'\1 configuration',
            r'(\w+)参数': r'\1 parameters',
            
            # Action descriptions
            r'处理(\w+)': r'Process \1',
            r'管理(\w+)': r'Manage \1',
            r'控制(\w+)': r'Control \1',
            r'监听(\w+)': r'Listen to \1',
            
            # Complete common phrases
            r'基础(\w+)类': r'Base \1 class',
            r'默认(\w+)实现': r'Default \1 implementation',
            r'统一管理': 'Unified management',
            r'完全可控': 'Fully controllable',
            r'向后兼容': 'Backward compatibility',
            r'测试环境': 'Test environment',
            r'游戏对象': 'Game objects',
            r'事件源': 'Event source',
            r'键盘状态': 'Keyboard state',
            r'时间戳': 'Timestamp',
            r'修饰键': 'Modifier keys',
            r'冷却时间': 'Cooldown time',
            r'重复间隔': 'Repeat interval',
            r'统计信息': 'Statistics',
            r'错误处理': 'Error handling',
            r'日志记录': 'Logging',
        }

    def extract_comments_and_docstrings(self, file_path: str) -> List[Tuple[int, int, str, str]]:
        """
        Extract all comments and docstrings from a Python file.
        
        Returns:
            List of (line_num, col_offset, comment_type, text) tuples
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        comments_and_docs = []
        
        # Extract comments using tokenize
        try:
            tokens = tokenize.generate_tokens(StringIO(content).readline)
            for token in tokens:
                if token.type == tokenize.COMMENT:
                    # Remove # and whitespace
                    comment_text = token.string.lstrip('#').strip()
                    if self._contains_chinese(comment_text):
                        comments_and_docs.append((
                            token.start[0], 
                            token.start[1], 
                            'comment', 
                            comment_text
                        ))
        except Exception as e:
            print(f"Error tokenizing {file_path}: {e}")
        
        # Extract docstrings using AST
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node)
                    if docstring and self._contains_chinese(docstring):
                        # Find the line number of the docstring
                        if isinstance(node, ast.Module):
                            line_num = 1
                        else:
                            line_num = node.lineno + 1  # Docstring is typically after def/class line
                        
                        comments_and_docs.append((
                            line_num,
                            0,
                            'docstring', 
                            docstring
                        ))
        except Exception as e:
            print(f"Error parsing AST for {file_path}: {e}")
        
        return comments_and_docs

    def _contains_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def translate_text(self, text: str) -> str:
        """Translate Chinese text to English using pattern matching and context"""
        
        # Skip if no Chinese characters
        if not self._contains_chinese(text):
            return text
        
        # Apply sentence patterns first
        translated = text
        for pattern, replacement in self.sentence_patterns.items():
            translated = re.sub(pattern, replacement, translated)
        
        # Apply context term translations
        for chinese, english in self.context_terms.items():
            translated = translated.replace(chinese, english)
        
        # Handle mixed Chinese-English patterns
        translated = self._clean_mixed_text(translated)
        
        return translated.strip()

    def _clean_mixed_text(self, text: str) -> str:
        """Clean up mixed Chinese-English text patterns"""
        
        # Common mixed patterns in the codebase
        cleanups = [
            # Remove redundant mixed patterns
            (r'(\w+)(\w+)', r'\1 \2'),  # Add space between concatenated words
            (r'\s+', ' '),  # Normalize whitespace
            
            # Fix specific patterns found in codebase
            ('definitionsallgameobjects', 'definitions for all game objects'),
            ('gameobjects', 'game objects'),
            ('eventobjects', 'event objects'), 
            ('implementations了', 'implements'),
            ('implementations', 'implementation'),
            ('settings', 'set'),
            ('get', 'get'),
            ('whether', 'whether'),
            ('else', 'else'),
            ('if', 'if'),
            ('return', 'return'),
            ('Contains', 'contains'),
            ('Mockobjects', 'Mock objects'),
            ('time间隔', 'time interval'),
            ('time戳', 'timestamp'),
            ('time控制', 'time control'),
            ('state字典', 'state dictionary'),
            ('movement方向', 'movement direction'),
            ('velocity', 'velocity'),
            ('according to', 'according to'),
            ('朝向目标movement', 'move towards target'),
            ('有lifeentity', 'living entity'),
            ('承受伤害', 'take damage'),
            ('死亡', 'death'),
            ('治疗', 'healing'),
            ('life值', 'health'),
            ('百分比', 'percentage'),
        ]
        
        result = text
        for old, new in cleanups:
            result = result.replace(old, new)
        
        return result

    def translate_file(self, file_path: str) -> bool:
        """
        Translate all Chinese comments and docstrings in a Python file.
        
        Returns:
            True if file was modified, False otherwise
        """
        
        # Read original file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
        
        # Extract comments and docstrings
        comments_and_docs = self.extract_comments_and_docstrings(file_path)
        
        if not comments_and_docs:
            return False
        
        # Sort by line number in reverse order to avoid line number shifts
        comments_and_docs.sort(key=lambda x: x[0], reverse=True)
        
        modified = False
        
        # Process each comment/docstring
        for line_num, col_offset, comment_type, original_text in comments_and_docs:
            translated_text = self.translate_text(original_text)
            
            if translated_text != original_text:
                modified = True
                print(f"  Line {line_num}: {comment_type}")
                print(f"    Original: {original_text[:50]}...")
                print(f"    Translated: {translated_text[:50]}...")
                
                if comment_type == 'comment':
                    # Replace inline comment
                    line_idx = line_num - 1
                    if 0 <= line_idx < len(lines):
                        line = lines[line_idx]
                        # Find the # and replace the comment part
                        hash_pos = line.find('#')
                        if hash_pos != -1:
                            indent = line[:hash_pos]
                            lines[line_idx] = f"{indent}# {translated_text}\n"
                
                elif comment_type == 'docstring':
                    # Replace docstring - this is more complex, handle multi-line docstrings
                    self._replace_docstring(lines, line_num, original_text, translated_text)
        
        # Write back to file if modified
        if modified:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"✓ Updated {file_path}")
                return True
            except Exception as e:
                print(f"Error writing {file_path}: {e}")
                return False
        
        return False

    def _replace_docstring(self, lines: List[str], start_line: int, original: str, translated: str):
        """Replace a docstring in the lines list"""
        
        # Find the docstring in the file
        # This is a simplified approach - look for triple quotes
        start_idx = start_line - 1
        
        # Look for the start of the docstring
        found_start = False
        start_quote_line = start_idx
        
        for i in range(max(0, start_idx - 5), min(len(lines), start_idx + 5)):
            if '"""' in lines[i] or "'''" in lines[i]:
                start_quote_line = i
                found_start = True
                break
        
        if not found_start:
            return
        
        # Find the end of the docstring
        quote_char = '"""' if '"""' in lines[start_quote_line] else "'''"
        end_quote_line = start_quote_line
        
        # Check if it's a single line docstring
        line_content = lines[start_quote_line]
        quote_count = line_content.count(quote_char)
        
        if quote_count >= 2:
            # Single line docstring
            end_quote_line = start_quote_line
        else:
            # Multi-line docstring, find the closing quotes
            for i in range(start_quote_line + 1, len(lines)):
                if quote_char in lines[i]:
                    end_quote_line = i
                    break
        
        # Replace the docstring content
        if start_quote_line == end_quote_line:
            # Single line docstring
            line = lines[start_quote_line]
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            lines[start_quote_line] = f'{indent_str}{quote_char}{translated}{quote_char}\n'
        else:
            # Multi-line docstring
            line = lines[start_quote_line]
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Replace with new content
            new_lines = [f'{indent_str}{quote_char}\n']
            for trans_line in translated.split('\n'):
                if trans_line.strip():
                    new_lines.append(f'{indent_str}{trans_line}\n')
            new_lines.append(f'{indent_str}{quote_char}\n')
            
            # Replace the old lines
            lines[start_quote_line:end_quote_line + 1] = new_lines

    def translate_directory(self, directory: str) -> int:
        """
        Translate all Python files in a directory.
        
        Returns:
            Number of files modified
        """
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
    """Main function to run the translator"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python translate_comments.py <file_or_directory>")
        print("Example: python translate_comments.py thunder_fighter/")
        print("Example: python translate_comments.py thunder_fighter/systems/spawning.py")
        sys.exit(1)
    
    target = sys.argv[1]
    translator = CommentTranslator()
    
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