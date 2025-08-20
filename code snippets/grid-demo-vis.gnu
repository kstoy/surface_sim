set xlabel "X"
set ylabel "Y"
set xrange [0:2]
set yrange [0:2]
set zrange [-2:1]
set term png

do for [ii=1:450] {
    set output sprintf('data/frame%03.0f.png',ii)
    splot 'demo_3x3.dat' every ::1::ii w l ls 1, \
          'demo_3x3.dat' every ::ii::ii w p ls 1
}