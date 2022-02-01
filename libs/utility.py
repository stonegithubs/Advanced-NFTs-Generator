from pathlib import WindowsPath
from typing import Any, Callable
from hashlib import sha1
from PIL import Image

import concurrent.futures
import random
import time
import os


class NFT:
    # Save an hash of all the paths of an NFT
    # Used to compare multiple NFTs
    NFT_COMPARISON_HASHES = []
    
    
    # @staticmethod
    # def __get_structure(folder_path: WindowsPath, returns_full_path: bool = False) -> list:
    #     '''Get the file / folder structure of a folder.

    #     Args:
    #         folder_path: Absolute path of the folder that needs to be scanned.
    #         returns_full_path: If True, returns WindowsPath-type absolute path(s).

    #     Returns:
    #         scanned: List of WindowsPath / str.
    #     '''
        
    #     data = os.listdir(folder_path)
    #     drv = len(data)
    #     scanned = []
        
    #     for i in range(drv):
    #         if returns_full_path:
    #             current_name = (folder_path / data[i]).resolve()
    #         else:
    #             current_name = data[i]
                
    #         scanned.append(current_name)
        
    #     Logger.pyprint(f'Structure scanned [{folder_path}]', 'DATA')
    #     return scanned
    
    
    # @staticmethod
    # def __get_character_layers(character_main_folder_path: WindowsPath) -> dict:
    #     '''Returns a dict that contains all the layers of a character.

    #     Args:
    #         character_main_folder_path: Absolute path to the character.

    #     Returns:
    #         character_layers_dict: Keys: layers, values: Dictionary of files (absolute path).
    #     '''
        
    #     folders = NFT.__get_structure(character_main_folder_path, True)
    #     drv = len(folders)
    #     character_layers_dict = {}
        
    #     for i in range(drv):
    #         folder_name = os.path.basename(folders[i])
    #         character_layers_dict[folder_name] = NFT.__get_structure(folders[i], True)
        
    #     Logger.pyprint('Scanned character layers', 'INFO')
    #     return character_layers_dict
    
    
    @staticmethod
    def __character_from_list(random_character_paths: list) -> Image.Image:
        '''Returns an image containing all the images from 'random_character_paths'
        added to the first image of the list.

        Args:
            random_character_paths: List of absolute path images randomly generated.

        Returns:
            img: Final character.
        '''
        
        img = Image.open(random_character_paths[0]).convert('RGBA')
        drv = len(random_character_paths)
        
        for i in range(1, drv):
            layer = Image.open(random_character_paths[i]).convert('RGBA')
            
            try:
                img = Image.alpha_composite(img, layer)
            except ValueError as err:
                Logger.pyprint(f'Alpha Composite error: {err}', 'ERRO')
                Logger.pyprint(f'Between [{random_character_paths[0]}] and [{random_character_paths[i]}] ', 'ERRO')
                
            
        Logger.pyprint('Merged images into character', 'INFO')
        return img
    
    
    @staticmethod
    def __merge_character_to_background(
        character_image: Image.Image,
        background_path: WindowsPath
    ) -> Image.Image:
        '''Merge the randomly generated character to a background.

        Args:
            character_image: Image of the generated character.
            background_path: Full absolute path of the background.

        Returns:
            bck: Image of the full NFT.
        '''
        
        bck = Image.open(background_path).convert('RGBA')
        
        try:
            bck = Image.alpha_composite(bck, character_image)
        except ValueError as err:
            Logger.pyprint(f'Alpha Composite error: {err}', 'ERRO')
            Logger.pyprint(f'Between [{bck}] and [{character_image}] ', 'ERRO')
        
        Logger.pyprint('Character merged to the background', 'INFO')
        return bck


    # @staticmethod
    # def get_index_in_paths_from_filename(paths: list, filename: str) -> int:
    #     '''Get the index of a filename inside a WindowsPath list.

    #     Args:
    #         paths: List of WindowsPath.
    #         filename: Name of the file to check.
            
    #     Returns:
    #         i: Index of the file in the list or None if not found.
    #     '''
        
    #     drv = len(paths)
        
    #     for i in range(drv):
    #         current_name = os.path.basename(paths[i])
    #         if current_name == filename:
    #             return i


    # @staticmethod
    # def __get_layers_name_from_paths(paths: list) -> list:
    #     '''Get a list of all the layers name used by 'paths'.

    #     Args:
    #         paths: List of WindowsPath.

    #     Returns:
    #         layers: Name of all the layers used in 'paths'.
    #     '''
        
    #     layers = []
    #     drv = len(paths)
        
    #     for i in range(drv):
    #         current_layer = os.path.basename(paths[i].parent)
    #         if current_layer not in layers:
    #             layers.append(current_layer)
                
    #     return layers
    
    
    # @staticmethod
    # def get_paths_in_paths_list_from_layer_name(paths: list, layer: str) -> list:
    #     '''Get a path in a paths list from a layer name.
    #     it returns a list of all paths in a specific layer.

    #     Args:
    #         paths: List of WindowsPath.
    #         layer: Name of the layer that is used to search paths.

    #     Returns:
    #         paths_in_paths_list: Every path used in the paths list that is inside the layer.
    #     '''
        
    #     paths_in_paths_list = []
    #     drv = len(paths)
        
    #     for i in range(drv):
    #         current_path_layer_name = os.path.basename(paths[i].parent)
    #         if current_path_layer_name == layer:
    #             paths_in_paths_list.append(paths[i])
                
    #     return paths_in_paths_list


    @staticmethod
    def __exception_handling(exceptions_list: list, paths: list) -> Any:
        '''Handle multiple exceptions / incompatibilities between layers.
        
        - 'ORDER_CHANGE' -> Change the order between two layers.
        - 'INCOMPATIBLE' -> NFT is regenerated if the listed images are used.

        Args:
            exceptions_list: List of all the exceptions (Check settings.py).
            paths: Original character paths list.

        Returns:
            paths: Modified paths list. (Or None if the NFT needs to be regenerated)
        '''
        
        drv = len(exceptions_list)
        paths_drv = len(paths)
        
        for i in range(drv):
            current_exception = exceptions_list[i]

            # Order changes handling
            if current_exception[0] == 'ORDER_CHANGE':
                layers_name = NFT.__get_layers_name_from_paths(paths)
                log = False
                
                # Check if it is a layer order change
                if current_exception[2] in layers_name:
                    is_layer_order_change = True
                else:
                    is_layer_order_change = False

                # Change order between two images
                if not is_layer_order_change:
                    first_path_ind = NFT.get_index_in_paths_from_filename(paths, current_exception[1])
                    second_path_ind = NFT.get_index_in_paths_from_filename(paths, current_exception[2])
                    
                    # If these two images are detected, then change the order
                    if first_path_ind is not None and second_path_ind is not None:
                        saved_path = paths[first_path_ind]
                        paths.pop(first_path_ind)
                        paths.insert(second_path_ind, saved_path)
                        log = True
                        
                # Change order between an image and a layer (Uses current_exception[2] as the layer name)
                # Note that it supports only one path, as the paths list is sorted,
                # It will use the first path in the list.
                else:
                    image_path_ind = NFT.get_index_in_paths_from_filename(paths, current_exception[1])
                    paths_from_layer = NFT.get_paths_in_paths_list_from_layer_name(paths, current_exception[2])
                    order_change_path_ind = paths.index(paths_from_layer[0])  # Index of the path
                    
                    # If the image is detected, then change the order
                    if image_path_ind is not None:
                        saved_path = paths[image_path_ind]
                        paths.pop(image_path_ind)
                        paths.insert(order_change_path_ind, saved_path)
                        log = True
                        
                if log:
                    Logger.pyprint(f'Order changed between "{current_exception[1]}" & "{current_exception[2]}"', 'DATA')
                    
            # Incompatibilities handling
            elif current_exception[0] == 'INCOMPATIBLE':
                incomp_list = current_exception[1:]
                incomp_drv = len(incomp_list)
                
                # Check if it is a layer incompatibility
                is_layer_incomp = False 
                layers_name = NFT.__get_layers_name_from_paths(paths)
                for j in range(incomp_drv):
                    if incomp_list[j] in layers_name:
                        is_layer_incomp = True
                        break
                
                # Handles Incompatibilities between multiple images
                if not is_layer_incomp:
                    incomp_paths = []
                    
                    # Add all the images index in path to a list
                    for j in range(incomp_drv):
                        current_path_ind = NFT.get_index_in_paths_from_filename(paths, incomp_list[j])
                        incomp_paths.append(current_path_ind)

                    # Regenerate the NFT is the images are all found
                    if None not in incomp_paths:
                        Logger.pyprint('Incompatible images found', 'WARN')
                        return None

                # Handles incompatibilities with a whole layer
                else:
                    # Check if the image is used (Returns None if not)
                    path_of_img = NFT.get_index_in_paths_from_filename(paths, incomp_list[0])

                    if path_of_img is not None:
                        for j in range(paths_drv):
                            # Get the layer name of every image
                            current_layer_of_img = os.path.basename(paths[j].parent)
                            
                            # Check if the layer name is the incompatible one
                            if current_layer_of_img == incomp_list[1]:
                                Logger.pyprint('Incompatibility with a layer found', 'WARN')
                                return None
                
        Logger.pyprint('Exceptions handled successfully', 'INFO')
        return paths


    @staticmethod
    def generate_unique_nft(
        settings,
        character_layers: dict,
        output_and_name_path: WindowsPath,
        is_saving_system_enabled: bool
    ):
        '''Generate an unique NFT (compared to others with a SHA1 hash).

        Args:
            settings: Settings class
            character_layers: All the layers of this character using __get_character_layers().
            output_and_name_path: Full path (Path + Name + '.png') where to save the NFT.
            is_saving_system_enabled: (FOR TESTING ONLY) Remove the saving system.
        '''

        # Multiple NFTs comparison system
        while True:
            # Generate a random background path
            background = Randomize.random_path_from_layer(character_layers, settings.backgrounds_folder)
            
            # Generate a random character (List of random paths)
            character = Randomize.character(character_layers, settings)

            # Exception Handling
            character = NFT.__exception_handling(settings.exceptions, character)

            # Comparison hash generation
            bytecode = bytes(f'__{background}__{character}__', encoding = 'utf-8')
            str_hash = sha1(bytecode).hexdigest()
            
            # If character is valid and the hash is unique, save it and break the while
            if character is not None:
                if str_hash not in NFT.NFT_COMPARISON_HASHES:
                    NFT.NFT_COMPARISON_HASHES.append(str_hash)
                    break
                Logger.pyprint(f'Duplicata of an NFT found [{str_hash}]', 'WARN')
            else:
                Logger.pyprint(f'Invalid character, the NFT will be regenerated..', 'ERRO')

        if is_saving_system_enabled:
            # Generate the image of the character
            character_image = NFT.__character_from_list(character)
        
            # Merge the background and the character image
            final_nft = NFT.__merge_character_to_background(character_image, background)
        
            # Save the image
            # character_image.save(output_and_name_path)
            final_nft.save(output_and_name_path)
        
        # Print saved image path
        Logger.pyprint(f'Saved NFT [{output_and_name_path}]', 'DATA', True)


    @staticmethod
    def generate_nfts(
        iterations: int,
        nft_names: str,
        settings,
        character_path: WindowsPath,
        output_folder_path: WindowsPath,
        is_saving_system_enabled: bool = True,
    ):
        '''Generate a number of unique NFTs for a specified character.

        Args:
            iterations: Total number of NFTs for this character.
            nft_names: Default name (coupled to a number).
            settings: Link to the settings in parameters.py.
            character_path: Path to the character layers folder.
            output_folder_path: Path to the output folder.
            is_saving_system_enabled: (FOR TESTING ONLY) Remove the saving system.
        '''
        
        # Save the time where it starts
        time_start = time.time_ns()
        
        # Get the number of zeros for zfill()
        zeros = len(str(iterations))
        
        # Get all the images and the layers
        layers = NFT.__get_character_layers(character_path)
        
        
        # Debug mode parsing
        if nft_names[0:5] == 'DEBUG':
            debug_mode = True
            debug_sleep = int(nft_names[6:]) / 1000  # Converts into ms
        else:
            debug_mode = False
            debug_sleep = 0

        # Generate every NFT with a name based on 'i' and zfill()
        for i in range(iterations):
            if not debug_mode:
                current_name = f'{nft_names}{str(i).zfill(zeros)}.png'
                nft_path = (output_folder_path / current_name).resolve()
            else:
                # (FOR TESTING ONLY) Erase the previous NFT by saving with the same name
                nft_path = (output_folder_path / 'DEBUG_NFT.png').resolve()
                time.sleep(debug_sleep)
                
            NFT.generate_unique_nft(settings, layers, nft_path, is_saving_system_enabled)

        # Print the total time that it took
        Logger.extime(time_start)
        
        # Returns True for multiprocessing purposes only
        return True
        
    
    @staticmethod
    def multiproc(function: Callable, args_list: list):
        '''Used to create multiple processes of an NFT generator.

        Args:
            function: Called function in the process.
            args_list: List of all the args for the function
            (**args_list is a list of an arguments list per function).

        **: Every object of the main args_list list is an array of arguments that will be called.
        in the order of every function, example: [[function_1_args], [function_2_args], ...].

        Returns:
            process_result: Returns a list of all the results.
        '''
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            process_result = []
            submit = [executor.submit(function, *args) for args in args_list]
            
            for process in concurrent.futures.as_completed(submit):
                process_result.append(process.result())
                
            return process_result

        
