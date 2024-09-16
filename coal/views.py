from django.shortcuts import render, redirect
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
from django.conf import settings
from .models import MiningActivity
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from django.conf import settings
import matplotlib.dates as mdates
from django.db.models import Count, Sum


def calculate_carbon_emissions(fuel_type, fuel_consumption, energy_grid_mix, energy_consumption, explosives_type, total_explosives_used):
    # Define emission factors
    fuel_emission_factors = {
        "Diesel": 2.68,  # kg CO₂ per liter
        "Petrol": 2.31,  # kg CO₂ per liter
        "LNG": 1.89,     # kg CO₂ per liter
        "CNG": 2.75      # kg CO₂ per cubic meter
    }
    electricity_emission_factors = {
        'coal': 0.92, 
        'natural_gas': 0.5, 
        'renewable': 0
    }
    explosives_emission_factors = {
        "dynamite": 0.4,     # kg CO₂ per kg
        "ANFO": 0.3,        # kg CO₂ per kg
        "emulsions": 0.35,  # kg CO₂ per kg
        "water_gels": 0.32  # kg CO₂ per kg
    }

    # Calculate emissions
    fuel_carbon_emission = fuel_emission_factors.get(fuel_type, 0) * fuel_consumption
    electricity_emission = electricity_emission_factors.get(energy_grid_mix, 0) * energy_consumption
    explosives_emission = explosives_emission_factors.get(explosives_type, 0) * total_explosives_used

    # Return total emissions
    return fuel_carbon_emission + electricity_emission + explosives_emission




def plot_pie_chart(fuels_percentage):
    # Labels for each fuel type
    all_labels = ['Diesel', 'Petrol', 'LNG', 'CNG']
    
    # Filter out zero percentages
    filtered_labels = [label for label, percentage in zip(all_labels, fuels_percentage) if percentage > 0]
    filtered_sizes = [size for size in fuels_percentage if size > 0]
    
    # Use a more vibrant color palette with hex values
    colors = ['#ff5733', '#33ccff', '#ffcc00', '#cc33ff']  # Adjusted to ensure enough colors for non-zero slices
    
    # Create the pie chart
    plt.figure(figsize=(7, 7))
    
    # Add explode to separate slices slightly
    explode = [0.05] * len(filtered_labels)  # Slightly offset each slice
    
    wedges, texts, autotexts = plt.pie(filtered_sizes, 
                                       explode=explode, 
                                       labels=filtered_labels, 
                                       colors=colors[:len(filtered_labels)], 
                                       autopct='%1.1f%%', 
                                       startangle=140, 
                                       pctdistance=0.85,  # Puts percentages closer to the center
                                       textprops={'color': 'black', 'fontsize': 12, 'fontweight': 'bold'},  # Labels in black and bold
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 2},  # Adding edge color and width
                                       shadow=True  # Adds shadow for a 3D effect
                                      )
    
    # Add styling to percentage texts
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
    
    # Draw a white circle in the center to create a donut-style pie chart
    center_circle = plt.Circle((0, 0), 0.70, fc='white')
    plt.gca().add_artist(center_circle)
    
    # Add the title
    plt.title('Fuel Usage Distribution', fontsize=16, fontweight='bold', color='black')
    
    # Equal axis ensures the pie chart is drawn as a circle.
    plt.axis('equal')
    
    # Save the plot as an image file in the static directory
    static_dir = settings.STATICFILES_DIRS[0]  # Path to the first static directory
    image_path = os.path.join(static_dir, 'pie_chart.png')
    
    plt.savefig(image_path, transparent=True, bbox_inches='tight')
    plt.close()  # Close the figure to free up memory

    return image_path



def plot_emissions_graph(dates, total_emissions, filename):
    # Ensure the media directory exists
    media_path = settings.MEDIA_ROOT
    if not os.path.exists(media_path):
        os.makedirs(media_path)
    
    # Define the full path for the saved plot
    file_path = os.path.join(media_path, filename)
    
    # Create and customize the plot
    plt.figure(figsize=(12, 6))
    plt.plot(dates, total_emissions, marker='o', linestyle='-', color='teal', linewidth=2, markersize=6)
    plt.xlabel('Date of Activity', fontsize=14)
    plt.ylabel('Total Emissions (kg CO2)', fontsize=14)
    plt.title('Total Emissions Over Time', fontsize=16, fontweight='bold')

    # Set the ticks to show for each date
    plt.xticks(dates)  # Set x-ticks to the actual dates

    # Format the x-axis to display dates as 'YYYY-MM-DD'
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    # Rotate the x-axis labels to prevent overlap
    plt.gcf().autofmt_xdate()

    # Add grid and legend
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(['Total Emissions'], loc='upper right')

    plt.tight_layout()
    
    # Save the plot
    plt.savefig(file_path)
    plt.close()  # Close the plot to free memory

def home(request):
    return render(request, 'coal/index.html')

def visme(request):
    return render(request, 'coal/visme.html')

