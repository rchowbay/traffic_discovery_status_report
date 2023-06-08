import sys
import math
import time
import csv
import concurrent.futures
import threading
from unicodedata import name
from halo import config_helper
from halo import halo_api_caller
from halo import utility
from halo import csv_operations


class App(object):

    def __init__(self):
        self.util = utility.Utility()
        self.config = config_helper.ConfigHelper()
        self.csv_operations_obj = csv_operations.CSVOperations()
        self.output_directory = self.config.output_directory
        self.table_header = self.config.table_header_columns
        self.row_counter = 0
        self.halo_api_caller_obj = None
        self.script_start_time = None
        self.absolute_path = None
        self.file_name = None
        self.current_time = None
        self.absolute_sub_directory_path = None
        self.td_status_filter = None
        self.halo_group_id = None

    def initialize_common_objects(self):
        self.util.log_stdout(" Creating HALO API CALLER Object ")
        self.halo_api_caller_obj = halo_api_caller.HaloAPICaller(self.config)

        self.util.log_stdout(
            " Checking the provided configuration parameters ")
        self.check_configs(self.config, self.halo_api_caller_obj, self.util)

    def main(self):
        self.td_status_filter = input(
            "Enter Traffic Discovery (TD) Status 'ENABLED / DISABLED / ALL (Default)': ") or "ALL"
        self.halo_group_id = input("Enter Group ID 'ALL (Default)': ") or "ALL"

        self.util.log_stdout(
            " Traffic Discovery Status Report Script Started ... ")
        self.script_start_time = time.time()

        # initilizing objects of HALOAPICALLER and CONFIG
        self.initialize_common_objects()

        self.util.log_stdout(
            " Retreiving HALO groups' IDs from the provided HALO account ")
        self.get_groups()

        self.util.log_stdout(
            " Operation Completed, Check the generated report CSV File! ")
        script_end_time = time.time()
        consumed_time = script_end_time - self.script_start_time
        optimized_consumed_time = round(consumed_time, 3)
        self.util.log_stdout(
            " Total Time Consumed = [%s] seconds " % (optimized_consumed_time))

    def get_groups(self):
        if self.halo_group_id == 'ALL':
            groups_list_object = self.halo_api_caller_obj.get_all_groups()
            groups_list_count = groups_list_object[0]['count']
        else:
            groups_list_object = self.halo_api_caller_obj.get_group_childs(
                self.halo_group_id)
            # add +1 for the parent group id
            groups_list_count = groups_list_object[0]['count']+1

        self.util.log_stdout(" Total Number of Groups= %s" % groups_list_count)
        if (groups_list_count > 0):
            self.absolute_sub_directory_path = self.csv_operations_obj.create_sub_directory(
                self.output_directory)
            groups_pages = math.ceil(groups_list_count/1000)

            threads = []
            for i in range(groups_pages):
                current_page = i+1
                self.util.log_stdout(
                    " Preparing/Creating Empty Partial CSV File to store results of thread No. [%s]" % current_page)
                thread_file_absolute_path, thread_file_name, thread_current_time = self.csv_operations_obj.prepare_thread_csv_file(
                    self.absolute_sub_directory_path, current_page)
                thread = threading.Thread(target=self.get_all_groups_per_page, args=(
                    current_page, thread_file_absolute_path, thread_file_name, thread_current_time))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            """
            with concurrent.futures.ThreadPoolExecutor(groups_pages) as executor:
                futures = []
                for page in range(groups_pages):
                    current_page = page+1
                    self.util.log_stdout(" Preparing/Creating Empty Partial CSV File to store results of thread No. [%s]" % current_page)
                    thread_file_absolute_path, thread_file_name, thread_current_time = self.csv_operations_obj.prepare_thread_csv_file(self.absolute_sub_directory_path , current_page)
                    futures.append(executor.submit(self.get_all_groups_per_page, current_page, thread_file_absolute_path, thread_file_name, thread_current_time ))
                concurrent.futures.wait(futures)
            """

            self.util.log_stdout(
                " Combining All Threads CSV files into one aggregated CSV File ")
            self.csv_operations_obj.combine_csv_files(
                self.absolute_sub_directory_path, self.table_header, self.td_status_filter, self.halo_group_id)

        else:
            self.util.log_stdout(
                " No HALO Groups Found in the specified  HALO account! ")

    def get_all_groups_per_page(self, current_page, thread_file_absolute_path, thread_file_name, thread_current_time):
        if self.halo_group_id == 'ALL':
            current_page_groups_object = self.halo_api_caller_obj.get_all_groups_per_page(
                current_page)
            flag = False
        else:
            current_page_groups_object = self.halo_api_caller_obj.get_group_childs_per_page(
                self.halo_group_id, current_page)
            flag = True
        thread_file_row_counter = 0
        for group in current_page_groups_object[0]['groups']:
            try:
                if flag == True:
                    self.get_group_traffic_discovery_status(
                        self.halo_group_id, thread_file_absolute_path, thread_file_name, thread_current_time, thread_file_row_counter)
                    thread_file_row_counter += 1
                    flag = False
                self.get_group_traffic_discovery_status(
                    group['id'], thread_file_absolute_path, thread_file_name, thread_current_time, thread_file_row_counter)
                thread_file_row_counter += 1
            except:
                self.initialize_common_objects()
                if flag == True:
                    self.get_group_traffic_discovery_status(
                        self.halo_group_id, thread_file_absolute_path, thread_file_name, thread_current_time, thread_file_row_counter)
                    thread_file_row_counter += 1
                    flag = False
                self.get_group_traffic_discovery_status(
                    group['id'], thread_file_absolute_path, thread_file_name, thread_current_time, thread_file_row_counter)
                thread_file_row_counter += 1

    def get_group_traffic_discovery_status(self, group_id, thread_file_absolute_path, thread_file_name, thread_current_time, thread_file_row_counter):
        self.util.log_stdout(
            " Retrieving Traffic Discovery Status for Group [%s] " % group_id)
        group_td_status_obj = self.halo_api_caller_obj.get_group_td_status(
            group_id)
        group_td_status = group_td_status_obj[0]['scanner_settings']['td_auto_scan']
        self.util.log_stdout(
            " Retrieving Group Name for Group [%s] " % group_id)
        group_details_obj = self.halo_api_caller_obj.get_group_details(
            group_id)
        group_name = group_details_obj[0]['group']['name']
        table_row = [group_id, group_name, group_td_status]

        with open(thread_file_absolute_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if thread_file_row_counter == 0:
                writer.writerow(self.table_header)
                writer.writerow(table_row)
                self.util.log_stdout(
                    " Writing Group ID: [%s], Group Name: [%s], TD Status: [%s] into the thread CSV file. " % (group_id, group_name,  group_td_status))
            else:
                self.util.log_stdout(
                    " Writing Group ID: [%s], Group Name: [%s], TD Status: [%s] into the thread CSV file. " % (group_id, group_name,  group_td_status))
                writer.writerow(table_row)

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
