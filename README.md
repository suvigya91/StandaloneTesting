# StandaloneTesting
Tests the proper deployment of different kernals (Amber, Coco, Gromacs, LSDmap) on the remote machine (Stampede)


# Code sample
## To create Blackbox handler for:

1. Amber: Required variables to be set:
	Blackbox (name = <name_of_kernel>,
			resource = <name_of_remote_supercomputer>)

2. Coco: Required variable to be set:
	Blackbox (name = <name_of_kernel>,
			resource = <name_of_remote_supercomputer>,
			grid = <number_of_grids>,
			dims = <number of dims>,
			num_CUs = <number_of_compute_units>,
			atom = <name_of_Atom>)

	default values if above variables are not set for Coco:
		grid = 5
		dims = 3
		num_CUs = 4
		atom = protein


## To execute the test, call
1. Copy the input files specific to Kernel in user_input. Required input files for:
	a. Amber:
		1. min.in
		2. min.inf
		3. md.crd
		4. topfile = penta.top
		5. penta.crd
		6. min.crd

	b. Coco:
		1. topfile = penta.top
		2. *.ncdf

2. For execution, call: 
	Blackbox.run()


## Available Kernels:
	1. Amber
	2. Coco
