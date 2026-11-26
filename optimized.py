import os
from tree_common import name_matches, make_line, child_prefix, can_enter, root_path, run_cli


def walk(path, lines, depth, prefix, folders_only, include, exclude, pretty, max_depth):
    if max_depth is not None and depth > max_depth:
        return

    visible = []
    with os.scandir(path) as entries:
        for entry in entries:
            if not name_matches(entry.name, include, exclude):
                continue
            is_dir = entry.is_dir()
            if folders_only and not is_dir:
                continue
            visible.append((entry.name, entry.path, is_dir))

    visible.sort()
    for i in range(len(visible)):
        name, full_path, is_dir = visible[i]
        last = i == len(visible) - 1
        lines.append(make_line(name, depth, prefix, last, pretty))
        if max_depth is not None and depth >= max_depth:
            continue
        if is_dir and can_enter(full_path):
            walk(full_path, lines, depth + 1, child_prefix(prefix, last),
                 folders_only, include, exclude, pretty, max_depth)


def build_tree(path, folders_only=False, include=None, exclude=None,
               pretty=False, max_depth=None):
    path = root_path(path)
    lines = [path]
    walk(path, lines, 1, '', folders_only, include, exclude, pretty, max_depth)
    return lines


if __name__ == '__main__':
    raise SystemExit(run_cli(build_tree))