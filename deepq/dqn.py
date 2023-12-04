import argparse
import itertools
import os
import sys

import numpy as np
import tensorflow as tf

sys.path.append('../')

from deepq import StatePotentialRewardShaper, Estimator, StatePreprocessor, PrioritizedReplayBuffer
from deepq import get_last_episode
from dotaenv import DotaEnvironment
from dotaenv.codes import STATE_DIM, ACTIONS_TOTAL


def copy_model_parameters(sess, estimator1, estimator2):
    
    e1_params = [t for t in tf.trainable_variables() if t.name.startswith(estimator1.scope)]
    e1_params = sorted(e1_params, key=lambda v: v.name)
    e2_params = [t for t in tf.trainable_variables() if t.name.startswith(estimator2.scope)]
    e2_params = sorted(e2_params, key=lambda v: v.name)

    update_ops = []
    for e1_v, e2_v in zip(e1_params, e2_params):
        op = e2_v.assign(e1_v)
        update_ops.append(op)

    sess.run(update_ops)


def make_epsilon_greedy_policy(estimator, acts):
    """
    Creates an epsilon-greedy policy based on a given Q-function approximator and epsilon.
    Args:
        estimator: An estimator that returns q values for a given state
        acts: Number of actions in the environment.
    Returns:
        A function that takes the (sess, state, epsilon) as an argument and returns
        the probabilities for each action in the form of a numpy array of length nA.
    """
    def policy_fn(sess, state, epsilon):
        A = np.ones(acts, dtype=float) * epsilon / acts
        q_values = estimator.predict(sess, np.expand_dims(state, 0))[0]
        best_action = np.argmax(q_values)
        A[best_action] += (1.0 - epsilon)
        return A
    return policy_fn


def populate_replay_buffer(replay_buffer, action_sampler, env):
    print("Populating replay memory...")
    state = env.reset()
    state = StatePreprocessor.process(state)
    done = False
    for t in itertools.count():
        if done or len(state) != STATE_DIM:
            break
        action_probs = action_sampler(state)
        action = np.random.choice(np.arange(len(action_probs)), p=action_probs)
        print("Step {step} state: {state}, action: {action}.".format(step=t, state=state, action=action))
        next_state, reward, done, _ = env.step(action=action)
        next_state = StatePreprocessor.process(next_state)
        replay_buffer.push(state, action, next_state, done, reward)
        state = next_state


