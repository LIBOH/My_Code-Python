import random


class GuessGame:
    def __init__(self) -> None:
        self.data = ['石头', '剪刀', '布']
        self.pl_score = 0
        self.pc_score = 0
        self.overtime = 0

    def _computer(self) -> str:
        """电脑出拳"""
        return random.choice(self.data)

    def _each_game(self):
        """每场对局"""
        while True:
            pl_choose = input('-> 玩家出：')
            pc_choose = self._computer()
            try:
                pl_value = self.data.index(pl_choose)
                pc_value = self.data.index(pc_choose)
                print(f'-> 电脑出：{pc_choose}')
            except ValueError:
                print('-> 请重新输入！')
                continue
            else:
                return pl_value, pc_value
            finally:
                pl_value, pc_value = 0, 0

    def _judge(self, pl_value, pc_value) -> int:
        """判断胜负"""
        match pl_value - pc_value:
            case 0:
                print('-> ------ 平局! -----\n')
                return 0

            case - 1 | 2:
                print('-> ----- 你赢了! -----\n')
                self.pl_score += 1
                return 1

            case 1 | -2:
                print('-> ----- 你输了! -----\n')
                self.pc_score += 1
                return -1

    def _judge_info(self, total_count=1) -> str:
        """胜负信息"""
        a = f'-> 回合数：{total_count} -- 加时赛次数：{self.overtime}\n'
        b = f'-> 玩家得分：{self.pl_score}\n'
        c = f'-> 电脑得分：{self.pc_score}\n'
        return a + b + c

    def _overtime(self):
        """加时赛"""
        while True:
            state = input('-> 请选择是否加时(Y/N)：')
            match state:
                case 'Y' | 'y':
                    self.overtime += 1
                    pl_value, pc_value = self._each_game()
                    if self._judge(pl_value, pc_value) != 0:
                        return True
                    continue
                case 'N' | 'n':
                    print()
                    return False
                case _:
                    print('-> 请重新输入！')
                    continue

    def game_mode_1(self):
        """游戏模式1"""
        pl_value, pc_value = self._each_game()
        self._judge(pl_value, pc_value)
        print(self._judge_info())

    def game_mode_2(self):
        """游戏模式2"""
        while True:
            try:
                count = int(input('-> 请输入你要游玩的回合数：'))
                total_count = count
                break
            except ValueError:
                print('-> 请输入阿拉伯数字！')
                continue
        while count:
            pl_value, pc_value = self._each_game()
            self._judge(pl_value, pc_value)
            count -= 1
        print(self.mode_2_expand(total_count))

    def mode_2_expand(self, total_count):
        """模式二拓展"""
        while True:
            if self.pl_score == self.pc_score:
                print(f'{self.pl_score} 比 {self.pc_score} - 平手')
                if self._overtime() is False:
                    return f'{self._judge_info(total_count)}-> 平手！'

            elif self.pl_score > self.pc_score:
                return f'{self._judge_info(total_count)}-> 恭喜你！'

            else:
                return f'{self._judge_info(total_count)}-> 很遗憾！'


if __name__ == '__main__':
    G = GuessGame()
    print('***************  猜拳游戏  ***************', end='\n' * 2)
    while True:
        mode = input('[1]单句游戏模式 [2]多局游戏模式 - ')
        if mode == '1':
            print('----------------------')
            G.game_mode_1()
            print('**********************')
            break
        elif mode == '2':
            print('----------------------')
            G.game_mode_2()
            print('**********************')
            break
        else:
            print('-> 请重新输入！\n')
