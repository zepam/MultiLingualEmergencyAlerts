#auto_collect_responses.cmd

executable = collect_responses.sh
arguments = ""

getenv     = true
log        = auto_collect_responses.log
error      = auto_collect_responses.err
notification = always

transfer_executable = true
#request_memory = 2*1024

# Run once every 2 days at midnight
cron_day_of_month = *
cron_month        = *
cron_day_of_week  = *
cron_hour         = 0
cron_minute       = 0

# Important: allow skipping days
cron_prep_time    = 300
cron_window       = 86400    # 24 hours window to allow execution
queue
