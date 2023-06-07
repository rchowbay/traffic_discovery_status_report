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
        # self.list_of_groups = []
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
        # self.table_data = []
        self.absolute_sub_directory_path = None

    def initialize_common_objects(self):
        self.util.log_stdout(" Creating HALO API CALLER Object ")
        self.halo_api_caller_obj = halo_api_caller.HaloAPICaller(self.config)

        self.util.log_stdout(
            " Checking the provided configuration parameters ")
        self.check_configs(self.config, self.halo_api_caller_obj, self.util)

    def main(self):
        self.util.log_stdout(
            " Traffic Discovery Status Report Script Started ... ")
        self.script_start_time = time.time()

        # initilizing objects of HALOAPICALLER and CONFIG
        self.initialize_common_objects()

        """
        self.util.log_stdout(
            " Checking & Retrieving Sub-groups of the provided Group ID ")
        list_of_groups_ids = self.group_childs_list(
            self.halo_api_caller_obj, self.halo_group_id, True)
        """

        self.util.log_stdout(
            " Retreiving all HALO groups' IDs of the specified HALO account ")
        self.get_all_groups()

        """
        self.util.log_stdout(
            " Preparing/Creating Empty CSV File to store report results ")
        self.absolute_path, self.file_name, self.current_time = self.csv_operations_obj.prepare_csv_file(
            self.output_directory)

        self.util.log_stdout(
            " Retrieving Groups Traffic Discovery Status ")

        groups_td_status_threads = math.ceil(len(self.list_of_groups)/500)
        with concurrent.futures.ThreadPoolExecutor(max_workers=groups_td_status_threads) as executor:
            for i in range(groups_td_status_threads):
                futures = [executor.submit(
                    self.get_groups_td_status, self.list_of_groups, i * 500, (i + 1) * 500)]
            concurrent.futures.wait(futures)

        # Creating threads.
        groups_td_status_threads = math.ceil(len(self.list_of_groups)/500)
        threads = []
        for i in range(groups_td_status_threads):
            threads.append(threading.Thread(target=self.get_groups_td_status, args=(self.list_of_groups, i * 500, (i + 1) * 500)))

        # Start all the threads.
        for thread in threads:
            thread.start()

        # Wait for all the threads to finish.
        for thread in threads:
            thread.join()

        self.util.log_stdout(
            " Adding Group Traffic Discovery Data into the CSV File ")
        self.write_to_csv(self.table_data)

        self.util.log_stdout(" Adding Total Number of Rows into the CSV file ")
        self.add_total_number_of_rows()
        """

        self.util.log_stdout(
            " Operation Completed, Check Generated CSV File! ")
        script_end_time = time.time()
        consumed_time = script_end_time - self.script_start_time
        optimized_consumed_time = round(consumed_time, 3)
        self.util.log_stdout(
            " Total Time Consumed = [%s] seconds " % (optimized_consumed_time))

    def get_all_groups(self):
        groups_list_object = self.halo_api_caller_obj.get_all_groups()
        groups_list_count = groups_list_object[0]['count']
        print(" =============== Total Number of Groups= %s" % groups_list_count)
        if (groups_list_count > 0):
            self.absolute_sub_directory_path = self.csv_operations_obj.create_sub_directory(self.output_directory)
            groups_pages = math.ceil(groups_list_count/1000)

            threads = []
            for i in range(groups_pages):
                current_page = i+1
                self.util.log_stdout(" Preparing/Creating Empty Partial CSV File to store results of thread No. [%s]" % current_page)
                thread_file_absolute_path, thread_file_name, thread_current_time = self.csv_operations_obj.prepare_thread_csv_file(self.absolute_sub_directory_path , current_page)
                thread = threading.Thread(target=self.get_all_groups_per_page, args=(current_page, thread_file_absolute_path, thread_file_name, thread_current_time))
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

            self.util.log_stdout(" Combining All Threads CSV files into one aggregated CSV File ")
            self.csv_operations_obj.combine_csv_files(self.absolute_sub_directory_path , self.table_header)

        else:
            self.util.log_stdout(
            " No HALO Groups Found in the specified  HALO account! ")

    def get_all_groups_per_page(self, current_page, thread_file_absolute_path, thread_file_name, thread_current_time ):
        current_page_groups_object = self.halo_api_caller_obj.get_all_groups_per_page(current_page)
        thread_file_row_counter = 0
        for group in current_page_groups_object[0]['groups']:
            print(" Getting TD Status of Group [%s]" % group['id'])
            try:
                self.get_group_traffic_discovery_status(group['id'], thread_file_absolute_path, thread_file_name, thread_current_time, thread_file_row_counter)
                thread_file_row_counter += 1
            except:
                self.initialize_common_objects()
                self.get_group_traffic_discovery_status(group['id'], thread_file_absolute_path, thread_file_name, thread_current_time, thread_file_row_counter)
                thread_file_row_counter += 1
            # self.list_of_groups.append(group['id'])

        self.util.log_stdout(" Adding Total Number of Rows into the CSV file of thread No. [%s]" % current_page)
        with open(thread_file_absolute_path, 'r') as readFile:
            reader = csv.reader(readFile)
            lines = list(reader)
            lines.insert(4, ["# Total Number of Rows = %s" %
                             (thread_file_row_counter)])
        with open(thread_file_absolute_path, 'w', newline='') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(lines)
        readFile.close()
        writeFile.close()

    def get_group_traffic_discovery_status(self, group_id, thread_file_absolute_path, thread_file_name, thread_current_time, thread_file_row_counter):
        self.util.log_stdout(
            " Retrieving Traffic Discovery Status for Group [%s] " % group_id)
        group_td_status_obj = self.halo_api_caller_obj.get_group_td_status(group_id)
        group_td_status = group_td_status_obj[0]['scanner_settings']['td_auto_scan']
        self.util.log_stdout(
            " Retrieving Group Name for Group [%s] " % group_id)
        group_details_obj = self.halo_api_caller_obj.get_group_details(group_id)
        group_name = group_details_obj[0]['group']['name']
        table_row = [group_id, group_name, group_td_status]
        
        # self.table_data.append(table_row)

        with open(thread_file_absolute_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if thread_file_row_counter == 0:
                writer.writerow(
                    ["# ------------------------------- #"])
                writer.writerow(
                    ["# Report Name: %s" % (thread_file_name)])
                writer.writerow(
                    ["# Report Generated at: %s" % (thread_current_time)])
                writer.writerow(
                    ["# Servers Filters: Group ID: [%s]" % (self.halo_group_id)])
                writer.writerow(
                    ["# ------------------------------- #"])
                writer.writerow(self.table_header)
                writer.writerow(table_row)
                # self.row_counter += 1
                self.util.log_stdout(
                    " Writing Row Number: [%s] into the CSV file " % thread_file_row_counter)
            else:
                self.util.log_stdout(
                    " Writing Row Number: [%s] into the CSV file " % thread_file_row_counter)
                writer.writerow(table_row)
                # self.row_counter += 1

    """
    def write_to_csv(self, table_data):
        with open(self.absolute_path, 'a', newline='') as f:
            writer = csv.writer(f)
            for table_row in len(table_data):
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
    """

    """            
    def get_groups_td_status(self, groups, start, end):
        for i in range(start, end):
            try:
                self.util.log_stdout(
                    " Retrieving Traffic Discovery Status for Group [%s] " % groups[i])
                group_td_status_obj = self.halo_api_caller_obj.get_group_td_status(
                    groups[i])
                group_details_obj = self.halo_api_caller_obj.get_group_details(
                    groups[i])
                group_td_status = group_td_status_obj[0]['scanner_settings']['td_auto_scan']
                group_name = group_details_obj[0]['group']['name']

                table_row = [groups[i], group_name, group_td_status]
                self.table_data.append(table_row)
                print(" =================== Data table Size = %s" %
                      len(self.table_data))
            except:
                self.initialize_common_objects()
                self.util.log_stdout(
                    " Retrieving Traffic Discovery Status for Group [%s] " % groups[i])
                group_td_status_obj = self.halo_api_caller_obj.get_group_td_status(
                    groups[i])
                group_details_obj = self.halo_api_caller_obj.get_group_details(
                    groups[i])
                group_td_status = group_td_status_obj[0]['scanner_settings']['td_auto_scan']
                group_name = group_details_obj[0]['group']['name']

                table_row = [groups[i], group_name, group_td_status]
                self.table_data.append(table_row)
                print(" =================== Data table Size = %s" %
                      len(self.table_data))
    """

    """
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
                    self.group_childs_list(halo_api_caller_obj, group['id'], False)
        return self.list_of_groups
    """

    """
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
    """
        
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
