import argparse
import os
import sys


def name_matches(name, include, exclude):
    if include is not None and include not in name:
        return False
    if exclude is not None and exclude in name:
        return False
    return True


def make_line(name, depth, prefix, last, pretty):
    if not pretty:
        return '    ' * depth + name
    if last:
        return prefix + '└── ' + name
    return prefix + '├── ' + name


def child_prefix(prefix, last):
    if last:
        return prefix + '    '
    return prefix + '│   '


def can_enter(path):
    # Не обходим ссылки на папки, чтобы не попасть в цикл.
    if os.path.islink(path):
        return False
    # Python 3.12+ умеет проверять точки соединения Windows.
    if hasattr(os.path, 'isjunction') and os.path.isjunction(path):
        return False
    return True


def root_path(path):
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isdir(path):
        raise ValueError('Указанный путь не существует или не является папкой')
    return path


def run_cli(build_tree):
    parser = argparse.ArgumentParser(description='Дерево файловой системы')
    parser.add_argument('path', help='Путь к папке')
    parser.add_argument('--folders-only', action='store_true', help='Только папки')
    parser.add_argument('--include', help='Включить имена с данным текстом')
    parser.add_argument('--exclude', help='Исключить имена с данным текстом')
    parser.add_argument('--pretty', action='store_true', help='Рисовать ветви')
    parser.add_argument('--max-depth', type=int, help='Максимальная глубина')
    args = parser.parse_args()
    if args.max_depth is not None and args.max_depth < 0:
        parser.error('Глубина должна быть неотрицательной')

    try:
        lines = build_tree(args.path, args.folders_only, args.include,
                           args.exclude, args.pretty, args.max_depth)
        print('\n'.join(lines))
    except (OSError, ValueError, RecursionError) as error:
        print('Ошибка:', error, file=sys.stderr)
        return 1
    return 0