
import pandas as pd
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

import os_navigation as os_nav

from job_utils import JobStatus, JobInfo


class JobMonitor:
    def __init__(
            self,
            job_log=os.path.join(os_nav.find_project_root(), 'data', 'jobs', 'all_jaguar_jobs.csv'),
            job_out_dir=os.path.join(os_nav.find_project_root(), 'out')
    ):
        self.job_log = job_log
        self.job_out_dir = job_out_dir

    @staticmethod
    def scrape_log(log_file_path):
        """
        Scrape the log file for the job status and return the appropriate JobStatus enum.
        """
        try:
            with open(log_file_path, 'r') as file:
                log_content = file.read()

            if "ERROR" in log_content or "FATAL ERROR" in log_content:
                return JobStatus.ERROR

            if "Job input completed:" in log_content:
                return JobStatus.FINISHED

            return JobStatus.RUNNING
        except FileNotFoundError:
            return JobStatus.QUEUED

    def update_status(self):
        # Read the current job log
        old_jobs = pd.read_csv(self.job_log)

        # Loop through each subdirectory in the job output directory
        for file in os.listdir(self.job_out_dir):
            job_dir = os.path.join(self.job_out_dir, file)
            if os.path.isdir(job_dir):
                job_status = JobStatus.QUEUED

                log_file_path = os.path.join(job_dir, f"{file}.log")

                if os.path.isfile(log_file_path):
                    # Scrape the log file for the job status
                    job_status = self.scrape_log(log_file_path)

                # Update the job status in the DataFrame
                old_jobs.loc[old_jobs[JobInfo.JOB_ID.value] == file, JobInfo.JOB_STATUS.value] = job_status.value

        # Save the updated DataFrame back to the CSV file
        old_jobs.to_csv(self.job_log, index=False)

        print("Job statuses updated successfully.")


def main():
    job_monitor = JobMonitor()
    job_monitor.update_status()


if __name__ == '__main__':
    main()
