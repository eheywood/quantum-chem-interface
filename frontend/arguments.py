## Beginnings of a CMD line interface
import argparse

__arguments = None

#Arguments in the form: 

def __parse():
	global __arguments

	parser = argparse.ArgumentParser()

	# Required Arguments
	#parser.add_argument('COORDS_1', help='Absolute of relative path to the .csv file outputted from the stitching '
	#										'program.')
	
	# Optional arguments

	#parser.add_argument('-o', '--output', dest='OUTPUT_FILE', default='output.csv',
	#					help='Path to save the data to. This will create an output directory in the directory given.'
    #					 ' If this is omitted, the data will be outputted into output.csv in the current directory')

	__arguments = parser.parse_args()

def get(argument):
    """Retrieve the value of a defined argument. This will automatically parse the arguments if needed

    :param argument: a string containing the argument dest defined above
    :return: the argument value, in the defined type
    """
    if __arguments is None:
        __parse()
    return vars(__arguments)[argument]