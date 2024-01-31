## Beginnings of a CMD line interface
import argparse

__arguments = None

#Arguments in the form: 

def __parse() -> None:
	global __arguments

	parser = argparse.ArgumentParser()

	# Required Arguments
	#parser.add_argument('COORDS_1', help='Absolute of relative path to the .csv file outputted from the stitching '
	#										'program.')
	
	# Optional arguments

	parser.add_argument('-v', '--verbose', action='store_true',
						help='Will print out the qibits and circuit as well as results from the simulation')

	__arguments = parser.parse_args()

def get(argument):
    """Retrieve the value of a defined argument. This will automatically parse the arguments if needed

    :param argument: a string containing the argument dest defined above
    :return: the argument value, in the defined type
    """
    if __arguments is None:
        __parse()
    return vars(__arguments)[argument]