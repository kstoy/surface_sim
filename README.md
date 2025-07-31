<h1>Surface-based manipulation simulation</h1>
<p>This project simulates a surface modelled as a fan of catenery curves connecting the three corners whose height can be controlled. It also simulates a ball moving around on the surface under the influence of gravity, but with no friction. The simulation builds on numpy and scipy (for a numerical solver). The visualization depends on matplotlib and Gnuplot.</p> 
 

<picture>
 <img alt="A gif of the surface" src="https://github.com/kstoy/surface_sim/blob/main/demo-w-visualization.gif">
</picture>


<p>This gif is the result of running the demo file demo-w-visualization.py. It shows the surface and the ball moving on this moving surface. Note, that the ball falls of the surface to demonstrate that in this case the z coordinate (the height) is set to -1.0. However, the rest of the system still acts as if it is on a surface that extends beyond what is shown.</p>

<picture>
 <img alt="The path of the ball on the surface" src="https://github.com/kstoy/surface_sim/blob/main/demo.jpeg">
</picture>

<p>It also possible to run the file demo.py. This generates a file demo.dat that contains the path of the ball in x, y, and z. This data can be visualized using the demo-vis.gnu which is a Gnuplot script. The path of the ball is identical to the one shown in the gif above.</p> 
