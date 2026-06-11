import gymnasium as gym
from gymnasium.wrappers import FlattenObservation
from gymnasium.wrappers import RecordVideo
import numpy as np
import matplotlib.pyplot as plt
import pickle #to save the q-table

def run_the_agent(episodes:int = 1000, render:bool = False, training:bool = True, rainy:bool = False, fickle_passenger:bool = False):

    total_rewards = []
    if not training:
        render = True #when we're not training, we want to see what the agent does.
        q_table = pickle.load(open("taxi_qtable.pkl","rb")) #we load the q-table we obtained during training, to see how the agent performs with it.
        episodes = 1 #we just want to see how it performs once.
    env = gym.make("Taxi-v4", render_mode = "human" if render else None, is_rainy = rainy, fickle_passenger = fickle_passenger)
    if training:
        q_table = np.zeros((env.observation_space.n, env.action_space.n))
    print(f"Q-table shape: {q_table.shape}") #the q-table has 500 rows and 6 columns: there are 500 different possible states and 6 actions each time.
    #It's full of 0, as our agent doesn't know anything yet.
    
    # Hyperparameters
    epsilon = 1 #we start by doing fully random actions.
    epsilon_decay_rate = 0.000025 #we decrease the exploration rate by 0.01 at each episode.
    min_epsilon = 0.0 #we still want some exploration, so we let it at 0.2
    alpha = 0.2 #learning rate, reprsenting how lmuch the q-table is updated at each steap.
    gamma = 0.9 #discount factor, representing how much the agent values future rewards compared to immediate rewards.
    rng = np.random.default_rng() #we use a random number, to go with the epsilon-greedy strategy.

    for i in range(episodes):



        state, info = env.reset()
        episode_over = False
        total_reward = 0
        while not episode_over:
            if rng.random() < epsilon and training: #epsilon-greedy strategy: we do a random action with a probability of epsilon, and the best action according to the q-table otherwise.
                action = env.action_space.sample() #do a random action
            else:
                 action = np.argmax(q_table[state,:]) #do the best action with respect to the q_table.

            
            new_state, reward, terminated, truncated, info = env.step(action)
            q_table[state, action] += alpha * (reward + gamma *np.max(q_table[new_state,:]) - q_table[state, action]) #update the q-table using the bellman equation.
            state  = new_state
            episode_over = terminated or truncated
            total_reward += reward
        epsilon = max(min_epsilon, epsilon-epsilon_decay_rate)
        if epsilon == min_epsilon:
            alpha = 0.0001 #once epsilon is at its minimum, we decrease the learning rate to stabilize the table
        total_rewards.append(total_reward)
        #print(f"Episode finished with total reward: {total_reward}")


        env.close()
    if training:
        print(f"Maximum reward obtained: {max(total_rewards)}")
        print(f"Average reward obtained: {np.mean(total_rewards)}")
        plt.figure()
        plt.plot(total_rewards)
        plt.xlabel("Episode")
        plt.ylabel("Total Reward")
        plt.title("Total Rewards over Episodes")
        plt.show()

        f = open("taxi_qtable.pkl","wb")
        pickle.dump(q_table, f)
        f.close()



if __name__ == "__main__": #aucune idée de ce que c'est, mais ça a l'air d'être un chien de garde contre les erreurs éventuelles.
    run_the_agent(episodes= 60000, render = False, training = False, rainy = False, fickle_passenger = False)