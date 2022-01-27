import pandas as pd

from params import params
from errors import DataAssignmentError, UnsupportedFieldName, UnsupportedValue, ValueDoesNotExist, MissingRequiredFieldError


class Sheet:
    """
    The base Sheet class.
    """
    def __init__(self, path, sheet_name):
        self.path = path
        self.sheet_name = sheet_name

        self.df = pd.read_excel(path, sheet_name=sheet_name)
        self.df.dropna(how='all', inplace=True)

        self.cols = self.df.columns

    def _skip_col(self, col, val):
        """
        Check if a column should be skipped.
        """
        # Check if val empty
        if pd.isna(val):
            return True

        # Check if col starts with '#'
        if col[0] == '#':
            return True

        return False

    def _standardize_field(self, field):
        """
        Convert a field to the standardized version (e.g., temperature --> temp).
        """
        for key in params:
            for param in params[key]:
                if field == param or field in params[key][param]['names']:
                    return param

        raise UnsupportedFieldName(field)

    def _check_required_cols(self, required_cols, cols, sheet_name):
        """
        Validate that all required columns are present.
        """
        for required_col in required_cols:
            if required_col in cols:
                continue

            required_col = required_col.replace('*', '')
            raise MissingRequiredFieldError(required_col, sheet_name)

    def _check_either_or_cols(self, either_or_cols, cols, sheet_name, message=""):
        """
        Validate that at least one of the either/or columns are present.
        """
        exists = False
        for either_or_col in either_or_cols:
            if either_or_col in cols:
                exists = True
                break
            
        if exists == False:
            raise MissingRequiredFieldError('quantity', sheet_name, message)

    def _parse_data(self, col_list, parsed_object, value, parsed_data, prop_params):
        """
        Parse a data column and attach to it'a appropriate parsed object.
        """
        # Check if data name exists in the data sheet
        if value not in parsed_data:
            raise ValueDoesNotExist(value, 'data')

        # Ensure the data is being applied to something
        if len(col_list) == 1:
            raise DataAssignmentError

        # Check if data should be applied to a property or condition
        prev_field = col_list[-2]
        if prev_field in prop_params:
            parent = parsed_object['prop'][prev_field]
        elif prev_field in params['cond']:
            parent = parsed_object['cond'][prev_field]
        else:
            raise DataAssignmentError

        parent['data'] = value

    def _parse_prop(self, col_list, field, value, parsed_object, prop_params):
        """
        Parse a property column with it's associated standard units and attributes.
        """
        # Create property dict
        parsed_object['prop'].update({
            field: {
                'attr': {},
                'data': {}
            }
        })

        parsed_object['prop'][field].update({'value': value})

        # Add property units
        unit = prop_params[field]['unit']
        if unit:
            parsed_object['prop'][field].update({'unit': unit})

        # Add property attributes
        if field in params['prop'] and len(col_list) > 1:
            parsed_object['prop'][col_list[-2]]['attr'].update({field: value})

    def _parse_cond(self, col_list, field, value, parsed_object):
        """
        Parse a condition column with it's associated standard units.
        """
        # Set parent to the parsed object or a property
        if len(col_list) == 1:
            parent = parsed_object
        else:
            parent = parsed_object['prop'][col_list[-2]]
        
        # Create condition dict
        if 'cond' in parent:
            parent['cond'].update({
                field: {
                    'data': {}
                }
            })
        else:
            parent['cond'] = ({
                field: {
                    'data': {}
                }
            }) 

        # Add condition value
        parent['cond'][field].update({'value': value})

        # Add condition units
        unit = params['cond'][field]['unit']
        if unit:
            parent['cond'][field].update({'unit': unit})


class ExperimentSheet(Sheet):
    """
    Experiment Excel sheet.
    """
    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self):
        # Validate required columns
        required_cols = ['*name']
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_experiment = {}
            for col in self.cols:
                # Define and clean value
                value = row[col]
                if isinstance(value, str):
                    value = value.strip()

                # Check if col should be skipped
                if self._skip_col(col, value) == True:
                    continue

                # Clean col
                col = col.replace('*', '')

                # Standardize col field
                col = self._standardize_field(col)

                # Populate parsed_experiment dict
                if col in params['experiment']:
                    parsed_experiment[col] = value

            self.parsed[row['*name'].strip()] = parsed_experiment

        return self.parsed


class DataSheet(Sheet):
    """
    Data Excel sheet.
    """
    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self, parsed_experiments):
        # Validate required columns
        required_cols = ['*name', '*type', '*path']
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_datum = {
                'base': {},
                'file': {},
                'cond': {}
            }
            for col in self.cols:
                # Define and clean value
                value = row[col]
                if isinstance(value, str):
                    value = value.strip()

                # Check if col should be skipped
                if self._skip_col(col, value) == True:
                    continue

                # Clean col and create col_list
                col = col.replace('*', '')
                col_list = col.split(':')

                # Define field
                field = col_list[-1]

                # Handle 'experiment' field
                if field == 'experiment':
                    if value in parsed_experiments:
                        parsed_datum['expt'] = value
                    else:
                        raise ValueDoesNotExist(value, 'experiment')
                    continue

                # Standardize field
                field = self._standardize_field(field)

                # Populate parsed_datum dict
                if field in params['data']:
                    parsed_datum['base'][field] = value

                elif field in params['file']:
                    parsed_datum['file'][field] = value

                elif field in params['cond']:
                    self._parse_cond(col_list, field, value, parsed_datum)

            self.parsed[row['*name'].strip()] = parsed_datum

        return self.parsed


