import numpy as np
import matplotlib.pyplot as plt


def raster(event_times_list, color='k', cell_count=15):
    ax = plt.gca()
    #for ith, trial in enumerate(event_times_list):
    for ith, trial in (event_times_list):
        plt.vlines(trial, ith -.2, ith + .2, color=color)
    #    print ith
    #    print trial

    plt.ylim(0, cell_count+1)
    #plt.xlim(0, cell_count)
    return ax

#if __name__ == '__main__':
    #nbins = 100
    #ntrials = 10
    #spikes = []
    #for i in range(ntrials):
        #spikes.append(np.arange(nbins)[np.random.rand(nbins) < .2])
    #fig = plt.figure()
    #ax = raster(spikes)
    #plt.title('Example raster plot')
    #plt.xlabel('time')
    #plt.ylabel('trial')
    #fig.show()
