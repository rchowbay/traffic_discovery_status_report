import os
import csv
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

    def prepare_thread_csv_file(self, output_directory, thread_id):
        # Preparing thread CSV file for writing
        current_time = Utility.date_to_iso8601(datetime.now())
        file_name = 'halo_groups_td_status_report_part-' + \
            str(thread_id) + '_' + current_time + '.csv'
        file_name = file_name.replace(':', '-')
        if output_directory == "":
            absolute_path = file_name
        else:
            absolute_path = output_directory + "/" + file_name
        return absolute_path, file_name, current_time

    def combine_csv_files(self, output_directory, table_header, td_status_filter, halo_group_id):
        # combine all threads CSV files into one csv file
        threads_files = os.listdir(output_directory)
        current_time = Utility.date_to_iso8601(datetime.now())
        file_name = 'halo_groups_td_status_report_' + current_time + '.csv'
        file_name = file_name.replace(':', '-')
        if output_directory == "":
            absolute_path = file_name
        else:
            absolute_path = output_directory + "/" + file_name

        with open(absolute_path, 'w', newline='') as output_csvfile:
            writer = csv.writer(output_csvfile)
            writer.writerow(table_header)
            for thread_file in threads_files:
                with open(output_directory+"/"+thread_file, 'r') as input_csvfile:
                    reader = csv.reader(input_csvfile)
                    for _ in range(7):
                        next(reader)
                    for row in reader:
                        writer.writerow(row)
                self.remove_csv_file(output_directory+"/"+thread_file)
        self.add_file_statistics(
            output_directory, file_name, current_time, td_status_filter, halo_group_id)

    def remove_csv_file(self, filename):
        # Remove threads CSV files
        if os.path.exists(filename):
            os.remove(filename)

    def create_sub_directory(self, output_directory):
        # Create sub-directory to hold the report of the current run
        current_time = Utility.date_to_iso8601(datetime.now())
        directory_name = 'td_status_report_' + current_time
        directory_name = directory_name.replace(':', '-')
        directory_name = directory_name.replace('.', '-')
        if output_directory == "":
            absolute_sub_directory_path = directory_name
        else:
            absolute_sub_directory_path = output_directory + "/" + directory_name
        if not os.path.exists(absolute_sub_directory_path):
            os.mkdir(absolute_sub_directory_path)
        return absolute_sub_directory_path

    def add_file_statistics(self, output_directory, file_name, current_time, td_status_filter, halo_group_id):
        # Add some overall statistics into the CSV file
        with open(output_directory + "/" + file_name, 'r') as readFile:
            reader = csv.reader(readFile)
            rows = []
            if td_status_filter == 'ENABLED':
                for row in reader:
                    if row[2] == 'True':
                        rows.append(row)
                td_disabled_status_rows = 0
                td_not_set_status_rows = 0
                total_rows = len(rows)
                td_enabled_status_rows = len(rows)
            elif td_status_filter == 'DISABLED':
                for row in reader:
                    if row[2] == 'False':
                        rows.append(row)
                td_enabled_status_rows = 0
                td_not_set_status_rows = 0
                total_rows = len(rows)
                td_disabled_status_rows = len(rows)
            else:
                rows = list(reader)
                total_rows, td_enabled_status_rows, td_disabled_status_rows, td_not_set_status_rows = self.row_counter(
                    output_directory, file_name)
            rows.insert(0, ["# ------------------------------- #"])
            rows.insert(1, ["# Report Name: %s" % (file_name)])
            rows.insert(2, ["# Report Generated at: %s" % (current_time)])
            rows.insert(
                3, ["# Results Filtered by Group TD Status = [%s] and Group ID = [%s]" % (td_status_filter, halo_group_id)])
            rows.insert(4, ["# Total Number of Groups = %s" % (total_rows)])
            rows.insert(5, ["# Total Number of Groups with TD Status Enabled = %s" % (
                td_enabled_status_rows)])
            rows.insert(6, ["# Total Number of Groups with TD Status Disabled = %s" % (
                td_disabled_status_rows)])
            rows.insert(7, ["# Total Number of Groups with TD Status Not Set = %s" % (
                td_not_set_status_rows)])
            rows.insert(8, ["# ------------------------------- #"])
        with open(output_directory + "/" + file_name, 'w', newline='') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(rows)

    def row_counter(self, output_directory, file_name):
        # Count Overall Statistics to be added into the main CSV file
        total_rows = 0
        td_enabled_status_rows = 0
        td_disabled_status_rows = 0
        td_not_set_status_rows = 0
        with open(output_directory+"/"+file_name, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[2] == 'True':
                    td_enabled_status_rows += 1
                elif row[2] == 'False':
                    td_disabled_status_rows += 1
                else:
                    td_not_set_status_rows += 1
            # to ignore header row value
            td_not_set_status_rows -= 1
        total_rows = td_enabled_status_rows+td_disabled_status_rows+td_not_set_status_rows
        return total_rows, td_enabled_status_rows, td_disabled_status_rows, td_not_set_status_rows
