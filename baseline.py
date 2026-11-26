import os
from tree_common import name_matches, make_line, child_prefix, can_enter, root_path, run_cli


def walk(path, lines, depth, prefix, folders_only, include, exclude, pretty, max_depth):
    if max_depth is not None and depth > max_depth:
        return

    visible = []
    for name in sorted(os.listdir(path)):
        full_path = os.path.join(path, name)
        is_dir = os.path.isdir(full_path)
        if folders_only and not is_dir:
            continue
        if not name_matches(name, include, exclude):
            continue
        visible.append((name, full_path, is_dir))

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
