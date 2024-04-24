
![image](https://github.com/akaraoglu/visuAlysium/assets/32932292/91e226a9-620d-4b3c-8d75-7dbc22703eb5)
# An experimental image editor

This application is a versatile image visualizer and editor that showcases the robust capabilities of Python combined with PyQt. It provides users with intuitive tools for basic image adjustments, including control over brightness and color settings. The software stands out with its extensive curve editing functionality, which allows advanced tone mapping to enhance details in shadows and highlights.

Designed to serve as a foundational platform, the application can be expanded or customized for a range of purposes, from educational and experimental tools to professional-grade image editing software. It serves as an ideal starting point for developers looking to create more specialized graphical applications.

As an open-source project, we actively encourage community involvement. The project provides a fertile ground for developers and users to adapt the software to meet their specific requirements or to contribute to its ongoing development. Whether you are looking to implement new features, refine existing ones, or simply learn from the architecture, your contributions are welcome.


# Getting Started

## Installing
A step by step series of examples that tell you how to get a development environment running:
```bash
git clone https://github.com/akaraoglu/visuAlysium.git
```

if VSCode:
```bash
Ctrl+Shift+B to build the project.
It will setup the project details automatically. 
```
else:    
```bash
cd visuAlysium
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
pip install -r requirements.txt
```
Run the project:
```bash
python main.py
```

## Example Main Window
![image](https://github.com/akaraoglu/visuAlysium/assets/32932292/a3310057-f709-4284-b913-db6aaf67e688)

## Example Editing Window
![image](https://github.com/akaraoglu/visuAlysium/assets/32932292/7efdd0c4-0115-40d2-bf93-7df47acf8c7d)

## Prerequisites
Before installing the project, ensure you have Python installed on your machine. Download it from [python.org](https://www.python.org/downloads/).

## Built With
PyQT6 - The GUI toolkit used
OpenCV - Open Source Computer Vision Library
rawpy - Used for processing RAW images
SciPy - Used for scientific computing and technical computing
NumPy - Fundamental package for scientific computing with Python
matplotlib - Plotting library for Python and its numerical mathematics extension NumPy

## Authors
- Ali Karaoglu

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE.md file for details.
