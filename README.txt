This project is an interactive data visualization dashboard built using Dash and Plotly. It analyzes how an NFL Team's passing defense performs based on different field positions, defensive alignments, and offensive formations. It displays average expected points added (EPA) for each matchup, helping gain insight into defensive efficiency across the field.

Dashboard Features

Interactive Filters:
- Select one or more Field Zones 
	- Example": "Backed Up" and "Midfield"
- Select one or more Defensive Alignments
	- Example: 3-4, Nickel and Dime

Heatmap Output:
- Rows: Defensive Alignments
- Columns: Offensive Formations
- Color & values: Average EPA allowed by the Team defense


How to Run the App
- Install dependencies:
	- pip install dash pandas plotly
- Run the application:
	- python football_project.py
	OR
	- run through the python file and it will give the http to go to. Use in Google Chrome
- Open Google Chrome to:
	- http://localhost:8050