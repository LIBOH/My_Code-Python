def fibonaci(num):
    """0, 1, 1, 2, 3, 5, 8, 13..."""
    # result = [0, 1]
    # if num == 1:
    #     return 1
    # else:
    #     for i in range(num):
    #         result.append(result[-1] + result[-2])
    #     return result[-1]

    if num == 1:
        return 1
    result = [0, 1]
    result.extend(result[-1] + result[-2] for _ in range(num))
    return result[-1]


if __name__ == '__main__':
    num = int(input("您要查看的数列的位置："))
    print(fibonaci(num))
