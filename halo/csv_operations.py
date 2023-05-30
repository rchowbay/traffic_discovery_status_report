from datetime import datetime
from halo.utility import Utility


class CSVOperations(object):
    """
    This class contains all operations deal with CSV file.

    """

    def prepare_csv_file(self, output_directory):
        # Preparing CSV file for writing
        current_time = Utility.date_to_iso8601(datetime.now())
        file_name = 'halo_groups_td_status_report_' + current_time + '.csv'
        file_name = file_name.replace(':', '-')
        if output_directory == "":
            absolute_path = file_name
        else:
            absolute_path = output_directory + "/" + file_name
        return absolute_path, file_name, current_time
