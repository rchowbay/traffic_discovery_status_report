import sys
import math
import time
import csv
import concurrent.futures
from unicodedata import name
from halo import config_helper
from halo import halo_api_caller
from halo import utility
from halo import csv_operations


class App(object):

    def __init__(self):
        self.list_of_groups = []
        self.util = utility.Utility()
        self.config = config_helper.ConfigHelper()
        self.csv_operations_obj = csv_operations.CSVOperations()
        self.output_directory = self.config.output_directory
        self.halo_group_id = self.config.halo_group_id
        self.table_header = self.config.table_header_columns
        self.row_counter = 0
        self.halo_api_caller_obj = None
        self.script_start_time = None
        self.absolute_path = None
        self.file_name = None
        self.current_time = None

    def main(self):
        self.util.log_stdout(
            " Traffic Discovery Status Report Script Started ... ")
        self.script_start_time = time.time()

        self.util.log_stdout(" Creating HALO API CALLER Object ")
        self.halo_api_caller_obj = halo_api_caller.HaloAPICaller(self.config)

        self.util.log_stdout(
            " Checking the provided configuration parameters ")
        self.check_configs(self.config, self.halo_api_caller_obj, self.util)

        self.util.log_stdout(
            " Checking & Retrieving Sub-groups of the provided Group ID ")
        list_of_groups_ids = self.group_childs_list(
            self.halo_api_caller_obj, self.halo_group_id, True)

        self.util.log_stdout(
            " Preparing/Creating Empty CSV File to store report results ")
        self.absolute_path, self.file_name, self.current_time = self.csv_operations_obj.prepare_csv_file(
            self.output_directory)

        self.util.log_stdout(
            " Retrieving Groups Traffic Discovery Status ")
        number_of_groups = len(list_of_groups_ids)
        with concurrent.futures.ThreadPoolExecutor(number_of_groups) as executor:
            futures = []
            for group_id in list_of_groups_ids:
                futures.append(executor.submit(
                    self.get_group_traffic_discovery_status, group_id))
            concurrent.futures.wait(futures)

        self.util.log_stdout(" Adding Total Number of Rows into the CSV file ")
        self.add_total_number_of_rows()

        self.util.log_stdout(
            " Operation Completed, Check Generated CSV File! ")
        script_end_time = time.time()
        consumed_time = script_end_time - self.script_start_time
        optimized_consumed_time = round(consumed_time, 3)
        self.util.log_stdout(
            " Total Time Consumed = [%s] seconds " % (optimized_consumed_time))

    def group_childs_list(self, halo_api_caller_obj, group_id, flag):
        if flag == True:
            self.list_of_groups.append(group_id)
        group_childs_list = halo_api_caller_obj.get_group_childs(group_id)
        group_childs_list_count = group_childs_list[0]['count']
        if (group_childs_list_count > 0):
            for group in group_childs_list[0]['groups']:
                if group['has_children'] == False:
                    self.list_of_groups.append(group['id'])
                else:
                    self.list_of_groups.append(group['id'])
                    group_childs_list(group['id'], False)
        return self.list_of_groups

    def get_group_traffic_discovery_status(self, group_id):
        self.util.log_stdout(
            " Retrieving Traffic Discovery Status for Group [%s] " % group_id)
        group_td_status_obj = self.halo_api_caller_obj.get_group_td_status(
            group_id)
        group_details_obj = self.halo_api_caller_obj.get_group_details(
            group_id)
        group_td_status = group_td_status_obj[0]['scanner_settings']['td_auto_scan']
        group_name = group_details_obj[0]['group']['name']

        table_row = [group_id, group_name, group_td_status]

        with open(self.absolute_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if self.row_counter == 0:
                writer.writerow(
                    ["# ------------------------------- #"])
                writer.writerow(
                    ["# Report Name: %s" % (self.file_name)])
                writer.writerow(
                    ["# Report Generated at: %s" % (self.current_time)])
                writer.writerow(
                    ["# Servers Filters: Group ID: [%s]" % (self.halo_group_id)])
                writer.writerow(
                    ["# ------------------------------- #"])
                writer.writerow(self.table_header)
                writer.writerow(table_row)
                self.row_counter += 1
                self.util.log_stdout(
                    " Writing Row Number: [%s] into the CSV file " % self.row_counter)
            else:
                self.util.log_stdout(
                    " Writing Row Number: [%s] into the CSV file " % self.row_counter)
                writer.writerow(table_row)
                self.row_counter += 1

    def add_total_number_of_rows(self):
        with open(self.absolute_path, 'r') as readFile:
            reader = csv.reader(readFile)
            lines = list(reader)
            lines.insert(4, ["# Total Number of Rows = %s" %
                             (self.row_counter)])
        with open(self.absolute_path, 'w', newline='') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(lines)
        readFile.close()
        writeFile.close()

    def check_configs(self, config, halo_api_caller, util):
        halo_api_caller_obj = halo_api_caller
        if halo_api_caller_obj.credentials_work() is False:
            util.log_stdout(" Halo credentials are bad!  Exiting! ")
            sys.exit(1)

        if config.sane() is False:
            util.log_stdout(" Configuration is bad!  Exiting! ")
            sys.exit(1)


if __name__ == "__main__":
    app = App()
    app.main()
