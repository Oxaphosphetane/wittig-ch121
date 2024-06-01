import pandas as pd
import os
import sys
import datetime as dt

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

import os_navigation as os_nav

from job_utils import JobStatus, JobInfo


class JobMonitor:
    log_date_format = "%a %b %d %H:%M:%S %Y"

    def __init__(
            self,
            job_log=os.path.join(os_nav.find_project_root(), 'data', 'jobs', 'all_jaguar_jobs.csv'),
            job_out_dir=os.path.join(os_nav.find_project_root(), 'out')
    ):
        self.job_log = job_log
        self.job_out_dir = job_out_dir

    @staticmethod
    def format_timedelta(delta):
        # Get the total number of seconds
        total_seconds = delta.total_seconds()

        # Extract hours, minutes, and seconds
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Format the result with one decimal place for seconds
        formatted_time = f"{int(hours):02}:{int(minutes):02}:{seconds:04.1f}"

        return formatted_time

    def scrape_log_for_runtime(self, job_id, job_status):
        """
        Scrape the log log_file for the job runtime.
        """
        try:
            with open(os.path.join(self.job_out_dir, job_id, f"{job_id}.log"), 'r') as log_file:
                log_lines = log_file.readlines()
        except FileNotFoundError:
            return

        start_time = None
        for line in log_lines:
            if f"Job {job_id} started on" in line:
                start_date_string = line.split(' at ')[-1].strip()
                try:
                    start_time = dt.datetime.strptime(start_date_string, JobMonitor.log_date_format)
                except Exception as e:
                    print(e)
                break

        if start_time is None:
            return

        if job_status == JobStatus.FINISHED or job_status == JobStatus.ERROR:
            for line in log_lines:
                if f"Finished:" in line:
                    end_date_string = line.split("Finished:")[-1].strip()
                    end_time = dt.datetime.strptime(end_date_string, JobMonitor.log_date_format)
                    break
        elif job_status == JobStatus.RUNNING:
            end_time = dt.datetime.now()
        else:
            return

        run_time = end_time - start_time
        return JobMonitor.format_timedelta(run_time)

    def scrape_log_for_status(self, job_id):
        """
        Scrape the log log_file for the job status and return the appropriate JobStatus enum.
        """
        try:
            with open(os.path.join(self.job_out_dir, job_id, f"{job_id}.log"), 'r') as log_file:
                log_content = log_file.read()

            if "ERROR" in log_content or "FATAL ERROR" in log_content:
                return JobStatus.ERROR

            if f"Job {job_id} completed" in log_content:
                return JobStatus.FINISHED

            return JobStatus.RUNNING
        except FileNotFoundError:
            return JobStatus.QUEUED

    def update_status(self):
        # Read the current job log
        old_jobs = pd.read_csv(self.job_log)

        new_entries = []

        # Loop through each subdirectory in the job output directory
        for file in os.listdir(self.job_out_dir):
            job_dir = os.path.join(self.job_out_dir, file)
            if os.path.isdir(job_dir):
                job_status = self.scrape_log_for_status(job_id=file)
                runtime = self.scrape_log_for_runtime(job_id=file, job_status=job_status)

                if old_jobs[old_jobs[JobInfo.JOB_ID.value] == file].empty:
                    # Add new job entry if it doesn't exist
                    new_entry = {
                        JobInfo.JOB_ID.value: file,
                        JobInfo.JOB_STATUS.value: job_status,
                        JobInfo.RUNTIME.value: runtime
                    }
                    new_entries.append(new_entry)
                else:
                    # Update the job status in the DataFrame
                    old_jobs.loc[old_jobs[JobInfo.JOB_ID.value] == file, JobInfo.JOB_STATUS.value] = job_status.value
                    old_jobs.loc[old_jobs[JobInfo.JOB_ID.value] == file, JobInfo.RUNTIME.value] = runtime

        # Convert the new entries to a DataFrame and concatenate with old_jobs
        if new_entries:
            new_jobs_df = pd.DataFrame(new_entries)
            updated_jobs = pd.concat([old_jobs, new_jobs_df], ignore_index=True)
        else:
            updated_jobs = old_jobs

        # Save the updated job log
        updated_jobs.to_csv(self.job_log, index=False)

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        print(old_jobs)
        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')

        # Count the number of each status
        print()
        for status in JobStatus:
            count = old_jobs[JobInfo.JOB_STATUS.value].value_counts().get(status.value, 0)
            print(f"Number of {status.value} jobs: {count}")

def main():
    job_monitor = JobMonitor()
    job_monitor.update_status()


if __name__ == '__main__':
    main()
