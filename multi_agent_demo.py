"""
Demo script for multi-agent training
"""
import pygame
from multi_agent_game import MultiAgentSnakeGame
from agent import Agent

def train_multi_agent(num_agents=2, num_episodes=100):
    """
    Train multiple agents simultaneously
    """
    game = MultiAgentSnakeGame(num_agents=num_agents)
    agents = [Agent() for _ in range(num_agents)]
    
    print(f"Starting multi-agent training with {num_agents} agents...")
    
    for episode in range(num_episodes):
        game.reset()
        episode_scores = [0] * num_agents
        
        while not game.all_done():
            # Get states for all agents
            states = [agent.get_state(game) if game.agents_data[i]['alive'] else None 
                     for i, agent in enumerate(agents)]
            
            # Get actions for all agents
            actions = []
            for i, (agent, state) in enumerate(zip(agents, states)):
                if state is not None and game.agents_data[i]['alive']:
                    action = agent.get_action(state)
                else:
                    action = [1, 0, 0]  # Default action for dead agents
                actions.append(action)
            
            # Execute actions
            rewards, dones, scores = game.play_step(actions)
            
            # Get new states
            new_states = [agent.get_state(game) if game.agents_data[i]['alive'] else None 
                         for i, agent in enumerate(agents)]
            
            # Train each agent
            for i, (agent, state, action, reward, new_state, done) in enumerate(
                zip(agents, states, actions, rewards, new_states, dones)):
                if state is not None:
                    agent.train_short_memory(state, action, reward, new_state, done)
                    agent.remember(state, action, reward, new_state, done)
                    
                    if done and not game.agents_data[i]['alive']:
                        agent.n_games += 1
                        agent.train_long_memory()
                
                episode_scores[i] = scores[i]
        
        # Episode summary
        alive_count = game.get_alive_count()
        avg_score = sum(episode_scores) / num_agents
        print(f"Episode {episode+1}/{num_episodes} - "
              f"Avg Score: {avg_score:.1f}, "
              f"Scores: {episode_scores}, "
              f"Agents alive at end: {alive_count}")
    
    # Save models
    for i, agent in enumerate(agents):
        agent.save_model(f'multi_agent_{i}.pth')
    
    print("Multi-agent training complete!")

if __name__ == '__main__':
    import sys
    
    # Get number of agents from command line or use default
    num_agents = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    num_episodes = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    train_multi_agent(num_agents, num_episodes)
