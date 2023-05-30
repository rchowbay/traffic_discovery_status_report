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
        self.cve_nvd_link_base = self.config.cve_nvd_link_base
        self.table_header = self.config.table_header_columns
        self.row_counter = 0
        self.halo_api_caller_obj = None
        self.script_start_time = None
        self.absolute_path = None
        self.file_name = None
        self.current_time = None

    def main(self):
        self.util.log_stdout(" Custom SVA Report Script Started ... ")
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
            " Retrieving Total Number of Servers belong to the provided Group/Groups ")
        groups_servers_list = self.list_servers_of_all_groups(
            self.halo_api_caller_obj, list_of_groups_ids)

        self.util.log_stdout(
            " Retrieving Server SVA Scan Results ")
        number_of_servers = len(groups_servers_list)
        with concurrent.futures.ThreadPoolExecutor(number_of_servers) as executor:
            futures = []
            for server in groups_servers_list:
                futures.append(executor.submit(
                    self.get_server_scan_details, server))
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
        if(group_childs_list_count > 0):
            for group in group_childs_list[0]['groups']:
                if group['has_children'] == False:
                    self.list_of_groups.append(group['id'])
                else:
                    self.list_of_groups.append(group['id'])
                    group_childs_list(group['id'], False)
        return self.list_of_groups

    def list_servers_of_all_groups(self, halo_api_caller_obj, list_of_group_ids):
        total_servers_list = []
        if(len(list_of_group_ids) > 0):
            for group_id in list_of_group_ids:
                group_servers_list = halo_api_caller_obj.get_group_servers(
                    group_id)
                group_servers_list_data = group_servers_list[0]
                try:
                    total_number_of_servers = group_servers_list_data['count']
                except:
                    total_number_of_servers = 0
                servers_pages = math.ceil(total_number_of_servers/100)
                for page in range(servers_pages):
                    current_page = page+1
                    page_group_servers_list = halo_api_caller_obj.get_group_servers_per_page(
                        group_id, current_page)
                    servers_list = page_group_servers_list[0]['servers']
                    total_servers_list.extend(servers_list)
        return total_servers_list

    def get_server_scan_details(self, server):
        server_id = server['id']
        hostname = server['hostname']
        self.util.log_stdout(
            " Retrieving SVA scan results for Server [%s] " % hostname)
        server_sva_scan_results = self.halo_api_caller_obj.get_server_sva_scan_details(
            server_id)
        server_scan_data = server_sva_scan_results[0]['scan']
        server_findings_list = server_scan_data['findings']
        for finding in server_findings_list:
            cve_entry_list = finding['cve_entries']
            for cve in cve_entry_list:
                # Checking/Validating HALO API Token Time
                current_temp_time = time.time()
                if((current_temp_time - self.script_start_time) > 880):
                    self.check_configs(
                        self.config, self.halo_api_caller_obj, self.util)

                cve_id = cve['cve_entry']
                self.util.log_stdout(
                    " Retrieving Details of CVE ID: [%s] " % cve_id)
                cve_details_result = self.halo_api_caller_obj.get_cve_details(
                    cve_id)
                cvss_v2_metrices = cve_details_result[0]['CVSS Metrics']
                cvss_v3_metrices = cve_details_result[0]['CVSS v3 Metrics']

                try:
                    v2_access_vector = cvss_v2_metrices['access_vector']
                except:
                    v2_access_vector = 'UNCLASSIFIED'

                try:
                    v2_access_complexity = cvss_v2_metrices['access_complexity']
                except:
                    v2_access_complexity = 'UNCLASSIFIED'

                try:
                    v2_authentication = cvss_v2_metrices['authentication']
                except:
                    v2_authentication = 'UNCLASSIFIED'

                try:
                    v2_confidentiality_impact = cvss_v2_metrices['confidentiality_impact']
                except:
                    v2_confidentiality_impact = 'UNCLASSIFIED'

                try:
                    v2_integrity_impact = cvss_v2_metrices['integrity_impact']
                except:
                    v2_integrity_impact = 'UNCLASSIFIED'

                try:
                    v2_availability_impact = cvss_v2_metrices['availability_impact']
                except:
                    v2_availability_impact = 'UNCLASSIFIED'

                try:
                    v3_attack_vector = cvss_v3_metrices['attack_vector']
                except:
                    v3_attack_vector = 'UNCLASSIFIED'

                try:
                    v3_attack_complexity = cvss_v3_metrices['attack_complexity']
                except:
                    v3_attack_complexity = 'UNCLASSIFIED'

                try:
                    v3_user_interaction = cvss_v3_metrices['user_interaction']
                except:
                    v3_user_interaction = 'UNCLASSIFIED'

                try:
                    v3_confidentiality_impact = cvss_v3_metrices['confidentiality_impact']
                except:
                    v3_confidentiality_impact = 'UNCLASSIFIED'

                try:
                    v3_integrity_impact = cvss_v3_metrices['integrity_impact']
                except:
                    v3_integrity_impact = 'UNCLASSIFIED'

                try:
                    v3_availability_impact = cvss_v3_metrices['availability_impact']
                except:
                    v3_availability_impact = 'UNCLASSIFIED'

                try:
                    v3_privileges_required = cvss_v3_metrices['privileges_required']
                except:
                    v3_privileges_required = 'UNCLASSIFIED'

                try:
                    v3_scope = cvss_v3_metrices['scope']
                except:
                    v3_scope = 'UNCLASSIFIED'

                try:
                    v3_base_severity = cvss_v3_metrices['base_severity']
                except:
                    v3_base_severity = 'UNCLASSIFIED'

                try:
                    v3_vector_string = cvss_v3_metrices['vector_string']
                except:
                    v3_vector_string = 'UNCLASSIFIED'

                filtered_issues_list_result = self.halo_api_caller_obj.get_issues_by_cve(
                    cve_id, hostname)
                issues_list = filtered_issues_list_result[0]['issues']
                try:
                    issue_first_seen_at = issues_list[0]['first_seen_at']
                    issue_last_seen_at = issues_list[0]['last_seen_at']
                except:
                    continue

                table_row = [server['platform'], server['platform'], server['os_version'], server['hostname'], server['server_label'], server['reported_fqdn'],
                             server['connecting_ip_address'], server['primary_ip_address'], server[
                    'connecting_ip_fqdn'], server['csp_provider'], server['csp_instance_id'],
                    server['csp_account_id'], server['csp_image_id'], server['csp_kernel_id'], server[
                    'csp_private_ip'], server['csp_instance_type'], server['csp_availability_zone'],
                    server['csp_region'], server['csp_security_groups'], server['csp_instance_tags'], server['aws_ec2'][
                        'ec2_instance_id'], server['aws_ec2']['ec2_account_id'], server['aws_ec2']['ec2_image_id'],
                    server['aws_ec2']['ec2_kernel_id'], server['aws_ec2']['ec2_private_ip'], server['aws_ec2']['ec2_instance_type'], server[
                        'aws_ec2']['ec2_availability_zone'], server['aws_ec2']['ec2_region'], server['aws_ec2']['ec2_security_groups'],
                    server['state'], server['group_path'], server_scan_data['completed_at'], finding[
                        'package_name'], finding['package_version'], finding['critical'], cve['cve_entry'],
                    cve['cvss_score'], v2_access_vector, v2_access_complexity, v2_authentication, v2_confidentiality_impact,
                    v2_integrity_impact, v2_availability_impact, v3_attack_vector, v3_attack_complexity, v3_user_interaction, v3_confidentiality_impact,
                    v3_integrity_impact, v3_availability_impact, v3_privileges_required, v3_scope, v3_base_severity, v3_vector_string, cve[
                        'remotely_exploitable'],
                    cve_details_result[0]['summary'], self.cve_nvd_link_base+cve_id, issue_first_seen_at, issue_last_seen_at]

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
