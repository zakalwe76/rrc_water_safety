# River Flow

| condition | Fours, Quads, Eights | Singles, Doubles, Pairs |
|-----------|----------------------|-------------------------|
| Black     | >=120                | >=100                   |
| Red       | 100.00 to 119.99     | 75.00 to 99.99          |
| Amber     | 75.00 to 99.99       | 50.00 to 74.99          |
| Green     | 0 to 74.99           | 0 to 49.99              |


# Wind Speed

| condition | Fours, Quads, Eights | Singles, Doubles, Pairs |
|-----------|----------------------|-------------------------|
| Black     | >= 15.6              | >=13.6                  |
| Red       | 13.6 to 15.5         | 11.3 to 13.5            |
| Amber     | 11.3 to 13.5         | 9.0 to 11.2             |
| Green     | 0 to 11.2            | 0 to 8.9                |

# Air Temnperature

| condition | Fours, Quads, Eights | Singles, Doubles, Pairs |
|-----------|----------------------|-------------------------|
| Black     | <=-3.0               | <= 0.0                  |
| Red       | -2.0 to 2.9          | 1.0 to 4.9              |
| Amber     | 3.0 to 6.9           | 5.0 to 8.9              |
| Green     | > 7.0                | > 9.0                   |

# Calculating Overall Rowing Conditions

If there are two or more "Red" conditions or one "Black" condition then the overall conditions are "NO ROWING" and there is no rowing
Otherwise, the overall conditions for a given category ("Fours, Quads, Eights", or "Singles, Doubles, Pairs") are the most severe condition across "River Flow", "Wind Speed", and "Air Temperature" with severities ranked from Least Severe (Green) to Most Severe (Black)
