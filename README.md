# ECS RideSharing Research

## Project Setup

#### Running on ECS's linux server
*Windows users: Consider installing [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) to ssh into the server.*
1. `ssh` into `linuxproj.ecs.soton.ac.uk` with your university username and password.
2. Clone the repository.
3. Navigate to root folder of project.
4. Run `./scripts/setup_env.sh`<br/>


#### Running on Personal Machine
*Windows users: [Set up](https://docs.microsoft.com/en-us/windows/wsl/install-win10) WSL so that bash scripts can be run.*
1. Ensure that Python 3.4.x or above is already installed.
2. Clone the repository.
3. In the `setup_env.sh`, change `python3` to `<path/to/python_interpreter>`, or `<python_interpreter>` if your python interpreter was added to `PATH` variable. </br>
4. Navigate to root folder of project.
5. Run `./scripts/setup_env.sh`

## Running the simulation
1. Navigate to the root folder of this project.
2. Specify parameters in `config.yaml`.
3. Run `source ./env/ride_sharing/bin/activate`
4. Run `python3 scripts/run_simulation.py`.
5. View the outputs in the `simulation_output` folder.

## Dataset
The dataset used to generate the transport network graph is the [Naptan Dataset](#https://data.gov.uk/dataset/ff93ffc1-6656-47d8-9155-85ea0b8f2251/national-public-transport-access-nodes-naptan) which consists of all public transport access points within the United Kingdom. Only bus stops are considered in this project, and the following bus stop properties are utilised:

- ATCOCode: The unique identifier for a stop.
- LocalityName: Locality (or cluster in our project) of a stop.
- Latitude: Latitude of a stop.
- Longitude: Longitude of a stop.

## Modifying config.yaml

Refer to [config.yaml](https://github.com/MaxOng99/ECS-Ridesharing/blob/main/config.yaml) for the structure of the configuration file. There are a few important things to take note:
1. [optimiser_params](#optimiser_params) takes a list of algorithms with their specified parameters.
2. const_params consists of [graph_params](#graph_params) and [passenger_params](#passenger_params) that will be constant throughout the experiment.
3. `var_param` consist of **only one parameter, from one parameter type (`graph_params` or `passenger_params`)**
4. For each algorithm (and their parameters) - variable parameter value combination, a separate configuration will be constructed, which can then be used to run an instance of a simulation. For example, if 2 algorithms and 4 variable parameter values are specified, there are a total of 8 simulation instances. Each of the 8 instances will have a different variable parameter, different optimiser, but the same const params.

There are four types of parameters, each of which are explained below:
#### experiment_params:
- `name: string`

    *Name of the experiment.*

- `runs: int`

    *Number of runs for each instance of a simulation.*

- `passenger_seed: int`

    *If there `runs > 1`, for the ith run, the seed used to generate passengers will be `passenger_seed + i`.*

- `algorithm_seed: int`

    *Seed value used to construct algorithms.*

#### graph_params
- `locality: "Westminster" | "Hackney" `

	*Represents the LocalityName as defined in the Naptan Dataset.*
- `num_locations: int`

	*The number of locations for*

- `avg_vehicle_speed: float`

	*The average bus speed when travelling between stations within a locality.*

#### passenger_params
- `num_passengers: int`

	*Number of riders for the 24 hours bus service.*
- `peak_probability: float`

	*The probability [0, 1] in which a rider travels during peak hours. There are 2 peak time frames, morning peak: [420, 560] and evening peak: [1020, 1140]. If a rider travels during peak hours, there is a 0.5 probability of travelling in the morning peak, or in the evenig peak*.

- `num_hotspots: int`

	*Number of hotspots within a locality. `num_hotspots` will first be sampled from locations of the specified `locality`. Then, `num_hotspots // 2` (division without remainder) hotspot locations will be allocated to the morning peak, while `num_hotspots - (num_hotspots // 2)` hotspot locations will be allocated to the evening peak. This means that if a passenger falls under either morning or evening peak (via `peak_probability` parameter), their departure and arrival locations will be sampled from the associated hotspot locations for each peak time frame, with uniform distribution.*

- `alpha`

	*Alpha parameter for beta distribution*

- `beta`

	*Beta parameter for beta distribution*
#### optimiser_params

- `algorithm: RGA | RGA ++ | IV2 `

- `algorithm_params: dictionary of key-value pairs`:

	**RGA**
		1. objective: gini_index | utilitarian
		2. multiple_iterations: True | False

	**RGA ++**
		1. objective: gini_index | utilitarian
		2. multiple_iterations: True | False

	**IV2**
		1. iterative_voting_rule: borda_count | popularity | harmonic | instant_runoff
		2. multiple_iterations: True | False

