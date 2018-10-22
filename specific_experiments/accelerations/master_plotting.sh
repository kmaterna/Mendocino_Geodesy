# Run the accel_mapping.gmt script
# On different areas. 

outdir="Whole_WUS_lssq_UNR/"

data_file=$outdir"MTJ_2016_lssq.txt"
out_base="_2016_lssq"

./accel_map_gps.gmt $data_file -121.8 -115.0 32.2 37.6 $outdir'SoCal'$out_base
./accel_map_gps.gmt $data_file -125.6 -110.0 32.5 48.5 $outdir'WUS'$out_base
./accel_map_gps.gmt $data_file -123.5 -119.0 35.6 40.0 $outdir'SF'$out_base
./accel_map_gps.gmt $data_file -125.2 -121.0 38.6 43.0 $outdir'MTJ'$out_base
