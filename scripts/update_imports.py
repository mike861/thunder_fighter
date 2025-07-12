#!/usr/bin/env python3
"""
Import路径更新脚本

自动更新所有Python文件中的import语句以匹配新的目录结构。
"""

import argparse
from pathlib import Path

# 定义旧路径到新路径的映射
IMPORT_MAPPINGS = {
    # Utils中的游戏逻辑移到systems
    'from thunder_fighter.utils.collisions import': 'from thunder_fighter.systems.collision import',
    'from thunder_fighter.utils.score import': 'from thunder_fighter.systems.scoring import',
    'from thunder_fighter.utils.stars import': 'from thunder_fighter.graphics.effects.stars import',

    # Input系统移到systems
    'from thunder_fighter.input.input_handler import': 'from thunder_fighter.systems.input.handler import',
    'from thunder_fighter.input.input_manager import': 'from thunder_fighter.systems.input.manager import',
    'from thunder_fighter.input.input_system import': 'from thunder_fighter.systems.input.facade import',
    'from thunder_fighter.input.input_events import': 'from thunder_fighter.systems.input.events import',
    'from thunder_fighter.input.key_bindings import': 'from thunder_fighter.systems.input.bindings import',
    'from thunder_fighter.input import': 'from thunder_fighter.systems.input import',

    # Sprites移到entities
    'from thunder_fighter.sprites.player import': 'from thunder_fighter.entities.player.player import',
    'from thunder_fighter.sprites.enemy import': 'from thunder_fighter.entities.enemies.enemy import',
    'from thunder_fighter.sprites.boss import': 'from thunder_fighter.entities.enemies.boss import',
    'from thunder_fighter.sprites.bullets import': 'from thunder_fighter.entities.projectiles.bullets import',
    'from thunder_fighter.sprites.missile import': 'from thunder_fighter.entities.projectiles.missile import',
    'from thunder_fighter.sprites.items import': 'from thunder_fighter.entities.items.items import',
    'from thunder_fighter.sprites.wingman import': 'from thunder_fighter.entities.player.wingman import',
    'from thunder_fighter.sprites.explosion import': 'from thunder_fighter.graphics.effects.explosion import',
    'from thunder_fighter.sprites import': 'from thunder_fighter.entities import',

    # Entities工厂移到对应子目录
    'from thunder_fighter.entities.player_factory import': 'from thunder_fighter.entities.player.player_factory import',
    'from thunder_fighter.entities.enemy_factory import': 'from thunder_fighter.entities.enemies.enemy_factory import',
    'from thunder_fighter.entities.boss_factory import': 'from thunder_fighter.entities.enemies.boss_factory import',
    'from thunder_fighter.entities.projectile_factory import': 'from thunder_fighter.entities.projectiles.projectile_factory import',
    'from thunder_fighter.entities.item_factory import': 'from thunder_fighter.entities.items.item_factory import',

    # UI重组
    'from thunder_fighter.graphics.ui_manager import': 'from thunder_fighter.graphics.ui.manager import',
    'from thunder_fighter.graphics.ui.boss_status_display import': 'from thunder_fighter.graphics.ui.components.boss_status_display import',
    'from thunder_fighter.graphics.ui.game_info_display import': 'from thunder_fighter.graphics.ui.components.game_info_display import',
    'from thunder_fighter.graphics.ui.health_bar import': 'from thunder_fighter.graphics.ui.components.health_bar import',
    'from thunder_fighter.graphics.ui.notification_manager import': 'from thunder_fighter.graphics.ui.components.notification_manager import',
    'from thunder_fighter.graphics.ui.player_stats_display import': 'from thunder_fighter.graphics.ui.components.player_stats_display import',
    'from thunder_fighter.graphics.ui.dev_info_display import': 'from thunder_fighter.graphics.ui.components.dev_info_display import',
    'from thunder_fighter.graphics.ui.screen_overlay_manager import': 'from thunder_fighter.graphics.ui.components.screen_overlay_manager import',
}

# 兼容性映射（为了向后兼容）
COMPATIBILITY_MAPPINGS = {
    'from thunder_fighter.utils.score import Score': 'from thunder_fighter.systems.scoring import ScoringSystem as Score',
    'from thunder_fighter.utils.collisions import': 'from thunder_fighter.systems.collision import CollisionSystem',
}

def update_file_imports(file_path: Path, dry_run: bool = False, verbose: bool = False):
    """更新单个文件的import语句"""
    if not file_path.suffix == '.py':
        return False

    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # 应用所有映射
        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes_made.append(f"  {old_import} -> {new_import}")

        # 应用兼容性映射
        for old_import, new_import in COMPATIBILITY_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes_made.append(f"  {old_import} -> {new_import}")

        # 如果有修改，写回文件
        if content != original_content:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            if verbose or dry_run:
                print(f"Updated imports in: {file_path}")
                for change in changes_made:
                    print(change)

            return True

        return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update import paths for refactored Thunder Fighter')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--path', default='.', help='Path to search for Python files')

    args = parser.parse_args()

    project_root = Path(args.path).resolve()
    thunder_fighter_dir = project_root / 'thunder_fighter'
    tests_dir = project_root / 'tests'

    updated_files = []

    # 更新主项目文件
    if thunder_fighter_dir.exists():
        for py_file in thunder_fighter_dir.rglob('*.py'):
            if update_file_imports(py_file, args.dry_run, args.verbose):
                updated_files.append(py_file)

    # 更新测试文件
    if tests_dir.exists():
        for py_file in tests_dir.rglob('*.py'):
            if update_file_imports(py_file, args.dry_run, args.verbose):
                updated_files.append(py_file)

    # 更新根目录的main.py
    main_py = project_root / 'main.py'
    if main_py.exists():
        if update_file_imports(main_py, args.dry_run, args.verbose):
            updated_files.append(main_py)

    # 输出总结
    if args.dry_run:
        print(f"\nDry run completed. Would update {len(updated_files)} files.")
    else:
        print(f"\nImport update completed! Updated {len(updated_files)} files.")

    if args.verbose:
        print("Updated files:")
        for file_path in updated_files:
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()
