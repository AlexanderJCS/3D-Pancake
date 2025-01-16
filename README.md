# 3D-Pancake

3D Pancake is a modified version of the algorithm described in the [Morales et al. 2013](https://doi.org/10.3389/fnana.2013.00020) paper. In short, it generates a 2-manifold mesh (i.e., a mesh that is three-dimensional but has no volume) that closely follows the morphology of the postsynaptic density (PSD). The mesh's surface area is then calculated to give an accurate measurement of the PSD's surface area.

We are interested in the 2-manifold surface area of the PSD since it is a good proxy of the PSD's surface area in apposition to the presynaptic active zone, which has been previously correlated to synaptic strength.

The main motivation for the 3D Pancake algorithm is to provide a more accurate and consistent method for calculating the PSD surface area for SBF-SEM datasets. According to our testing, prior voxel-to-mesh or voxel-to-surface-area algorithms are inaccurate. The [Morales et al. 2013](https://doi.org/10.3389/fnana.2013.00020) algorithm fails to accurately calculate PSD surface area for SBF-SEM datasets, since it was designed for FIB-SEM (which has a higher z-resolution). The 3D Pancake algorithm modifies the Morales et al. 2013 method to work better with SBF-SEM datasets. In addition, it is implemented as a plugin for the [Dragonfly 3D World software](https://dragonfly.comet.tech/en/product-overview/dragonfly-3d-world), a more widely-used software for analyzing large 3D datasets.

## Installation

Please read the [installation instructions](./INSTALLATION.md) for information on how to install the plugin.

## User Guide

Please see the [user guide](USER_GUIDE.md) to learn how to use this plugin.

## Run Configurations

If you plan on developing this plugin, you will most likely want to run some test scripts. Below show the PyCharm run configurations for different scripts. Before doing this, make sure to follow Dragonfly's [PyCharm setup guide for plugin development](https://dev.theobjects.com/dragonfly_4_0_release/Documentation/SetupForDevelopmentWithPyCharm/setupfordevelopmentwithpycharm.html).

### Quick Run
![image](https://github.com/user-attachments/assets/b6380e15-d80d-4d00-a994-35d4e6b99636)

### Accuracy Tests
![image](https://github.com/user-attachments/assets/dde907cb-8764-47c1-8369-277ddeb2a201)

### Time Tests
![image](https://github.com/user-attachments/assets/da967456-2dc8-49a2-8598-ca08a781faa6)