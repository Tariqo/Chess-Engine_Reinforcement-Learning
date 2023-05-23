from keras.models import Model, clone_model, load_model
from keras.layers import Input, Conv2D, Reshape, Dot
from keras.optimizers import SGD
import random
import numpy as np

class Q_learning(object):

    def __init__(self, env, color):
        self.agent = Agent(color= color)
        self.env = env
        self.memory = []
        self.memsize = 1000
        self.reward_trace = []
        self.sampling_probs = []
        self.color = color


    def learn(self, iters=100, c=10):
        for k in range(iters):
            if k % c == 0:
                print("iter", k)
                self.agent.fix_model()
            self.env.reset()
            move, _ = random.choice(self.env.get_legal_moves_engine('white'))
            self.env.move_piece(self.env.tiles[move[0]][move[1]].piece, self.env.tiles[move[2]][move[3]])
            self.env.set_turn('white' if self.env.turn == 'black' else 'black')
            self.play_game(k, maxiter=30)
        self.agent.save_model(self.color)

    def learn_display(self):
        self.play_game_display(20, greedy=True)
        self.agent.save_model()
    
    def play_game(self, k, greedy=False, maxiter=30):

        episode_end = False
        turncount = 0

        eps = max(0.05, 1 / (1 + (k / 250))) if not greedy else 0.

        # Play a game of chess
        while not episode_end:
            state = self.env.layer_board
            explore = np.random.uniform(0, 1) < eps  # determine whether to explore
            if explore:
                try:
                    self.sfish.set_fen_position(self.env.save_to_FEN())
                    top3_moves = [i['Move'] for i in self.sfish.get_top_moves(3)]
                except:
                    self.agent.save_model('black')
                move_str = random.choice(top3_moves)
                pR,pF = (8 - int(move_str[1])) , ord(move_str[0]) - ord('a') 
                move = (8 - int(move_str[3])) , ord(move_str[2]) - ord('a')
                # move = self.env.get_random_action()
                # move_from, move_to = move
                move_from, move_to = pR * 8 +pF , move[0] * 8 +move[1]
                move = move_from, move_to
                # move = self.env.get_random_action()
                # move_from, move_to = move

            else:
                action_values = self.agent.get_action_values(np.expand_dims(state, axis=0))
                action_values = np.reshape(np.squeeze(action_values), (64, 64))
                action_space = self.env.project_legal_moves()  # The environment determines which moves are legal
                action_values = np.multiply(action_values, action_space)
                move_from = np.argmax(action_values, axis=None) // 64
                move_to = np.argmax(action_values, axis=None) % 64
                moves = [(move_f,move_t) for move_f,move_t in self.env.get_legal_moves_engine_stables(self.env.turn) if \
                        ((move_f == move_from) and (move_t == move_to))]
                if len(moves) == 0:  # If all legal moves have negative action value, explore.
                    move = self.env.get_random_action()
                    move_from, move_to = move
                else:
                    move = random.choice(moves)  # If there are multiple max-moves, pick a random one.


            episode_end, reward = self.env.step(move)
            new_state = self.env.layer_board
            if len(self.memory) > self.memsize:
                self.memory.pop(0)
                self.sampling_probs.pop(0)
            turncount += 1
            if turncount > maxiter:
                episode_end = True
                reward = 0
            if episode_end:
                new_state = new_state * 0
            self.memory.append([state, (move_from, move_to), reward, new_state])
            self.sampling_probs.append(1)

            self.reward_trace.append(reward)

            self.update_agent(turncount)

        return self.env

    def play_game_display(self,k, greedy=False, maxiter=30):
        episode_end = False
        turncount = 0
        
        eps = max(0.05, 1 / (1 + (k / 250))) if not greedy else 0.

        state = self.env.layer_board
        explore = np.random.uniform(0, 1) < eps  # determine whether to explore
        if explore:
            move = self.env.get_random_action()
            move_from, move_to = move
        else:
            vals = self.agent.get_action_values(np.expand_dims(state, axis=0))
            vals = np.reshape(np.squeeze(vals), (64, 64))
            actions = self.env.project_legal_moves()  # The environment determines which moves are legal
            vals = np.multiply(vals, actions)
            move_from = np.argmax(vals, axis=None) // 64
            move_to = np.argmax(vals, axis=None) % 64
            moves = [(move_f,move_t) for move_f,move_t in self.env.get_legal_moves_engine_stables(self.env.turn) if \
                    ((move_f == move_from) and (move_t == move_to))]
            if len(moves) == 0:  # If all legal moves have negative action value, explore.
                move = self.env.get_random_action()
                move_from, move_to = move
            else:
                move = random.choice(moves)  # If there are multiple max-moves, pick a random one.


        episode_end, reward = self.env.step(move, True)
        new_state = self.env.layer_board
        if len(self.memory) > self.memsize:
            self.memory.pop(0)
            self.sampling_probs.pop(0)
        turncount += 1
        if turncount > maxiter:
            episode_end = True
            reward = 0
        if episode_end:
            new_state = new_state * 0
        self.memory.append([state, (move_from, move_to), reward, new_state])
        self.sampling_probs.append(1)

        self.reward_trace.append(reward)

        self.update_agent(turncount)

        return move

    def sample_memory(self, turncount):
        minibatch = []
        memory = self.memory[:-turncount]
        probs = self.sampling_probs[:-turncount]
        sample_probs = [probs[n] / np.sum(probs) for n in range(len(probs))]
        indices = np.random.choice(range(len(memory)), min(1028, len(memory)), replace=True, p=sample_probs)
        for i in indices:
            minibatch.append(memory[i])

        return minibatch, indices

    def update_agent(self, turncount):
        if turncount < len(self.memory):
            minibatch, indices = self.sample_memory(turncount)
            td_errors = self.agent.network_update(minibatch)
            for n, i in enumerate(indices):
                self.sampling_probs[i] = np.abs(td_errors[n])
    
    def choose_move(self):
        k = 30
        eps = 1
        state = self.env.layer_board
        explore = np.random.uniform(0, 1) < eps  # determine whether to explore
        if explore:
            move = self.env.get_random_action()
            move_from, move_to = move
        else:
            self.agent.fix_model()
            vals = self.agent.get_action_values(np.expand_dims(state, axis=0))
            vals = np.reshape(np.squeeze(vals), (64, 64))
            actions = self.env.project_legal_moves()  # The environment determines which moves are legal
            vals = np.multiply(vals, actions)
            move_from = np.argmax(vals, axis=None) // 64
            move_to = np.argmax(vals, axis=None) % 64
            moves = [(move_f,move_t) for move_f,move_t in self.env.get_legal_moves_engine_stables(self.env.turn) if \
                    ((move_f == move_from) and (move_t == move_to))]
            if len(moves) == 0:  # If all legal moves have negative action value, explore.
                move = self.env.get_random_action()
                move_from, move_to = move
            else:
                move = random.choice(moves)  # If there are multiple max-moves, pick a random one.
        move_from = move[0] // 8, move[0] % 8
        move_to = move[1] // 8, move[1] % 8
        return move_from,move_to



