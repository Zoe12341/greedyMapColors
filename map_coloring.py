# Name:       - Zoe Buck
# References: - https://simple.wikipedia.org/wiki/Four_color_theorem#:~:text=Intuitively%2C%20the%20four%20color%20theorem,adjacent%20have%20the%20same%20color', https://compgeek.co.in/four-colour-problem-by-dsatur/, https://github.com/geopandas/geopandas/issues/1041 

#The following packages are for visualization purposes only!
import numpy as np 
import geopandas as gpd
import geopandas.datasets as data
import matplotlib.pyplot as plt
import csv


#Solving coloring with greedy algorithm


def loadData():
    """Loads data about countries and their neighbors from a CSV file into a dictionary. For example visualization purposes.

    :return: (dict) A dictionary where keys are country names and values are sets of neighboring countries.
    
    >>> world_countries = loadData()
    >>> 'LT' in world_countries  # Check if Lithuania ('LT') is loaded
    True
    """

    world_countries = {}
    with open('color-World-countries.csv') as csvfile: 
        csvreader = csv.reader(csvfile)#, #delimiter=' ', quotechar='|')
        header = csvreader.__next__()
        for row in csvreader:
            country_name = row[0]
            neighbor = row[2]
            if country_name not in world_countries.keys(): #create set
                if neighbor != '':
                    world_countries[country_name] = {neighbor}  
                else: 
                    world_countries[country_name] = {}
            else:
                if neighbor != '':
                    world_countries[country_name].add(neighbor)
    print(world_countries["LT"])
    return world_countries

def most_neighbors(world_countries):
    """Finds the country with the highest number of neighbors.
    
    :param world_countries: (dict) A dictionary where keys are country names and values are sets of neighbors.
    :return: (str) The country with the most neighbors.
    
    >>> world_countries = {"A": {"B", "C"}, "B": {"A"}, "C": {"A", "D"}}
    >>> most_neighbors(world_countries)
    'A'
    """

    max_degree = 0
    max_node = None
    for country in world_countries.keys():
        if len(world_countries[country]) >= max_degree:
            max_degree = len(world_countries[country])
            max_node = country
    return max_node
        


def bubble_sort(countries, graph):
    """Sorts countries by their degree (number of neighbors) in descending order.
    
    :param countries: (list) List of country names.
    :param graph: (dict) A dictionary where keys are country names and values are sets of neighbors.
    :return: (list) The sorted list of countries.
    
    >>> graph = {"A": {"B", "C"}, "B": {"A"}, "C": {"A", "D"}, "D": {"C"}}
    >>> bubble_sort(["A", "B", "C", "D"], graph)
    ['A', 'C', 'B', 'D']
    """
    n = len(countries)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if len(graph[countries[j]]) < len(graph[countries[j + 1]]):
                countries[j], countries[j + 1] = countries[j + 1], countries[j]
    return countries



def greedy_saturation(graph):
    """Applies a DSATUR-based greedy algorithm to color the graph.
    
    :param graph: (dict) A dictionary where keys are country names and values are sets of neighbors.
    :return: (dict) A dictionary mapping each country to its assigned color index (1-based).
    
    Example usage:
    >>> graph = {"A": {"B", "C"}, "B": {"A"}, "C": {"A", "D"}, "D": {"C"}}
    >>> solution = greedy_saturation(graph)
    >>> solution["A"]
    "red"
    """
    # Initial setup
    colors = {}
    saturation = {country: 0 for country in graph}  # Saturation levels
    uncolored = list(graph.keys())  # List of uncolored countries
    
    # Sort countries by number of neighbors in descending order
    uncolored = bubble_sort(uncolored, graph)
    
    available_colors = ["red", "orange", "yellow", "green"]  # Using only 4 colors 

    while uncolored:
        # Choose the next country to color
        current_country = max(uncolored, key=lambda country: (saturation[country], len(graph[country]))) #pick one with most saturation, if there is a tie, use the one with the largest number of neighbors
        
        # Find the colors of the neighboring countries
        neighbor_colors = {colors[neighbor] for neighbor in graph[current_country] if neighbor in colors}

        # Assign the first available color not used by neighbors
        for color in available_colors:
            if color not in neighbor_colors:
                colors[current_country] = color
                break

        # Update saturation levels of neighbors
        for neighbor in graph[current_country]:
            if neighbor not in colors:
                # Increase saturation if this color is new for the neighbor
                neighbor_colors = {colors[n] for n in graph[neighbor] if n in colors}
                saturation[neighbor] = len(neighbor_colors)

        # Remove the colored country from the uncolored list
        uncolored.remove(current_country)

    return colors



