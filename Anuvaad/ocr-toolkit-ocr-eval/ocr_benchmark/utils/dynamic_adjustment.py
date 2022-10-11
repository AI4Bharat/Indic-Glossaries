import cv2
import numpy as np
import config

def get_energy_density(image):
    binary  = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,101,15)
    distance_transform =cv2.distanceTransform(binary.copy(), distanceType=cv2.DIST_L2, maskSize=5)
    energy_density = 1 /  (distance_transform + 1)**2
    cv2.imwrite('dist.png',energy_density*255)
    return energy_density

def get_equilibrium_delta(boundry,energy_density ,axis):
    # y is axis 1, x is axis 0    
    boundry_energy  = energy_density[int(boundry[0]) : int(boundry[3]) , int(boundry[1]) : int(boundry[2])]
    inital_boundry = boundry_energy.shape[1 - axis]  * 0.5
    delta = inital_boundry - np.argmin(boundry_energy.sum(axis=axis))
    return delta

def correct_region(region,energy_density):

    image_height      = energy_density.shape[0]
    box = region['boundingBox']['vertices']
    box_height =  box[3]['y'] - box[0]['y']
    box_widht  =  box[1]['x'] - box[0]['x']
    box_left   =  box[0]['x']
    box_right  =  box[1]['x']
    box_top    =  box[0]['y']
    box_bottom =  box[3]['y']

    if box_height > 0:
        #order : top, left, right, bottom
        margin = 0.25
        boundry_top    = [ max(box_top - box_height * margin ,0), box_left ,box_right ,box_top + box_height * margin]
        boundry_bottom = [ box_bottom - box_height * margin , box_left ,box_right ,min(box_bottom + box_height * margin,image_height)]

        top_delta    = get_equilibrium_delta(boundry_top , energy_density,axis=1)
        bottom_delta = get_equilibrium_delta(boundry_bottom, energy_density,axis=1)
        #print(top_delta, bottom_delta)
        region['boundingBox']= {'vertices'  : [{'x':box_left,'y':max(0,int(box_top - top_delta))},\
                                                                 {'x':box_right,'y':max(0,int(box_top - top_delta))},\
                                                                 {'x':box_right,'y':max(0,int(box_bottom -bottom_delta))},\
                                                                 {'x':box_left,'y': max(0, int(box_bottom -bottom_delta))}]}
        return region
    else:
        return region

def validate_region(region):
    box = region['boundingBox']['vertices'] 

    #check for negative coords :
    for v in box:
        for coord in v:
            if v[coord] < 0 :
                return False
    #check for orientation:
    if box[0]['y'] >= box[2]['y'] or box[0]['x'] >= box[1]['x']:
        return False
    else :
        return True


def get_corrected_regions(regions,energy_density):
    corrected_regions = []
    for idx, region in enumerate(regions ):
            try :
                if validate_region(region):
                    corrected_regions.append(correct_region(region,energy_density))
            except Exception as e :
                config.logging.error('Error in processing region {} for dm due to {}'.format(region,e),exc_info=True)
    return corrected_regions


def coord_adjustment(page_path, regions):
    energy_density    = get_energy_density(page_path)
    corrected_regions = get_corrected_regions(regions,energy_density)
    return corrected_regions



