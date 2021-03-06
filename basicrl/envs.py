import os
import numpy
import gym

from gym.spaces.box import Box

from baselines import bench
from baselines.common.atari_wrappers import make_atari, wrap_deepmind

try:
    import pybullet_envs
except ImportError:
    pass

try:
    import gym_minigrid
    from gym_minigrid.wrappers import *
except:
    pass


def make_env(env_id, seed, rank, log_dir, size=None, video=False):
    def _thunk():

        env = gym.make(env_id)

        env.seed(seed + rank)

        if size is not None:
            env.gridSize = size

        # If the input has shape (W,H,3), wrap for PyTorch convolutions
        obs_shape = env.observation_space.shape
        if len(obs_shape) == 3 and obs_shape[2] == 3:
            env = WrapPyTorch(env)

        #env = StateBonus(env)

        if video:
            env = gym.wrappers.Monitor(
                env,
                "./monitor",
                video_callable=lambda episode_id: True,
                force=True
            )

        return env

    return _thunk

class WrapPyTorch(gym.ObservationWrapper):
    def __init__(self, env=None):
        super(WrapPyTorch, self).__init__(env)
        obs_shape = self.observation_space.shape
        self.observation_space = Box(
            self.observation_space.low[0,0,0],
            self.observation_space.high[0,0,0],
            [obs_shape[2], obs_shape[1], obs_shape[0]]
        )

    def _observation(self, observation):
        return observation.transpose(2, 0, 1)
