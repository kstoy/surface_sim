set term jpeg
set output "demo.jpeg"

set xrange [-0.2:1.2]
set yrange [-0.2:1.2]
set zrange [-2:2]

set xlabel "X"
set ylabel "Y"
set zlabel "Z"

set title "Ball path"

splot "demo.dat" with lines notitle
