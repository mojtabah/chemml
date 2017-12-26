import os
import sys
import pandas as pd
import numpy as np
import warnings
import fnmatch

from ..utils.utilities import std_datetime_str


def Merge(X1, X2):
    """
    todo: add more functionality for header overlaps
    Merge same length data frames.

    :param X1: pandas data frame
        first data frame
    :param X2: pandas data frame
        second data frame
    :return: pandas data frame
    """
    if not isinstance(X1,pd.DataFrame) or not isinstance(X2,pd.DataFrame):
        msg = 'both X1 and X2 must be pandas dataframe'
        raise TypeError(msg)
    if X1.shape[0] != X2.shape[0]:
        msg= 'Two input data frames should be in the same length'
        raise ValueError(msg)
    X = X1.join(X2,lsuffix='_X1',rsuffix='_X2')
    return X

class Split(object):
    """
    split data frame by columns

    :param: select: integer or list (default = 1)
        integer: number of columns to be selected from the first of data as first data frame (X1)
        list: list of headers to be selected as first data frame (X1)
    :return: two pandas data frame: X1 and X2
    """
    def __init__(self,selection=1):
        self.selection = selection

    def fit(self,X):
        """
        fit the split task to the input data frame

        :param X:  pandas data frame
        original pandas data frame
        :return: two pandas data frame: X1 and X2
        """
        if not isinstance(X,pd.DataFrame):
            msg = 'X must be a pandas dataframe'
            raise TypeError(msg)
        if isinstance(self.selection,list):
            X1 = X.loc[:,self.selection]
            X2 = X.drop(self.selection,axis=1)
        elif isinstance(self.selection,int):
            if self.selection >= X.shape[1]:
                msg = 'The first output data frame is empty, because passed a bigger number than actual number of columns'
                warnings.warn(msg)
            X1 = X.iloc[:,:self.selection]
            X2 = X.iloc[:,self.selection:]
        else:
            msg = "selection parameter must ba a list or an integer"
            raise TypeError(msg)
        return X1, X2

