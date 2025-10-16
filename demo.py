"""
Demo script to test RL training without display
This demonstrates the agent can learn to play the game
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy video driver for headless

from snake_game import SnakeGameAI
from agent import Agent
import time

def demo_training(num_games=5):
    """
    Run a quick training demo
    Args:
        num_games: Number of games to run
    """
    print("="*50)
    print("Snake Game RL Training Demo")
    print("="*50)
    print(f"\nTraining for {num_games} games...")
    print()
    
    agent = Agent()
    game = SnakeGameAI()
    
    scores = []
    start_time = time.time()
    
    while agent.n_games < num_games:
        # Get old state
        state_old = agent.get_state(game)
        
        # Get move
        final_move = agent.get_action(state_old)
        
        # Perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)
        
        # Train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        
        # Remember
        agent.remember(state_old, final_move, reward, state_new, done)
        
        if done:
            # Train long memory
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            
            scores.append(score)
            
            print(f"Game {agent.n_games}: Score = {score}, "
                  f"Avg = {sum(scores)/len(scores):.1f}, "
                  f"Max = {max(scores)}")
    
    elapsed_time = time.time() - start_time
    
    print()
    print("="*50)
    print("Training Complete!")
    print("="*50)
    print(f"Total Games: {num_games}")
    print(f"Average Score: {sum(scores)/len(scores):.2f}")
    print(f"Max Score: {max(scores)}")
    print(f"Min Score: {min(scores)}")
    print(f"Time Elapsed: {elapsed_time:.2f} seconds")
    print(f"Games/Second: {num_games/elapsed_time:.2f}")
    print()
    
    # Save the model
    agent.save_model('demo_model.pth')
    print("Model saved to ./model/demo_model.pth")
    print()


def demo_game_api():
    """
    Demonstrate the game API
    """
    print("="*50)
    print("Snake Game API Demo")
    print("="*50)
    print()
    
    game = SnakeGameAI()
    
    print("Initial State:")
    print(f"  Snake Length: {len(game.snake)}")
    print(f"  Score: {game.score}")
    print(f"  Head Position: {game.head}")
    print(f"  Food Position: {game.food}")
    print()
    
    # Get state
    state = game.get_state()
    print("State Vector (11 dimensions):")
    print(f"  {state}")
    print()
    
    # Perform some actions
    print("Performing 5 actions...")
    for i in range(5):
        action = [1, 0, 0]  # Move straight
        reward, game_over, score = game.play_step(action)
        print(f"  Step {i+1}: Reward={reward}, Score={score}, Game Over={game_over}")
        
        if game_over:
            print("  Game ended!")
            break
    
    print()
    print("Final State:")
    print(f"  Snake Length: {len(game.snake)}")
    print(f"  Score: {game.score}")
    print()


if __name__ == '__main__':
    # Run API demo
    demo_game_api()
    
    print()
    print()
    
    # Run training demo (reduced for quick test)
    demo_training(num_games=5)
