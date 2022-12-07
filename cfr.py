import random
import time
class Node:
    def __init__(self):
        self.regret_sum = [0, 0]
        self.avg_strategy = [0, 0]
    def get_avg_strategy(self):
        sum = 0
        strategy = [0, 0]
        for i in range(2):
            strategy[i] = self.avg_strategy[i]
            sum += strategy[i]
        if sum == 0:
            return [0.5, 0.5]
        for i in range(2):
            strategy[i] /= sum
        return strategy

class Poker:
    def __init__(self):
        self.node_map = {}
        self.all_cards = [i for i in range(3)]
        self.cards = [0, 0]
        self.action = ['P', 'B']
        self.ctr = 0
    def get_strategy(self, information, prob):
        current_node = self.node_map.get(information, None)
        if current_node == None:
            self.node_map[information] = Node()
            return [0.5, 0.5]
        strategy = [0, 0]
        sum = 0
        for i in range(2):
            strategy[i] = max(0, current_node.regret_sum[i])
            sum += strategy[i]
        if sum == 0:
            return [0.5, 0.5]
        for i in range(2):
            strategy[i] /= sum
        for i in range(2):
            self.node_map[information].avg_strategy[i] += prob * strategy[i]
        return strategy
    def train(self, iterations):
        scenario = [
            [0, 1 ,2],
            [0, 2, 1],
            [1, 0, 2],
            [1, 2, 0],
            [2, 0, 1],
            [2, 1, 0]
        ]
        total_util = 0
        for i in range(iterations):
            random.shuffle(self.all_cards)
            # self.all_cards = scenario[i % len(scenario)]
            self.cards[0] = self.all_cards[0]
            self.cards[1] = self.all_cards[1]
            total_util += self.play("", [1, 1])
        print('avg util = ', total_util / iterations)
    def check_terminal(self, history):
        round = len(history)
        hero = round % 2
        villian = 1 - hero
        # print('history = ', history, 'hero = ', hero)

        if len(history) == 2: # check for terminal state
            if history[-2:] == 'PP':
                if self.cards[hero] > self.cards[villian]:
                    return 1
                else:
                    return -1
            if history[-2:] == 'BB':
                if self.cards[hero] > self.cards[villian]:
                    return 2
                else:
                    return -2
            if history[-2:] == 'BP':
                return 1
        if len(history) == 3:
            if history[-3:] == 'PBP':
                return 1
            if history[-3:] == 'PBB':
                if self.cards[hero] > self.cards[villian]:
                    return 2
                else:
                    return -2
        return 3 # continue to play
    def play(self, history, prob) -> int:
        self.ctr += 1
        round = len(history)
        hero = round % 2
        villian = 1 - hero
        # print(round, history)

        if self.check_terminal(history) != 3:
            return self.check_terminal(history)


        information = str(self.cards[hero]) + history
        strategy = self.get_strategy(information, prob[hero])
        node = self.node_map[information]
        util = 0
        child_util = [0, 0]

        t1 = time.time()

        for i in range(2):
            new_history = history + self.action[i]
            probability = strategy[i]
            new_prob = prob.copy()
            new_prob[hero] *= probability
            child_util[i] = - self.play(new_history, new_prob)
            util += strategy[i] * child_util[i]

        for i in range(2):
            self.node_map[information].regret_sum[i] += prob[villian] * (child_util[i] - util)

        t2 = time.time()
        # print('time cost:', t2 - t1)
        
        return util

if __name__ == '__main__':
    poker = Poker()
    t1 = time.time()
    poker.train(100000)
    t2 = time.time()
    print('training time:', t2 - t1)
    print('total training action:', poker.ctr)
    for key in poker.node_map:
        print(str(int(key[0])+1) + key[1:], poker.node_map[key].get_avg_strategy())
    