class XYZreader(object):
    """ (XYZreader)
    Read molecules' geometry (cartesian coordinates) from one or more XYZ files.

    Parameters
    ----------
    path_pattern: string or list of string
        A pattern or a list of patterns. Each pattern consists of file name and path.
        The pattern can contain any special character in the following list:

            *       : matches everything (zero or more characters)
            ?       : matches any single character
            [seq]   : matches any character in seq
            [!seq]  : matches any character not in seq
            /       : filename seperator

        Note: seq can indicate a range of characters by giving two characters and separating them by a '-'.
              However, the range is limited to a single character. That's why this parameter also accept a list of
              patterns for different length of characters. For example, range(1,30) = '[1-9]' and '[1-9][0-9]'

        The pattern matching is implemented by fnmatch library- Unix filename pattern matching.
        Note: The pattern must include the extension at the end. The only acceptable extension is '.xyz'.

    path_root: string, optional (default = None)
        fixed (with no special character) part of the path.
        If path is None, this function tries to open the file as a single
        file (without any pattern matching). It is a fixed path to subdirectories
        or files. Therefore, none of the above special characters except '/'
        can be used.
        If not None, it determines the path that this function walk through
        and look for every file that matches the pattern in the file name. To start
        walking from the curent directory, the path value should be '.'

    Z: dictionary
        A dictionary of nuclear charges with respect to the chemical symbols of all atom types in the xyz files.

    reader: string, optional (default = 'auto')
        Available options : 'auto' and 'manual'
        If 'auto', the openbabel readstring function creat the molecule object.
        The type of files for openbabel class has been set to 'xyz', thus the format
        of the file should also follow a typical xyz format. However, with 'manual'
        reader you can skip some lines from top or bottom of xyz files.

    skip_lines: list of two integers, optional (default = [2,0])
        Number of lines to skip (int) from top and bottom of the xyz files, respectively.
        Based on the original xyz format only 2 lines from top and zero from
        bottom of a file can be skipped. Thus, number of atoms in the first line
        can also be ignored.
        Only available for 'manual' reader.

    Attributes
    ----------
    max_n_atoms: integer
        Maximum number of atoms in one molecule.
        This can be useful if you want to set this parameter in the feature representation methods
        like Coulomb_Matrix.

    Examples
    --------
        (1)
        file: 'Mydir/1f/1_opt.xyz'
        path: None
        >>> one file will be read: 'Mydir/1f/1_opt.xyz'

        (2)
        file: '[1,2,3,4]?/*_opt.xyz'
        path: 'Mydir'
        >>> sample files to be read: 'Mydir/1f/1_opt.xyz', 'Mydir/2c/2_opt.xyz', ...

        (3)
        file: '[!1,2]?/*_opt.xyz'
        path: '.'
        >>> sample files to be read: './3f/3_opt.xyz', 'Mydir/7c/7_opt.xyz', ...

        (4)
        file: '*['f','c']/*_opt.xyz'
        path: 'Mydir'
        >>> sample files to be read: 'Mydir/1f/1_opt.xyz', 'Mydir/2c/2_opt.xyz', ...

        (5)
        file: '[%s]?/[!%s]_opt.xyz'
        path: 'Mydir/all'
        arguments: 1,4,7,10
        >>> sample files to be read: 'Mydir/all/1f/1_opt.xyz', 'Mydir/all/2c/2_opt.xyz', ...
    """
    def __init__(self, path_pattern, path_root=None, Z = {'Ru': 44.0, 'Re': 75.0, 'Rf': 104.0, 'Rg': 111.0, 'Ra': 88.0, 'Rb': 37.0, 'Rn': 86.0, 'Rh': 45.0, 'Be': 4.0, 'Ba': 56.0, 'Bh': 107.0, 'Bi': 83.0, 'Bk': 97.0, 'Br': 35.0, 'H': 1.0, 'P': 15.0, 'Os': 76.0, 'Es': 99.0, 'Hg': 80.0, 'Ge': 32.0, 'Gd': 64.0, 'Ga': 31.0, 'Pr': 59.0, 'Pt': 78.0, 'Pu': 94.0, 'C': 6.0, 'Pb': 82.0, 'Pa': 91.0, 'Pd': 46.0, 'Cd': 48.0, 'Po': 84.0, 'Pm': 61.0, 'Hs': 108.0, 'Uup': 115.0, 'Uus': 117.0, 'Uuo': 118.0, 'Ho': 67.0, 'Hf': 72.0, 'K': 19.0, 'He': 2.0, 'Md': 101.0, 'Mg': 12.0, 'Mo': 42.0, 'Mn': 25.0, 'O': 8.0, 'Mt': 109.0, 'S': 16.0, 'W': 74.0, 'Zn': 30.0, 'Eu': 63.0, 'Zr': 40.0, 'Er': 68.0, 'Ni': 28.0, 'No': 102.0, 'Na': 11.0, 'Nb': 41.0, 'Nd': 60.0, 'Ne': 10.0, 'Np': 93.0, 'Fr': 87.0, 'Fe': 26.0, 'Fl': 114.0, 'Fm': 100.0, 'B': 5.0, 'F': 9.0, 'Sr': 38.0, 'N': 7.0, 'Kr': 36.0, 'Si': 14.0, 'Sn': 50.0, 'Sm': 62.0, 'V': 23.0, 'Sc': 21.0, 'Sb': 51.0, 'Sg': 106.0, 'Se': 34.0, 'Co': 27.0, 'Cn': 112.0, 'Cm': 96.0, 'Cl': 17.0, 'Ca': 20.0, 'Cf': 98.0, 'Ce': 58.0, 'Xe': 54.0, 'Lu': 71.0, 'Cs': 55.0, 'Cr': 24.0, 'Cu': 29.0, 'La': 57.0, 'Li': 3.0, 'Lv': 116.0, 'Tl': 81.0, 'Tm': 69.0, 'Lr': 103.0, 'Th': 90.0, 'Ti': 22.0, 'Te': 52.0, 'Tb': 65.0, 'Tc': 43.0, 'Ta': 73.0, 'Yb': 70.0, 'Db': 105.0, 'Dy': 66.0, 'Ds': 110.0, 'I': 53.0, 'U': 92.0, 'Y': 39.0, 'Ac': 89.0, 'Ag': 47.0, 'Uut': 113.0, 'Ir': 77.0, 'Am': 95.0, 'Al': 13.0, 'As': 33.0, 'Ar': 18.0, 'Au': 79.0, 'At': 85.0, 'In': 49.0},
              reader='auto', skip_lines=[2, 0]):
        self.path_pattern = path_pattern
        self.path_root = path_root
        self.Z = Z
        self.reader = reader
        self.skip_lines = skip_lines

    def __file_reader(self, filename):
        if self.reader == 'auto':
            # sys.path.insert(0, "/user/m27/pkg/openbabel/2.3.2/lib")
            # import pybel
            # import openbabel
            mol = open(filename, 'r').read()
            # mol = pybel.readstring("xyz", mol)
            molecule = [(a.OBAtom.GetAtomicNum(), a.OBAtom.x(), a.OBAtom.y(), a.OBAtom.z()) for a in mol.atoms]
            return np.array(molecule)
        elif self.reader == 'manual':
            mol = open(filename, 'r').readlines()
            if len(mol) == 0:
                return np.array([])
            mol = mol[self.skip_lines[0]:len(mol) - self.skip_lines[1]]
            molecule = []
            for atom in mol:
                atom = atom.replace('\t', ' ')
                atom = atom.strip().split(' ')
                atom = list(filter(lambda x: x != '', atom))
                molecule.append([self.Z[atom[0]], float(atom[1]), float(atom[2]), float(atom[3])])
            return np.array(molecule)

    def read(self):
        """
        read the XYZ files based on the path_pattern and path_root parameters and create the output ductionary.

        Return
        ------
        molecules: dictionary
            dictionary of molecules with ['mol', 'file'] keys
            The value of 'file' is the name and path of the file that was read to create the molecule.
            The value of 'mol' is the numpy array of 4 values for each atom in the molecule. The four values are
             nuclear charge, X-coordinate, Y-coordinate, and Z-coordinate, respectively.
        """
        if isinstance(self.path_pattern, str):
            self.path_pattern = [self.path_pattern]

        molecules = {}
        mols = []
        it = 0
        max_nAtoms = 1
        for pattern in self.path_pattern:
            file_name, file_extension = os.path.splitext(pattern)
            if file_extension == '':
                msg = 'file extension not indicated'
                raise ValueError(msg)
            elif file_extension != '.xyz':
                msg = "file extension '%s' not available - xyz is the only acceptable extension" % file_extension
                raise ValueError(msg)

            if self.path_root:
                for root, directories, filenames in os.walk(self.path_root):
                    file_path = [os.path.join(root, filename) for filename in filenames]
                    for fn in fnmatch.filter(file_path, os.path.join(self.path_root, pattern)):
                        mol = self.__file_reader(fn)
                        max_nAtoms = max(max_nAtoms, len(mol))
                        it+=1
                        molecules[it] = {'file':fn, 'mol': mol}
                        mols.append(mol)
            else:
                mol = self.__file_reader(file_name)
                max_nAtoms = max(max_nAtoms, len(mol))
                it += 1
                molecules[it] = {'file': file_name, 'mol': mol}
        self.max_n_atoms = max_nAtoms
        return molecules

