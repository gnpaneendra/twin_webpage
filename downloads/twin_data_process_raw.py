# Author: G N PANEENDRA

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.ticker as mtick
from matplotlib.ticker import MaxNLocator
import os
import sys
import glob
from tqdm import tqdm

# Fucntions

# To extract time from filenames and convert them to UTC
def extract_utc_time_from_filename(filename):
	basename = os.path.basename(filename)
	time_str = basename.split('_')[3] + '_' + basename.split('_')[4].split('.')[0]
	ist_time = datetime.strptime(time_str, '%Y-%m-%d_%H-%M-%S')
	ist_offset = timedelta(seconds=19800)
	utc_time = ist_time - ist_offset
	return utc_time

# For mean subtraction
def meansub(antenna_v):
	antenna_mean = np.mean(antenna_v, axis=0)
	antenna_v_mean_sub = antenna_v - antenna_mean
	return antenna_v_mean_sub

# FFT
def fft(ch1_v, ch2_v, fft_length):
	ch1_spec = []
	ch2_spec = []
	cross_spec = []
	
	for anv in range(len(ch1_v[:,0])):			
		# Perform FFT
		fft_ch1 = np.fft.fft(ch1_v[anv,:])
		fft_ch2 = np.fft.fft(ch2_v[anv,:])
		N = len(ch1_v[anv,:])
		
		# Calculating the power
		ch1_mag = (np.abs(fft_ch1))**2 / N
		ch2_mag = (np.abs(fft_ch2))**2 / N
		  
		# Taking only the positive frequencies
		ch1_spec.append(ch1_mag[:fft_length //2])
		ch2_spec.append(ch2_mag[:fft_length //2])
		   
		# Correlation
		cross_power = fft_ch1 * np.conj(fft_ch2)
		   
		# Calculate correlation power
		cross_spectrum_magnitude = (np.abs(cross_power))**2 / N**2
				
		# Taking only the positive frequencies
		cross_spec.append(cross_spectrum_magnitude[:fft_length // 2])
		
	ch1_spec = np.array(ch1_spec)
	ch2_spec = np.array(ch2_spec)
	cross_spec = np.array(cross_spec)
		
	return ch1_spec, ch2_spec, cross_spec

# Bandpass isolation and satellite RFI masking
def bpirm(freq, spec1, spec2, both):

	# Pass band isolation
	freq_mask = (freq >= 179e6) & (freq <= 361e6)
	bp_freq = freq[freq_mask]
	bp_spec1 = spec1[:, freq_mask]
	bp_spec2 = spec2[:, freq_mask]
	bp_both = both[:, freq_mask]

	for spec in(bp_spec1, bp_spec2, bp_both):			
		
		non_rfi_mask_range = (bp_freq >= 350e6) & (bp_freq <= 360e6)
		nrfim = spec[:, non_rfi_mask_range]
		rfi_replace = np.median(non_rfi_mask_range)

		rfi_bands = [(180e6, 181.5e6), (220e6, 222e6), (238.5e6, 241.5e6), (243e6, 271e6), (278e6, 283e6), (320e6, 322e6), (343.9e6, 345e6), (347e6, 351e6)]

		for low, high in rfi_bands:
			rfi_band_mask = (bp_freq >= low) & (bp_freq <= high)
			rfirows = spec[:,rfi_band_mask]
			replace_block = np.tile(rfi_replace, (rfirows.shape[1], 1))
			replace_block = np.array(replace_block)
			replace_block = replace_block.T
			spec[:,rfi_band_mask] = replace_block

	return bp_freq, bp_spec1, bp_spec2, bp_both

def plot(spec, freq, time, name):
	
	# Summing of the spectrum horizontally and vertically
	ver_sum_spec = np.mean(spec, axis = 1)
	hor_sum_spec = np.mean(spec, axis = 0)
	
	xm = np.std(hor_sum_spec)
	xmax_1 = 3*xm
	xmax_2 = 3*xm
	ym = np.std(ver_sum_spec)
	ymax = 0.07*ym
	ymin = np.min(ver_sum_spec)/2
	
	# To convert datetime to Matplotlib numeric time
	time_num = mdates.date2num(time)
	
	desired_ticks = 10
	tick_times = np.linspace(time_num[0], time_num[-1], desired_ticks) 

	fig = plt.figure(figsize=(22, 12))
	gs = GridSpec(2, 2, width_ratios=[1, 3], height_ratios=[3, 1])
	fig.suptitle(f"{date} Gauribidanur Two-Element Interferometer (TWIN) Spectrograph (RRI)- {name}, {time_1} - {time_n}", fontsize=15)

	# Subplot - 1
	ax1 = fig.add_subplot(gs[0, 0])
	ax1.plot(hor_sum_spec, freq)
	ax1.set_xlabel('Power', fontsize=14)
	ax1.set_ylabel('Frequency (MHz)', fontsize=14)
	ax1.yaxis.set_major_locator(MaxNLocator(prune=None))
	ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x * 1e-6:.0f}'))
	ax1.set_ylim(freq[0], freq[len(freq)-1])
	ax1.tick_params(axis='both', labelsize=14)
#	ax1.set_xlim(0, xmax_1)
	
	# Subplot - 2 (Waterfall plot)
	ax2 = fig.add_subplot(gs[0, 1])
	c = ax2.imshow(spec.T, aspect='auto', cmap='jet',
		vmin=0, vmax=xmax_2,
		extent=[time_num[0], time_num[-1], freq[0], freq[-1]],
		origin='lower')
	ax2.set_xlabel('Time (UTC)', fontsize=14)
	ax2.set_ylabel('Frequency (MHz)', fontsize=14)
	ax2.yaxis.set_major_locator(MaxNLocator(prune=None))
	ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x * 1e-6:.0f}'))
	ax2.xaxis_date()
	ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
	ax2.set_xticks(tick_times)
	ax2.set_xticklabels([mdates.num2date(t).strftime('%H:%M') for t in tick_times])
	ax2.tick_params(axis='both', labelsize=14)
	#fig.colorbar(c, ax=ax2)

	# Subplot - 3
	ax3 = fig.add_subplot(gs[1, 1])
	ax3.plot(time, ver_sum_spec)
	ax3.set_xlabel('Time (UTC)', fontsize=14)
	ax3.set_ylabel('Power', fontsize=14)
	ax3.xaxis_date()
	ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
	ax3.set_xticks(tick_times)
	ax3.set_xticklabels([mdates.num2date(t).strftime('%H:%M') for t in tick_times])
	ax3.set_xlim(time[0], time[len(time)-1])
	#ax3.set_ylim(ymin, ymax)
	ax3.tick_params(axis='both', labelsize=14)
	
	fig.tight_layout()
	
	filename = f'{date_name}_TWIN_{name}_{time_1_name}_{time_n_name}.pdf'
	full_path = os.path.join(output_directory, filename)
	plt.savefig(full_path, dpi=400)
	print(f'\nFigure saved as {filename} in {output_directory}')
	
	plt.show()

path = r'/path/to/data/raw/2025_11_18/'
#path = str(sys.argv[1])

print(f"\nData directory: {path}")

nf = int(os.popen(f"ls {path}/*.csv | wc -l").read().strip())
print(f"\nNo. of files: {nf}")
if nf == 0:
	sys.exit("There are no files in this folder")

# Sort the files based on the time and read each .csv file
files = glob.glob(os.path.join(path, '*.csv'))
files_sorted_by_time = sorted(files, key=extract_utc_time_from_filename)
print("\nFiles are sorted according to time")


date = extract_utc_time_from_filename(files_sorted_by_time[0]).strftime('%Y/%m/%d')
date_name = extract_utc_time_from_filename(files_sorted_by_time[0]).strftime('%Y-%m-%d')
time_1 = extract_utc_time_from_filename(files_sorted_by_time[0]).strftime('%H:%M:%S')
time_n = extract_utc_time_from_filename(files_sorted_by_time[-1]).strftime('%H:%M:%S')
time_1_name = extract_utc_time_from_filename(files_sorted_by_time[0]).strftime('%H-%M-%S')
time_n_name = extract_utc_time_from_filename(files_sorted_by_time[-1]).strftime('%H-%M-%S')
print(f"\nObservation date: {date}")
print(f"Observation time(UT): {time_1} - {time_n}\n")

print("Reading the file...")
ch1 = []
ch2 = []
time_values = []

for filename in tqdm(files_sorted_by_time):
	
	df = pd.read_csv(filename)
	CH1 = df.iloc[:, 0]
	CH2 = df.iloc[:, 1]                             
	
	ch1.append(CH1)
	ch2.append(CH2)
	
	time_values.append(extract_utc_time_from_filename(filename))

month = date.split('/')[1]
year = date.split('/')[0]

#utc_time = np.array([t.strftime('%H:%M') for t in time_values])
utc_time = np.array(time_values)
ch1_v = np.array(ch1)
ch2_v = np.array(ch2)
print("Done")

print("\nPerforming mean subtraction...", end=" ")
# Mean subtraction
ch1_v_mean_sub = meansub(ch1_v)
ch2_v_mean_sub = meansub(ch2_v)
print("Done")

print("\nPerforming FFT...", end=" ")
# Sampling parameter
sampling_rate = 1.25e9  # in Hz
fft_length = len(ch1_v_mean_sub[0])

# Frequency axis for the FFT (only positive frequencies)
frequencies = np.fft.fftfreq(fft_length, 1 / sampling_rate)[:fft_length // 2]

# Performing FFT
ch1_spec, ch2_spec, crc_spec = fft(ch1_v_mean_sub, ch2_v_mean_sub, fft_length)
print("Done")

print("\nBand pass isolation and frequency domaind RFI Mitigation...", end=" ")
# rfim_Band pass isolation 
bp_frequencies, ch1_bp_spec, ch2_bp_spec, crc_bp_spec = bpirm(frequencies, ch1_spec, ch2_spec, crc_spec)
print("Done")

output_directory = os.path.expanduser(f'~/path/to/output/{date_name}')
os.makedirs(output_directory, exist_ok=True)

# Plotting
plot(ch1_bp_spec, bp_frequencies, utc_time, name = 'Channel-1')
plot(ch2_bp_spec, bp_frequencies, utc_time, name = 'Channel-2')
plot(crc_bp_spec, bp_frequencies, utc_time, name = 'Cross-corelated')
