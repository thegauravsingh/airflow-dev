from datetime import timedelta
from typing import Optional
from pendulum import Date, DateTime, Time, timezone, parse
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
from sears_business_calendar import SearsBusinessCalendar
from airflow.plugins_manager import AirflowPlugin
from airflow.timetables.base import DagRunInfo, DataInterval, TimeRestriction, Timetable

UTC = timezone("UTC")

#Gotham_BD = CustomBusinessDay(calendar=SearsBusinessCalendar())
#s = pd.date_range('2018-07-01', end='2018-07-31', freq=Gotham_BD)
#df = pd.DataFrame(s, columns=['Date'])
#holiday_cal = SearsBusinessCalendar()
#df1 = df2 = pd.DataFrame()
#df1['Date'] = holiday_cal.holidays(start='2022-01-01', end='2022-12-31').to_frame(index=False)
#
#class FixedTimetable(Timetable):
#    def infer_manual_data_interval(self, run_after: DateTime) -> DataInterval:
#        pass

holiday_cal = SearsBusinessCalendar()
holiday_df = pd.DataFrame()
holiday_df['Date'] = holiday_cal.holidays(start='2022-01-01', end='2022-12-31').to_frame(index=False)

class FixedTimetable(Timetable):

    def infer_manual_data_interval(self, run_after: DateTime) -> DataInterval:
        run_after_str = run_after.format('YYYY-MM-DD')
        rows = (holiday_df['Date'] >= run_after_str) 
        remaining_holidays = holiday_df.loc[rows]
        start = parse(str(remaining_holidays['Date'].iloc[0])).naive()
        end = parse(str(remaining_holidays['Date'].iloc[1])).naive()
        start = start.replace(tzinfo=UTC)
        end =  end.subtract(days=1)      
        end =  end.replace(tzinfo=UTC)        
        return DataInterval(start=start, end=end)

    def next_dagrun_info(
        self,
        *,
        last_automated_data_interval: Optional[DataInterval],
        restriction: TimeRestriction,
    ) -> Optional[DagRunInfo]:
        if last_automated_data_interval is not None:  # There was a previous run on the regular schedule.
            last_start = last_automated_data_interval.start
            last_start_str = last_start.format('YYYY-MM-DD')
            rows = (holiday_df['Date'] >= last_start_str) 
            remaining_holidays = holiday_df.loc[rows]
            next_start = parse(str(remaining_holidays['Date'].iloc[0])).naive()
            next_end = parse(str(remaining_holidays['Date'].iloc[1])).naive()
            next_start = next_start.replace(tzinfo=UTC)
            next_end = next_end.subtract(days=1)      
            next_end = next_end.replace(tzinfo=UTC)        
        else:  # This is the first ever run on the regular schedule.
            next_start = restriction.earliest
            if next_start is None:  # No start_date. Don't schedule.
                return None
            if not restriction.catchup: # If the DAG has catchup=False, today is the earliest to consider.
                next_start = max(next_start, DateTime.combine(Date.today(), Time.min).replace(tzinfo=UTC))
            next_start_str = next_start.format('YYYY-MM-DD')
            rows = (holiday_df['Date'] >= next_start_str)             
            remaining_holidays = holiday_df.loc[rows]
            print('next_start_str :', next_start_str)
            if remaining_holidays is not None:
                next_start = parse(str(remaining_holidays['Date'].iloc[0])).naive()
                next_end = parse(str(remaining_holidays['Date'].iloc[1])).naive()
                next_start = next_start.replace(tzinfo=UTC)
                next_end = next_end.subtract(days=1)      
                next_end = next_end.replace(tzinfo=UTC)    
            else:
                next_end = next_start.subtract(days=1).replace(tzinfo=UTC)  
        if restriction.latest is not None and next_start > restriction.latest:
            return None  # Over the DAG's scheduled end; don't schedule.
        return DagRunInfo.interval(start=next_start, end=next_end)



class FixedTimetablePlugin(AirflowPlugin):
    name = "fixed_timetable_plugin"
    timetables = [FixedTimetable]
