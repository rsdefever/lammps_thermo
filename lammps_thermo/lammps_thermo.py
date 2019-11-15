# Ryan DeFever
# Maginn Research Group
# University of Notre Dame
# 2019 Nov 15

import numpy as np
import time

class LAMMPSThermo:
    """Extract and manipulate thermodynamic information
    from a LAMMPS log file
    """

    def __init__(self,filename,start_keyword='Step',end_keyword='Loop',
            skip_sections=0,incomplete=False):
        """Create the LAMMPSThermo object

        Parameters
        ----------
        filename : string 
            Name of the LAMMPS logfile
        start_keyword  : string, optional
            First word on the header line before the
            thermo data of interest
        end_keyword : string, optional
            First word on the line following the
            thermo data of interest
        skip_sections : int, optional
            Number of sections of thermo data
            to skip before reading in data

        Returns:
        --------
        thermo_data : LAMMPSThermo
            Structure with thermo data extracted
            from lammps log file

        """

        self.filename = filename

        self.header_map, self.data = self._read_thermo_data(
                start_keyword,end_keyword,skip_sections,incomplete)

    def extract_props(self,props):
        """Extracts the desired property

        Parameters
        ----------
        props : string or list
            Name (or list of names) of thermo property(ies) to extract. 
            This (these) should match the keywords used in the lammps
            'thermo_style' command.

        Returns:
        --------
        requested_props : np.ndarray, shape=(self.data.shape[0],len(props))

        """

        if isinstance(props,str):
            props = [props]
        elif not isinstance(props,list):
            raise ValueError("props must be a string (single property) or "
                    "a list of strings (multiple properties)")

        for prop in props:
            if prop not in self.header_map.keys():
                raise ValueError("Selected property {} does not exist in the "
                        "LAMMPSThermo object. Available choices are: "
                        "{}".format(prop,self.header_map.keys()))

        requested_props = np.empty(shape=(self.data.shape[0],0))
        for prop in props:
            add_prop = self.data[:,self.header_map[prop]].reshape(-1,1)
            requested_props = np.hstack((requested_props,add_prop))

        return requested_props

    def available_props(self):
        return list(self.header_map.keys())

    def _read_thermo_data(self,start_keyword,end_keyword,
            skip_sections,incomplete):
        """Reads filename and extracts thermo information

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
                    if line_list[0] == end_keyword:
                        end_idx = i
                        if found_sections > skip_sections:
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
        if not incomplete:
            try:
                end_idx
            except NameError:
                raise NameError('Ending keyword {} not found in'
                        'LAMMPS log file'.format(end_keyword))
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


