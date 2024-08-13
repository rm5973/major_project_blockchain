from pythreejs import *
from IPython.display import display
from selenium import webdriver
import time

# Create a 3D scene with a simple cube
scene = Scene(children=[Mesh(geometry=BoxGeometry(1, 1, 1),
                             material=MeshBasicMaterial(color='blue'))])

# Create a perspective camera
camera = PerspectiveCamera(position=[3, 3, 3], fov=20)

# Create a renderer
renderer = Renderer(camera=camera, scene=scene,
                    controls=[OrbitControls(controlling=camera)],
                    width=800, height=600)

# Display the renderer
display(renderer)

# Save the rendered scene as an image
driver = webdriver.Chrome()  # You may need to install the appropriate driver for your browser
driver.get("about:blank")
time.sleep(1)  # Wait for the page to load

# Take a screenshot of the entire browser window
driver.save_screenshot("rendered_image.png")

# Close the browser
driver.quit()
