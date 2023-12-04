# Reinforcement Learning Driven Dota 2 Bot Development

![DOTA2](https://github.com/soumyendra98/DQN-Game-Bot/blob/main/images/download.gif)


## Team Members:
- Soumyendra Shrivastava (016670121)
- Siddhant Sancheti (016710421)


## Summary 📝

Our project ambitiously aims to develop a bot for the intricate and competitive MOBA game, Dota 2. Utilizing the principles of Reinforcement Learning (RL) and Deep Q-Networks (DQN), we aspire to create an AI-driven bot capable of making sophisticated real-time decisions, setting new standards in AI for gaming.

## Background and Motivation 🌐

Dota 2, as a complex and strategic MOBA game, offers a unique challenge in AI and RL. The game's multifaceted environment presents numerous opportunities for AI to make real-time, strategic decisions, a scenario that is not only limited to gaming but extends to various real-world applications.

## Why This Project? 🔍

- Exploring AI's Potential: Our project is a continuation of the legacy set by OpenAI Five, pushing the boundaries of AI in strategic decision-making.
- Innovative Approach: Leveraging DQN, we aim to enhance our bot's learning process, allowing it to adapt to the dynamic nature of Dota 2.
- Real-World Applications: Success in this project could pave the way for implementing similar AI strategies in real-life scenarios demanding quick and strategic decision-making.

## Current Approaches 🔄

Current methodologies primarily involve RL and DQN for training bots to navigate Dota 2's multifaceted environment. While significant progress has been made, the quest for a bot that can match or surpass human proficiency remains open, underscoring the need for ongoing innovation.

## Project Goal 🎯

To create a Dota 2 bot that exemplifies high-level strategic play and decision-making using DQN.

## Scope 📈

### In Scope

- Development and training of the Dota 2 bot using DQN.
- Iterative evaluation and refinement of the bot’s performance.

### Out of Scope

- Utilizing ML algorithms beyond the scope of DQN.
- Commercial deployment of the bot.

## Deliverables 📦

A comprehensive Python-based implementation of the Dota 2 bot, encompassing all RL elements: Agent, Environment, Action, Policy, and Reward systems.

## Risks and Rewards ⚖️

### Risks
- Computational Resources: The complexity of Dota 2 might require extensive computational power and time.
- Game Mechanics: Unpredictable challenges in game mechanics could pose hurdles in the learning process.

### Rewards

- AI in Gaming: A breakthrough would significantly advance the use of AI in gaming.
- Broader Applications: The methodologies could be replicated in other areas requiring strategic real-time decision-making.

## Implementation and Results 🚀

### Methodology

We employed a blend of Python, RL, and DQN in our implementation. The project was structured as follows:

- Environment Setup: Customized Dota 2 environment for the bot.
  
- Agent Development: Utilizing RL principles to develop the decision-making agent.
  
- Training Process: Leveraging DQN for training the bot.
  
- Iterative Testing: Continuous testing and refinement of the bot's strategies.
  
## Code Snippets

```
# Example of the action function
def get_action(state, eps):
    # Epsilon-greedy strategy for action selection
    if random.uniform(0, 1) > eps:
        return self.network.predict(state=state)
    else:
        return random.randint(0, output_shape - 1)
```

This snippet showcases our implementation of the epsilon-greedy strategy in the bot's decision-making process.

## Results and Contributions

- Bot Proficiency: Achieved a high level of gameplay proficiency in Dota 2.

- Innovative Solutions: Developed novel solutions to enhance strategic gameplay.

- AI Learning Efficiency: Demonstrated the effectiveness of DQN in rapid learning and adaptation.

## Conclusions and Future Work 🔮

The project successfully demonstrated the potential of DQN in developing a proficient Dota 2 bot. Our approach has opened avenues for further exploration in AI's role in gaming and other strategic, real-time decision-making domains.

## Future Directions

- Scalability: Exploring the scalability of our approach to other complex gaming environments.

- Algorithm Enhancement: Continual refinement of DQN and RL methodologies for improved efficiency.

- Real-world Applications: Applying the insights gained to real-world scenarios requiring strategic decision-making.