class Agent(object):

    def __init__(self, gamma=0.5, lr=0.01, color = ''):
        self.gamma = gamma
        self.learning_rate = lr
        self.init_network()
        self.weight_memory = []
        self.long_term_mean = []
        self.load_model(color)
        self.fix_model()

    def init_network(self):
        optimizer = SGD(learning_rate=self.learning_rate, momentum=0.0, decay=0.0, nesterov=False)
        input_layer = Input(shape=(8, 8, 8), name='board_layer')
        inter_layer_1 = Conv2D(1, (1, 1), data_format="channels_first")(input_layer)  # 1,8,8
        inter_layer_2 = Conv2D(1, (1, 1), data_format="channels_first")(input_layer)  # 1,8,8
        flat_1 = Reshape(target_shape=(1, 64))(inter_layer_1)
        flat_2 = Reshape(target_shape=(1, 64))(inter_layer_2)
        output_dot_layer = Dot(axes=1)([flat_1, flat_2])
        output_layer = Reshape(target_shape=(4096,))(output_dot_layer)
        self.model = Model(inputs=[input_layer], outputs=[output_layer])
        self.model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

    def fix_model(self):
        optimizer = SGD(learning_rate=self.learning_rate, momentum=0.0, decay=0.0, nesterov=False)
        self.fixed_model = clone_model(self.model)
        self.fixed_model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
        self.fixed_model.set_weights(self.model.get_weights())

    def network_update(self, minibatch):
        states, moves, rewards, new_states = [], [], [], []
        td_errors = []
        episode_ends = []
        for sample in minibatch:
            states.append(sample[0])
            moves.append(sample[1])
            rewards.append(sample[2])
            new_states.append(sample[3])

            if np.array_equal(sample[3], sample[3] * 0):
                episode_ends.append(0)
            else:
                episode_ends.append(1)
        
        max_q = np.array(rewards) + np.array(episode_ends) * self.gamma * np.max(
            self.fixed_model.predict(np.stack(new_states, axis=0)), axis=1)

        state = self.model.predict(np.stack(states, axis=0))  # batch x 64 x 64

        state = np.reshape(state, (len(minibatch), 64, 64))
        for idx, move in enumerate(moves):
            td_errors.append(state[idx, move[0], move[1]] - max_q[idx])
            state[idx, move[0], move[1]] = max_q[idx]
        state = np.reshape(state, (len(minibatch), 4096))

        self.model.fit(x=np.stack(states, axis=0), y=state, epochs=1, verbose=0)

        return td_errors

    def get_action_values(self, state):
        return self.fixed_model.predict(state) + np.random.randn() * 1e-9

    def policy_gradient_update(self, states, actions, rewards, action_spaces, actor_critic=False):
        n_steps = len(states)
        Returns = []
        targets = np.zeros((n_steps, 64, 64))
        for t in range(n_steps):
            action = actions[t]
            targets[t, action[0], action[1]] = 1
            if actor_critic:
                R = rewards[t, action[0] * 64 + action[1]]
            else:
                R = np.sum([r * self.gamma ** i for i, r in enumerate(rewards[t:])])
            Returns.append(R)

        if not actor_critic:
            mean_return = np.mean(Returns)
            self.long_term_mean.append(mean_return)
            train_returns = np.stack(Returns, axis=0) - np.mean(self.long_term_mean)
        else:
            train_returns = np.stack(Returns, axis=0)
        targets = targets.reshape((n_steps, 4096))
        self.weight_memory.append(self.model.get_weights())
        self.model.fit(x=[np.stack(states, axis=0),
                          train_returns,
                          np.concatenate(action_spaces, axis=0)
                          ],
                       y=[np.stack(targets, axis=0)],
                       verbose=0
                       )
    def save_model(self,color =''):
        if color == 'black':
            self.model.save('BQ_Learn')
        else:
            self.model.save('Q_Learn')

    def load_model(self, color = ''):
        try:
            if color == 'black':
                self.model = load_model('BQ_Learn')
            else:
                self.model = load_model('Q_Learn')
        except IOError:
            print("Modal not found. Starting with an empty Modal.")
