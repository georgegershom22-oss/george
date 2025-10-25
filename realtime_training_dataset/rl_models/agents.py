#!/usr/bin/env python3
"""
Reinforcement Learning Agents for Furnace Control
Includes PPO, SAC, and custom multi-objective agents
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Normal, MultivariateNormal
from typing import Dict, List, Tuple, Optional, Any
import pickle
import json
from collections import deque, namedtuple
import random
import matplotlib.pyplot as plt

# Experience tuple for replay buffer
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

class ActorCriticNetwork(nn.Module):
    """Actor-Critic network for PPO agent"""
    
    def __init__(self, 
                 state_dim: int, 
                 action_dim: int, 
                 hidden_dims: List[int] = [256, 256]):
        super(ActorCriticNetwork, self).__init__()
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Shared feature layers
        layers = []
        prev_dim = state_dim
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim
        
        self.shared_layers = nn.Sequential(*layers)
        
        # Actor head (policy)
        self.actor_mean = nn.Linear(prev_dim, action_dim)
        self.actor_log_std = nn.Parameter(torch.zeros(action_dim))
        
        # Critic head (value function)
        self.critic = nn.Linear(prev_dim, 1)
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.orthogonal_(module.weight, 0.01)
            module.bias.data.zero_()
    
    def forward(self, state):
        """Forward pass through the network"""
        features = self.shared_layers(state)
        
        # Actor output
        action_mean = self.actor_mean(features)
        action_std = torch.exp(self.actor_log_std.clamp(-20, 2))
        
        # Critic output
        value = self.critic(features)
        
        return action_mean, action_std, value
    
    def get_action_and_value(self, state, action=None):
        """Get action and value for given state"""
        action_mean, action_std, value = self.forward(state)
        
        # Create distribution
        dist = Normal(action_mean, action_std)
        
        if action is None:
            action = dist.sample()
        
        log_prob = dist.log_prob(action).sum(axis=-1)
        entropy = dist.entropy().sum(axis=-1)
        
        return action, log_prob, entropy, value

class PPOAgent:
    """Proximal Policy Optimization agent for furnace control"""
    
    def __init__(self,
                 state_dim: int,
                 action_dim: int,
                 lr: float = 3e-4,
                 gamma: float = 0.99,
                 gae_lambda: float = 0.95,
                 clip_ratio: float = 0.2,
                 value_coef: float = 0.5,
                 entropy_coef: float = 0.01,
                 max_grad_norm: float = 0.5):
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Hyperparameters
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_ratio = clip_ratio
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.max_grad_norm = max_grad_norm
        
        # Networks
        self.network = ActorCriticNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.network.parameters(), lr=lr)
        
        # Training data storage
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        self.dones = []
        
        # Metrics
        self.training_metrics = {
            'policy_loss': [],
            'value_loss': [],
            'entropy_loss': [],
            'total_loss': [],
            'episode_rewards': []
        }
    
    def get_action(self, state: np.ndarray, deterministic: bool = False) -> Tuple[np.ndarray, float, float]:
        """Get action from policy"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            action, log_prob, entropy, value = self.network.get_action_and_value(state_tensor)
        
        if deterministic:
            action_mean, _, _ = self.network(state_tensor)
            action = action_mean
        
        return action.cpu().numpy()[0], log_prob.cpu().item(), value.cpu().item()
    
    def store_transition(self, state, action, reward, value, log_prob, done):
        """Store transition for training"""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.dones.append(done)
    
    def compute_gae(self, next_value: float = 0.0) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute Generalized Advantage Estimation"""
        advantages = []
        gae = 0
        
        values = self.values + [next_value]
        
        for step in reversed(range(len(self.rewards))):
            delta = self.rewards[step] + self.gamma * values[step + 1] * (1 - self.dones[step]) - values[step]
            gae = delta + self.gamma * self.gae_lambda * (1 - self.dones[step]) * gae
            advantages.insert(0, gae)
        
        advantages = torch.FloatTensor(advantages).to(self.device)
        returns = advantages + torch.FloatTensor(self.values).to(self.device)
        
        return advantages, returns
    
    def update(self, next_value: float = 0.0, update_epochs: int = 4, batch_size: int = 64):
        """Update policy using PPO"""
        if len(self.states) == 0:
            return
        
        # Compute advantages and returns
        advantages, returns = self.compute_gae(next_value)
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(self.states)).to(self.device)
        actions = torch.FloatTensor(np.array(self.actions)).to(self.device)
        old_log_probs = torch.FloatTensor(self.log_probs).to(self.device)
        
        # Training loop
        for epoch in range(update_epochs):
            # Create mini-batches
            indices = torch.randperm(len(states))
            
            for start in range(0, len(states), batch_size):
                end = start + batch_size
                batch_indices = indices[start:end]
                
                batch_states = states[batch_indices]
                batch_actions = actions[batch_indices]
                batch_advantages = advantages[batch_indices]
                batch_returns = returns[batch_indices]
                batch_old_log_probs = old_log_probs[batch_indices]
                
                # Forward pass
                _, new_log_probs, entropy, values = self.network.get_action_and_value(
                    batch_states, batch_actions
                )
                
                # Policy loss
                ratio = torch.exp(new_log_probs - batch_old_log_probs)
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio) * batch_advantages
                policy_loss = -torch.min(surr1, surr2).mean()
                
                # Value loss
                value_loss = F.mse_loss(values.squeeze(), batch_returns)
                
                # Entropy loss
                entropy_loss = -entropy.mean()
                
                # Total loss
                total_loss = (policy_loss + 
                            self.value_coef * value_loss + 
                            self.entropy_coef * entropy_loss)
                
                # Backward pass
                self.optimizer.zero_grad()
                total_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.network.parameters(), self.max_grad_norm)
                self.optimizer.step()
                
                # Store metrics
                self.training_metrics['policy_loss'].append(policy_loss.item())
                self.training_metrics['value_loss'].append(value_loss.item())
                self.training_metrics['entropy_loss'].append(entropy_loss.item())
                self.training_metrics['total_loss'].append(total_loss.item())
        
        # Clear storage
        self.clear_storage()
    
    def clear_storage(self):
        """Clear stored transitions"""
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()
        self.dones.clear()
    
    def save(self, filepath: str):
        """Save agent"""
        torch.save({
            'network_state_dict': self.network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_metrics': self.training_metrics
        }, filepath)
    
    def load(self, filepath: str):
        """Load agent"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.network.load_state_dict(checkpoint['network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.training_metrics = checkpoint['training_metrics']

