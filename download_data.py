from bloby.BossDataFetcher import fetch_data_from_boss

boss_params = {
    'config': 'neurodata.cfg',
    'collection': 'cell_detection',
    'experiment': 'Insula_Atenolol-1_171204_new',
    'channel': 'Ch1',
    'dtype': 'uint16',
    'z_range': [0, 1280],
    'y_range': [0, 2560],
    'x_range': [0, 2160],
    'resolution': 0,
    'filename': 'atenolol_r0.tiff'
}

fetch_data_from_boss(boss_params)
