#!/usr/bin/env python3
"""
Moon Phase Calendar with Events
Authors: <Your Names>
Course: <Course name>
Semester: <Fall 2025>

A lunar calendar that computes moon phases, illumination, rise/set times,
and correlates with user events. Identifies dark-sky observing windows,
supermoons, and lunar eclipses.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from skyfield import api
from skyfield import almanac
from skyfield.api import load
import seaborn as sns

class MoonCalendar:
    def __init__(self, year=2025, location_lat=40.7128, location_lon=-74.0060):
        """
        Initialize the Moon Calendar
        
        Parameters:
        year (int): Year for the calendar
        location_lat (float): Latitude for location (default: NYC)
        location_lon (float): Longitude for location (default: NYC)
        """
        self.year = year
        self.location_lat = location_lat
        self.location_lon = location_lon
        
        # Load Skyfield data
        self.ts = api.load.timescale()
        self.eph = load('de421.bsp')
        
        # Create location
        self.location = self.eph['earth'] + api.Topos(location_lat, location_lon)
        
        # Initialize data storage
        self.moon_data = None
        self.events_data = None
        
    def load_events(self, events_file='events.csv'):
        """Load user events from CSV file"""
        try:
            self.events_data = pd.read_csv(events_file)
            print(f"Loaded {len(self.events_data)} events from {events_file}")
            return True
        except FileNotFoundError:
            print(f"Events file {events_file} not found. Creating template...")
            self.create_events_template()
            return False
    
    def create_events_template(self):
        """Create a template events.csv file"""
        template_data = {
            'date': ['2025-01-15', '2025-02-14', '2025-03-20'],
            'event_name': ['New Year Observing', 'Valentine Stargazing', 'Spring Equinox Party'],
            'event_type': ['observing', 'social', 'celebration'],
            'priority': ['high', 'medium', 'low'],
            'notes': ['Dark sky session', 'Romantic stargazing', 'Equinox celebration']
        }
        template_df = pd.DataFrame(template_data)
        template_df.to_csv('events.csv', index=False)
        print("Created events.csv template. Please edit with your events.")
    
    def calculate_moon_phases(self):
        """Calculate moon phases for the year"""
        start_date = datetime(self.year, 1, 1)
        end_date = datetime(self.year, 12, 31)
        
        # Convert to Skyfield times
        t0 = self.ts.from_datetime(start_date)
        t1 = self.ts.from_datetime(end_date)
        
        # Find moon phases
        t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(self.eph))
        
        moon_phases = []
        for ti, phase in zip(t, y):
            moon_phases.append({
                'datetime': ti.utc_datetime(),
                'phase': phase,
                'phase_name': self.get_phase_name(phase)
            })
        
        return moon_phases
    
    def get_phase_name(self, phase):
        """Convert phase number to name"""
        phase_names = {
            0: 'New Moon',
            1: 'First Quarter',
            2: 'Full Moon',
            3: 'Last Quarter'
        }
        return phase_names.get(phase, 'Unknown')
    
    def calculate_illumination(self, date):
        """Calculate moon illumination for a given date"""
        t = self.ts.from_datetime(date)
        moon = self.eph['moon']
        sun = self.eph['sun']
        
        # Get positions
        moon_pos = moon.at(t)
        sun_pos = sun.at(t)
        
        # Calculate illumination
        moon_geocentric = moon_pos.observe(self.eph['earth']).apparent()
        sun_geocentric = sun_pos.observe(self.eph['earth']).apparent()
        
        # Calculate phase angle and illumination
        phase_angle = moon_geocentric.separation_from(sun_geocentric).degrees
        illumination = (1 + np.cos(np.radians(phase_angle))) / 2
        
        return illumination * 100  # Return as percentage
    
    def calculate_moon_rise_set(self, date):
        """Calculate moon rise and set times for a given date"""
        t = self.ts.from_datetime(date)
        
        # Find moon rise/set times
        f = almanac.risings_and_settings(self.eph, self.eph['moon'], self.location)
        t_rise_set, y = almanac.find_discrete(t, t + 1, f)
        
        rise_times = []
        set_times = []
        
        for ti, is_rising in zip(t_rise_set, y):
            if is_rising:
                rise_times.append(ti.utc_datetime())
            else:
                set_times.append(ti.utc_datetime())
        
        return rise_times, set_times
    
    def identify_dark_sky_windows(self, illumination_threshold=20):
        """Identify periods with low illumination for dark sky observing"""
        # This would analyze the illumination data to find periods
        # where illumination is below the threshold
        pass
    
    def identify_supermoons(self):
        """Identify supermoons (when moon is closest to Earth)"""
        # This would calculate moon distance and identify closest approaches
        pass
    
    def identify_lunar_eclipses(self):
        """Identify lunar eclipses"""
        # This would use Skyfield to find lunar eclipses
        pass
    
    def generate_calendar_data(self):
        """Generate comprehensive calendar data for the year"""
        print("Generating moon calendar data...")
        
        # Calculate moon phases
        moon_phases = self.calculate_moon_phases()
        
        # Create daily data
        start_date = datetime(self.year, 1, 1)
        end_date = datetime(self.year, 12, 31)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        calendar_data = []
        
        for date in date_range:
            illumination = self.calculate_illumination(date)
            rise_times, set_times = self.calculate_moon_rise_set(date)
            
            calendar_data.append({
                'date': date,
                'illumination': illumination,
                'moon_rise': rise_times[0] if rise_times else None,
                'moon_set': set_times[0] if set_times else None,
                'is_dark_sky': illumination < 20
            })
        
        self.moon_data = pd.DataFrame(calendar_data)
        print(f"Generated calendar data for {len(self.moon_data)} days")
        
        return self.moon_data
    
    def plot_calendar(self):
        """Create visualization of the moon calendar"""
        if self.moon_data is None:
            self.generate_calendar_data()
        
        # Set up the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Plot illumination over time
        ax1.plot(self.moon_data['date'], self.moon_data['illumination'], 
                color='blue', alpha=0.7, linewidth=1)
        ax1.fill_between(self.moon_data['date'], self.moon_data['illumination'], 
                         alpha=0.3, color='blue')
        ax1.axhline(y=20, color='red', linestyle='--', alpha=0.7, 
                   label='Dark Sky Threshold (20%)')
        ax1.set_ylabel('Illumination (%)')
        ax1.set_title(f'Moon Illumination Calendar {self.year}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot dark sky windows
        dark_sky_data = self.moon_data[self.moon_data['is_dark_sky']]
        if not dark_sky_data.empty:
            ax2.scatter(dark_sky_data['date'], [1] * len(dark_sky_data), 
                       color='red', alpha=0.6, s=20, label='Dark Sky Windows')
        
        ax2.set_ylabel('Dark Sky Windows')
        ax2.set_title('Dark Sky Observing Opportunities')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
        
        plt.tight_layout()
        plt.show()
    
    def correlate_with_events(self):
        """Correlate moon data with user events"""
        if self.events_data is None:
            print("No events data loaded")
            return
        
        # Convert event dates to datetime
        self.events_data['date'] = pd.to_datetime(self.events_data['date'])
        
        # Merge with moon data
        merged_data = pd.merge(
            self.events_data, 
            self.moon_data, 
            on='date', 
            how='left'
        )
        
        print("Event-Moon Correlation:")
        print(merged_data[['date', 'event_name', 'illumination', 'is_dark_sky']].head(10))
        
        return merged_data

def main():
    """Main function to run the moon calendar"""
    print("Moon Phase Calendar with Events")
    print("=" * 40)
    
    # Initialize calendar
    calendar = MoonCalendar(year=2025)
    
    # Load events
    calendar.load_events()
    
    # Generate calendar data
    calendar.generate_calendar_data()
    
    # Create visualization
    calendar.plot_calendar()
    
    # Correlate with events
    calendar.correlate_with_events()
    
    print("\nCalendar generation complete!")

if __name__ == "__main__":
    main()
