# Author: G N Paneendra

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from datetime import datetime
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import sys
from rich.progress import track

# Functions

# For mean subtraction
def meansub(ch_v):
	ch_mean = np.mean(ch_v, axis=0)
	ch_v_mean_sub = ch_v - ch_mean
	return ch_v_mean_sub

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
		ch1_mag = (np.abs(fft_ch1))**2 / N**2
		ch2_mag = (np.abs(fft_ch2))**2 / N**2
		  
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
		
		rfi_mask_range = (bp_freq >= 320e6) & (bp_freq <= 340e6)
		rfim = spec[:, rfi_mask_range]
		
		rfi_replace = np.median(rfim, axis=1)

		rfi_bands = [(180e6, 181.5e6), (190e6, 190.2e6), (197.6e6, 198.2e6), (199.88e6, 200.1e6), (209.8e6, 210.25e6), (229.85e6, 230.05e6), (243e6, 270e6)]

		for low, high in rfi_bands:
			rfi_band_mask = (bp_freq >= low) & (bp_freq <= high)
			rfirows = spec[:,rfi_band_mask]
			replace_block = np.tile(rfi_replace, (rfirows.shape[1], 1))
			replace_block = np.array(replace_block)
			replace_block = replace_block.T
			spec[:,rfi_band_mask] = replace_block
			
	return bp_freq, bp_spec1, bp_spec2, bp_both
	
# Function to plot
def plot(spec, freq, time, name):
	# Summing of the spectrum horizontally and vertically for cross correlated spectrum
	ver_sum_spec = np.mean(spec, axis = 1)
	hor_sum_spec = np.mean(spec, axis = 0)
	
	v = np.std(hor_sum_spec)
	vh = 2*v
	
	# TO PRODUCE SPECTROGRAPH OF ch 1
	plt.figure(figsize=(18, 12))
	gs = GridSpec(2, 2, width_ratios=[1, 2], height_ratios=[2, 1])

	# Subplot - 1
	plt.subplot(gs[0, 0])
	plt.plot(hor_sum_spec, freq)
	plt.xlabel('Power', fontsize=12)
	plt.ylabel('Frequency (MHz)', fontsize=12)
	plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x * 1e-6:.0f}'))
	plt.ylim(freq[0], freq[len(freq)-1])
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)

	# Subplot - 2 (Waterfall plot)
	plt.subplot(gs[0, 1])
	plt.imshow(spec.T, aspect='auto', cmap='jet', vmin=0, vmax=vh, extent=[time[0], time[-1], freq[0], freq[-1]], origin='lower')
	#plt.colorbar(label='Power')
	plt.title(f"{date}, {start_time} - {end_time}, Gauribidanur Two-Element Interferometer Spectrograph (RRI)- {name}", fontsize=16)
	plt.xlabel('Time (UTC)', fontsize=12)
	plt.ylabel('Frequency (MHz)', fontsize=12)
	plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x * 1e-6:.0f}'))
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)

	# Subplot - 3
	plt.subplot(gs[1, 1])
	plt.plot(time, ver_sum_spec)
	plt.xlabel('Time (UTC)', fontsize=12)
	plt.ylabel('Power', fontsize=12)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
	plt.xlim(time[0], time[len(time)-1])
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)
	
	plt.tight_layout()
	
	filename = f'{date}_TWIN_{name}_{time_1_name}_{time_n_name}.pdf'
	full_path = os.path.join(output_directory, filename)
	plt.savefig(full_path, dpi=400)
	print(f'\nFigure saved as {filename} in {output_directory}')
	
	plt.show()
	
path = r'~/path/to/data/combined/2025_05_30.csv'
#path = str(sys.argv[1])

file_name = os.path.basename(os.path.normpath(path))
print(f"\nCurrent file: {file_name}")

print("\nReading the file...", end=" ")
df = pd.read_csv(path)
ch1_v = df.iloc[:, 1:9953]
ch2_v = df.iloc[:, 9953:df.shape[1]]
date_time = df.iloc[:, 0]

ch1_v = np.array(ch1_v)
ch2_v = np.array(ch2_v)
utc_time = np.array([datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in date_time])
print("Done")

date = utc_time[0].strftime('%Y-%m-%d')
time_1 = utc_time[0].strftime('%H:%M:%S')
time_n = utc_time[-1].strftime('%H:%M:%S')
print(f"\nObservation date: {date}")
print(f"Observation time(UT): {time_1} - {time_n} ")

print("\nPerforming mean subtraction...", end=" ")
# Mean subtraction
ch1_v_mean_sub = meansub(ch1_v)
ch2_v_mean_sub = meansub(ch2_v)
print("Done")

# Sampling parameter
sampling_rate = 1.25e9  # in Hz
fft_length = len(ch1_v_mean_sub[0])

# Performing FFT
ch1_spec, ch2_spec, cross_spec = fft(ch1_v_mean_sub, ch2_v_mean_sub, fft_length)

# Frequency axis for the FFT (only positive frequencies)
frequencies = np.fft.fftfreq(fft_length, 1 / sampling_rate)[:fft_length // 2]
cn = np.arange(len(frequencies))

# Band pass isolation 
bp_frequencies, ch1_bp_spec, ch2_bp_spec, cross_bp_spec = bpirm(frequencies, ch1_spec, ch2_spec, cross_spec)
bpcn = np.arange(len(bp_frequencies))

output_directory = os.path.expanduser(f'~/path/to/output/{date}')
os.makedirs(output_directory, exist_ok=True)

plot(ch1_bp_spec, bp_frequencies, selected_time, name = 'Channel 1')
plot(ch2_bp_spec, bp_frequencies, selected_time, name = 'Channel 2')
plot(cross_bp_spec, bp_frequencies, selected_time, name = 'Correlated')
