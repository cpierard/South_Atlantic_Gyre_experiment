#!/usr/bin/env python
# coding: utf-8
import xarray as xr
from parcels import FieldSet, ParticleSet, AdvectionRK4, JITParticle
from parcels import ErrorCode, DiffusionUniformKh, Field #, AdvectionDiffusionM1
from datetime import timedelta
import datetime
import numpy as np
import pickle

n_points = 10000 # particles per sampling site
n_days = 2#(9*30)+(365*2) # number of days to simulate
K_bar = 10 # diffusion value
n_site = 13

# The file go from:
# 23 oct 2018 - 23 nov 2018
# 23 nov 2018 - 23 dic 2018
# 23 dic 2018 - 23 jan 2019
# data = '../data/GLOBAL_ANALYSIS_FORECAST_PHY_001_024_SMOC/*.nc' # local computer
data = '/data/oceanparcels/input_data/CMEMS/GLOBAL_ANALYSIS_FORECAST_PHY_001_024_SMOC/*.nc' #gemini

filesnames = {'U': data,
             'V': data}

variables = {'U': 'utotal',
             'V': 'vtotal'} # Use utotal

dimensions = {'lat': 'latitude',
              'lon': 'longitude',
              'time': 'time'}
indices = {'lat': range(1, 900), 'lon': range(1284, 2460)}

def delete_particle(particle, fieldset, time, indices=indices):
    particle.delete()

# 24 samples going from 4 jan to 23 jan 2019
fieldset = FieldSet.from_netcdf(filesnames, variables, dimensions,
                                allow_time_extrapolation=False, indices=indices)

# Diffusion
size2D = (fieldset.U.grid.ydim, fieldset.U.grid.xdim)

fieldset.add_field(Field('Kh_zonal', data=K_bar * np.ones(size2D),
                         lon=fieldset.U.grid.lon, lat=fieldset.U.grid.lat,
                         mesh='spherical'))
fieldset.add_field(Field('Kh_meridional', data=K_bar * np.ones(size2D),
                         lon=fieldset.U.grid.lon, lat=fieldset.U.grid.lat,
                         mesh='spherical'))

# Opening file with positions and sampling dates.
infile = open('NIOZ_sampling_locations.pkl','rb')
nioz_samples = pickle.load(infile)
infile.close()

np.random.seed(0) # to repeat experiment in the same conditions
# Create the cluster of particles around the sampling site
# with a radius of 1/24 deg (?). 
lon_cluster = (np.random.rand(n_points)-0.5)/24 + nioz_samples['longitude'][n_site]
lat_cluster = (np.random.rand(n_points)-0.5)/24 + nioz_samples['latitude'][n_site]
date_cluster = np.repeat(nioz_samples['date'][n_site], n_points)
pset = ParticleSet.from_list(fieldset=fieldset, 
                             pclass=JITParticle,  # the type of particles (JITParticle or ScipyParticle)
                             lon=lon_cluster, # 
                             lat=lat_cluster, 
                             time=date_cluster)

# creating the Particle set
pset = ParticleSet.from_list(fieldset=fieldset,
                             pclass=JITParticle,
                             lon=lon_cluster,
                             lat=lat_cluster,
                             time=date_cluster)

# Output file
output_file = pset.ParticleFile(name=f"/scratch/cpierard/SAG/test_SAG_K{K_bar}_site{n_site}", outputdt=timedelta(hours=24))

# Execute!
pset.execute(pset.Kernel(AdvectionRK4) + DiffusionUniformKh,
             runtime=timedelta(days=n_days),
             dt=timedelta(hours=1),
             output_file=output_file,
            recovery={ErrorCode.ErrorOutOfBounds:delete_particle})
output_file.close()

