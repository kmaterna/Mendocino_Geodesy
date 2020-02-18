# A new function to remove postseismic deformation
# February 17, 2020
# The first model is from Hines et al., JGR, 2016

import numpy as np 
import datetime as dt 
import os, sys
import gps_io_functions
import offsets
import gps_ts_functions



# HELPER FUNCTIONS # 
def get_station_hines(station_name):
	model_file = "../../GPS_POS_DATA/Remove_postseismic/Hines/Stations/"+station_name+"_psmodel.pos";
	if os.path.isfile(model_file):
		[Data0] = gps_io_functions.read_pbo_pos_file(model_file);
	else:
		Data0 = [];
	return Data0;

def fit_offset(dtarray, data, interval, offset_num_days):
	# Solves for offsets at a given time. 
	before_indeces = [];
	after_indeces = [];

	# Find the indeces of nearby days
	for i in range(len(dtarray)):
		deltat_start=dtarray[i]-interval[0];  # the beginning of the interval
		deltat_end = dtarray[i]-interval[1];  # the end of the interval
		if deltat_start.days >= -offset_num_days and deltat_start.days<=0: 
			before_indeces.append(i);
		if deltat_end.days <= offset_num_days and deltat_end.days >= 0: 
			after_indeces.append(i);

	# Identify the value of the offset. 
	if before_indeces==[] or after_indeces==[] or len(before_indeces)==1 or len(after_indeces)==1:
		offset=0;
		print("Warning: no data before or after offset. Returning 0");
	else:
		before_mean= np.nanmean( [data[x] for x in before_indeces] );
		after_mean = np.nanmean( [data[x] for x in after_indeces] );
		offset=after_mean-before_mean;
		if offset==np.nan:
			print("Warning: np.nan offset found. Returning 0");
			offset=0;
	return offset;



def remove_by_model(Data0):
	# Right now configured for the Hines data. 
	starttime1=dt.datetime.strptime("20100403","%Y%m%d");
	endtime1=dt.datetime.strptime("20100405","%Y%m%d");
	starttime2=dt.datetime.strptime("20150328","%Y%m%d");
	endtime2=dt.datetime.strptime("20150330","%Y%m%d");	

	# Input Hines data. 
	model_data = get_station_hines(Data0.name);

	if model_data ==[]:
		return Data0;

	# These will be the same size. 
	# Data0, model = gps_ts_functions.pair_gps_model_keeping_gps(Data0, model_data);  # leaves data outside of the model timespan
	Data0, model = gps_ts_functions.pair_gps_model(Data0, model_data);  # removes data outside of the model timespan. 
	
	# Subtract the model from the data. 
	dtarray=[]; dE_gps=[]; dN_gps=[]; dU_gps=[]; Se_gps=[]; Sn_gps=[]; Su_gps=[];
	for i in range(len(Data0.dtarray)):
		dtarray.append(Data0.dtarray[i]);
		dE_gps.append(Data0.dE[i] - model.dE[i]);
		dN_gps.append(Data0.dN[i] - model.dN[i]);
		dU_gps.append(Data0.dU[i] - model.dU[i]);
		Se_gps.append(Data0.Se[i]);
		Sn_gps.append(Data0.Sn[i]);
		Su_gps.append(Data0.Su[i]);

	# In this method, we correct for offsets at the beginning and end of the modeled time series. 
	interval1 = [starttime1, endtime1];
	east_offset1 = fit_offset(dtarray, dE_gps, interval1, 20);
	north_offset1 = fit_offset(dtarray, dN_gps, interval1, 20);
	vert_offset1 = fit_offset(dtarray, dU_gps, interval1, 20);
	interval2 = [starttime2, endtime2];
	east_offset2 = fit_offset(dtarray, dE_gps, interval2, 20);
	north_offset2 = fit_offset(dtarray, dN_gps, interval2, 20);
	vert_offset2 = fit_offset(dtarray, dU_gps, interval2, 20);

	offsets_obj = offsets.Offsets(e_offsets=[east_offset1, east_offset2], 
		n_offsets=[north_offset1, north_offset2], u_offsets=[vert_offset1, vert_offset2], evdts=[starttime1, starttime2]);

	corrected_data = gps_io_functions.Timeseries(name=Data0.name, coords=Data0.coords, dtarray=dtarray, dE=dE_gps, dN=dN_gps, dU=dU_gps, Se=Se_gps, Sn=Sn_gps, Su=Su_gps, EQtimes=Data0.EQtimes);
	corrected_data = offsets.remove_offsets(corrected_data, offsets_obj);
	# corrected_data = Data0;
	return corrected_data;




