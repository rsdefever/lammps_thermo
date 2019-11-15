# Ryan DeFever
# Maginn Research Group
# University of Notre Dame
# 2019 Nov 15

import numpy as np
import pickle
import h5py
import time

class LAMMPSThermo:
    """Extract and manipulate thermodynamic information
    from a LAMMPS log file
    """

    def __init__(self,filename,start_keyword='Step',end_keyword='Loop',
            skip_sections=0):
        """Create the LAMMPSThermo object

        Thermo data can be read from a LAMMPS log file or a pickle
        or HDF5 file which contains a previously created LAMMPSThermo
        object.

        Parsing a LAMMPS logfile: 'start_keyword' specifies the first
        word on the header line prior to the start of the thermo data.
        If there are multiple sections of thermo data (i.e., from multiple
        simulations performed within a single input script) in the logfile,
        the 'skip_sections' parameter can be used to skip N sections of thermo
        data. This parameter can also be used if the 'start_keyword' appears
        as the first word on a line(s) of the logfile prior to the actual
        thermo data section. The 'end_keyword' parameter should be set to None
        if the simulation has not completed by the end of the logfile --
        i.e., the final line of the log file is still thermo data.

        Parameters
        ----------
        filename : string
            Name of the file to read. Normally a LAMMPS logfile
            but could be a pickle (.pickle,.pkl) or hdf5
            (.hdf5,.hf5,.hdf) file containing a previously created
            LAMMPSThermo object
        start_keyword  : string, optional
            First word on the header line before the
            thermo data of interest
        end_keyword : string, optional
            First word on the line following the
            thermo data of interest. Set to None if the
            LAMMPS simulation has not completed (or if the
            last line of the log file is still thermo data
            for any reason)
        skip_sections : int, optional
            Number of sections of thermo data
            to skip before reading in data

        Attributes
        ----------
        header_map : Dict
            Dictionary that maps between the header name
            (i.e., from the lammps 'thermo_style' command
            and the column number
        data : np.ndarray
            The thermo data
        filename : the filename where the data was read from

        """

        self.filename = filename

        hdf5_extensions = ['.hdf5','.hf5','.hdf']
        pickle_extensions = ['.pickle','.pkl']

        if self.filename.endswith(tuple(pickle_extensions)):
            self.header_map, self.data = self._load_pickle()
        elif self.filename.endswith(tuple(hdf5_extensions)):
            self.header_map, self.data = self._load_hdf5()
        else:
            self.header_map, self.data = self._read_lammps_log(
                    start_keyword,end_keyword,skip_sections)

    def prop(self,props,tstart=None,tend=None):
        """Extracts the desired property(ies)

        Parameters
        ----------
        props : string or list
            Name (or list of names) of thermo property(ies) to extract.
            This (these) should match the keywords used in the lammps
            'thermo_style' command.
        tstart : float, optional
            Starting time to return thermo properties
        tend : float, optional
            Ending time to return thermo properties

        Returns:
        --------
        requested_props : np.ndarray, shape=(self.data.shape[0],len(props))

        """

        if isinstance(props,str):
            props = [props]
        elif not isinstance(props,list):
            raise ValueError("props must be a string (single property) or "
                    "a list of strings (multiple properties)")

        if tstart is not None or tend is not None:
            if 'Time' not in self.header_map.keys():
                raise ValueError("tstart and tend parameters only supported "
                                 "if 'Time' data is present.")
            if tstart is not None and tend is not None:
                if tstart > tend:
                    raise ValueError("tstart = {} is greater "
                            "than tend = {}".format(tstart,tend))
        for prop in props:
            if prop not in self.header_map.keys():
                raise ValueError("Selected property {} does not exist in the "
                        "LAMMPSThermo object. Available choices are: "
                        "{}".format(prop,self.header_map.keys()))

        if tstart is not None:
            try:
                col = self.header_map['Time']
                idx_start = np.where(self.data[:,col] >= tstart)[0][0]
            except IndexError:
                raise IndexError("tstart = {} appears to be greater than "
                                 "any time. Check your choice and units"
                                 .format(tstart))
        else:
            idx_start = None
        if tend is not None:
            try:
                col = self.header_map['Time']
                idx_end = np.where(self.data[:,col] <= tend)[0][-1] + 1
            except IndexError:
                raise IndexError("tend = {} appears to be less than "
                                 "any time. Check your choice and units"
                                 .format(tend))
        else:
            idx_end = None

        requested_props = np.empty(shape=(self.data.shape[0],0))
        for prop in props:
            add_prop = self.data[:,self.header_map[prop]].reshape(-1,1)
            requested_props = np.hstack((requested_props,add_prop))

        return requested_props[idx_start:idx_end]

    def available_props(self):
        return list(self.header_map.keys())

    def save_pickle(self,outname):
        with open(outname,'wb') as pf:
            pickle.dump(self,pf)

    # TODO: Write error handling for bad pickle file
    def _load_pickle(self):
        with open(self.filename,'rb') as pf:
            old = pickle.load(pf)
        return old.header_map, old.data

    def save_hdf5(self,outname):
        with h5py.File(outname,'w') as h5f:
            dataset = h5f.create_dataset('lammps_thermo',data=self.data)
            for key,val in self.header_map.items():
                dataset.attrs[key] = val

    # TODO: Write error handling for incorrectly formatted hdf5
    def _load_hdf5(self):
        with h5py.File(self.filename,'r') as h5f:
            dataset = h5f['lammps_thermo']
            data = dataset[:]
            header_map = {}
            for header,col in dataset.attrs.items():
                header_map[header] = col

        assert len(header_map) == data.shape[1],\
                "Mismatch between number of columns in the dataset "\
                "and the number of key-value pairs as dataset attributes."

        return header_map, data

    def _read_lammps_log(self,start_keyword,end_keyword,
            skip_sections):
        """Reads a lammps logfile and extracts thermo information

        Parameters
        ----------
        start_keyword : string
            First word on the header line before the
            thermo data of interest
        end_keyword : string, optional
            First word on the line following the
            thermo data of interest

        Returns:
        --------
        extracted_data : np.ndarray
        col_map : dict

        """

        print("Extracting LAMMPS thermo info from: {}".format(self.filename))
        log_data = []
        found_sections = 0
        start = time.time()
        with open(self.filename) as log_file:
            for i,line in enumerate(log_file):
                line_list = line.strip().split()
                log_data.append(line_list)
                try:
                    if line_list[0] == start_keyword:
                        start_idx = i
                        found_sections += 1
                    if line_list[0] == end_keyword and \
                       found_sections > skip_sections:
                        end_idx = i
                        break
                except IndexError:
                    continue
        end = time.time()
        print("Time to scan file: {}, {} lines/sec".format(end-start,len(log_data)/(end-start)))
        # Make sure we found starting and ending indices
        try:
            start_idx
        except NameError:
            raise NameError('Keyword {} not found in LAMMPS log file'.format(
                start_keyword))
        if end_keyword is not None:
            try:
                end_idx
            except NameError:
                raise NameError("Ending keyword '{}' not found in "
                        "LAMMPS log file. If the last line of the "
                        "log file still contains thermo data use the "
                        "'end_keyword=None' option".format(end_keyword))
        else:
            end_idx = i

        n_lines = end_idx - start_idx
        assert n_lines > 0

        # Extract column headers and create dictionary to map
        # thermo property name to column index
        col_headers = log_data[start_idx]
        col_map = { prop : i for i,prop in enumerate(col_headers) }

        # Extract data into numpy array
        start = time.time()
        extracted_data = np.asarray(log_data[start_idx+1:end_idx],dtype=np.float64)
        end = time.time()
        print("Time to load numpy array: {}".format(end-start))

        return col_map, extracted_data


