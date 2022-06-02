# Input ...........................................................................................
# Directories
path_idx = './data/raw/GSIM_GRDC_dictionary.csv'
path_grdc = './data/raw/GRDC_discharges.csv'
path_gsim = './data/raw/GSIM_discharges.csv'
kge_limit = 0.95

# Plotting
plot = False
export = False

# Packages ........................................................................................
import pandas, datetime, numpy
import matplotlib.pyplot as plt

# Processing ......................................................................................
# Importing dataframes
df_idx  = pandas.read_csv(path_idx, sep=';', index_col=None)
df_idx = df_idx[df_idx.Agree == 1]
n = df_idx.shape[0]

# Filtering data based on error and correlation
df_idx = df_idx.dropna(how='any', axis=0).sort_values(by='KGE', ascending=True).reset_index(drop=True)
df_idx = df_idx[(df_idx.KGE >= kge_limit) & (df_idx['T-test'] >= 0.05) & (df_idx['F-test'] >= 0.05)]
stations_dict = dict(zip(df_idx.GSIM, df_idx.GRDC))
stations_sel = list(stations_dict.keys())
print(f'Stations considered: {df_idx.shape[0]}/{n} ({int(round(df_idx.shape[0]/n*100,0))}%)')

# Importing time-series
df_gsim = pandas.read_csv(path_gsim, sep=';', index_col=0).T
df_grdc = pandas.read_csv(path_grdc, sep=';', index_col=0)
df_grdc.index, df_gsim.index = pandas.to_datetime(df_grdc.index), pandas.to_datetime(df_gsim.index)
df_grdc = df_grdc.groupby(pandas.Grouper(freq='MS')).mean()

# Plotting
if plot == True:
    print('Plotting started...')
    
    # Time framing dataframes
    df_gsim_tf = df_gsim[(df_gsim.index >= datetime.datetime(1980,1,1)) & (df_gsim.index <= datetime.datetime(2015,12,31))]
    df_grdc_tf = df_grdc[(df_grdc.index >= datetime.datetime(1980,1,1)) & (df_grdc.index <= datetime.datetime(2015,12,31))]
    print("  '-> Datasets imported and formatted")

    # Plotting: comparing time-series
    for row,col in df_idx.iterrows():
        grdc, gsim = df_grdc_tf.loc[:,str(col['GRDC'])], df_gsim_tf.loc[:,str(col['GSIM'])]
        df_tmp = pandas.DataFrame([grdc, gsim], index=['grdc','gsim']).T
        df_tmp['resid'] = df_tmp.gsim - df_tmp.grdc
        
        fig, (ax0, ax1, ax2) = plt.subplots(1, 3, gridspec_kw={'width_ratios': [1,3,3]}, figsize=(30,5), facecolor='w', edgecolor='k')
        title = f"Station: {col['GRDC']} ({col['GSIM']})  |  cumulative error = {round(col['Error_m3/s'],3)} m3/s  |  NRMSE = {round(col['NRMSE'],4)}  |  KGE = {round(col['KGE'],2)}  |  T-test = {round(col['T-test'],4)}  |  F-test = {round(col['F-test'],4)}  |  distance = {int(col['Distance_m'])} m  |  number of common months = {int(col['Months'])}  |  name: [{col['Station_grdc']}] - [{col['Station_gsim']}]  |  river: [{col['River_grdc']}] - [{col['River_gsim']}]"
        plt.suptitle(title,fontsize=14, y=0.96)

        # Plot 1:1
        vmax = max(gsim.max().max(), grdc.max().max())
        ax0.scatter(gsim, grdc, s=4)
        ax0.tick_params(axis='both', which='major', labelsize=8)
        ax0.set_xlim(0,vmax), ax0.set_ylim(0,vmax)
        ax0.set_ylabel('GRDC', fontsize=8), ax0.set_xlabel('GSIM', fontsize=8)

        # Plot time-series
        ax1.plot(grdc.index, grdc, label='GRDC',  c='b', linewidth=1)
        ax1.plot(gsim.index, gsim, label='GSIM', c='r', linewidth=0.5, marker='o', markersize=3)
        ax1.tick_params(axis='both', which='major', labelsize=8)
        ax1.set_xlabel('Dates', fontsize=8), ax1.set_ylabel('Discharge (m3/s)', fontsize=8)
        ax1.legend()

        # Plot time-series
        ax2.bar(df_tmp.index, df_tmp.resid, 1)
        ax2.tick_params(axis='both', which='major', labelsize=8)
        ax2.set_xlabel('Dates', fontsize=8), ax2.set_ylabel('Change in discharge (m3/s)', fontsize=8)
        ax2.grid(visible=True, which='major', axis='y', alpha=0.35)

        fig.tight_layout()
        if export == True: fig.savefig(f"./results/{col['GRDC']}.png", bbox_inches='tight')
        plt.show()
    print("  '-> Plotting finished")
    
# Combining GSIM dataset with selected GRDC time-series
stations = df_gsim.columns.tolist()
dates = pandas.date_range(df_gsim.index[0], df_grdc.index[-1], freq='MS')
data = numpy.empty((len(dates), df_gsim.shape[1]))
for station in stations:
    i = stations.index(station)
    if station in stations_sel:
        grdc, gsim = df_grdc.loc[:,str(stations_dict[station])], df_gsim.loc[:,station]
        df_tmp = pandas.DataFrame([grdc, gsim], index=['grdc','gsim']).T
        ts = numpy.where(pandas.notna(df_tmp.grdc), df_tmp.grdc, df_tmp.gsim)
    else:
        ts = df_gsim.loc[:,station].reindex(dates)
    data[:,i] = ts
df_out = pandas.DataFrame(data, index=dates, columns=df_gsim.columns)

# Exporting
df_out.T.to_csv('./results/GSIM-GRDC_discharges.csv', sep=';')
print('Done!')