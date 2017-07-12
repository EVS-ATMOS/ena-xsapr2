#!/usr/bin/env python
#all our favourite imports
from matplotlib import pyplot as plt
import numpy as np
import pyart
from netCDF4 import num2date
import pytz
import cartopy
import os
import sys
#warnings.filterwarnings("ignore")

def plot_xsapr2_ppi(radar, field = 'reflectivity', cmap=None,
               vmin=None, vmax=None, sweep=None, fig=None):

    if sweep is None:
        sweep = 0


    # Lets get some geographical context
    lats = radar.gate_latitude
    lons = radar.gate_longitude

    min_lon = lons['data'].min()
    min_lat = lats['data'].min()
    max_lat = lats['data'].max()
    max_lon = lons['data'].max()

    print('min_lat:', min_lat, ' min_lon:', min_lon,
          ' max_lat:', max_lat, ' max_lon:', max_lon)

    index_at_start = radar.sweep_start_ray_index['data'][sweep]
    time_at_start_of_radar = num2date(radar.time['data'][index_at_start],
                                      radar.time['units'])
    GMT = pytz.timezone('GMT')
    local_time = GMT.fromutc(time_at_start_of_radar)
    fancy_date_string = local_time.strftime('%A %B %d at %I:%M %p %Z')
    print(fancy_date_string)
    if fig is None:
        fig = plt.figure(figsize = [15,10])
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    lat_0 = display.loc[0]
    lon_0 = display.loc[1]

    # Main difference! Cartopy forces you to select a projection first!
    projection = cartopy.crs.Mercator(
                    central_longitude=lon_0,
                    min_latitude=min_lat, max_latitude=max_lat)

    title = 'X-SAPR2 ' + field.replace('_',' ') + ' \n' + fancy_date_string

    display.plot_ppi_map(
        field, 0, colorbar_flag=False,
        title=title,
        projection=projection,
        min_lon=min_lon, max_lon=max_lon, min_lat=min_lat, max_lat=max_lat,
        vmin=vmin, vmax=vmax, cmap=cmap)

    lb = display._get_colorbar_label(field)
    cb = plt.colorbar(display.plots[0], shrink=.7, aspect=30, pad=0.01)
    cb.set_label(lb)

    # Mark the radar
    display.plot_point(lon_0, lat_0, label_text='X-SAPR2')

    # Plot some lat and lon lines
    gl = display.ax.gridlines(draw_labels=True,
                              linewidth=2, color='gray', alpha=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False

def gen_name(odir, radar, field):
    rad_start_date = num2date(ena_radar.time['data'][0], ena_radar.time['units'])
    dstr = rad_start_date.strftime('%Y%d%m_%H%M')
    fname = 'xsapr2_ena_quicklook_' + field + '_' + dstr + '.png'
    fqn = os.path.join(odir, fname)
    return fqn

def auto_plot_ppi(quicklook_directory, radar, field, param_table):
    fig = plt.figure(figsize = [15,10])
    plot_xsapr2_ppi(radar, field = field, cmap=param_table[field]['cmap'],
               vmin=param_table[field]['vmin'],
                vmax=param_table[field]['vmax'], sweep = 0, fig=fig)
    plt.savefig(gen_name(quicklook_directory, radar, field))
    plt.close(fig)


if __name__ == '__main__':
    print('welcome to quicklooking')
    try:
        filename = sys.argv[1]
        odir = sys.argv[2]
    except IndexError:
        print('Usage: quicklooks.py /path/to/file.h5 /path/to/quicklooks/')

    ena_radar =  pyart.aux_io.gamic_hdf5.read_gamic(filename, file_field_names=True)
    for field_name in list(ena_radar.fields.keys()):
        try:
            print(field_name, ':', ena_radar.fields[field_name]['units'])
        except KeyError:
            print(field_name, ':', 'Unavailable')

    #page 44 of https://github.com/scollis/CfRadial/blob/master/docs/CfRadialDoc.v2.0.draft.pdf
    z_name = 'equivalent_reflectivity_factor'
    v_name = 'radial_velocity_of_scatterers_away_from_instrument'
    wth_name = 'doppler_spectrum_width'
    zdr_name = 'log_differential_reflectivity_hv'
    ldr_name = 'log_linear_depolarization_ratio_hv'
    phidp_name = 'differential_phase_hv'
    kdp_name = 'specific_differential_phase_hv'
    rhv_name = 'cross_correlation_ratio_hv'
    power_name = 'log_power'
    sqi_name = 'normalized_coherent_power'
    zc_name = 'corrected_equivalent_reflectivity_factor'
    vc_name = 'corrected_radial_velocity_of_scatterers_away_from_instrument'
    zdrc_name = 'corrected_log_differential_reflectivity_hv'
    class_name = 'radar_echo_classification'
    snr_name = 'signal_to_noise_ratio'

    trans_table = {'Z': {'standard_name': z_name, 'name': 'reflectivity'},
                   'UZ': {'standard_name': z_name, 'name': 'uncorrected_reflectivity'},
                  'UZDR1': {'standard_name': zdr_name, 'name': 'uncorrected_differential_reflectivity_1'},
                  'ZDR1': {'standard_name': zdr_name, 'name': 'differential_reflectivity_1'},
                  'CWv': {'standard_name': wth_name, 'name': 'corrected_spectral_width_vertical'},
                  'AZh': {'standard_name': z_name, 'name': 'attenuation_corrected_reflectivity_horizontal'},
                  'Wh': {'standard_name': wth_name, 'name': 'spectral_width_horizontal'},
                  'UnVh': {'standard_name': vc_name, 'name': 'unfolded_radial_velocity_horizontal'},
                  'SNRv': {'standard_name': snr_name, 'name': 'signal_to_noise_ratio_vertical'},
                  'UPHIDP': {'standard_name': phidp_name, 'name': 'unfolded_differential_phase'},
                  'KDP': {'standard_name': kdp_name, 'name': 'specific_differential_phase'},
                  'AZDR': {'standard_name': zdrc_name, 'name': 'attenuation_corrected_differential_reflectivity'},
                  'RHOHV': {'standard_name': rhv_name, 'name': 'cross_correlation_ratio_hv', 'units': 'unitless'},
                  'ZDR': {'standard_name': zdr_name, 'name': 'differential_reflectivity'},
                  'Wv': {'standard_name': wth_name, 'name': 'spectral_width_vertical'},
                  'Vv': {'standard_name': v_name, 'name': 'radial_velocity_vertical'},
                  'UZv': {'standard_name': z_name, 'name': 'uncorrected_reflectivity_vertical'},
                  'SQIh': {'standard_name': sqi_name, 'name': 'normalized_coherent_power_horizontal', 'units': 'unitless'},
                  'PHIDP': {'standard_name': phidp_name, 'name': 'differential_phase'},
                  'CMAP': {'standard_name': class_name, 'name': 'clutter_map', 'units': 'unitless'},
                  'SNRh': {'standard_name': snr_name, 'name': 'signal_to_noise_ratio_horizontal'},
                  'Vh': {'standard_name': v_name, 'name': 'radial_velocity_horizontal'},
                  'CWh': {'standard_name': wth_name, 'name': 'corrected_spectral_width_horizontal'},
                  'AZDR1': {'standard_name': zdrc_name, 'name': 'attenuation_corrected_differential_reflectivity_1'},
                  'UZh': {'standard_name': z_name, 'name': 'uncorrected_refelctivity_horizontal'},
                  'Zv': {'standard_name': z_name, 'name': 'reflectivity_horizontal_vertical'},
                  'URHOHV':  {'standard_name': rhv_name, 'name': 'uncorrected_cross_correlation_ratio_hv', 'units': 'unitless'},
                  'Zh': {'standard_name': z_name, 'name': 'reflectivity_horizontal_vertical'},
                  'CLASS': {'standard_name': class_name, 'name': 'echo_id', 'units': 'unitless'},
                  'UZDR': {'standard_name': zdr_name, 'name': 'uncorrected_differential_reflectivity'},
                  'UnVv': {'standard_name': vc_name, 'name': 'unfolded_radial_velocity_vertical'},
                  'SQIv': {'standard_name': sqi_name, 'name': 'normalized_coherent_power_vertical', 'units': 'unitless'}}

    for field_name in list(ena_radar.fields.keys()):
        for transfer_item in list(trans_table[field_name].keys()):
            if transfer_item != 'name':
                ena_radar.fields[field_name][transfer_item] = trans_table[field_name][transfer_item]
        ena_radar.fields[field_name]['HDF_name'] = field_name
        ena_radar.fields[trans_table[field_name]['name']] = ena_radar.fields.pop(field_name)

    for field_name in list(ena_radar.fields.keys()):
        strr = field_name + ' -: '
        for this in list(ena_radar.fields[field_name].keys()):
            if this != 'data':
                strr += this + ': ' + str(ena_radar.fields[field_name][this]) + ', '
        print(strr)

    maps = pyart.graph.cm
    nyq = ena_radar.instrument_parameters['nyquist_velocity']['data'][0]

    standard_z = {'vmin' : -40, 'vmax' : 40, 'cmap': maps.NWSRef}
    standard_zdr = {'vmin' : -10, 'vmax' : 0, 'cmap': maps.LangRainbow12}
    standard_width = {'vmin' : 0, 'vmax' : nyq/2.0, 'cmap': maps.LangRainbow12}
    standard_snr = {'vmin' : -30, 'vmax' : 30, 'cmap': maps.NWSRef}
    standard_vel = {'vmin' : -nyq, 'vmax' : nyq, 'cmap': maps.NWSVel}
    standard_zto = {'vmin' : 0, 'vmax' : 1, 'cmap': maps.LangRainbow12}
    standard_phidp_180 = {'vmin' : -180, 'vmax' : 180, 'cmap': maps.LangRainbow12}
    standard_snr = {'vmin' : -80, 'vmax' : 10, 'cmap': maps.NWSRef}

    plotting_table = {'reflectivity': standard_z,
                  'uncorrected_reflectivity': standard_z,
                  'uncorrected_differential_reflectivity_1': standard_zdr,
                  'differential_reflectivity_1': standard_zdr,
                  'corrected_spectral_width_vertical': standard_width,
                  'attenuation_corrected_reflectivity_horizontal': standard_z,
                  'spectral_width_horizontal': standard_width,
                  'unfolded_radial_velocity_horizontal': {'vmin' : -nyq*2.0, 'vmax' : nyq*2.0, 'cmap': maps.NWSVel},
                  'signal_to_noise_ratio_vertical': standard_snr,
                  'unfolded_differential_phase': {'vmin' : 0, 'vmax' : 180, 'cmap': maps.LangRainbow12},
                  'specific_differential_phase': {'vmin' : -1, 'vmax' : 8, 'cmap': maps.LangRainbow12},
                  'attenuation_corrected_differential_reflectivity': standard_zdr,
                  'cross_correlation_ratio_hv': {'vmin' : 0.5, 'vmax' : 1, 'cmap': maps.LangRainbow12},
                  'differential_reflectivity': standard_zdr,
                  'spectral_width_vertical': standard_width,
                  'radial_velocity_vertical': standard_vel,
                  'uncorrected_reflectivity_vertical': standard_z,
                  'normalized_coherent_power_horizontal': standard_zto,
                  'differential_phase': standard_phidp_180,
                  'clutter_map': {'vmin' : 0, 'vmax' : 10, 'cmap': maps.LangRainbow12},
                  'signal_to_noise_ratio_horizontal': standard_snr,
                  'radial_velocity_horizontal': standard_vel,
                  'corrected_spectral_width_horizontal': standard_width,
                  'attenuation_corrected_differential_reflectivity_1': standard_zdr,
                  'uncorrected_refelctivity_horizontal': standard_z,
                  'reflectivity_horizontal_vertical': standard_z,
                  'uncorrected_cross_correlation_ratio_hv':  {'vmin' : 0.5, 'vmax' : 1, 'cmap': maps.LangRainbow12},
                  'reflectivity_horizontal_vertical': standard_z,
                  'echo_id': {'vmin' : 0, 'vmax' : 10, 'cmap': maps.LangRainbow12},
                  'uncorrected_differential_reflectivity': standard_zdr,
                  'unfolded_radial_velocity_vertical': standard_vel,
                  'normalized_coherent_power_vertical': standard_zto}
    os.makedirs(odir, exist_ok=True)
    if ena_radar.scan_type == 'ppi':
        for fld in list(ena_radar.fields.keys()):
            print(gen_name(odir, ena_radar, fld))
            auto_plot_ppi(odir, ena_radar, fld, plotting_table)
    else:
        print('Only PPIs right now')