class MaterialSheet(Sheet):
    """
    Material Excel sheet.
    """
    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self, parsed_data, parsed_processes=None):
        # Validate required columns
        required_cols = ['*name']
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_material = {
                'base': {},
                'iden': {},
                'prop': {},
                'cond': {}
            }

            for col in self.cols:
                # Define and clean value
                value = row[col]
                if isinstance(value, str):
                    value = value.strip()

                # Check if col should be skipped
                if self._skip_col(col, value) == True:
                    continue

                # Clean col and create col_list
                col = col.replace('*', '')
                col_list = col.split(':')

                # Define field
                field = col_list[-1]

                # Handle list fields
                if field == 'keywords' or field == 'hazard':
                    parsed_material['base'][field] = row[field].split(',')
                    continue
                elif field == 'names':
                    parsed_material['iden']['names'] = row['names'].split(',')
                    continue

                # Handle process field
                if field == 'process':
                    # Check that process field exists in process sheet
                    if parsed_processes and value not in parsed_processes:
                        raise ValueDoesNotExist(value, 'process')

                    parsed_material['process'] = value
                    continue

                # Handle data
                if field == 'data':
                    self._parse_data(col_list, parsed_material, value, parsed_data, params['material_prop'])
                    continue

                # Standardize field
                field = self._standardize_field(field)

                # Handle base material fields
                if field in params['material']:
                    parsed_material['base'][field] = value

                # Handle material identity fields
                elif field in params['material_iden']:
                    parsed_material['iden'][field] = value

                # Handle properties
                elif field in params['material_prop']:
                    self._parse_prop(col_list, field, value, parsed_material, params['material_prop'])

                # Handle conditions
                elif field in params['cond']:
                    self._parse_cond(col_list, field, value, parsed_material)

            self.parsed[row['*name'].strip()] = parsed_material

        return self.parsed


class ProcessSheet(Sheet):
    """
    Process Excel sheet.
    """
    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self, parsed_experiments, parsed_data):
        # Validate required columns
        required_cols = ['*experiment', '*name']
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_process = {
                'base': {},
                'prop': {},
                'cond': {}
            }
            for col in self.cols:
                # Define and clean value
                value = row[col]
                if isinstance(value, str):
                    value = value.strip()

                # Check if col should be skipped
                if self._skip_col(col, value) == True:
                    continue

                # Clean col and create col_list
                col = col.replace('*', '')
                col_list = col.split(':')

                # Define field
                field = col_list[-1]

                # Handle 'experiment' field
                if field == 'experiment':
                    if value in parsed_experiments:
                        parsed_process['expt'] = value
                    continue

                # Handle lists
                if field == 'keywords':
                    parsed_process['keywords'] = row['keywords'].split(',')
                    continue

                # Handle data
                if field == 'data':
                    self._parse_data(col_list, parsed_process, value, parsed_data, params['process_prop'])
                    continue

                # Sandardize field
                field = self._standardize_field(field)

                # Handle base process fields
                if field in params['process']:
                    parsed_process['base'][field] = value

                # Handle properties
                elif field in params['process_prop']:
                    self._parse_prop(col_list, field, value, parsed_process, params['process_prop'])

                # Handle conditions
                elif field in params['cond']:
                    self._parse_cond(col_list, field, value, parsed_process)

            self.parsed[row['*name'].strip()] = parsed_process

        return self.parsed


class IngrSheet(Sheet):
    """
    Ingredient Excel sheet.
    """
    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self, parsed_processes, parsed_reagents):
        for process, process_df in self.df.groupby(level=0):
            process_cols = process_df.columns

            # Validate required columns
            required_cols = ['*process', '*keyword', '*material']
            self._check_required_cols(required_cols, process_cols, self.sheet_name)

            # Validate either/or columns
            either_or_cols = ['mole', 'mass', 'volume']
            message = " Options: mole, mass, and/or volume."
            self._check_either_or_cols(either_or_cols, process_cols, self.sheet_name, message)

            parsed_ingrs = {}
            for index, row in process_df.iterrows():
                parsed_ingr = {
                    'quantity': {}
                }
                for col in process_cols:
                    # Define and clean value
                    value = row[col]
                    if isinstance(value, str):
                        value = value.strip()

                    # Check if col should be skipped
                    if self._skip_col(col, value) == True:
                        continue

                    # Clean col and create col_list
                    col = col.replace('*', '')
                    col_list = col.split(':')

                    # Define field
                    field = col_list[-1]

                    # Handle process field
                    if field == 'process':
                        if value not in parsed_processes:
                            raise ValueDoesNotExist(value, 'process')
                        continue

                    # Handle material field
                    if field == 'material':
                        if value not in parsed_reagents:
                            raise ValueDoesNotExist(value, 'reagent')
                        continue

                    # Validate keyword field
                    if field == 'keyword':
                        if value not in params['ingrs_keywords']:
                            raise UnsupportedValue(value, field)

                    # Handle process ingredient fields
                    if field in params['process_ingr']:
                        unit = params['process_ingr'][field]['unit']
                        if unit:
                            # Skip if a quantity field has already been parsed
                            if len(parsed_ingr['quantity']) > 0:
                                continue

                            # Add quantity field with units
                            parsed_ingr['quantity'][field] = {'value': value}
                            parsed_ingr['quantity'][field].update({'unit': params['process_ingr'][field]['unit']})

                        else:
                            parsed_ingr[field] = value

                    else:
                        raise UnsupportedFieldName(field)

                parsed_ingrs[row['*material'].strip()] = parsed_ingr

            if row['*process'] in self.parsed:
                self.parsed[row['*process']].update(parsed_ingrs)
            else:
                self.parsed[row['*process']] = parsed_ingrs

        return self.parsed