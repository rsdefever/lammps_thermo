# Ryan DeFever
# Maginn Research Group
# University of Notre Dame
# 2019 Nov 15

class LAMMPSThermo:
    """Extract and manipulate thermodynamic information
    from a LAMMPS log file
    """

    def __init__(self,filename,start_keyword='Step',end_keyword='Loop',
            skip_sections=0):
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

        self.header_map, self.data = _read_thermo_data(filename,
                start_keyword,end_keyword,skip_sections)

    def _read_thermo_data(filename,start_keyword,end_keyword,
            skip_sections):
         """Reads filename and extracts thermo information

        Parameters
        ----------
        filename : string 
            Name of the LAMMPS logfile
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
        log_data = []
        with open(filename) as log_file:
            for line in log_file:
                log_data.append(line.strip().split())

        # Extract the relevant thermo data
        found_sections = 0
        for i,line in enumerate(log_data):
            try:
                if line[0] == start_keyword:
                    start_idx = i
                    found_sections += 1
                if line[0] == end_keyword:
                    end_idx = i
                    if found_sections > skip_sections:
                        break
            except IndexError:
                continue

        # Make sure we found starting and ending indices
        try:
            start_idx
        except NameError:
            raise NameError('Keyword {} not found in LAMMPS log file'.format(
                keyword))
        try:
            end_idx
        except NameError:
            raise NameError('Ending keyword {} not found in'
                    'LAMMPS log file'.format(end_keyword))

        n_lines = end_idx - start_idx
        assert n_lines > 0
        
        # Extract column headers and create dictionary to map
        # thermo property name to column index
        col_headers = data[start_idx]
        col_map = { prop : i for i,prop in enumerate(col_headers) }

        # Extract data into numpy array
        extracted_data = np.loadtxt(filen,skiprows=start_idx,max_rows=n_lines)

        return col_map, extracted_data

