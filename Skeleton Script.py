import czifile
import matplotlib.pyplot as plt
import scipy.ndimage as ndi
import skimage.filters as skfilt
import csv
import os 
from skimage import morphology
from skan import csr

input_folder_name='data' #input folder name
output_folder='tables' #output folder name
spacing_nm = (0.75, 0.08, 0.08) #pixel dimensions in format XY, Z, Z - they ask for pixel spacing, I am not sure I am right here. Must check

#Import files
li=os.listdir(input_folder_name)
filename_list=[]
for el in li:
    if el[-3:]=='czi':
	    filename_list.append(el)
print(filename_list)

# Starts for loop 
for i,filename in enumerate(filename_list):
    print('processing file {}, this is file {} of {}'.format(filename,i+1,len(filename_list)))
    
    
#identifies filepath for saving example skeleton image from file under the same name in same places
    filepath = 'data/{}'.format(filename)
# Loads czi data 
    mydata = czifile.imread('data/{}'.format(filename))
# czi data has unnecessary dimensions as printed below
    print("The data we loaded has shape")
    print(mydata.shape)
# unnecessary czi dimensions are removed by removing all dimensions that = 1
    mydata = mydata.squeeze()
    print("The data we squeezed has shape")
    print(mydata.shape)
# define channels, we are only interested in channel 2 as that is what 
# the mitochondrial stain is detected up in
    channel2 = mydata[1]
    print("Channel 2 data has shape:", channel2.shape)
# gaussian filter the mitochondrial channel
    filtered2 = ndi.gaussian_filter(channel2, 1.0)
# define threshold value of the filtered image using otsu algorithm
    threshold_value2 = skfilt.threshold_otsu(filtered2)
#Subtract threshold value from image to get 3d binary stack
    mask2 = filtered2 >= threshold_value2
    
#Consider filtering branches by using shape index
    
#Generate Skeleton from 3d binary stack
    skeleton = morphology.skeletonize_3d(mask2)
#analyse skeleton using Skan
    pixel_graph, coordinates, degrees, = csr.skeleton_to_csgraph(skeleton, spacing=spacing_nm)
# summarize data into skeleton; need to ensure spacing is correct. 
    branch_data = csr.summarise(skeleton, spacing=spacing_nm)
# export raw branch_data to csv file
    branch_data_csv = branch_data.to_csv("{}/Skeleton_Table_{}.csv".format(output_folder,filename), index= None, header=True)
    print('raw skeleton data has been exported')
# Open list & define each of the mean values of the branch data
    skeleton_stats_list = [['branch-distance', 'branch-type','img-coord-0-0','img-coord-0-1',
               'img-coord-0-2','img-coord-1-0','img-coord-1-1',
               'img-coord-1-2','coord-0-0','coord-0-1',
               'coord-0-2','coord-1-0','coord-1-1',
               'coord-1-2','euclidean-distance']]
# Generate mean values for each of the parameters described
# in the skeleton_stats_list
    skeleton_stats = [
            branch_data['branch-distance'].mean(),
            branch_data['branch-type'].mean(),
            branch_data['img-coord-0-0'].mean(),
            branch_data['img-coord-0-1'].mean(),
            branch_data['img-coord-0-2'].mean(),
            branch_data['img-coord-1-0'].mean(),
            branch_data['img-coord-1-1'].mean(),
            branch_data['img-coord-1-2'].mean(),
            branch_data['coord-0-0'].mean(),
            branch_data['coord-0-1'].mean(),
            branch_data['coord-0-2'].mean(),
            branch_data['coord-1-0'].mean(),
            branch_data['coord-1-1'].mean(),
            branch_data['coord-1-2'].mean(),
            branch_data['euclidean-distance'].mean(),
            ]
# add averaged values in skeleton_stats to the skeleton_stats_list we created earlier    
    skeleton_stats_list.append(skeleton_stats)
    file_out = open("{}/Skeleton_Stats_{}.csv".format(output_folder,filename), "w")
    writer = csv.writer(file_out)
    writer.writerows(skeleton_stats_list)
    file_out.close()
    print('skeleton_stats has been exported')
# draw example skeleton and export to 'data'
    from skan import draw
    fig, ax = plt.subplots()
    draw.overlay_skeleton_2d(channel2[6], skeleton[6], dilate=1, axes=ax);
    plt.savefig('{}_mask1.png'.format(filepath))
    plt.close()
    print('skeleton figure has been exported')
    
    