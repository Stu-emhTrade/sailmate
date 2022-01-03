import sys


def main():
    print('signal k running')
    for line in sys.stdin:
        if int(line) == 5:
            continue
        else:
            print(int(line) * 2)


if __name__ == '__main__':
    main()