def greedy_neighbors(world_countries):
    ''' Greedy Algorithm approach that colors in country with the largets number of neighbors first. 
    Not garenteed to use the least number of colors, but has a maximum number of colors of n-1 where n is the largest number of neighbors any country has
    '''
    """Applies a greedy algorithm to color a map based on neighboring countries. Colors in the countries with the most neighbors first. 
    
    :param world_countries: (dict) A dictionary where keys are country names and values are sets of neighbors.
    :return: (dict) A dictionary where keys are country names and values are assigned colors.
    
    >>> world_countries = {"A": {"B", "C"}, "B": {"A"}, "C": {"A", "D"}, "D": {"C"}}
    >>> solution = greedy_neighbors(world_countries)
    >>> solution["A"]
    'red'
    """

    colorDict = {}
    for country in world_countries.keys():
        colorDict[country]=["red","orange","yellow","green", "blue", "purple"]
    theSolution={}

    while world_countries: 
        node = most_neighbors(world_countries)
        theSolution[node] = colorDict[node][0]
        for neighbor in world_countries[node]:
            if colorDict[node][0] in colorDict[neighbor]: 
                colorDict[neighbor].remove(colorDict[node][0])
        del world_countries[node]
    return theSolution



def mapVisualization(countryColors):

    """Visualizes a map with countries colored based on the given color assignments.
    
    :param countryColors: (dict) A dictionary mapping ISO_A2 country codes to colors.
    :return: None
    
    Example usage:
    >>> countryColors = {"US": "red", "CA": "green", "MX": "blue"}
    >>> mapVisualization(countryColors)
    """
    
    world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")

    # Hard coding ISO_A2 values in for France, Norway, Cyprus, and Portugal becuase I encountered issues with the default values
    #https://github.com/geopandas/geopandas/issues/1041
    world.loc[world['NAME'] == 'France', 'ISO_A2'] = 'FR'
    world.loc[world['NAME'] == 'Norway', 'ISO_A2'] = 'NO'
    world.loc[world['NAME'] == 'N. Cyprus', 'ISO_A2'] = 'CY'
    world.loc[world['NAME'] == 'Somaliland', 'ISO_A2'] = 'SO'


    # Add a new column to the GeoDataFrame for the colors
    world['color'] = world['ISO_A2'].map(countryColors)

    # Fill NaN values with a gray color
    world['color'] = world['color'].fillna('lightgray')

    # Plot the map
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world.boundary.plot(ax=ax, linewidth=1)  # Draw country boundaries
    world.plot(ax=ax, color=world['color'], edgecolor='black')  # Fill countries with specified colors

    # Add a title
    plt.title('Map of Countries Colored with Greedy Neighbor Algorithm', fontsize=15)
    plt.axis('off')  # Turn off axis

    # Show the map
    plt.show()



def main():
    """Main function to load country data, apply greedy coloring algorithms, and visualize the results."""

    countryData = loadData()
    colors = greedy_neighbors(countryData) #uncomment to view results from greedy_neighbors algorithm 

    #colors2 = greedy_saturation(countryData)
    mapVisualization(colors)
    #mapVisualization(colors2)


if __name__ == "__main__":
    main()