import json
from dft_parameters import *
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

import os_navigation as os_nav
import subprocess
from typing import List, Dict
from job import *
from slurm_manager import jaguar_sub
import molecule as mol



# Define JobManager Class