def dashboard(request):
    try:
        # Query and count occurrences of each fuel type
        fuel_counts = MiningActivity.objects.values('fuel_type').annotate(count=Count('fuel_type'))

        # Initialize the fuels dictionary
        fuels = {'Diesel': 0, 'Petrol': 0, 'LNG': 0, 'CNG': 0}

        # Populate the dictionary based on the counts
        for entry in fuel_counts:
            fuel_type = entry['fuel_type']
            count = entry['count']
            if fuel_type in fuels:
                fuels[fuel_type] = count

        print(fuels)
        total_fuels = sum(fuels.values())

    
        fuel_percentages = [((count / total_fuels) * 100) for fuel, count in fuels.items()]

        print(fuel_percentages)
        plot_url = plot_pie_chart(fuel_percentages)
        emissions_url = os.path.join(settings.MEDIA_URL, 'temp.png')
        print('Emission URL:', emissions_url)
        # Sum of fuel_consumption
        total_fuel_consumption = MiningActivity.objects.aggregate(total_fuel=Sum('fuel_consumption'))['total_fuel'] or 0
        # Sum of coal_extracted
        total_coal_extracted = MiningActivity.objects.aggregate(total_coal=Sum('quantity_extracted'))['total_coal'] or 0
        # Sum of electricity_used
        total_electricity_used = MiningActivity.objects.aggregate(total_energy=Sum('energy_consumption'))['total_energy'] or 0
        # Sum of carbon_emitted
        total_carbon_emitted = MiningActivity.objects.aggregate(total_carbon=Sum('carbon_emitted'))['total_carbon'] or 0

        return render(request, 'coal/dashboard.html',
            {'title':'Dashboard','plot_url':plot_url, 'emissions_url':emissions_url,
            'total_fuel_consumption':total_fuel_consumption, 'total_coal_extracted':total_coal_extracted,
            'total_electricity_used':total_electricity_used, 'total_carbon_emitted':total_carbon_emitted})
    except Exception as E:
        print("Error:", E)
        return redirect(form)

def form(request):
    if request.method == "POST":
        # Capture form values from POST request
        activity_date_str = request.POST.get('activity_date')
        material_type = request.POST.get('material_type')
        total_quantity = int(request.POST.get('total_quantity'))
        energy_consumption = int(request.POST.get('energy_consumption'))
        fuel_consumption = int(request.POST.get('fuel_consumption'))
        energy_grid_mix = request.POST.get('energy_grid_mix')
        fuel_type = request.POST.get('fuel_type')
        explosives_type = request.POST.get('explosives_type')
        explosives_amount = int(request.POST.get('explosives_amount'))  # New field
        operational_hours_str = request.POST.get('operational_hours')
        downtime_duration_str = request.POST.get('downtime_duration')
        production_rate = float(request.POST.get('production_rate'))
        trucks_loaded = int(request.POST.get('trucks_loaded'))
        distance_mined = int(request.POST.get('distance_mined'))

        # Convert date string to date object
        try:
            activity_date = datetime.strptime(activity_date_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'coal/form.html', {'error': 'Invalid date format'})

        # Convert duration strings to timedelta objects
        def parse_duration(duration_str):
            """Convert a HH:MM or HH:MM:SS string into a timedelta object."""
            parts = list(map(int, duration_str.split(':')))
            if len(parts) == 2:
                # If format is HH:MM
                hours, minutes = parts
                seconds = 0
            elif len(parts) == 3:
                # If format is HH:MM:SS
                hours, minutes, seconds = parts
            else:
                return timedelta()  # Default to zero duration if parsing fails
            
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)

        operational_hours = parse_duration(operational_hours_str)
        downtime_duration = parse_duration(downtime_duration_str)

        # Create a new MiningActivity instance
        mining_activity = MiningActivity(
            date_of_activity=activity_date,
            material_extracted=material_type,
            quantity_extracted=total_quantity,
            energy_consumption=energy_consumption,
            fuel_consumption=fuel_consumption,
            energy_grid_mix=energy_grid_mix,
            fuel_type=fuel_type,
            explosives_type=explosives_type,
            total_explosives_used=explosives_amount,  # New field
            operational_hours=operational_hours,
            downtime_duration=downtime_duration,
            production_rate=production_rate,
            trucks_loaded=trucks_loaded,
            distance_mined=distance_mined,
            carbon_emitted=calculate_carbon_emissions(fuel_type, fuel_consumption, energy_grid_mix, energy_consumption, explosives_type, explosives_amount)
        )

        mining_activity.save()

        total_emissions = []
        dates = []
        activities_asc = MiningActivity.objects.all().order_by('date_of_activity')
        print("Activities asc:",activities_asc)
        for activity in activities_asc:
            total_emissions.append(activity.carbon_emitted)
            dates.append(activity.date_of_activity)
        print("Total Emissions:", total_emissions)
        print("Dates:", dates)
        plot_emissions_graph(dates, total_emissions, 'temp.png')
        plot_url = os.path.join(settings.MEDIA_URL, 'temp.png')
        print("Plot URL:", plot_url)
        # Render the template with the mining activity object
        return redirect(dashboard)
    else:
        # Render the form for GET request
        return render(request, 'coal/form.html', {'title': 'Input Form'})