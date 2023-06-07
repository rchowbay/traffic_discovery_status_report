import sys
import os
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from halo import halo_api_caller
from halo import config_helper
from halo import csv_operations

list_of_groups = []


def get_all_groups_test():
    config = config_helper.ConfigHelper()
    halo_api_caller_obj = halo_api_caller.HaloAPICaller(config)
    halo_api_caller_obj.authenticate_client()
    groups_list = halo_api_caller_obj.get_all_groups()
    print(groups_list[0]['count'])


def get_group_childs_test(group_id, flag):
    config = config_helper.ConfigHelper()
    halo_api_caller_obj = halo_api_caller.HaloAPICaller(config)
    halo_api_caller_obj.authenticate_client()
    if flag == True:
        list_of_groups.append(group_id)
    group_childs_list = halo_api_caller_obj.get_group_childs(group_id)
    group_childs_list_count = group_childs_list[0]['count']
    if (group_childs_list_count > 0):
        for group in group_childs_list[0]['groups']:
            if group['has_children'] == False:
                list_of_groups.append(group['id'])
            else:
                list_of_groups.append(group['id'])
                get_group_childs_test(group['id'], False)
    print(len(list_of_groups))


def get_group_td_status_test(group_id):
    config = config_helper.ConfigHelper()
    halo_api_caller_obj = halo_api_caller.HaloAPICaller(config)
    halo_api_caller_obj.authenticate_client()
    group_td_status = halo_api_caller_obj.get_group_td_status(group_id)
    print(group_td_status[0]['scanner_settings']['td_auto_scan'])

def combine_csv_files_test(output_directory, table_header):
    csv_operations_obj = csv_operations.CSVOperations()
    csv_operations_obj.combine_csv_files(output_directory, table_header)

def create_sub_directory_test(output_directory):
    csv_operations_obj = csv_operations.CSVOperations()
    csv_operations_obj.create_sub_directory(output_directory)

def remove_csv_file_test(file_name):
    csv_operations_obj = csv_operations.CSVOperations()
    csv_operations_obj.remove_csv_file(file_name)

def add_file_statistics_test(output_directory, file_name, current_time, filter):
    csv_operations_obj = csv_operations.CSVOperations()
    csv_operations_obj.add_file_statistics(output_directory, file_name, current_time, filter)

def row_counter_test(output_directory, file_name):
    csv_operations_obj = csv_operations.CSVOperations()
    total_rows, td_enabled_status_rows, td_disabled_status_rows, td_not_set_status_rows = csv_operations_obj.row_counter(output_directory, file_name)
    print("Total Rows = %s" % total_rows)
    print("TD Status Enabled Rows = %s" % td_enabled_status_rows)
    print("TD Status Disabled Rows = %s" % td_disabled_status_rows)
    print("TD Status Not-Set Rows = %s" % td_not_set_status_rows)

if __name__ == "__main__":
    # get_all_groups_test()
    # get_group_childs_test("67b04036a8c411e9a8b62930f061b45d", False)
    # get_group_td_status_test("67b04036a8c411e9a8b62930f061b45d")
    output_directory = r'C:\Users\tmiller\tmp_output_dir\td_status_report_2023-06-07T12-37-28-006755'
    # table_header_columns = ['HALO Group ID', 'HALO Group Name', 'TD Status']
    # combine_csv_files_test(output_directory, table_header_columns)
    # create_sub_directory_test(output_directory)
    file_name = 'halo_groups_td_status_report_2023-06-07T12-56-11.971615.csv'
    row_counter_test(output_directory, file_name)
