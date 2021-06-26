# Class for grid settings and plotting maps on the grid
# Latitudes are at [90, -90] with decreasing order
# Longitudes are at [-180, 180] with increasing order

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from matplotlib.patches import Ellipse, Circle
from matplotlib import cm

rainbow = {"red"   : ((0., 0.53, 0.53), (0.077, 0.69, 0.69), (0.154, 0.84, 0.84), (0.231, 0.1,  0.1),  (0.308, 0.32, 0.32), (0.385, 0.48, 0.48), (0.462, 0.3,  0.3),  (0.539, 0.56, 0.56), (0.616, 0.79,  0.79),  (0.693, 0.965, 0.965), (0.77, 0.96, 0.96), (0.847, 0.94, 0.94), (0.924, 0.91,  0.91),  (1., 0.86, 0.86)),
           "green" : ((0., 0.18, 0.28), (0.077, 0.47, 0.47), (0.154, 0.75, 0.75), (0.231, 0.39, 0.39), (0.308, 0.54, 0.54), (0.385, 0.68, 0.68), (0.462, 0.7,  0.7),  (0.539, 0.79, 0.79), (0.616, 0.875, 0.875), (0.693, 0.93,  0.93),  (0.77, 0.75, 0.75), (0.847, 0.57, 0.57), (0.924, 0.375, 0.375), (1., 0.02, 0.02)),
           "blue"  : ((0., 0.45, 0.45), (0.077, 0.65, 0.65), (0.154, 0.87, 0.87), (0.231, 0.69, 0.69), (0.308, 0.78, 0.78), (0.385, 0.87, 0.87), (0.462, 0.39, 0.39), (0.539, 0.53, 0.53), (0.616, 0.67,  0.67),  (0.693, 0.33,  0.33),  (0.77, 0.25, 0.25), (0.847, 0.18, 0.18), (0.924, 0.11,  0.11),  (1., 0.05, 0.05))}

diverge = {"red"   : ((0., 0.24, 0.24), (0.1, 0.23, 0.23), (0.2, 0.46, 0.46), (0.3, 0.7,  0.7),  (0.4, 0.9,  0.9),  (0.5, 1.0,  1.0),  (0.6, 1.0,  1.0),  (0.7, 0.97, 0.97), (0.8, 0.93, 0.93), (0.9, 0.82, 0.82), (1., 0.7,  0.7)),
           "green" : ((0., 0.32, 0.32), (0.1, 0.54, 0.54), (0.2, 0.71, 0.71), (0.3, 0.86, 0.86), (0.4, 0.96, 0.96), (0.5, 0.98, 0.98), (0.6, 0.89, 0.89), (0.7, 0.74, 0.74), (0.8, 0.53, 0.53), (0.9, 0.3,  0.3),  (1., 0.11, 0.11)),
           "blue"  : ((0., 0.63, 0.63), (0.1, 0.79, 0.79), (0.2, 0.89, 0.89), (0.3, 0.96, 0.96), (0.4, 0.99, 0.99), (0.5, 0.82, 0.82), (0.6, 0.66, 0.66), (0.7, 0.49, 0.49), (0.8, 0.34, 0.34), (0.9, 0.24, 0.24), (1., 0.24, 0.24))}

RE = 6.371229E6 # Earth radius

def getStep(minval, maxval):
    steps = np.array([5, 10, 20, 30, 60])
    idx = np.searchsorted(steps, (maxval-minval)/5.)
    idx = min(idx, len(steps)-1)
    return steps[idx]

# Get boundes for grid cells (mid-between the nodes, dimension one larger than that of nodes)
def getBounds(nodes):
    bounds = (nodes[1:] + nodes[:-1])/2.
    bound0 = nodes[0] - (nodes[1]-nodes[0])/2.
    boundN = nodes[-1] + (nodes[-1]-nodes[-2])/2.
    return np.append(np.append(bound0, bounds), boundN)

# Get min/max bounds of grid cells from bounds array
def getMinMaxBnd(bounds):
    minbnd = bounds[:-1] if bounds[-1] > bounds[0] else bounds[1:]
    maxbnd = bounds[1:] if bounds[-1] > bounds[0] else bounds[:-1]
    return minbnd, maxbnd

