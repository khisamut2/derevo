import argparse
import os
import platform
import statistics
import tempfile
import time
import baseline
import optimized


def create_files(path, count):
    for i in range(10):
        os.mkdir(os.path.join(path, 'dir_' + str(i)))
    for i in range(count):
        folder = os.path.join(path, 'dir_' + str(i % 10))
        filename = os.path.join(folder, 'file_' + str(i) + '.txt')
        with open(filename, 'w'):
            pass


def measure(path, repeats, folders_only=False, exclude=None):
    first = baseline.build_tree(path, folders_only, exclude=exclude)
    second = optimized.build_tree(path, folders_only, exclude=exclude)
    if first != second:
        raise ValueError('Результаты двух версий различаются')

    times_base = []
    times_opt = []
    for i in range(repeats):
        start = time.perf_counter()
        baseline.build_tree(path, folders_only, exclude=exclude)
        times_base.append(time.perf_counter() - start)

        start = time.perf_counter()
        optimized.build_tree(path, folders_only, exclude=exclude)
        times_opt.append(time.perf_counter() - start)

    return statistics.median(times_base), statistics.median(times_opt)


def show_result(count, mode, first, second):
    print(f'| {count} | {mode} | {first:.6f} | {second:.6f} | {first / second:.2f} |')


def main():
    parser = argparse.ArgumentParser(description='Замеры времени')
    parser.add_argument('--sizes', nargs='+', type=int, default=[100, 1000, 5000])
    parser.add_argument('--repeats', type=int, default=9)
    args = parser.parse_args()
    if min(args.sizes) < 0 or args.repeats < 1:
        parser.error('Неверный размер или число повторов')

    print('Python', platform.python_version(), platform.platform())
    print('Повторов:', args.repeats)
    print('| Файлов | Режим | Baseline, с | Optimized, с | Ускорение |')
    print('|---:|---|---:|---:|---:|')
    for count in args.sizes:
        with tempfile.TemporaryDirectory() as path:
            create_files(path, count)
            first, second = measure(path, args.repeats)
            show_result(count, 'Все', first, second)
            first, second = measure(path, args.repeats, folders_only=True)
            show_result(count, 'Только папки', first, second)
            first, second = measure(path, args.repeats, exclude='.txt')
            show_result(count, 'Исключить файлы', first, second)


if __name__ == '__main__':
    main()