class SaveFile(object):
    """
    Write DataFrame to a comma-seprated values(csv) file
    :param: output_directory: string, the output directory to save output files

    """
    def __init__(self, filename, output_directory = None, record_time = False, format ='csv',
                 index = False, header = True):
        self.filename = filename
        self.record_time = record_time
        self.output_directory = output_directory
        self.format = format
        self.index = index
        self.header = header

    def fit(self, X, main_directory='.'):
        """
        Write DataFrame to a comma-seprated values (csv) file
        :param: X: pandas DataFrame
        :param: main_directory: string, if there is any main directory for entire cheml project
        :return: nothing
        """
        if not isinstance(X, pd.DataFrame):
            msg = 'X must be a pandas dataframe'
            raise TypeError(msg)

        if self.output_directory:
            self.output_directory = main_directory + '/' + self.output_directory
            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory)
            if self.record_time:
                self.file_path = '%s/%s_%s.%s'%(self.output_directory, self.filename,std_datetime_str(),self.format)
                X.to_csv(self.file_path, index=self.index, header = self.header)
            else:
                self.file_path = '%s/%s.%s' % (self.output_directory, self.filename,self.format)
                X.to_csv(self.file_path, index=self.index, header = self.header)
        else:
            if self.record_time:
                self.file_path = '%s/%s_%s.%s'%(main_directory,self.filename,std_datetime_str(),self.format)
                X.to_csv(self.file_path, index=self.index, header = self.header)
            else:
                self.file_path = '%s/%s.%s' %(main_directory,self.filename,self.format)
                X.to_csv(self.file_path, index=self.index, header = self.header)

class StoreFile(object):
    """
    Write everything in to a text file
    :param: output_directory: string, the output directory to save output files

    """
    def __init__(self, filename, output_directory = None, record_time = False, format ='txt'):
        self.filename = filename
        self.record_time = record_time
        self.output_directory = output_directory
        self.format = format

    def fit(self, X, main_directory='.'):
        """
        Write DataFrame to a comma-seprated values (csv) file
        :param: X: pandas DataFrame
        :param: main_directory: string, if there is any main directory for entire cheml project
        :return: nothing
        """

        if self.output_directory:
            self.output_directory = main_directory + '/' + self.output_directory
            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory)
            if self.record_time:
                self.file_path = '%s/%s_%s.%s'%(self.output_directory, self.filename,std_datetime_str(),self.format)
            else:
                self.file_path = '%s/%s.%s' % (self.output_directory, self.filename,self.format)
        else:
            if self.record_time:
                self.file_path = '%s/%s_%s.%s'%(main_directory,self.filename,std_datetime_str(),self.format)
            else:
                self.file_path = '%s/%s.%s' %(main_directory,self.filename,self.format)
        with open(self.file_path, 'a') as file:
            file.write('%s\n' % str(X))