def deep_q_learning(sess,
                    env,
                    q_estimator,
                    target_estimator,
                    num_steps,
                    experiment_dir,
                    replay_memory_size=5000,
                    update_target_estimator_every=500,
                    discount_factor=0.999,
                    epsilon_start=1.0,
                    epsilon_end=0.1,
                    epsilon_decay_steps=10000,
                    update_q_values_every=4,
                    batch_size=32,
                    restore=True):

    # Create directories for checkpoints and summaries
    checkpoint_dir = os.path.join(experiment_dir, "checkpoints")
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    checkpoint_path = os.path.join(checkpoint_dir, "model")
    reward_dir = os.path.join(experiment_dir, "rewards")
    if not os.path.exists(reward_dir):
        os.makedirs(reward_dir)
    reward_writer = tf.summary.FileWriter(reward_dir)

    starting_episode = 0

    saver = tf.train.Saver()
    if restore:
        starting_episode = get_last_episode(reward_dir)
        # Load a previous checkpoint if we find one
        latest_checkpoint = tf.train.latest_checkpoint(checkpoint_dir)
        if latest_checkpoint:
            print("Loading model checkpoint {}...\n".format(latest_checkpoint))
            saver.restore(sess, latest_checkpoint)

    total_t = sess.run(tf.train.get_global_step())

    # The epsilon decay schedule
    epsilons = np.linspace(epsilon_start, epsilon_end, epsilon_decay_steps)

    reward_shaper = StatePotentialRewardShaper('replays/')
    reward_shaper.load()

    replay_buffer = PrioritizedReplayBuffer(
        replay_memory_size=replay_memory_size,
        total_steps=num_steps,
        reward_shaper=reward_shaper,
        discount_factor=discount_factor,
        save_dir=experiment_dir)

    # The policy we're following
    policy = make_epsilon_greedy_policy(q_estimator, ACTIONS_TOTAL)

    # Populate the replay memory with initial experience
    action_sampler = lambda state: policy(sess, state, epsilons[min(total_t, epsilon_decay_steps-1)])
    populate_replay_buffer(replay_buffer, action_sampler, env)

    print('Training is starting...')
    # Training the agent
    for i_episode in itertools.count(starting_episode):
        episode_reward = 0
        multiplier = 1

        # Save the current checkpoint
        saver.save(tf.get_default_session(), checkpoint_path)

        # Reset the environment
        state = env.reset()
        state = StatePreprocessor.process(state)
        done = False

        # One step in the environment
        for t in itertools.count():
            if total_t >= num_steps:
                return

            eps = epsilons[min(total_t, epsilon_decay_steps-1)]

            if done or len(state) != STATE_DIM:
                print("Finished episode with reward", episode_reward)
                summary = tf.Summary(value=[tf.Summary.Value(tag="rewards", simple_value=episode_reward)])
                reward_writer.add_summary(summary, i_episode)
                summary = tf.Summary(value=[tf.Summary.Value(tag="eps", simple_value=eps)])
                reward_writer.add_summary(summary, i_episode)
                break

            # Maybe update the target estimator
            if total_t % update_target_estimator_every == 0:
                copy_model_parameters(sess, q_estimator, target_estimator)
                print("\nCopied model parameters to target network.")

            print('State potential:', reward_shaper.get_state_potential(state))

            # Take a step
            action_probs = policy(sess, state, eps)
            action = np.random.choice(np.arange(len(action_probs)), p=action_probs)
            print("state: {state}, action: {action}.".format(state=state, action=action))

            next_state, reward, done, _ = env.step(action=action)
            next_state = StatePreprocessor.process(next_state)

            episode_reward += reward * multiplier
            multiplier *= discount_factor

            # Save transition to replay memory
            replay_buffer.push(state, action, next_state, done, reward)

            if total_t % update_q_values_every == 0:
                # Sample a minibatch from the replay memory
                samples, weights, idx = replay_buffer.sample(batch_size, total_t)
                states, actions, next_states, dones, rewards, _ = map(np.array, zip(*samples))

                not_dones = np.invert(dones).astype(np.float32)
                # Calculate q values and targets (Double DQN)
                next_q_values = q_estimator.predict(sess, next_states)
                best_actions = np.argmax(next_q_values, axis=1)
                next_q_values_target = target_estimator.predict(sess, next_states)
                targets = (
                    rewards +
                    discount_factor * not_dones * next_q_values_target[np.arange(batch_size), best_actions])

                # Perform gradient descent update
                predictions = q_estimator.update(sess, states, actions, targets, weights)

                # Update transition priorities
                deltas = np.abs(predictions - targets)
                replay_buffer.update_priorities(idx, deltas)

            print("\rStep {}, episode {} ({}/{})".format(t, i_episode, total_t, num_steps), end="\t")
            sys.stdout.flush()

            state = next_state
            total_t += 1


def main():
    parser = argparse.ArgumentParser(description='Trains the agent by DQN')
    parser.add_argument('experiment', help='specifies the experiment name')
    args = parser.parse_args()

    env = DotaEnvironment()

    # Where we save our checkpoints and graphs
    experiment_dir = os.path.join(os.path.abspath("./experiments/"), args.experiment)

    tf.reset_default_graph()
    # Create a global step variable
    global_step = tf.Variable(0, name="global_step", trainable=False)

    # Create estimators
    q_estimator = Estimator(
        STATE_DIM,
        ACTIONS_TOTAL,
        scope="q",
        summaries_dir=experiment_dir)
    target_estimator = Estimator(
        STATE_DIM,
        ACTIONS_TOTAL,
        scope="target_q")

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        deep_q_learning(
            sess=sess,
            env=env,
            q_estimator=q_estimator,
            target_estimator=target_estimator,
            experiment_dir=experiment_dir,
            num_steps=500000,
            replay_memory_size=10000,
            epsilon_decay_steps=100000,
            epsilon_start=0.5,
            epsilon_end=0.1,
            update_target_estimator_every=1000,
            update_q_values_every=4,
            batch_size=32,
            restore=False)

    env.close()


if __name__ == "__main__":
    main()
