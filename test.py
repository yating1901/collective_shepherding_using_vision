

from simulation import Simulation

simulation = Simulation(N=20,  # Number of agents in the environment
                        T=2500,  # Simulation timesteps
                        width=500,  # Arena width in pixels
                        height=500,  # Arena height in pixels
                        agent_radius=10)  # Agent radius in pixels

# we loop through all the agents of the created simulation
print("Setting parameters for agent", end = ' ')

for agent in simulation.agents:
    print(f"{agent.id}", end=', ')

    # changing angular noise (sigma)
    agent.noise_sig = 0.1

    # changing their default flocking parameters
    agent.s_att = 0.02  # attraction strength (AU)
    agent.s_rep = 5  # repulsion strength (AU)
    agent.s_alg = 10  # alignment strength (AU)

    agent.r_att = 200  # attraction range (px)
    agent.r_rep = 50  # repulsion range (px)
    agent.r_alg = 100  # alignment range (px)

    agent.steepness_att = -0.5  # steepness in attraction force calculation (sigmoid)
    agent.steepness_rep = -0.5  # steepness in repulsion force calculation (sigmoid)
    agent.steepness_alg = -0.5  # steepness in alignment force calculation (sigmoid)

    # changing maximum velocity and simulation timesteps
    agent.v_max = 2
    agent.dt = 0.05

# Now we can start the simulation with the changed agents
simulation.start()