import numpy as np
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import ChannelResource, ExperimentResource, CoordinateFrameResource
import configparser

class NeuroDataResource:
    def __init__(self, host, token, collection, experiment, requested_channels,
                 x_range=None,
                 y_range=None,
                 z_range=None, resolution=0):

        self._bossRemote = BossRemote({'protocol': 'https',
                                       'host': host,
                                       'token': token})
        self.collection = collection
        self.experiment = experiment
        self.resolution = resolution

        self.channels = self._bossRemote.list_channels(collection, experiment)

        if len(requested_channels) == 0:
            self.requested_channels = self.channels
        else:
            self.requested_channels = requested_channels

        self._get_coord_frame_details()
        # validate range
        #if not self.correct_range(z_range, y_range, x_range):
        #    raise Exception("Error: Inccorect dimension range")

        self.x_range = x_range or [0,self.max_dimensions[2]]
        self.y_range = y_range or [0,self.max_dimensions[1]]
        self.z_range = z_range or [0,self.max_dimensions[0]]


    def _get_coord_frame_details(self):
        exp_resource = ExperimentResource(self.experiment, self.collection)
        coord_frame = self._bossRemote.get_project(exp_resource).coord_frame

        coord_frame_resource = CoordinateFrameResource(coord_frame)
        data = self._bossRemote.get_project(coord_frame_resource)

        self.max_dimensions = (data.z_stop, data.y_stop, data.x_stop)
        self.voxel_size = (data.z_voxel_size, data.y_voxel_size, data.x_voxel_size)


    def _get_channel(self, chan_name):
        """
        Helper that gets a fully initialized ChannelResource for an *existing* channel.
        Args:
            chan_name (str): Name of channel.
            coll_name (str): Name of channel's collection.
            exp_name (str): Name of channel's experiment.
        Returns:
            (intern.resource.boss.ChannelResource)
        """
        chan = ChannelResource(chan_name, self.collection, self.experiment)
        return self._bossRemote.get_project(chan)

    def assert_channel_exists(self, channel):
        return channel in self.channels

    def get_cutout(self, chan, zRange=None, yRange=None, xRange=None):
        if chan not in self.channels:
            print('Error: Channel Not Found in this Resource')
            return
        if zRange is None or yRange is None or xRange is None:
            print('Error: You must supply zRange, yRange, xRange kwargs in list format')
            return

        channel_resource = self._get_channel(chan)
        datatype = channel_resource.datatype

        data = self._bossRemote.get_cutout(channel_resource,
                                           self.resolution,
                                           xRange,
                                           yRange,
                                           zRange)

        #Datatype check. Recast to original datatype if data is float64
        if data.dtype == datatype:
            return data
        else:
            return data.astype(datatype)

    def correct_range(self, z_range, y_range, x_range):
        x_start, x_end = x_range
        if x_start < 0 or x_end > self.max_dimensions[2]:
            return False
        y_start, y_end = y_range
        if y_start < 0 or y_end > self.max_dimensions[1]:
            return False
        z_start, z_end = z_range
        if z_start < 0 or z_end > self.max_dimensions[0]:
            return False
        return True

'''
    Parses .cfg files for BOSS metadata

    Input:
        boss_config_file neurodata.cfg file
    Output:
        Dictionary of Boss metadata
'''
def get_boss_config(boss_config_file):
    config = configparser.ConfigParser()
    config.read(boss_config_file)
    # dictionary of BOSS metadata
    remote_metadata = {}
    # BOSS API
    remote_metadata["token"] = config['Default']['token']
    # BOSS Host
    remote_metadata["host"] = config['Default']['host']
    # Boss experiment
    remote_metadata["experiment"] = config['shared']['experiment']
    # Boss collection
    remote_metadata["collection"] = config['shared']['collection']
    # Boss channels
    channels = config["Parallel"]["channels"]
    channels = channels.split(",")
    remote_metadata["channels"] = channels
    # Parse x_range
    if "x_range" in config["Parallel"]:
        x_range = config["Parallel"]["x_range"]
        x_range = x_range.split(",")
        remote_metadata["x_range"] = list(map(int, x_range))
    else:
        remote_metadata["x_range"] = None
    # Parse y_range
    if "y_range" in config["Parallel"]:
        y_range = config["Parallel"]["y_range"]
        y_range = y_range.split(",")
        remote_metadata["y_range"] = list(map(int, y_range))
    else:
        remote_metadata["y_range"] = None
    # Parse z_range
    if "z_range" in config["Parallel"]:
        z_range = config["Parallel"]["z_range"]
        z_range = z_range.split(",")
        remote_metadata["z_range"]= list(map(int, z_range))
    else:
        remote_metadata["z_range"]= None


    if "resolution" in config["Parallel"]:
        remote_metadata["resolution"] = int(config["Parallel"]["resolution"])
    else:
        remote_metadata["resolution"] = 0


    return remote_metadata

'''
    Instantiate resource

    Input:
        config_file path and name of neurodata.cfg file
    Output:
        NeuroData resource
'''
def get_boss_resource(config_file):
    config = get_boss_config(config_file)
    resource = NeuroDataResource(config["host"],
                                 config["token"],
                                 config["collection"],
                                 config["experiment"],
                                 config["channels"],
                                 config["x_range"],
                                 config["y_range"],
                                 config["z_range"],
                                 config["resolution"])
    return resource