class Randomize:
    @staticmethod
    def accessories(list_of_accessories: list[WindowsPath], settings) -> list[WindowsPath]:
        '''Generate a random list of accessories based on the max amount.

        Args:
            list_of_accessories: List of all the accessories.
            settings: Link to the settings in parameters.py.

        Returns:
            accessories_paths_list: List of random accessories absolute path.
        '''
        
        added_indexes = []
        accessories_paths_list = []
        drv = len(list_of_accessories)
        
        accessories_rarity = random.randrange(0, settings.accessories_rarity)
        
        if accessories_rarity == 0:
            randomizer = random.randrange(0, settings.max_accessories_amount)
            
            while len(added_indexes) < randomizer:
                random_accessory_index = random.randrange(0, drv)
                
                # Checked if the index is not already inside of the list
                if random_accessory_index not in added_indexes:
                    added_indexes.append(random_accessory_index)
                    
            # For comparison hashing
            # Every list should be in the same order
            added_indexes.sort()

            # Add accessories path to the list
            for i in range(randomizer):
                current_path = list_of_accessories[added_indexes[i]]
                accessories_paths_list.append(current_path)

            Logger.pyprint('Random accessories generated', 'INFO')
            
        return accessories_paths_list


    @staticmethod
    def duplicator(list_of_images: list, image_rarifier: list) -> list:
        '''Allows to modify the chances to use a specific image inside a list,
        it works by duplicating the element from it's filename and insert it multiple times.
        
        Example:
            ['path_2_filename.png', 3] -> [path_0, path_1, path_2, path_2, path_2].

        Args:
            list_of_images: List of all the images inside a folder.
            image_rarifier: List of multiple arrays defined as ['image.png', number_of_duplicata].

        Returns:
            list_of_images: Modified or not by this function.
        '''
        
        drv = len(image_rarifier)
        
        for i in range(drv):
            current_list = image_rarifier[i]
            
            if current_list[1] > 1:
                is_in_list = NFT.get_index_in_paths_from_filename(list_of_images, current_list[0])
                if is_in_list is not None:
                    for _ in range(current_list[1] - 1):
                        list_of_images.insert(is_in_list, list_of_images[is_in_list])

        return list_of_images


    @staticmethod
    def character(
        character_layers: dict,
        settings
    ) -> list[WindowsPath]:
        '''Generate a random list of all tha layers for one NFT.

        Args:
            character_layers: Dictionary generated with NFT.__get_character_layers().
            settings: Link to the settings in parameters.py.

        Returns:
            character_paths: List of layers absolute path.
        '''
        
        character_paths_list = []
        keys = list(character_layers.keys())
        number_of_layers = len(keys)
        
        # All layers dict
        for i in range(number_of_layers):
            if keys[i] != settings.backgrounds_folder:
                if keys[i] != settings.accessories_folder:
                    # Add duplicated image paths to modify chances
                    current_list = Randomize.duplicator(character_layers[keys[i]], settings.image_rarifier)
                    current_list_len = len(current_list)

                    # Rarity System: Add a randomizer that includes the optional layer
                    # if the randomizer is equal to 0
                    include = True
                    if keys[i] in settings.optional_layers:
                        ind_of_rarity = settings.optional_layers.index(keys[i])
                        rnd_optional = random.randrange(0, settings.optional_rarity[ind_of_rarity])
                        if rnd_optional != 0:
                            include = False

                    # Add random image path if included
                    if include:
                        rnd = random.randrange(0, current_list_len)
                        character_paths_list.append(current_list[rnd])
                else:
                    # Add accessories separately
                    if settings.max_accessories_amount > 0:
                        character_paths_list += Randomize.accessories(
                            character_layers[keys[i]],
                            settings
                        )

        Logger.pyprint('Random character generated', 'INFO')
        return character_paths_list


    @staticmethod
    def random_path_from_layer(character_layers: dict, layer_name: str) -> WindowsPath:
        '''Returns a random path between all the files found inside one layer.

        Args:
            character_layers: All the layers of this character using __get_character_layers().
            layer_name: Name of one of the character layers where to get a random path.

        Returns:
            random_file[drv]: Returns a random path.
        '''
        
        paths = character_layers[layer_name]
        drv = random.randrange(0, len(paths))
        
        Logger.pyprint(f'Random path generated [{paths[drv]}]', 'DATA')
        return paths[drv]