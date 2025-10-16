"""
Configuration for game difficulty levels and reward shaping
"""

# Difficulty Levels
DIFFICULTY_LEVELS = {
    'easy': {
        'speed': 10,
        'board_width': 800,
        'board_height': 600,
        'description': 'Slower speed, larger board'
    },
    'medium': {
        'speed': 15,
        'board_width': 640,
        'board_height': 480,
        'description': 'Default settings'
    },
    'hard': {
        'speed': 25,
        'board_width': 480,
        'board_height': 360,
        'description': 'Faster speed, smaller board'
    }
}

# Custom Reward Shaping Parameters
REWARD_PARAMS = {
    'default': {
        'food_reward': 10,
        'death_penalty': -10,
        'step_penalty': 0,
        'closer_to_food_reward': 0,
        'description': 'Standard reward system'
    },
    'encouraging': {
        'food_reward': 20,
        'death_penalty': -5,
        'step_penalty': 0,
        'closer_to_food_reward': 0.1,
        'description': 'More rewards, less penalty'
    },
    'strict': {
        'food_reward': 10,
        'death_penalty': -20,
        'step_penalty': -0.01,
        'closer_to_food_reward': 0,
        'description': 'Harsh penalties, encourages efficiency'
    },
    'shaped': {
        'food_reward': 10,
        'death_penalty': -10,
        'step_penalty': 0,
        'closer_to_food_reward': 0.5,
        'description': 'Rewards getting closer to food'
    }
}

# Default settings
DEFAULT_DIFFICULTY = 'medium'
DEFAULT_REWARD_PROFILE = 'default'
