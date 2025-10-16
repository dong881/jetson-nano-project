"""
Tests for enhanced features
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DIFFICULTY_LEVELS, REWARD_PARAMS
from leaderboard import Leaderboard
from advanced_agents import PPOAgent, A3CAgent
from snake_game import SnakeGameAI
from multi_agent_game import MultiAgentSnakeGame


class TestDifficultyLevels(unittest.TestCase):
    """Test difficulty level configuration"""
    
    def test_difficulty_levels_exist(self):
        """Test that all difficulty levels are defined"""
        self.assertIn('easy', DIFFICULTY_LEVELS)
        self.assertIn('medium', DIFFICULTY_LEVELS)
        self.assertIn('hard', DIFFICULTY_LEVELS)
    
    def test_difficulty_settings(self):
        """Test that difficulty levels have correct settings"""
        easy = DIFFICULTY_LEVELS['easy']
        self.assertEqual(easy['speed'], 10)
        
        medium = DIFFICULTY_LEVELS['medium']
        self.assertEqual(medium['speed'], 15)
        
        hard = DIFFICULTY_LEVELS['hard']
        self.assertEqual(hard['speed'], 25)
    
    def test_game_uses_difficulty(self):
        """Test that game respects difficulty setting"""
        game_easy = SnakeGameAI(640, 480, difficulty='easy')
        self.assertEqual(game_easy.game_speed, 10)
        
        game_hard = SnakeGameAI(640, 480, difficulty='hard')
        self.assertEqual(game_hard.game_speed, 25)


class TestRewardShaping(unittest.TestCase):
    """Test custom reward shaping"""
    
    def test_reward_profiles_exist(self):
        """Test that reward profiles are defined"""
        self.assertIn('default', REWARD_PARAMS)
        self.assertIn('encouraging', REWARD_PARAMS)
        self.assertIn('strict', REWARD_PARAMS)
        self.assertIn('shaped', REWARD_PARAMS)
    
    def test_reward_parameters(self):
        """Test reward parameters"""
        default = REWARD_PARAMS['default']
        self.assertEqual(default['food_reward'], 10)
        self.assertEqual(default['death_penalty'], -10)
        
        shaped = REWARD_PARAMS['shaped']
        self.assertGreater(shaped['closer_to_food_reward'], 0)
    
    def test_game_uses_rewards(self):
        """Test that game uses custom rewards"""
        game = SnakeGameAI(640, 480, reward_profile='encouraging')
        self.assertEqual(game.reward_params['food_reward'], 20)


class TestLeaderboard(unittest.TestCase):
    """Test leaderboard system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lb = Leaderboard()
        # Clean up any existing leaderboard
        if os.path.exists('leaderboard.json'):
            os.remove('leaderboard.json')
        self.lb = Leaderboard()
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists('leaderboard.json'):
            os.remove('leaderboard.json')
    
    def test_add_score(self):
        """Test adding score to leaderboard"""
        result = self.lb.add_score(10, 'human', 'easy')
        self.assertTrue(result)
        
        top = self.lb.get_top_scores(1)
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0]['score'], 10)
    
    def test_leaderboard_sorting(self):
        """Test that leaderboard sorts correctly"""
        self.lb.add_score(10, 'human', 'easy')
        self.lb.add_score(20, 'DQN', 'medium')
        self.lb.add_score(5, 'PPO', 'hard')
        
        top = self.lb.get_top_scores(3)
        self.assertEqual(top[0]['score'], 20)
        self.assertEqual(top[1]['score'], 10)
        self.assertEqual(top[2]['score'], 5)
    
    def test_leaderboard_max_entries(self):
        """Test that leaderboard respects max entries"""
        for i in range(15):
            self.lb.add_score(i, 'human', 'easy')
        
        top = self.lb.get_top_scores(20)
        self.assertLessEqual(len(top), 10)
    
    def test_is_high_score(self):
        """Test high score detection"""
        self.lb.add_score(10, 'human', 'easy')
        
        self.assertTrue(self.lb.is_high_score(15))
        self.assertTrue(self.lb.is_high_score(5))  # Less than 10 entries


class TestAdvancedAgents(unittest.TestCase):
    """Test PPO and A3C agents"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game = SnakeGameAI(200, 200)
    
    def test_ppo_agent_creation(self):
        """Test PPO agent initialization"""
        agent = PPOAgent()
        self.assertIsNotNone(agent.model)
        self.assertEqual(agent.n_games, 0)
    
    def test_ppo_agent_action(self):
        """Test PPO agent can get action"""
        agent = PPOAgent()
        state = agent.get_state(self.game)
        action = agent.get_action(state, training=False)
        
        self.assertEqual(len(action), 3)
        self.assertEqual(sum(action), 1)  # One-hot encoded
    
    def test_a3c_agent_creation(self):
        """Test A3C agent initialization"""
        agent = A3CAgent()
        self.assertIsNotNone(agent.model)
        self.assertEqual(agent.n_games, 0)
    
    def test_a3c_agent_action(self):
        """Test A3C agent can get action"""
        agent = A3CAgent()
        state = agent.get_state(self.game)
        action = agent.get_action(state, training=False)
        
        self.assertEqual(len(action), 3)
        self.assertEqual(sum(action), 1)  # One-hot encoded
    
    def test_ppo_training(self):
        """Test PPO training doesn't crash"""
        agent = PPOAgent()
        state = agent.get_state(self.game)
        action = agent.get_action(state)
        
        # Add some experience
        for _ in range(5):
            agent.remember(state, action, 10, False)
        
        # Train (should not crash)
        agent.train()
    
    def test_a3c_training(self):
        """Test A3C training doesn't crash"""
        agent = A3CAgent()
        state = agent.get_state(self.game)
        action = agent.get_action(state)
        
        # Add some experience
        for _ in range(5):
            agent.remember(state, action, 10, False)
        
        # Train (should not crash)
        agent.train_on_episode()


class TestMultiAgent(unittest.TestCase):
    """Test multi-agent system"""
    
    def test_multi_agent_creation(self):
        """Test multi-agent game initialization"""
        game = MultiAgentSnakeGame(num_agents=2)
        self.assertEqual(game.num_agents, 2)
        self.assertEqual(len(game.agents_data), 2)
    
    def test_multi_agent_reset(self):
        """Test multi-agent game reset"""
        game = MultiAgentSnakeGame(num_agents=2)
        game.reset()
        
        self.assertEqual(len(game.agents_data), 2)
        for agent_data in game.agents_data:
            self.assertTrue(agent_data['alive'])
            self.assertEqual(agent_data['score'], 0)
    
    def test_multi_agent_play_step(self):
        """Test multi-agent play step"""
        game = MultiAgentSnakeGame(num_agents=2)
        actions = [[1, 0, 0], [1, 0, 0]]
        
        rewards, dones, scores = game.play_step(actions)
        
        self.assertEqual(len(rewards), 2)
        self.assertEqual(len(dones), 2)
        self.assertEqual(len(scores), 2)
    
    def test_multi_agent_get_state(self):
        """Test getting state for each agent"""
        game = MultiAgentSnakeGame(num_agents=2)
        
        state0 = game.get_state(0)
        state1 = game.get_state(1)
        
        self.assertEqual(len(state0), 11)
        self.assertEqual(len(state1), 11)
    
    def test_multi_agent_all_done(self):
        """Test all_done method"""
        game = MultiAgentSnakeGame(num_agents=2)
        
        self.assertFalse(game.all_done())
        
        # Mark all as dead
        for agent_data in game.agents_data:
            agent_data['alive'] = False
        
        self.assertTrue(game.all_done())


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
