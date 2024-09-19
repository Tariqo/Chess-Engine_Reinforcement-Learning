# Chess Reinforcement Learning Engine Using Q-Learning
## Motivation
Artificial intelligence has dominated discussions for the past ten years when it comes to software development. As technology continues to advance, it has become easier to run hundreds of millions of simulations in very short amounts of time. 

Reinforcement learning, a subfield of machine learning, focuses on training agents to interact with an environment and optimize their behavior through trial and error by running millions of training episodes. It has been successfully applied in industries such as robotics, video games, finance, and more.

This thesis focuses on chess, a complex board game that has long served as a testing ground for various machine learning techniques. By implementing a reinforcement learning engine using the Q-learning algorithm in a custom-made chess environment, we can explore how intelligent agents can learn to play chess and improve their gameplay over time.

## Thesis Objective
The goal of this thesis is to investigate the effectiveness of reinforcement learning, specifically the Q-learning algorithm, within the context of chess. We will design and implement a custom chess environment that allows an AI agent to:

- Interact with the chessboard and make moves based on its learned policies.
- Learn from experience by receiving rewards or penalties based on the outcomes of its moves.
- Adjust its strategy over time to improve its gameplay.

## Features
- Custom chess environment built from scratch.
- Implementation of Q-learning algorithm to train the agent.
- Reward-based learning where the agent receives feedback on its moves.
- Progressive improvement in agent strategy through trial and error.

### Installation Guide

## Requirements
There are no high-end system requirements to run this project. The following specifications are preferred, but even more modest systems should be able to run the chess game:

- **Processor (CPU)**: 1.0GHz or faster
- **Memory (RAM)**: 2 GB or more
- **Graphics Card (GPU)**: None required
- **Storage**: 200MB of free space
- **Operating System**: Compatible with all major operating systems (Windows, macOS, Linux)

### Software Requirements

Before using the project, ensure the following software components are installed:

- **Python 3.6** or later
- **Pip 22.0** or later
- Additional Python packages specified in the `requirements.txt` file

#### Installation Instructions

To install all the necessary dependencies, open a terminal or command prompt and navigate to the project directory. Then, run the following command:

```bash
$ pip install -r requirements.txt