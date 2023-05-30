import sys
import os
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from halo import halo_api_caller
from halo import config_helper

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


if __name__ == "__main__":
    get_all_groups_test()
    get_group_childs_test("67b04036a8c411e9a8b62930f061b45d", False)
    get_group_td_status_test("67b04036a8c411e9a8b62930f061b45d")
