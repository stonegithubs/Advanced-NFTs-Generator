from settings import GlobalSettings, CharacterSettings
from libs import PathsHandling, Logger
from pathlib import Path

import os


class ExceptionsHandling:
    @staticmethod
    def order_change_mode(current_exception: list[str], layers_list: list[str]) -> str:
        '''Returns the mode of the order change.
        
        Args:
            current_exception (list[str]): Current exception handled in the loop.
            layers_list (list[str]): The list of all the layers found inside the 'paths' var.
            
        Returns:
            str: The mode of the order change.
        '''
        
        order_change_mode = GlobalSettings.order_change_modes[0]
    
        # Layer before image check
        if current_exception[1] in layers_list:
            order_change_mode = GlobalSettings.order_change_modes[1]
        # Image before layer check
        if current_exception[2] in layers_list:
            order_change_mode = GlobalSettings.order_change_modes[2]
        # Layer before layer check
        if current_exception[1] in layers_list and order_change_mode == GlobalSettings.order_change_modes[2]:
            order_change_mode = GlobalSettings.order_change_modes[3]
            
        if order_change_mode != GlobalSettings.order_change_modes[0] and len(current_exception) > 3:
            Logger.pyprint('In this mode, "ORDER CHANGE" only supports two images / layers', 'WARN', True)
            
        return order_change_mode
    
    
    @staticmethod
    def order_change(paths: list[Path], current_exception: list[str]) -> list[Path]:
        '''Change the order between two images or one image and layers.
        
        Examples:
            - ["ORDER_CHANGE", "name", "put_before_this_layer"]
            - ["ORDER_CHANGE", "name", "put_before_this_image"]
            - ["ORDER_CHANGE", "layer", "put_before_this_image"]
            - `/!\ Not implemented yet /!\` ["ORDER_CHANGE", "layer", "put_before_this_layer"]

        Args:
            paths (list[Path]): List of all the paths used for one NFT.
            current_exception (list[str]): Current exception handled in the loop.

        Returns:
            list[Path]: Modified list of paths.
        '''
        
        layers_list = PathsHandling.get_layer_names_from_paths(paths)
        order_change_mode = ExceptionsHandling.order_change_mode(current_exception, layers_list)

        # IMAGE BEFORE IMAGE
        if order_change_mode == GlobalSettings.order_change_modes[0]:
            first_path_index = PathsHandling.get_index_in_paths_list_from_filename(paths, current_exception[1])
            second_path_index = PathsHandling.get_index_in_paths_list_from_filename(paths, current_exception[2])

            # If these two images are detected, change the order
            if first_path_index is not None and second_path_index is not None:
                saved_path = paths[first_path_index]
                paths.pop(first_path_index)
                paths.insert(second_path_index, saved_path)


        # LAYER BEFORE IMAGE
        elif order_change_mode == GlobalSettings.order_change_modes[1]:
            paths_from_layer = PathsHandling.get_paths_from_layer_name(paths, current_exception[1])
            image_path_index = PathsHandling.get_index_in_paths_list_from_filename(paths, current_exception[2])
            
            # If the image is detected and one of the path is used, change the order
            if len(paths_from_layer) > 0 and image_path_index is not None:
                for path in paths_from_layer:

                    try:
                        paths.remove(path)
                        paths.insert(image_path_index, path)
                    except ValueError as err:
                        Logger.pyprint(f'Order change path error [{err}]', 'ERRO', True)


        # IMAGE BEFORE LAYER
        elif order_change_mode == GlobalSettings.order_change_modes[2]:
            image_path_index = PathsHandling.get_index_in_paths_list_from_filename(paths, current_exception[1])
            paths_from_layer = PathsHandling.get_paths_from_layer_name(paths, current_exception[2])
            
            # Check if there's at least one path in the list
            if len(paths_from_layer) > 0:
                order_change_path_index = paths.index(paths_from_layer[0])  # First path index in 'paths_from_layer'
            else:
                order_change_path_index = None
            
            # If the image is detected and one of the path is used, change the order
            if image_path_index is not None and order_change_path_index is not None:
                saved_path = paths[image_path_index]
                paths.pop(image_path_index)
                paths.insert(order_change_path_index, saved_path)


        # LAYER BEFORE LAYER
        elif order_change_mode == GlobalSettings.order_change_modes[3]:
            '''
            '''
            
        return paths

    
    @staticmethod
    def incompatibilities(paths: list[Path], current_exception: list[str]):
        '''Check incompatibilities with one image and one layer or multiple images.
        
        Examples:
            - ["INCOMPATIBLE", "image_1.png", "image_2.png", "image_3.png"]
            - ["INCOMPATIBLE", "image.png", "layer"]

        Args:
            paths (list[Path]): List of all the paths used for one NFT.
            current_exception (list[str]): Current exception handled in the loop.

        Returns:
            list[Path] OR None: Valid list of path or None if an incompatibility is found.
        '''
        
        paths_driver = len(paths)
        incompatibles = current_exception[1:]
        incompatibility_driver = len(incompatibles)
        
        # Check if it's a layer incompatibility
        is_layer_incompatibility = False
        layers_name_list = PathsHandling.get_layer_names_from_paths(paths)
        for i in range(incompatibility_driver):
            if incompatibles[i] in layers_name_list:
                is_layer_incompatibility = True
                break
        
        # Handles Incompatibilities between multiple images
        if not is_layer_incompatibility:
            incompatible_paths = []
            
            # Add all the images index in path to a list
            for i in range(incompatibility_driver):
                current_path_index = PathsHandling.get_index_in_paths_list_from_filename(
                                        paths,
                                        incompatibles[i]
                                     )
                incompatible_paths.append(current_path_index)
            
            # Regenerate the NFT is the images are all found
            if None not in incompatible_paths:
                Logger.pyprint('Incompatible images found', 'WARN')
                return None  # Regenerate the NFT
        
        # Handles incompatibilities with a whole layer
        else:
            if incompatibility_driver > 2:
                Logger.pyprint('Incompatibility in layer mode only supports one image and one layer', 'WARN', True)
                
            # Check if the image is used (Returns None if not)
            image_path = PathsHandling.get_index_in_paths_list_from_filename(paths, incompatibles[0])
            
            # If the image is used, check the incompatibility
            if image_path is not None:
                for i in range(paths_driver):
                    # Get the layer name of every image
                    current_layer = os.path.basename(paths[i].parent)
                    
                    # Check if the layer name is the incompatible one
                    if current_layer == incompatibles[1]:
                        Logger.pyprint('Incompatibility with a layer found', 'WARN')
                        return None  # Regenerate the NFT

        return paths
    
    
    @staticmethod
    def delete(paths: list[Path], current_exception: list[str]):
        '''Delete all the layers listed (for a full suit etc..)
        
        Example:
            - ['DELETE', 'space suit.png', '05_jackets', '03_trousers']

        Args:
            paths (list[Path]): List of all the paths used for one NFT.
            current_exception (list[str]): Current exception handled in the loop.

        Returns:
            list[Path]: Modified list of paths.
        '''
        
        image_path_index = PathsHandling.get_index_in_paths_list_from_filename(paths, current_exception[1])
        
        if image_path_index is not None:
            layers_to_delete = current_exception[2:]
            driver = len(layers_to_delete)
            
            for i in range(driver):
                paths = PathsHandling.delete_paths_from_layer_name(paths, layers_to_delete[i])
        
        return paths
            


    @staticmethod
    def exceptions_handling(paths: list[Path], settings: CharacterSettings):
        '''Handle multiple exceptions / incompatibilities between layers.
        
        - 'ORDER_CHANGE' -> Change the order between two layers / images.
        - 'INCOMPATIBLE' -> NFT is regenerated if the test is not passed.
        - 'DELETE' -> Deletes all the images of specific layers if the specified image is used.

        Args:
            paths (list[Path]): Randomized character paths list.
            settings (CharacterSettings): Link to the settings.
            
        Returns:
            list[Path] OR None: Modified paths list. (Or None if the NFT needs to be regenerated)
        '''
    
        exceptions = settings.exceptions
        exceptions_driver = len(exceptions)
        
        for i in range(exceptions_driver):
            current_exception = exceptions[i]
            
            # Order change exception (Returns the default 'paths' var if unavailable)
            if current_exception[0] == GlobalSettings.exceptions_list[0]:
                paths = ExceptionsHandling.order_change(paths, current_exception)
                
            # Incompatibility exception (Returns None to regenerate the NFT)
            elif current_exception[0] == GlobalSettings.exceptions_list[1]:
                paths = ExceptionsHandling.incompatibilities(paths, current_exception)
                
                # If it's incompatible, it's not necessary to continue the exceptions handling
                if paths is None:
                    break
            
            # Delete exception (Deletes multiple layers)
            elif current_exception[0] == GlobalSettings.exceptions_list[2]:
                paths = ExceptionsHandling.delete(paths, current_exception)
                
            # Error
            else:
                Logger.pyprint(f'Invalid exception name in {current_exception}', 'ERRO', True)
        
        return paths