class SACAgent:
    """Soft Actor-Critic agent for continuous control"""
    
    def __init__(self,
                 state_dim: int,
                 action_dim: int,
                 lr: float = 3e-4,
                 gamma: float = 0.99,
                 tau: float = 0.005,
                 alpha: float = 0.2,
                 buffer_size: int = 1000000):
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.tau = tau
        self.alpha = alpha
        
        # Networks
        self.actor = SACActorNetwork(state_dim, action_dim).to(self.device)
        self.critic1 = SACCriticNetwork(state_dim, action_dim).to(self.device)
        self.critic2 = SACCriticNetwork(state_dim, action_dim).to(self.device)
        self.target_critic1 = SACCriticNetwork(state_dim, action_dim).to(self.device)
        self.target_critic2 = SACCriticNetwork(state_dim, action_dim).to(self.device)
        
        # Copy parameters to target networks
        self.target_critic1.load_state_dict(self.critic1.state_dict())
        self.target_critic2.load_state_dict(self.critic2.state_dict())
        
        # Optimizers
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr)
        self.critic1_optimizer = optim.Adam(self.critic1.parameters(), lr=lr)
        self.critic2_optimizer = optim.Adam(self.critic2.parameters(), lr=lr)
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_size)
        
        # Metrics
        self.training_metrics = {
            'actor_loss': [],
            'critic1_loss': [],
            'critic2_loss': [],
            'episode_rewards': []
        }
    
    def get_action(self, state: np.ndarray, deterministic: bool = False) -> np.ndarray:
        """Get action from policy"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            if deterministic:
                action, _ = self.actor.get_deterministic_action(state_tensor)
            else:
                action, _ = self.actor.get_action(state_tensor)
        
        return action.cpu().numpy()[0]
    
    def store_transition(self, state, action, reward, next_state, done):
        """Store transition in replay buffer"""
        self.replay_buffer.add(state, action, reward, next_state, done)
    
    def update(self, batch_size: int = 256):
        """Update SAC networks"""
        if len(self.replay_buffer) < batch_size:
            return
        
        # Sample batch
        batch = self.replay_buffer.sample(batch_size)
        states = torch.FloatTensor(batch.state).to(self.device)
        actions = torch.FloatTensor(batch.action).to(self.device)
        rewards = torch.FloatTensor(batch.reward).to(self.device)
        next_states = torch.FloatTensor(batch.next_state).to(self.device)
        dones = torch.BoolTensor(batch.done).to(self.device)
        
        # Update critics
        with torch.no_grad():
            next_actions, next_log_probs = self.actor.get_action(next_states)
            target_q1 = self.target_critic1(next_states, next_actions)
            target_q2 = self.target_critic2(next_states, next_actions)
            target_q = torch.min(target_q1, target_q2) - self.alpha * next_log_probs
            target_q = rewards + self.gamma * (1 - dones.float()) * target_q
        
        current_q1 = self.critic1(states, actions)
        current_q2 = self.critic2(states, actions)
        
        critic1_loss = F.mse_loss(current_q1, target_q)
        critic2_loss = F.mse_loss(current_q2, target_q)
        
        self.critic1_optimizer.zero_grad()
        critic1_loss.backward()
        self.critic1_optimizer.step()
        
        self.critic2_optimizer.zero_grad()
        critic2_loss.backward()
        self.critic2_optimizer.step()
        
        # Update actor
        new_actions, log_probs = self.actor.get_action(states)
        q1_new = self.critic1(states, new_actions)
        q2_new = self.critic2(states, new_actions)
        q_new = torch.min(q1_new, q2_new)
        
        actor_loss = (self.alpha * log_probs - q_new).mean()
        
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        # Update target networks
        self.soft_update(self.critic1, self.target_critic1)
        self.soft_update(self.critic2, self.target_critic2)
        
        # Store metrics
        self.training_metrics['actor_loss'].append(actor_loss.item())
        self.training_metrics['critic1_loss'].append(critic1_loss.item())
        self.training_metrics['critic2_loss'].append(critic2_loss.item())
    
    def soft_update(self, source, target):
        """Soft update target network"""
        for target_param, source_param in zip(target.parameters(), source.parameters()):
            target_param.data.copy_(self.tau * source_param.data + (1.0 - self.tau) * target_param.data)

class SACActorNetwork(nn.Module):
    """SAC Actor Network"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super(SACActorNetwork, self).__init__()
        
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.mean = nn.Linear(hidden_dim, action_dim)
        self.log_std = nn.Linear(hidden_dim, action_dim)
        
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.xavier_uniform_(module.weight)
            module.bias.data.zero_()
    
    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        
        mean = self.mean(x)
        log_std = self.log_std(x).clamp(-20, 2)
        
        return mean, log_std
    
    def get_action(self, state):
        mean, log_std = self.forward(state)
        std = torch.exp(log_std)
        
        normal = Normal(mean, std)
        x_t = normal.rsample()
        action = torch.tanh(x_t)
        
        log_prob = normal.log_prob(x_t)
        log_prob -= torch.log(1 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(1, keepdim=True)
        
        return action * 20.0, log_prob  # Scale to [-20, 20]
    
    def get_deterministic_action(self, state):
        mean, _ = self.forward(state)
        return torch.tanh(mean) * 20.0, None

class SACCriticNetwork(nn.Module):
    """SAC Critic Network"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super(SACCriticNetwork, self).__init__()
        
        self.fc1 = nn.Linear(state_dim + action_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)
        
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.xavier_uniform_(module.weight)
            module.bias.data.zero_()
    
    def forward(self, state, action):
        x = torch.cat([state, action], dim=1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class ReplayBuffer:
    """Experience replay buffer"""
    
    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)
    
    def add(self, state, action, reward, next_state, done):
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        return Experience(*zip(*batch))
    
    def __len__(self):
        return len(self.buffer)

class MultiObjectiveAgent:
    """Multi-objective RL agent with Pareto optimization"""
    
    def __init__(self,
                 state_dim: int,
                 action_dim: int,
                 num_objectives: int = 4,
                 lr: float = 3e-4):
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_objectives = num_objectives
        
        # Multiple critics for different objectives
        self.critics = nn.ModuleList([
            SACCriticNetwork(state_dim, action_dim).to(self.device)
            for _ in range(num_objectives)
        ])
        
        # Shared actor
        self.actor = SACActorNetwork(state_dim, action_dim).to(self.device)
        
        # Optimizers
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr)
        self.critic_optimizers = [
            optim.Adam(critic.parameters(), lr=lr)
            for critic in self.critics
        ]
        
        # Objective weights (can be adapted)
        self.objective_weights = torch.ones(num_objectives).to(self.device) / num_objectives
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(1000000)
    
    def get_action(self, state: np.ndarray, deterministic: bool = False) -> np.ndarray:
        """Get action from policy"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            if deterministic:
                action, _ = self.actor.get_deterministic_action(state_tensor)
            else:
                action, _ = self.actor.get_action(state_tensor)
        
        return action.cpu().numpy()[0]
    
    def store_transition(self, state, action, rewards, next_state, done):
        """Store transition with multi-objective rewards"""
        # rewards should be a list/array of rewards for each objective
        self.replay_buffer.add(state, action, rewards, next_state, done)
    
    def update(self, batch_size: int = 256):
        """Update multi-objective networks"""
        if len(self.replay_buffer) < batch_size:
            return
        
        batch = self.replay_buffer.sample(batch_size)
        states = torch.FloatTensor(batch.state).to(self.device)
        actions = torch.FloatTensor(batch.action).to(self.device)
        rewards = torch.FloatTensor(batch.reward).to(self.device)  # Shape: [batch_size, num_objectives]
        next_states = torch.FloatTensor(batch.next_state).to(self.device)
        dones = torch.BoolTensor(batch.done).to(self.device)
        
        # Update each critic
        for i, (critic, optimizer) in enumerate(zip(self.critics, self.critic_optimizers)):
            with torch.no_grad():
                next_actions, _ = self.actor.get_action(next_states)
                target_q = critic(next_states, next_actions)
                target_q = rewards[:, i] + 0.99 * (1 - dones.float()) * target_q.squeeze()
            
            current_q = critic(states, actions).squeeze()
            critic_loss = F.mse_loss(current_q, target_q)
            
            optimizer.zero_grad()
            critic_loss.backward()
            optimizer.step()
        
        # Update actor using weighted combination of critics
        new_actions, log_probs = self.actor.get_action(states)
        
        q_values = []
        for critic in self.critics:
            q_values.append(critic(states, new_actions))
        
        q_values = torch.cat(q_values, dim=1)  # Shape: [batch_size, num_objectives]
        
        # Weighted combination
        weighted_q = torch.sum(q_values * self.objective_weights.unsqueeze(0), dim=1)
        
        actor_loss = -weighted_q.mean()
        
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
    
    def adapt_weights(self, performance_metrics: Dict[str, float]):
        """Adapt objective weights based on performance"""
        # Simple adaptation strategy - can be made more sophisticated
        objectives = ['warpage', 'strain', 'density', 'temperature']
        
        for i, obj in enumerate(objectives):
            if obj in performance_metrics:
                # Increase weight if performance is poor
                if performance_metrics[obj] < 0.5:  # Threshold
                    self.objective_weights[i] *= 1.1
                else:
                    self.objective_weights[i] *= 0.9
        
        # Normalize weights
        self.objective_weights = self.objective_weights / self.objective_weights.sum()

if __name__ == "__main__":
    # Example usage
    state_dim = 7
    action_dim = 6
    
    # Test PPO agent
    ppo_agent = PPOAgent(state_dim, action_dim)
    
    # Test SAC agent
    sac_agent = SACAgent(state_dim, action_dim)
    
    # Test multi-objective agent
    mo_agent = MultiObjectiveAgent(state_dim, action_dim, num_objectives=4)
    
    print("Agents initialized successfully!")
    
    # Test action generation
    test_state = np.random.random(state_dim)
    
    ppo_action, _, _ = ppo_agent.get_action(test_state)
    sac_action = sac_agent.get_action(test_state)
    mo_action = mo_agent.get_action(test_state)
    
    print(f"PPO action: {ppo_action}")
    print(f"SAC action: {sac_action}")
    print(f"Multi-objective action: {mo_action}")