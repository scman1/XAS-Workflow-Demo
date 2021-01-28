#!/usr/bin/perl

# All the tasks of the basic workflow can be performed in Demeter,
# this script shows how to do it.
# 
# The code for each task has been documented in the demeter programing guide
# Example derived from code published at:
#   https://bruceravel.github.io/demeter/documents/DPG

# First example of importing a Mu(e) data file and plotting it

use Demeter;
# 1.1. Import data         |File: fes2_rt01_mar02.xmu            | 
# 1.2. Normalisation       |Parameters:                          |
#                          |  Pre-edge range = -117.00 to 30.000 |
# 1.3. Save Athena Project |                                     |FeS2_dmtr.prj

sub start (){
	my $input_file = "fes2_rt01_mar02.xmu";
	my $group_name = "FeS2_xmu";

	# if no argument passed, show warning and use defaults
	
	if (!@ARGV or $#ARGV < 1) {
		print "Need two provide two argument\n - File name\n - Group name";
		print "Arguments passed: $#ARGV + 1";
	}
	else{
		my $test_argument = $ARGV[0];
		if (-e $test_argument) {
			print "Reading from file: $test_argument\n";
			$input_file = $test_argument;
			}
		else{
			print "Input file does not exist: $test_argument\n";
			print "Reading from default file: $input_file\n";
		}
		$group_name = $ARGV[1];
		print "Group Name: $group_name\n";
	}
	

	my $data = Demeter::Data -> new(file => $input_file,
									name => $group_name,
								);
	$data -> plot('E');
	sleep 5;
}

start()