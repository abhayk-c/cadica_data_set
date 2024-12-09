from .cadica_constants import *
from .cadica_errors import*
import os
from enum import Enum

base_path = "/Users/abhaycuram/Desktop/ML Projects/Jeremy Fast AI/Data Sets/CADICA"

class CadicaDataSetSamplingPolicy(Enum):
    NONE = 1
    BALANCED_SAMPLING = 2

class CadicaDataSet:

    #region Initialization
    
    def __init__(self, path):
        if os.path.isdir(path):
            self.base_path = path
            self.lesioned_image_paths_dict = {}
            self.nonlesioned_image_paths_dict = {}
            self.lesioned_images_set = set()
            self.nonlesioned_images_set = set()
        else:
            raise CadicaDataSetError.root_dir_not_found() 
    
    #endregion

    #region Core Public Methods
    
    def load(self):
        if os.path.isdir(self.base_path):
            selectedVideosPath = os.path.join(self.base_path, CadicaConstants.VIDEOS_DIR)
            if os.path.isdir(selectedVideosPath):
                patient_dir_paths = list(map(lambda dir: os.path.join(selectedVideosPath, dir), filter(lambda dir: not dir.startswith('.'), os.listdir(selectedVideosPath))))
                for patient_dir_path in patient_dir_paths:
                    if os.path.isdir(patient_dir_path):
                        lesion_videos_txt_file_path = os.path.join(patient_dir_path, CadicaConstants.LESION_VIDEOS_TXT)
                        non_lesion_videos_txt_file_path = os.path.join(patient_dir_path, CadicaConstants.NONLESION_VIDEOS_TXT)
                        if os.path.isfile(lesion_videos_txt_file_path) and os.path.isfile(non_lesion_videos_txt_file_path):
                            lesion_video_dirs = self._read_cadica_txt_file(lesion_videos_txt_file_path)
                            nonlesion_video_dirs = self._read_cadica_txt_file(non_lesion_videos_txt_file_path)
                            lesion_video_dir_paths = list(map(lambda dir: os.path.join(patient_dir_path, dir), lesion_video_dirs))
                            nonlesion_video_dir_paths = list(map(lambda dir: os.path.join(patient_dir_path, dir), nonlesion_video_dirs))
                            if lesion_video_dir_paths:
                                for lesion_video_dir_path in lesion_video_dir_paths:
                                    if os.path.isdir(lesion_video_dir_path):
                                        path_components = (lesion_video_dir_path.strip(os.sep)).split(os.sep)
                                        video_dir = path_components[-1]
                                        patient_dir = path_components[-2]
                                        selected_image_frame_file_paths = self._get_selected_image_frame_file_paths(patient_dir, video_dir, lesion_video_dir_path)
                                        image_paths_key = os.path.join(patient_dir, video_dir)
                                        self.lesioned_image_paths_dict[image_paths_key] = selected_image_frame_file_paths
                                        self.lesioned_images_set.update(selected_image_frame_file_paths)
                                    else:
                                        raise CadicaDataSetError.video_dirs_not_found()
                            if nonlesion_video_dir_paths:
                                for nonlesion_video_dir_path in nonlesion_video_dir_paths:
                                    if os.path.isdir(nonlesion_video_dir_path):
                                        path_components = (nonlesion_video_dir_path.strip(os.sep)).split(os.sep)
                                        video_dir = path_components[-1]
                                        patient_dir = path_components[-2]
                                        selected_image_frame_file_paths = self._get_selected_image_frame_file_paths(patient_dir, video_dir, nonlesion_video_dir_path)
                                        image_paths_key = os.path.join(patient_dir, video_dir)
                                        self.nonlesioned_image_paths_dict[image_paths_key] = selected_image_frame_file_paths
                                        self.nonlesioned_images_set.update(selected_image_frame_file_paths)
                                    else:
                                        raise CadicaDataSetError.video_dirs_not_found()
                        else:
                            raise CadicaDataSetError.videos_txt_files_not_found()
                    else:
                        raise CadicaDataSetError.patient_dirs_not_found()
            else:
                raise CadicaDataSetError.selected_videos_dir_not_found()
        else:
            raise CadicaDataSetError.root_dir_not_found()
    
    def get_training_data_image_paths(self, sampling_policy: CadicaDataSetSamplingPolicy): 
        image_paths = []
        lesioned_image_paths = list(self.lesioned_image_paths_dict.values())
        nonlesioned_image_paths = list(self.nonlesioned_image_paths_dict.values())
        if sampling_policy == CadicaDataSetSamplingPolicy.NONE:
            image_paths.extend(list(lesioned_image_paths))
            image_paths.extend(list(nonlesioned_image_paths))
        elif sampling_policy == CadicaDataSetSamplingPolicy.BALANCED_SAMPLING:
            max_image_count = min(len(lesioned_image_paths), len(nonlesioned_image_paths))
            self._update_image_paths_for_balanced_sampling(image_paths, max_image_count, self.nonlesioned_image_paths_dict)
            self._update_image_paths_for_balanced_sampling(image_paths, max_image_count, self.lesioned_image_paths_dict)
        return image_paths
    
    def is_lesioned_image(self, image_path):
        return image_path in self.lesioned_images_set

    def is_nonlesioned_image(self, image_path):
        return image_path in self.nonlesioned_images_set

    #endregion

    #region Private Helpers
    
    def _get_selected_image_frame_file_paths(self, patient_dir, video_dir, cur_path):        
        selected_frames_txt_file_name = "_".join([patient_dir, video_dir, CadicaConstants.SELECTED_FRAMES_TXT])
        selected_frames_txt_file_path = os.path.join(cur_path, selected_frames_txt_file_name)
        if os.path.isfile(selected_frames_txt_file_path):
            selected_image_frames = self._read_cadica_txt_file(selected_frames_txt_file_path)
            selected_image_frame_file_names = list(map(lambda image_frame: image_frame + CadicaConstants.PNG_EXT, selected_image_frames))
            return list(map(lambda image_frame_file_name: os.path.join(cur_path, CadicaConstants.INPUT_DIR, image_frame_file_name), selected_image_frame_file_names))
        else:
            raise CadicaDataSetError.selected_frames_txt_file_not_found()

    def _read_cadica_txt_file(self, file):
        lines = []
        # You might want to wrap this in a try, catch, finally just to be safe.
        f = open(file, "r")
        for line in f:
            sanitized_line = line.strip()
            lines.append(sanitized_line)
        f.close()
        return lines
    
    def _update_image_paths_for_balanced_sampling(self, image_paths, max_count, image_paths_dict):
        local_count = 0
        for image_path_key in image_paths_dict:
            if local_count >= max_count:
                break
            else:
                cur_image_paths = image_paths_dict[image_path_key]
                image_paths.extend(cur_image_paths)
                local_count += len(cur_image_paths)
    
    #endregion

cadica_data_set = CadicaDataSet(base_path)
cadica_data_set.load()
lesioned_image_paths = cadica_data_set.lesioned_image_paths_dict
nonlesioned_image_paths = cadica_data_set.nonlesioned_image_paths_dict
sorted_lesioned_image_paths = dict(sorted(lesioned_image_paths.items()))
sorted_nonlesioned_image_paths = dict(sorted(nonlesioned_image_paths.items()))
lesioned_images = cadica_data_set.lesioned_images_set
nonlesioned_images = cadica_data_set.nonlesioned_images_set
print(sorted_lesioned_image_paths)
print(sorted_nonlesioned_image_paths)
print(lesioned_images)
print(nonlesioned_images)