class Grid:

    # Grid can be initialized in two ways:
    # - by grid dimensions (nlat/nlon) => regular grid is set to fit in
    # - by grid nodes (lat/lon) => grid cell bounds are adapted to fit in
    def __init__(self, nlat = None, nlon = None, lat = None, lon = None):
        if nlat is not None and nlon is not None:
            self.nlat = nlat
            self.nlon = nlon
            lat_step = 180./nlat
            lon_step = 360./nlon
            self.lat = np.arange(  90 - lat_step/2., -90, -lat_step)
            self.lon = np.arange(-180 + lon_step/2., 180, lon_step)
        if lat is not None and lon is not None:
            self.nlat = len(lat)
            self.nlon = len(lon)
            self.lat = np.clip(lat, -90, 90)
            self.lon = np.clip(lon, -180, 180)
        self.meshlat = np.clip(getBounds(self.lat), -90, 90)
        self.meshlon = np.clip(getBounds(self.lon), -180, 180)
        self.dlat = np.abs(self.meshlat[1:] - self.meshlat[:-1])
        self.dlon = np.abs(self.meshlon[1:] - self.meshlon[:-1])
        self.lonmin, self.lonmax = getMinMaxBnd(self.meshlon)
        self.latmin, self.latmax = getMinMaxBnd(self.meshlat)
        self.meshlon, self.meshlat = np.meshgrid(self.meshlon, self.meshlat)
        self.area = 2 * RE**2 * self.dlon[None,:] * np.pi/180 * np.sin(0.5 * self.dlat[:,None] * np.pi/180) * np.cos(self.lat[:,None] * np.pi/180)
        self.dx = self.dlon[None,:]/360 * 2*np.pi*RE * np.cos(self.lat[:,None] * np.pi/180)
        self.dy = self.dlat[:,None]/180 * np.pi*RE * np.ones_like(self.dlon[None,:])
        self.contfrac = 1

    def meanmask(self, data, mask = 1, dosum = False):
        if hasattr(data, "mask"): loc_area = np.where(data.mask == False, self.area * self.contfrac * mask, 0)
        else: loc_area = self.area * self.contfrac * mask
        if dosum == False: out = (data * loc_area).sum(axis=-1).sum(axis=-1) / loc_area.sum(axis=-1).sum(axis=-1)
        else: out = (data * loc_area).sum(axis=-1).sum(axis=-1)
        return out

    def plotmap(self, data, ptype = "map", title = "", ltitle = "", rtitle = "", info = None, filename = "test.png", dpi = 125,
                drawcoast = True, drawgrid = True, levels = 20, vmin = None, vmax = None, bounds = None, ticks = None, zoom = dict(north = 90, south = -90, west = -180, east = 180), custom_cmap=None, plot_cbar=True, label_cbar=None, region=None,cmap_ticks=None,cbar_tick_labels=None,alpha=None):

        # What version supports using an array for alpha?  More recent
        # than 3.4.
        print("Plotting a map using Matplotlib version {}.".format(matplotlib.__version__))

        # I need an axes object for some of these methods
        fig, ax = plt.subplots(figsize=(7, 7))

        delta = 3
        north = min( 90, max(self.lat) + delta, zoom["north"] + delta)
        south = max(-90, min(self.lat) - delta, zoom["south"] - delta)
        west = max(-180, min(self.lon) - delta, zoom["west"] - delta)
        east = min( 180, max(self.lon) + delta, zoom["east"] + delta)
        m = Basemap(projection = "mill", llcrnrlat = south, urcrnrlat = north, llcrnrlon = west, urcrnrlon = east, resolution = "l")
        if drawcoast: m.drawcoastlines(linewidth=0.5)
        if drawgrid:
            if north-south > 150: parallels = [-80, -60, -30, 0, 30, 60, 80]
            else: parallels = np.arange(-90, 91, getStep(south, north))
            m.drawparallels(parallels, labels = [1, 0, 1, 1])
            m.drawmeridians(np.arange(-180, 181, getStep(west, east)), labels = [0, 0, 0, 1])
        if ptype == "map":
            cmap = matplotlib.colors.LinearSegmentedColormap("my_colormap", rainbow, levels)
        elif ptype == "dif":
            cmap = matplotlib.colors.LinearSegmentedColormap("my_colormap", diverge, levels)
            lim = max(abs(np.percentile(data.compressed(), 1)), abs(np.percentile(data.compressed(), 99))) if type(data) is np.ma.masked_array else max(abs(np.percentile(data, 1)), abs(np.percentile(data, 99)))
            vmin = -lim
            vmax = lim
        elif ptype == "custom_cmap":
            cmap = custom_cmap
        elif ptype == "correlation":
            cmap = plt.get_cmap("coolwarm")
        elif ptype == 'correlation_truncated':

            # The point of this is go from blue to white, then stay white for
            # a while, and then go white to red.  In this way, weak correlation
            # values won't be shown.
            coolwarm = cm.get_cmap('coolwarm', 256)
            cool=coolwarm(0.0)
            warm=coolwarm(1.0)
            trunc_colors = {"red"   : [[0.0, cool[0], cool[0]],
                                       [0.4, 1.0, 1.0],
                                       [0.6, 1.0, 1.0],
                                       [1.0, warm[0], warm[0]]],
                            "green"   : [[0.0, cool[1],cool[1]],
                                         [0.4, 1.0, 1.0],
                                         [0.6, 1.0, 1.0],
                                         [1.0, warm[1],warm[1]]],
                            "blue"   : [[0.0, cool[2],cool[2]],
                                        [0.4, 1.0, 1.0],
                                        [0.6, 1.0, 1.0],
                                        [1.0, warm[2],warm[2]]]}
            cmap = matplotlib.colors.LinearSegmentedColormap("my_colormap", trunc_colors, levels)

        #endif

        norm = None if bounds is None else matplotlib.colors.BoundaryNorm(boundaries=bounds, ncolors=levels)
        if bounds is not None: vmin = vmax = None
        o = (self.meshlat <= north) & (self.meshlat >= south) & (self.meshlon >= west) & (self.meshlon <= east)
        inorth = np.where(self.lat <= north)[0][0]
        isouth = np.where(self.lat >= south)[0][-1]
        iwest = np.where(self.lon >= west)[0][0]
        ieast = np.where(self.lon <= east)[0][-1]
        cmesh = m.pcolormesh(self.meshlon[inorth:isouth+2,iwest:ieast+2], self.meshlat[inorth:isouth+2,iwest:ieast+2], data[inorth:isouth+1,iwest:ieast+1],
                                 shading = "flat", cmap = cmap, latlon = True, vmin = vmin, vmax = vmax, norm = norm, alpha = alpha)
        if plot_cbar:
            cbar = m.colorbar(cmesh, pad = 0.08, location = "right")
            if label_cbar is not None:
                cbar.set_label(label_cbar)
            #endif
            if cbar_tick_labels is not None:
                cbar.set_ticklabels(cbar_tick_labels)
            #endif
        #endif
        if bounds is not None: cbar.set_ticks(bounds)
        if ticks is not None: cbar.set_ticks(ticks)
        if info is not None: plt.annotate(info, xy = (0.05, 0.05), xycoords = "axes fraction")
        if title != "": plt.title(title)
        if ltitle != "": plt.title(ltitle, loc = "left")
        if rtitle != "": plt.title(rtitle, loc = "right")
        # Plot some regions
        if region: # This is a list of lists

            #x,y=m(0.0,0.0)
            #print("Origin at ",x,y)

            for region_bounds in region: # [lon, lat, width, height, angle]
                # The map returns lon,lat
                x,y=m(region_bounds[0],region_bounds[1])
                #ax.text(x, y, 'Lagos{}'.format(region_bounds[0]),fontsize=12,fontweight='bold',
                #    ha='left',va='bottom',color='k')
                delx,dely=m(region_bounds[2],region_bounds[3])
                width1,height1=m(region_bounds[0]-region_bounds[2],region_bounds[1]-region_bounds[3])
                width2,height2=m(region_bounds[0]+region_bounds[2],region_bounds[1]+region_bounds[3])
                width=width2-width1
                height=height2-height1
            #    print("REGION ",region_bounds,x,y,width,height)
                ax.add_artist(Ellipse((x,y), width,height,angle=region_bounds[4],fc=None,Fill=False,ec="red",lw=2))

            #endif

            ax.add_artist(Ellipse((0.0,0.0), 0.5,0.5))

        #endif

        plt.tight_layout()

        fig.savefig(filename, dpi = dpi)
        #plt.clf()
        plt.close()

    def setRegrid(self, grid):
        print("Building regrid...")
        self.reg = np.empty((grid.nlat, grid.nlon), dtype = object)
        for i in range(grid.nlat):
            for j in range(grid.nlon):
                self.reg[i,j] = []
                ns, ms = np.where( ( ((self.latmin >= grid.latmin[i]) & (self.latmin <= grid.latmax[i])) | ((self.latmax >= grid.latmin[i]) & (self.latmax <= grid.latmax[i])) | ((self.latmin <= grid.latmin[i]) & (self.latmax >= grid.latmax[i])) )[:,None] &
                                   ( ((self.lonmin >= grid.lonmin[j]) & (self.lonmin <= grid.lonmax[j])) | ((self.lonmax >= grid.lonmin[j]) & (self.lonmax <= grid.lonmax[j])) | ((self.lonmin <= grid.lonmin[j]) & (self.lonmax >= grid.lonmax[j])) )[None,:] )
                for n, m in zip(ns, ms):
                    lon1 = max(grid.lonmin[j], self.lonmin[m])
                    lon2 = min(grid.lonmax[j], self.lonmax[m])
                    lat1 = max(grid.latmin[i], self.latmin[n])
                    lat2 = min(grid.latmax[i], self.latmax[n])
                    subarea = 2 * RE**2 * (lon2-lon1) * np.pi/180 * np.sin(0.5 * (lat2-lat1) * np.pi/180) * np.cos((lat2+lat1)/2. * np.pi/180)
                    if subarea > 0: self.reg[i,j].append((n,m,subarea))
                    if subarea < 0: raise Exception("ERROR")
        self.regtask = "recalc %sx%s to %sx%s" % (self.nlat, self.nlon, grid.nlat, grid.nlon)
        print("Regrid has been set : %s" % self.regtask)

    def regrid(self, data, add_masked_area = False, ltake_dominant_fraction = False):
        # I have added the take_dominant_fraction flag.  If True, this sets
        # the value of the pixel equal to the value in the subpixel with
        # the most area.  It's use for maps that are classifications, like
        # the Koppen-Geiger maps.
        # If we have a time, lat, lon variable, do this
        if len(data.shape) == 3:
            nlat, nlon = self.reg.shape
            ntime = data.shape[0]
            newdata = np.ma.array(np.zeros((ntime, nlat, nlon)), mask=True)
            for k in range(ntime):
                print(k)
                for i in range(nlat):
                    for j in range(nlon):
                        totarea = 0
                        for n,m,subarea in self.reg[i,j]:
                            if data[k,n,m] is not np.ma.masked:
                                if newdata[k,i,j] is np.ma.masked: newdata[k,i,j] = 0
                                newdata[k,i,j] += data[k,n,m] * subarea
                            if data[k,n,m] is not np.ma.masked or add_masked_area:
                                totarea += subarea
                        if newdata[k,i,j] is not np.ma.masked: newdata[k,i,j] /= totarea
            return newdata

        # But sometimes we just have lat,lon without a time axis.  Still can regrid
        elif len(data.shape) == 2:
            nlat, nlon = self.reg.shape
            newdata = np.ma.array(np.zeros((nlat, nlon)), mask=True)
            for i in range(nlat):
                for j in range(nlon):
                    totarea = 0
                    maxarea=-1.0
                    for n,m,subarea in self.reg[i,j]:
                        if ltake_dominant_fraction:
                            if data[n,m] is not np.ma.masked:
#                                print("data ",n,m,data[n,m])
                                if subarea > maxarea:
                                    maxarea=subarea
                                    newdata[i,j]=data[n,m]
                                #endif
                            #endif
                        else:
                            if data[n,m] is not np.ma.masked:
                                if newdata[i,j] is np.ma.masked: newdata[i,j] = 0
                                newdata[i,j] += data[n,m] * subarea
                                if data[n,m] is not np.ma.masked or add_masked_area:
                                    totarea += subarea
                                    if newdata[i,j] is not np.ma.masked: newdata[i,j] /= totarea
                        #endif
                    #endfor
            return newdata

        # If we have a time, veget, lat, lon variable, do this
        elif len(data.shape) == 4:
            nlat, nlon = self.reg.shape
            ntime = data.shape[0]
            npfts = data.shape[1]
            newdata = np.ma.array(np.zeros((ntime, npfts, nlat, nlon)), mask=True)
            for k in range(ntime):
                print(k)
                for kk in range(npfts):
                    print(kk)
                    for i in range(nlat):
                        for j in range(nlon):
                            totarea = 0
                            for n,m,subarea in self.reg[i,j]:
                                if data[k,kk,n,m] is not np.ma.masked:
                                    if newdata[k,kk,i,j] is np.ma.masked: newdata[k,kk,i,j] = 0
                                    newdata[k,kk,i,j] += data[k,kk,n,m] * subarea
                                    if data[k,kk,n,m] is not np.ma.masked or add_masked_area:
                                        totarea += subarea
                                if newdata[k,kk,i,j] is not np.ma.masked: newdata[k,kk,i,j] /= totarea
            return newdata

        # The regrid above deals with a mean for the whole pixel.  For some things,
        # like forest area, we don't need the mean, we need a sum.  So we
        # repartation based on areas, and then don't divide by the total.
    def regrid_sum(self, data, add_masked_area = False):

        # If we have a time, lat, lon variable, do this
        if len(data.shape) == 3:
            nlat, nlon = self.reg.shape
            ntime = data.shape[0]
            newdata = np.ma.array(np.zeros((ntime, nlat, nlon)), mask=True)
            for k in range(ntime):
                print(k)
                for i in range(nlat):
                    for j in range(nlon):
                        #totarea = 0
                        for n,m,subarea in self.reg[i,j]:
                            if data[k,n,m] is not np.ma.masked:
                                if newdata[k,i,j] is np.ma.masked: newdata[k,i,j] = 0
                                newdata[k,i,j] += data[k,n,m] * subarea
                            #if data[k,n,m] is not np.ma.masked or add_masked_area:
                            #    totarea += subarea
                        #if newdata[k,i,j] is not np.ma.masked: newdata[k,i,j] /= totarea
            return newdata

            # But sometimes we just have lat,lon without a time axis.  Still can regrid
        elif len(data.shape) == 2:
            nlat, nlon = self.reg.shape
            newdata = np.ma.array(np.zeros((nlat, nlon)), mask=True)
            for i in range(nlat):
                for j in range(nlon):
                    #totarea = 0
                    for n,m,subarea in self.reg[i,j]:
                        if data[n,m] is not np.ma.masked:
                            if newdata[i,j] is np.ma.masked: newdata[i,j] = 0
                            newdata[i,j] += data[n,m] * subarea
                            #if data[n,m] is not np.ma.masked or add_masked_area:
                            #    totarea += subarea
                        #if newdata[i,j] is not np.ma.masked: newdata[i,j] /= totarea
            return newdata

        # If we have a time, veget, lat, lon variable, do this
        elif len(data.shape) == 4:
            nlat, nlon = self.reg.shape
            ntime = data.shape[0]
            npfts = data.shape[1]
            newdata = np.ma.array(np.zeros((ntime, npfts, nlat, nlon)), mask=True)
            for k in range(ntime):
                print(k)
                for kk in range(npfts):
                    print(kk)
                    for i in range(nlat):
                        for j in range(nlon):
                            #totarea = 0
                            for n,m,subarea in self.reg[i,j]:
                                if data[k,kk,n,m] is not np.ma.masked:
                                    if newdata[k,kk,i,j] is np.ma.masked: newdata[k,kk,i,j] = 0
                                    newdata[k,kk,i,j] += data[k,kk,n,m] * subarea
                                    #if data[k,kk,n,m] is not np.ma.masked or add_masked_area:
                                    #    totarea += subarea
                                #if newdata[k,kk,i,j] is not np.ma.masked: newdata[k,kk,i,j] /= totarea
            return newdata
