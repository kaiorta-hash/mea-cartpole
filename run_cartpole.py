import time
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime
from mea_integration import IntegratedMEAInterface
from openai_integration import IntegratedOpenAIGymAPI
 
 
def save_episode_data(episode_steps, episode_rewards, timestamp):
    """Save episode data to a CSV file"""
    filename = f"cartpole_episode_data_{timestamp}.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Episode', 'Steps', 'Reward'])
        for i in range(len(episode_steps)):
            writer.writerow([i+1, episode_steps[i], episode_rewards[i]])
    print(f"Episode data saved to {filename}")
 
 
def plot_episode_data(episode_steps, episode_rewards, timestamp):
    """Plot episode steps and rewards"""
    plt.figure(figsize=(12, 5))
 
    plt.subplot(1, 2, 1)
    plt.plot(range(1, len(episode_steps)+1), episode_steps, marker='o')
    plt.title('Steps per Episode')
    plt.xlabel('Episode')
    plt.ylabel('Steps')
    plt.grid(True)
 
    plt.subplot(1, 2, 2)
    plt.plot(range(1, len(episode_rewards)+1), episode_rewards, marker='o', color='orange')
    plt.title('Reward per Episode')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.grid(True)
 
    plt.tight_layout()
    plt.savefig(f"cartpole_performance_{timestamp}.png")
    print(f"Performance plot saved to cartpole_performance_{timestamp}.png")
 
 
def run_integrated_dishbrain():
    """Run the integrated DishBrain experiment."""
    mea_interface = IntegratedMEAInterface()
 
    if not mea_interface.connect_to_device():
        print("Failed to connect to MEA device. Exiting.")
        return
 
    gym_api = None
 
    try:
        if not mea_interface.start_recording():
            print("Failed to start recording. Exiting.")
            return
 
        gym_api = IntegratedOpenAIGymAPI(mea_interface)
        episodes = 100
 
        episode_steps = []
        episode_rewards = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
 
        for episode in range(episodes):
            print(f"Starting Episode {episode + 1}/{episodes}")
            gym_api.initialize_training()
 
            done = False
            step_count = 0
 
            while not done:
                time.sleep(0.05)
                pole_angle, pole_angular_velocity, reward, terminated = gym_api.run_single_frame()
                mea_interface.stimulate_neurons(pole_angle, pole_angular_velocity, reward)
                done = terminated
                step_count += 1
 
                if step_count % 10 == 0:
                    print(f"Episode {episode + 1}, Step {step_count}, Reward so far: {gym_api.total_reward}")
 
            print(f"Episode {episode + 1} completed with total reward: {gym_api.total_reward}")
 
            episode_steps.append(step_count)
            episode_rewards.append(gym_api.total_reward)
 
            time.sleep(1.0)
 
        save_episode_data(episode_steps, episode_rewards, timestamp)
        plot_episode_data(episode_steps, episode_rewards, timestamp)
 
    except KeyboardInterrupt:
        print("\nExperiment interrupted by user.")
 
    except Exception as e:
        import traceback
        print(f"Error during experiment: {e}")
        traceback.print_exc()
 
    finally:
        mea_interface.disconnect()
        # BUG 14 FIX: close the Gym environment on exit
        # guarded by None check in case gym_api was never created
        if gym_api is not None:
            gym_api.env.close()
        print("Experiment completed.")
 
 
if __name__ == "__main__":
    run_integrated_dishbrain()