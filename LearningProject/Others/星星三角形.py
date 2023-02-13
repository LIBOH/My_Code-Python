while True:
    try:
        num = input('单行最多星星的个数(输入"q"退出):')
        if num == 'q':
            break
        else:
            num = int(num)

    except ValueError:
        print('请输入阿拉伯数字或q.')
        continue

    for i in range(1, num * 2):
        if i <= num:
            print(i * '*')
        else:
            print((num * 2 - i) * '*')