def slurm_script(block):
    """(slurm_script):
        if part of your code must be run on a cluster and you need to make a slurm
        script for that purpose, this function helps you to do so.

    Parameters
    ----------
    style: string, optional(default=exclusive)
        Available options:
            - exclusive : makes the slurm script based on exclusive selection of cores per nodes.

    nnodes: int, optional(default = 1)
        number of available empty nodes in the cluster.

    input_slurm_script: string, optional(default = None)
        The file path to the prepared slurm script. We also locate place of
        --nodes and -np in the script and make sure that provided numbers are
        equal to number of nodes(nnodes). Also, the exclusive option must be
        included in the script to have access to an entire node.

    output_slurm_script: string, optional(default = 'script.slurm')
        The path and name of the slurm script file that will be saved after
        changes by this function.

    Returns
    -------
    The function will write a slurm script file with the filename passed by
    output_slurm_script.

    """
    style = block['parameters']['style'][1:-1]
    pyscript_file = cmlnb["file_name"]
    nnodes = int(block['parameters']['nnodes'])
    input_slurm_script = block['parameters']['input_slurm_script'][1:-1]
    output_slurm_script = block['parameters']['output_slurm_script'][1:-1]

    cmlnb["run"] = "# how to run: sbatch %s" % output_slurm_script

    if style == 'exclusive':
        if input_slurm_script != 'None':
            file = ['#!/bin/sh\n', '#SBATCH --time=99:00:00\n', '#SBATCH --job-name="nn"\n',
                    '#SBATCH --output=nn.out\n', '#SBATCH --clusters=chemistry\n', '#SBATCH --partition=beta\n',
                    '#SBATCH --account=pi-hachmann\n', '#SBATCH --exclusive\n', '#SBATCH --nodes=1\n', '\n',
                    '# ====================================================\n', '# For 16-core nodes\n',
                    '# ====================================================\n', '#SBATCH --constraint=CPU-E5-2630v3\n',
                    '#SBATCH --tasks-per-node=1\n', '#SBATCH --mem=64000\n', '\n', '\n',
                    'echo "SLURM job ID         = "$SLURM_JOB_ID\n',
                    'echo "Working Dir          = "$SLURM_SUBMIT_DIR\n', 'echo "Temporary scratch    = "$SLURMTMPDIR\n',
                    'echo "Compute Nodes        = "$SLURM_NODELIST\n', 'echo "Number of Processors = "$SLURM_NPROCS\n',
                    'echo "Number of Nodes      = "$SLURM_NNODES\n', 'echo "Tasks per Node       = "$TPN\n',
                    'echo "Memory per Node      = "$SLURM_MEM_PER_NODE\n', '\n', 'ulimit -s unlimited\n',
                    'module load intel-mpi\n', 'module load python\n', 'module list\n',
                    'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/projects/hachmann/packages/Anaconda:/projects/hachmann/packages/rdkit-Release_2015_03_1:/user/m27/pkg/openbabel/2.3.2/lib\n',
                    'date\n', '\n', '\n', 'echo "Launch job"\n', 'export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so\n',
                    'export I_MPI_FABRICS=shm:tcp\n', '\n', 'mpirun -np 2 python test.py\n']
            file[8] = '#SBATCH --nodes=%i\n' % nnodes
            file[-1] = 'mpirun -np %i python %s\n' % (nnodes, pyscript_file)
        else:
            file = open(input_slurm_script, 'r')
            file = file.readlines()
            exclusive_flag = False
            nodes_flag = False
            np_flag = False
            for i, line in enumerate(file):
                if '--exclusive' in line:
                    exclusive_flag = True
                elif '--nodes' in line:
                    nodes_flag = True
                    ind = line.index('--nodes')
                    file[i] = line[:ind] + '--nodes=%i\n' % nnodes
                elif '-np' in line:
                    np_flag = True
                    ind = line.index('--nodes')
                    file[i] = line[:ind] + '--nodes=%i\n' % nnodes
            if not exclusive_flag:
                file = file[0] + ['#SBATCH --exclusive\n'] + file[1:]
                msg = "The --exclusive option is not available in the slurm script. We added '#SBATCH --exclusive' to the first of file."
                warnings.warn(msg, UserWarning)
            if not nodes_flag:
                file = file[0] + ['#SBATCH --nodes=%i\n' % nnodes] + file[1:]
                msg = "The --nodes option is not available in the slurm script. We added '#SBATCH --nodes=%i' to the first of file." % nnodes
                warnings.warn(msg, UserWarning)
            if not np_flag:
                file.append('mpirun -np %i python %s\n' % (nnodes, pyscript_file))
                msg = "The -np option is not available in the slurm script. We added 'mpirun -np %i python %s'to the end of file." % (
                nnodes, pyscript_file)
                warnings.warn(msg, UserWarning)

        script = open(output_slurm_script, 'w')
        for line in file:
            script.write(line)
        script.close()

